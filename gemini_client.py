import google.genai as genai
from google.genai import types
import tempfile
import os
import logging
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Google's Gemini API for USP generation using the new google-genai SDK."""
    
    def __init__(self, api_key=None):
        """Initialize the Gemini client with API key."""
        # Use hardcoded API key as requested
        self.api_key = "AIzaSyByp7PcPQ2DqmcBfh-MZcUJZlndq8EG-cw"
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.0-flash"
        logger.info("Gemini client initialized successfully")
    
    def call_gemini_api(self, SYSTEM_PROMPT, file_content):
        """Make a call to the Gemini API with the given prompt and content."""
        try:
            start_time = time.time()
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=file_content,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.0,
                    response_mime_type="text/plain",
                )
            )
            
            if time.time() - start_time > 120:
                raise TimeoutError("Model took too long. Skipping and retrying later.")
                
            return response.text, "Gemini"
        except Exception as e:
            error_msg = f"Error calling Gemini API: {str(e)}"
            logger.error(error_msg)
            return error_msg, "Error"
    
    def generate_usp_from_pdf(self, pdf_file, existing_usp: str) -> Dict[str, Any]:
        """Generate USP from PDF using Gemini API."""
        try:
            # Create the system prompt exactly as specified
            SYSTEM_PROMPT = f"""
            You are provided with the raw OCR text extracted from a brochure for a premium residential project. Your task is to extract the unique selling propositions (USPs) that will positively influence potential buyer decisions, keeping in mind the expectations of buyers in this segment.
            Focus on the following aspects, aligning with the expectations of a premium homebuyer:
            •	Thematic and Architectural Uniqueness
            •	Facilities and Luxury Amenities
            •	Technology and Security Features 
            •	Landscape and Environment 
            •	Location Highlights 
            •	Awards and Recognition
            •	Any Other Unique Features that enhance lifestyle, convenience, and security.
            NOTE:
            •	Keep in mind that the OCR text may contain noise, so filter out any irrelevant content.
            •	Output the USPs as bullet points, ensuring each bullet point is 20 words or less.
            •	Ensure each point provides factual details about the project based on the information available in the brochure.
            •	*Important : If and only if the proper name of an architect, designer, builder, consultant, or developer is explicitly mentioned in the brochure, include it in the USPs, Do not use common nouns such as designers or architect without the presence of a proper noun*
            •	Arrange them in descending order, with the most unique and attractive USP at the top.
            •	Give priority to factual details explicitly mentioned in the text, such as the size of the clubhouse, project density, and greenery.
            •	Use a professional tone in your bullet points.
            •	Do not include headers in the bullet points.
            •	Ensure grammatical correctness and capitalize the first letters of proper nouns.
            •	Focus on: (factual information, lifestyle appeal, and renowned names associated with the project).
            •	Include unique points and factual information from the following reference points given to you.
            Reference Points:
            {existing_usp}
            """
            
            temp_file_path = None
            try:
                # Save the Streamlit UploadedFile to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    # Get raw bytes from the UploadedFile object
                    temp_file.write(pdf_file.getvalue())
                    temp_file_path = temp_file.name
                    file_upload= self.client.files.upload(file=temp_file_path)
                
                # Call Gemini API with the extracted text
                usp_result, source = self.call_gemini_api(SYSTEM_PROMPT, file_upload)
                
                if source == "Error":
                    return {"error": usp_result}
                
                logger.info("Successfully generated USPs from PDF")
                return {"original_usp": usp_result}
            finally:
                # Clean up the temporary file
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    time.sleep(3)
                
        except Exception as e:
            error_msg = f"Error generating USP from PDF: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def convert_usp_to_75_chars(self, usp_content: str) -> Dict[str, Any]:
        """Convert each USP point to 75 character limit."""
        try:
            SYSTEM_PROMPT = "Convert each point into a 75-character limit, without losing the factual data of the point:"
            
            # Call Gemini API with the text content
            result, source = self.call_gemini_api(SYSTEM_PROMPT, usp_content)
            
            if source == "Error":
                return {"error": result}
            
            logger.info("Successfully converted USPs to 75-character limit")
            return {"char_limited_usp": result}
            time.sleept(3)
        except Exception as e:
            error_msg = f"Error converting USPs to 75-character limit: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def process_pdf_for_usp(self, pdf_file, existing_usp: str) -> Dict[str, Any]:
        """Process a PDF file to generate USPs and then convert to 75-character limit."""
        try:
            # First API call: Generate USPs from PDF
            usp_result = self.generate_usp_from_pdf(pdf_file, existing_usp)
            
            if "error" in usp_result:
                return usp_result
            
            # Second API call: Convert USPs to 75-character limit
            limited_result = self.convert_usp_to_75_chars(usp_result["original_usp"])
            
            if "error" in limited_result:
                return limited_result
            
            # Return both results for display
            return {
                "original_usp": usp_result["original_usp"],
                "char_limited_usp": limited_result["char_limited_usp"]
            }
        except Exception as e:
            error_msg = f"Error in USP processing pipeline: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
