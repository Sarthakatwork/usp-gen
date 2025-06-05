import streamlit as st
import pandas as pd
import time
from io import BytesIO
import os
import tempfile
import requests
# Assuming gemini_client.py exists and has a GeminiClient class with process_pdf_for_usp method
from gemini_client import GeminiClient

#Performance optimization
@st.cache_resource
def get_gemini_client():
    """Create and return a cached Gemini client instance."""
    return GeminiClient()

# Setting page configuration with optimized settings
st.set_page_config(
    page_title="USP Generator",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "USP Generator - Powered by Gemini AI"
    }
)

# Initialize session state variables for Tab 1
if "xid" not in st.session_state:
    st.session_state.xid = ""

if "existing_usp" not in st.session_state:
    st.session_state.existing_usp = ""

if "reset_triggered" not in st.session_state:
    st.session_state.reset_triggered = False

if "gemini_response" not in st.session_state:
    st.session_state.gemini_response = {}

# Initialize session state for Tab 2 if needed later, currently not strictly necessary for just rendering

# --- DARK THEME CSS ---
st.markdown("""
<style>
    /* Global Dark Theme */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stSidebar"], [data-testid="stMetricValue"], .stTabs [data-baseweb="tab-panel"],
    .stTabs [data-baseweb="tab-list"], section[data-testid="stSidebar"] > div {
        background-color: #0f1117;
        color: #f8f9fa;
    }

    /* Header styling */
    .main-header {
        color: #ffffff;
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-align: center;
        text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.3);
        background: linear-gradient(90deg, #4b5eba, #7986cb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 10px 0;
        letter-spacing: -0.5px;
    }

    /* Subheader styling */
    .sub-header {
        color: #ffffff;
        font-size: 1.6rem;
        font-weight: 600;
        margin-bottom: 1.2rem;
        border-bottom: 2px solid #4b5eba;
        padding-bottom: 10px;
        letter-spacing: -0.3px;
    }

    /* Card styling */
    .card {
        background-color: #1a1c24;
        border-radius: 12px;
        padding: 28px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
        margin-bottom: 28px;
        color: #f8f9fa;
        border-left: 4px solid #4b5eba;
        position: relative;
        overflow: hidden;
    }

    .card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(to bottom right, rgba(75, 94, 186, 0.05), transparent);
        pointer-events: none;
    }

    /* Button styling */
    .stButton > button {
        background-color: #4b5eba;
        color: white;
        font-weight: 500;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.9rem;
    }

    .stButton > button:hover {
        background-color: #3a4a9e;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
    }

    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.2);
    }

    /* Success button */
    .success-btn > button {
        background-color: #28a745;
    }

    .success-btn > button:hover {
        background-color: #218838;
    }

    /* Reset button */
    .reset-btn > button {
        background-color: #dc3545;
    }

    .reset-btn > button:hover {
        background-color: #c82333;
    }

    /* Footer styling */
    footer {
        visibility: hidden;
    }

    /* Remove fullscreen button from elements */
    .element-container button[title="View fullscreen"] {
        display: none;
    }

    /* Streamlit default element adjustments */
    div[data-testid="stVerticalBlock"] {
        gap: 0.8rem;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1a1c24;
        padding: 10px 10px 0 10px;
        border-radius: 10px 10px 0 0;
        border-bottom: 1px solid #2d2d2d;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #2d2d2d;
        border-radius: 8px 8px 0 0;
        gap: 1px;
        padding: 10px 20px;
        color: #f8f9fa;
        font-weight: 500;
        border: none;
        transition: all 0.2s ease;
        letter-spacing: 0.3px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #4b5eba;
        color: white;
        font-weight: 600;
        box-shadow: 0 -4px 10px rgba(0, 0, 0, 0.1);
    }

    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background-color: #3d3d3d;
        color: #ffffff;
    }

    .stTabs [data-baseweb="tab-panel"] {
        background-color: #1a1c24;
        border-radius: 0 0 10px 10px;
        padding: 20px;
        border: none;
    }

    /* Text input and area styling */
    .stTextInput > div > div > input {
        background-color: #2d2d2d;
        color: #f8f9fa;
        border: 1px solid #3d3d3d;
        border-radius: 8px;
        padding: 12px;
        font-size: 1rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: #4b5eba;
        box-shadow: 0 0 0 2px rgba(75, 94, 186, 0.3);
    }

    .stTextArea > div > div > textarea {
        background-color: #2d2d2d;
        color: #f8f9fa;
        border: 1px solid #3d3d3d;
        border-radius: 8px;
        padding: 12px;
        font-size: 1rem;
    }

    .stTextArea > div > div > textarea:focus {
        border-color: #4b5eba;
        box-shadow: 0 0 0 2px rgba(75, 94, 186, 0.3);
    }

    /* File uploader styling */
    .stFileUploader > div {
        background-color: #2d2d2d;
        border: 2px dashed #4b5eba;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }

    .stFileUploader > div:hover {
        background-color: #3d3d3d;
        border-color: #7986cb;
        transform: translateY(-2px);
    }

    /* Progress bar styling */
    .stProgress > div > div > div {
        background-color: #4b5eba;
        background-image: linear-gradient(45deg, rgba(255, 255, 255, 0.15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, 0.15) 50%, rgba(255, 255, 255, 0.15) 75%, transparent 75%, transparent);
        background-size: 1rem 1rem;
        animation: progress-bar-stripes 1s linear infinite;
    }

    @keyframes progress-bar-stripes {
        0% { background-position: 1rem 0; }
        100% { background-position: 0 0; }
    }

    /* Dataframe styling */
    .dataframe-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    }

    .dataframe {
        border-collapse: collapse;
        width: 100%;
        background-color: #1a1c24;
    }

    .dataframe th {
        background-color: #4b5eba;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .dataframe td {
        padding: 10px;
        border-bottom: 1px solid #3d3d3d;
    }

    .dataframe tr:hover {
        background-color: #2d2d2d;
    }

    /* Label styling */
    label {
        font-weight: 500;
        color: #a0a8d9;
        font-size: 1.05rem;
        letter-spacing: 0.2px;
        margin-bottom: 5px;
    }

    /* Info message styling */
    .stAlert {
        background-color: #2d2d2d;
        border-radius: 8px;
        border-left: 4px solid #4b5eba;
        padding: 10px 15px;
    }

    /* Success message styling */
    .element-container div[data-testid="stAlert"][data-baseweb="notification"] {
        background-color: rgba(40, 167, 69, 0.2);
        border-left-color: #28a745;
    }

    /* Error message styling */
    .element-container div[data-testid="stAlert"][data-baseweb="notification"][data-alert-type="error"] {
        background-color: rgba(220, 53, 69, 0.2);
        border-left-color: #dc3545;
    }

    /* Code block styling */
    .stCodeBlock {
        background-color: #2d2d2d;
        border-radius: 8px;
        border: 1px solid #3d3d3d;
    }

    /* Responsive design adjustments */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
        }

        .sub-header {
            font-size: 1.3rem;
        }

        .card {
            padding: 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<h1 class="main-header">99 acres USP Generator</h1>', unsafe_allow_html=True)

# Main app content - Tabs
tab1, tab2 = st.tabs(["Single File", "Bulk Processing"])

# --- Content for Tab 1 ---
with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Generate USP</h2>', unsafe_allow_html=True)

    # Reset logic for tab1 inputs
    if st.session_state.reset_triggered:
        st.session_state.xid = ""
        st.session_state.existing_usp = ""
        st.session_state.gemini_response = {} # Also clear response on reset
        st.session_state.reset_triggered = False
        # Need to explicitly clear file uploader state as well if desired
        # This often requires re-rendering the element, which rerunning does.

    # Input form
    col1, col2 = st.columns(2)

    with col1:
        # Using default key for text inputs, which is fine in a single tab
        st.text_input("XID No.", key="xid",
                           help="Enter the property identifier")
        st.text_area("Existing USP (if any)", key="existing_usp", height=150,
                                   help="Enter any existing USP content to be considered")

    with col2:
        # Add a key to the file uploader to ensure state is handled correctly
        uploaded_pdf = st.file_uploader("Upload Property PDF", type=["pdf"],
                               help="Upload the property PDF document (max 20MB)", key="single_uploader")

        # Add file size validation
        if uploaded_pdf:
            file_size = len(uploaded_pdf.getvalue()) / (1024 * 1024)  # Size in MB
            # Check against the stated 100MB limit
            if file_size > 100:
                st.error(f"File size ({file_size:.2f}MB) exceeds 100MB limit. Please upload a smaller file.")
                uploaded_pdf = None # Clear the uploader state by setting the variable to None
            else:
                st.info(f"File size: {file_size:.2f}MB")

        col_process, col_reset = st.columns(2)
        with col_process:
            # Disable button if no valid file is uploaded
            process_button = st.button("Generate USP", disabled=uploaded_pdf is None, key="single_process_button")

        with col_reset:
             # Reset button for the single file tab
            reset_button = st.button("Reset", key="reset_single_button")
            if reset_button:
                st.session_state.reset_triggered = True
                st.rerun() # Rerun to clear inputs and results

    st.markdown('</div>', unsafe_allow_html=True) # Close the input card div

    # Process PDF and generate USP with error handling and progress tracking
    # This block should only execute after the process button is clicked and a file is uploaded
    if process_button and uploaded_pdf:
        try:
            # Create progress indicators
            progress_bar = st.progress(0, text="Initializing...")
            status_text = st.empty()

            # Step 1: Initialize client
            status_text.text("Initializing Gemini client...")
            progress_bar.progress(10, text="Initializing...")
            client = get_gemini_client()

            # Step 2: Upload and process PDF
            status_text.text("Uploading and processing PDF...")
            progress_bar.progress(30, text="Processing PDF...")
            # No need to save to temp file explicitly if passing BytesIO

            # Step 3: Generate USPs
            status_text.text("Generating USPs from PDF content...")
            progress_bar.progress(60, text="Generating USPs...")
            # Pass the BytesIO object directly and the current input values
            result = client.process_pdf_for_usp(uploaded_pdf, st.session_state.existing_usp) # Use session state values
            progress_bar.progress(90, text="Finalizing...")

            # Step 4: Complete
            status_text.text("Processing complete!")
            progress_bar.progress(100, text="Complete!")

            # Store response in session state
            if isinstance(result, dict) and "error" not in result:
                st.session_state.gemini_response = result
                # Rerun to display results section which depends on session state
                st.rerun()
            else:
                error_msg = result.get("error", "Unknown error occurred")
                st.error(f"Error processing PDF: {error_msg}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please try again with a different PDF file.")
        finally:
             # Ensure progress bar and status text are cleared or finished
             progress_bar.empty()
             status_text.empty()


    # Display results with optimized UI - only show if response exists
    if st.session_state.gemini_response and "original_usp" in st.session_state.gemini_response:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        # Section: Full-length USPs
        st.markdown('<h2 class="sub-header">Generated USPs</h2>', unsafe_allow_html=True)
        # Use a unique key for this text area
        st.text_area("Original USPs", st.session_state.gemini_response.get("original_usp", ""), height=250, key="original_usp_display")

        # Copy button for full USPs
        # Use a unique key for this button
        if st.button("Copy Original USPs", key="copy_original_button"):
            st.code(st.session_state.gemini_response.get("original_usp", ""), language="text")
            st.success("Original USPs copied to clipboard!")

        # Section: 75-character USPs
        st.markdown('<h3 class="sub-header" style="margin-top: 30px;">USPs extracted in 75 characters</h3>', unsafe_allow_html=True)

        # Use a unique key for this text area
        st.text_area("Shortened USPs (75 chars)", st.session_state.gemini_response.get("char_limited_usp", ""), height=250, key="short_usp_display")

        # Copy button for shortened USPs
        # Use a unique key for this button
        if st.button("Copy 75-char USPs", key="copy_short_button"):
            st.code(st.session_state.gemini_response.get("char_limited_usp", ""), language="text")
            st.success("75-character USPs copied to clipboard!")

        # Create DataFrame for download with optimized memory usage
        output_data = {
            # Use session state values for XID and EXISTING_USP from when the process button was clicked
            "XID": [st.session_state.xid],
            "EXISTING_USP": [st.session_state.existing_usp],
            "USP": [st.session_state.gemini_response.get("original_usp", "")],
            "75 char USP": [st.session_state.gemini_response.get("char_limited_usp", "")] # Added 75 char USP to single download
        }
        output_df = pd.DataFrame(output_data)

        # Prepare download options
        col_excel, col_csv = st.columns(2)

        with col_excel:
            # Excel download
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                output_df.to_excel(writer, index=False, sheet_name='USP Results')
            buffer.seek(0)

            st.download_button(
                label="Download as Excel",
                data=buffer,
                # Use session state xid for filename
                file_name=f"USP_Result_{st.session_state.xid}.xlsx",
                mime="application/vnd.ms-excel",
                key="single_excel_download" # Unique key
            )

        with col_csv:
            # CSV download
            csv_buffer = BytesIO()
            output_df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)

            st.download_button(
                label="Download as CSV",
                data=csv_buffer,
                # Use session state xid for filename
                file_name=f"USP_Result_{st.session_state.xid}.csv",
                mime="text/csv",
                key="single_csv_download" # Unique key
            )

        st.markdown('</div>', unsafe_allow_html=True) # Close the results card div


# --- Content for Tab 2 ---
with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    # Format instruction before bulk processing header
    st.markdown("""
     <div style="color: white; font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">
     📄 EXCEL FILE UPLOADED SHOULD BE EXACT SAME AS IN THIS FORMAT:<br>
     <code>XID | PDF_URL | EXISTING_USP</code>
     </div>
     <h2 class="sub-header">Bulk Processing</h2>
     """, unsafe_allow_html=True)


    # Add a key to the file uploader for bulk processing
    uploaded_bulk_file = st.file_uploader(
        "Upload Excel or CSV File",
        type=["xlsx", "csv"],
        help="Upload a file with columns: XID, PDF_URL, EXISTING_USP",
        key="bulk_uploader" # Unique key for the bulk uploader
    )

    if uploaded_bulk_file:
        try:
            # Read the uploaded file with optimized memory usage
            if uploaded_bulk_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_bulk_file, dtype={
                    'XID': str,
                    'PDF_URL': str,
                    'EXISTING_USP': str
                })
            else: # Assume xlsx
                df = pd.read_excel(uploaded_bulk_file, dtype={
                    'XID': str,
                    'PDF_URL': str,
                    'EXISTING_USP': str
                })

            # Validate required columns are present
            required_columns = ['XID', 'PDF_URL'] # EXISTING_USP is optional
            if not all(col in df.columns for col in required_columns):
                 missing = [col for col in required_columns if col not in df.columns]
                 st.error(f"Uploaded file is missing required columns: {', '.join(missing)}")
                 df = pd.DataFrame() # Clear df to prevent processing

            # Fill NaN in 'EXISTING_USP' to empty string for easier processing
            if 'EXISTING_USP' in df.columns:
                 df['EXISTING_USP'] = df['EXISTING_USP'].fillna('')
            else:
                 df['EXISTING_USP'] = '' # Add the column if missing, filled with empty strings

             # Fill NaN in 'PDF_URL' with None for easier checking
            if 'PDF_URL' in df.columns:
                df['PDF_URL'] = df['PDF_URL'].replace('', None).dropna() # Replace empty strings with None, then drop actual NaNs
                df['PDF_URL'] = df['PDF_URL'].where(pd.notna, None) # Ensure remaining NaNs are None

            # Display preview with limited rows for performance
            if not df.empty:
                st.markdown('<h3 style="font-size: 1.3rem; margin-top: 20px; margin-bottom: 10px; color: #a0a8d9;">Preview of uploaded data:</h3>', unsafe_allow_html=True)
                st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                st.dataframe(df.head(), use_container_width=True) # Show first 5 rows
                st.markdown('</div>', unsafe_allow_html=True)

                # Process button - only show if DataFrame is not empty
                if st.button("Process All Entries", key="process_bulk_button"): # Unique key
                    # Initialize progress tracking
                    total_rows = len(df)
                    # Use .copy() to avoid SettingWithCopyWarning when modifying the original df
                    results_df = df.copy()
                    results_df['USP'] = ""
                    results_df["75 char USP"] ="" # ADDED: Initialize the 75 char USP column
                    results_df['STATUS'] = "Pending" # Column for status

                    progress_bar = st.progress(0, text=f"Processing 0/{total_rows} entries...")
                    status_text = st.empty()

                    # Initialize client outside the loop
                    client = get_gemini_client()

                    # Process each row
                    # Iterate using iterrows() for simpler access by column name, though slightly less performant than itertuples for very large DFs
                    # Or continue using itertuples but access original df for PDF_URL
                    # Let's stick with itertuples and access original df for PDF_URL as planned for efficiency
                    for i, row in enumerate(results_df.itertuples(index=True)): # Use index=True to get the original index
                        original_index = row.Index # Get the index from the original dataframe

                        try:
                            # Update progress
                            progress = int((i / total_rows) * 100)
                            progress_bar.progress(progress, text=f"Processing {i+1}/{total_rows}: {row.XID}...")
                            # status_text.text(f"Processing {i+1}/{total_rows}: {row.XID}") # Using text in progress bar

                            # Get PDF_URL from the original dataframe as results_df doesn't have it
                            # The PDF_URL column might have None values from the cleanup step
                            pdf_url = df.loc[original_index, 'PDF_URL']

                            # Ensure URL exists and is not NaN/None before attempting download
                            if not pdf_url or not isinstance(pdf_url, str):
                                results_df.loc[original_index, 'STATUS'] = "Error: Missing or Invalid PDF_URL"
                                continue # Skip to next row

                            # Ensure http/https prefix (basic check)
                            if not (pdf_url.startswith('http://') or pdf_url.startswith('https://')):
                                results_df.loc[original_index, 'STATUS'] = "Error: PDF_URL missing http(s)://"
                                continue

                            existing_usp_val = row.EXISTING_USP # existing_usp_val is already correct from results_df copy

                            # Download PDF from URL
                            try:
                                # status_text.text(f"Processing {i+1}/{total_rows}: {row.XID} - Downloading PDF...")
                                response = requests.get(pdf_url, timeout=60) # Increased timeout
                                response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
                                pdf_content = BytesIO(response.content)

                                # Process PDF with row-specific existing USP
                                # status_text.text(f"Processing {i+1}/{total_rows}: {row.XID} - Generating USP...")
                                result = client.process_pdf_for_usp(pdf_content, existing_usp_val)

                                if isinstance(result, dict) and "error" not in result:
                                    results_df.loc[original_index, 'USP'] = result.get("original_usp", "") # Use .get for safety
                                    results_df.loc[original_index,'75 char USP'] = result.get("char_limited_usp", "") # ADDED: Populate 75 char USP
                                    results_df.loc[original_index, 'STATUS'] = "Success"
                                else:
                                    error_msg = result.get("error", "Unknown processing error") if isinstance(result, dict) else str(result)
                                    results_df.loc[original_index, 'STATUS'] = f"Processing Error: {error_msg[:150]}..." # Truncate long errors

                            except requests.exceptions.Timeout:
                                results_df.loc[original_index, 'STATUS'] = "Error: PDF Download Timeout (60s)"
                            except requests.exceptions.RequestException as req_e:
                                results_df.loc[original_index, 'STATUS'] = f"Error downloading PDF: {str(req_e)[:150]}..."
                            except Exception as e:
                                # Catch any exception during processing the downloaded PDF
                                results_df.loc[original_index, 'STATUS'] = f"Processing Error: {str(e)[:150]}..."

                        except Exception as e:
                            # Catch any unexpected error during row iteration (less likely with inner try/except)
                             results_df.loc[original_index, 'STATUS'] = f"Unexpected Error: {str(e)[:150]}..."


                    # Complete progress
                    progress_bar.progress(100, text="Processing complete!")
                    status_text.success("Bulk processing finished!")
                    time.sleep(2) # Keep completion message visible briefly
                    progress_bar.empty()
                    status_text.empty()


                    # Display results
                    st.markdown('<h3 style="font-size: 1.3rem; margin-top: 20px; margin-bottom: 10px; color: #a0a8d9;">Processing Results:</h3>', unsafe_allow_html=True)
                    st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                    st.dataframe(results_df, use_container_width=True) # Display the results_df
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Prepare download options
                    # results_df now contains XID, EXISTING_USP, USP, 75 char USP, STATUS
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        results_df.to_excel(writer, index=False, sheet_name='Bulk USP Results')
                    buffer.seek(0)

                    st.download_button(
                        label="Download Results as Excel",
                        data=buffer,
                        file_name="Bulk_USP_Results.xlsx",
                        mime="application/vnd.ms-excel",
                         key="bulk_excel_download" # Unique key
                    )

            # No need for an else here, if df is empty after validation, the button isn't shown.

        except Exception as e:
            # Catch errors during file reading/initialization
            st.error(f"Error reading or initializing file processing: {e}")
            st.info("Please ensure the file format is correct (xlsx or csv) and contains the columns: XID, PDF_URL, EXISTING_USP (optional).")


    st.markdown('</div>', unsafe_allow_html=True) # Close the bulk card div


# --- Footer (outside of both tabs) ---
st.markdown("""
<div style="text-align: center; margin-top: 30px; color: #f8f9fa; font-size: 0.9rem; padding: 15px; background-color: #1a1c24; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);">
    <div style="font-weight: 600; margin-bottom: 5px;">USP Generator v1.1 | Developed for 99 acres</div>
</div>
""", unsafe_allow_html=True)

# Clean up temporary files and resources when the app is done
# Ensure this is defined outside of any 'with' block
def cleanup():
    """Clean up temporary resources when the app exits."""
    # Example cleanup - more robust cleanup might be needed depending on GeminiClient implementation
    # This basic cleanup looks for temporary PDF files
    temp_dir = tempfile.gettempdir()
    # print(f"Attempting cleanup in: {temp_dir}") # For debugging
    for item in os.listdir(temp_dir):
        # Check if the file looks like one created by pdf processing or is a temp file
        # Be cautious with cleanup to avoid deleting unrelated files
        if item.endswith('.pdf') or item.startswith('tmp'): # Added check for common temp file prefixes
            file_path = os.path.join(temp_dir, item)
            try:
                # print(f"Attempting to remove: {file_path}") # For debugging
                if os.path.isfile(file_path): # Ensure it's a file
                   os.remove(file_path)
                   # print(f"Removed: {file_path}") # For debugging
            except Exception as e:
                # print(f"Error removing {file_path}: {e}") # For debugging
                pass # Ignore errors during cleanup

# Register cleanup function to run when app exits - Must be at the top level
import atexit
atexit.register(cleanup)