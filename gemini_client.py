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
        self.api_key = "AIzaSyB7FYoAqAbB3nRj1ceGvneHDpmR0uNXRyw"
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
You are provided with the attached brochure for a premium residential project. Your task is to extract the unique
selling propositions (USPs) that will positively influence potential buyer decisions, keeping in mind the expectations of buyers in this segment.

Focus on the following aspects, aligning with the expectations of a premium homebuyer:
• Thematic and Architectural Uniqueness  
• Facilities and Luxury Amenities (give special attention to rare or distinctive offerings)  
• Technology and Security Features  
• Landscape and Environment  
• Location Highlights  
• Awards and Recognition  
• Any Other Unique Features that enhance lifestyle, convenience, and security

# Output Rules:
- Output the USPs as bullet points (•), each with 20 words or fewer.
- Each bullet must be unique — do **not repeat or paraphrase** the same feature across multiple bullets.
- If multiple facts refer to the same feature (e.g., clubhouse size and facilities), **combine them into one single, strong bullet point**.
- Do not include section headers (like “Location” or “Amenities”) — only clean bullet points.
- Use a crisp, professional tone.
- Do not exceed 8–10 bullet points in total.

# Do NOT include generic or basic information such as:
• BHK availability  
• "RERA registered"  
• Generic mentions of water, security, or power backup  
• Statements like "modern lifestyle", "perfect home", etc. without factual support
• Do not prefix USPs with Project Name, make them standalone and self contained.

# Focus MORE on:
• Rare or luxury amenities (e.g., golf course, rooftop pool, private theatre, wellness spa, curated landscaping, etc.)  
• Concrete factual highlights (e.g., 50,000 sq. ft. clubhouse, 80% open space, 1.5-acre sky park)  
• Known celebrity architects, design firms, or international partnerships  
• Location benefits with names (e.g., "close to Airport Terminal 3", not "prime location")

# ADDITIONAL DATA SOURCE:
You may also use key points from the following reference input to enrich the USPs:
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
            time.sleep(2)
            
            if "error" in usp_result:
                return usp_result
            
            # Second API call: Convert USPs to 75-character limit
            # limited_result = self.convert_usp_to_75_chars(usp_result["original_usp"])
            # time.sleep(2)
            # if "error" in limited_result:
            #     return limited_result
            
            # Return both results for display
            return {
                "original_usp": usp_result["original_usp"],
                #"char_limited_usp": limited_result["char_limited_usp"]
            }
        except Exception as e:
            error_msg = f"Error in USP processing pipeline: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
