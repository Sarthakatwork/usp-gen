import streamlit as st
import pandas as pd
import time
from io import BytesIO
import os
import tempfile
import requests
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

# Initialize session state variables
if "xid" not in st.session_state:
    st.session_state.xid = ""
    
if "existing_usp" not in st.session_state:
    st.session_state.existing_usp = ""
    
if "reset_triggered" not in st.session_state:
    st.session_state.reset_triggered = False

if "gemini_response" not in st.session_state:
    st.session_state.gemini_response = {}

#DARK THEME CSS
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

# Main app content
tab1, tab2 = st.tabs(["Single File", "Bulk Processing"])

with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Generate USP</h2>', unsafe_allow_html=True)
    
    # Reset logic
    if st.session_state.reset_triggered:
        st.session_state.xid = ""
        st.session_state.existing_usp = ""
        st.session_state.gemini_response = {}
        st.session_state.reset_triggered = False
    
    # Input form
    col1, col2 = st.columns(2)
    
    with col1:
        xid = st.text_input("XID No.", key="xid", 
                           help="Enter the property identifier")
        existing_usp = st.text_area("Existing USP (if any)", key="existing_usp", height=150,
                                   help="Enter any existing USP content to be considered")
    
    with col2:
        uploaded_pdf = st.file_uploader("Upload Property PDF", type=["pdf"], 
                               help="Upload the property PDF document (max 20MB)")
# file size validation...


        
        # Add file size validation
        if uploaded_pdf:
            file_size = len(uploaded_pdf.getvalue()) / (1024 * 1024)  # Size in MB
            if file_size > 50:
                st.error("File size exceeds 20MB limit. Please upload a smaller file.")
                uploaded_pdf = None
            else:
                st.info(f"File size: {file_size:.2f}MB")
        
        col_process, col_reset = st.columns(2)
        with col_process:
            process_button = st.button("Generate USP", disabled=not uploaded_pdf)
            if not uploaded_pdf and process_button:
                st.info("Please upload a PDF file first")
        with col_reset:
            reset_button = st.button("Reset", key="reset_single")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process PDF and generate USP with error handling and progress tracking
    if process_button and uploaded_pdf:
        try:
            # Create progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Initialize client
            status_text.text("Initializing Gemini client...")
            progress_bar.progress(10)
            client = get_gemini_client()
            time.sleep(0.5)  # Small delay for UI feedback
            
            # Step 2: Upload and process PDF
            status_text.text("Uploading and processing PDF...")
            progress_bar.progress(30)
            time.sleep(0.5)  # Small delay for UI feedback
            
            # Step 3: Generate USPs
            status_text.text("Generating USPs from PDF content...")
            progress_bar.progress(60)
            result = client.process_pdf_for_usp(uploaded_pdf, existing_usp)
            progress_bar.progress(90)
            
            # Step 4: Complete
            status_text.text("Processing complete!")
            progress_bar.progress(100)
            
            # Store response in session state
            if isinstance(result, dict) and "error" not in result:
                st.session_state.gemini_response = result
                time.sleep(0.5)  # Small delay for UI feedback
                status_text.empty()  # Clear status message
            else:
                error_msg = result.get("error", "Unknown error occurred")
                st.error(f"Error processing PDF: {error_msg}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please try again with a different PDF file.")
    
    # Display results with optimized UI - only showing 75-character USPs
    if st.session_state.gemini_response and "char_limited_usp" in st.session_state.gemini_response:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h2 class="sub-header">Generated USPs</h2>', unsafe_allow_html=True)
        
        # Display only the 75-character USPs
        st.text_area("", st.session_state.gemini_response["char_limited_usp"], height=250, key="limited_usp_display")
        
        # Add copy button for convenience
        if st.button("Copy USPs", key="copy_limited"):
            st.code(st.session_state.gemini_response["char_limited_usp"], language="text")
            st.success("USPs copied to clipboard!")
        
        # Create DataFrame for download with optimized memory usage
        output_data = {
            "XID": [xid],
            "EXISTING_USP": [existing_usp],
            "USP": [st.session_state.gemini_response["char_limited_usp"]]
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
                file_name=f"USP_Result_{xid}.xlsx",
                mime="application/vnd.ms-excel"
            )
        
        with col_csv:
            # CSV download
            csv_buffer = BytesIO()
            output_df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            st.download_button(
                label="Download as CSV",
                data=csv_buffer,
                file_name=f"USP_Result_{xid}.csv",
                mime="text/csv"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if reset_button:
        st.session_state.reset_triggered = True
        st.rerun()

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        #Format instruction before bulk processing header
        st.markdown("""
         <div style="color: white; font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">
         📄 EXCEL FILE UPLOADED SHOULD BE EXACT SAME AS IN THIS FORMAT:<br>
         <code>XID | PDF_URL | EXISTING_USP</code>
         </div>
         <h2 class="sub-header">Bulk Processing</h2>
         """, unsafe_allow_html=True)

        
        uploaded_file = st.file_uploader(
            "Upload Excel or CSV File", 
            type=["xlsx", "csv"],
            help="Upload a file with columns: XID, PDF_URL, EXISTING_USP"
        )
        
        if uploaded_file:
            try:
                # Read the uploaded file with optimized memory usage
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file, dtype={
                        'XID': str,
                        'PDF_URL': str,
                        'EXISTING_USP': str
                    })
                else:
                    df = pd.read_excel(uploaded_file, dtype={
                        'XID': str,
                        'PDF_URL': str,
                        'EXISTING_USP': str
                    })
                
                # Display preview with limited rows for performance
                st.markdown('<h3 style="font-size: 1.3rem; margin-top: 20px; margin-bottom: 10px; color: #a0a8d9;">Preview of uploaded data:</h3>', unsafe_allow_html=True)
                st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                st.dataframe(df.head(5), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Process button
                if st.button("Process All Entries"):
                    # Initialize progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Initialize client
                    client = get_gemini_client()
                    
                    # Initialize results dataframe
                    results_df = pd.DataFrame(columns=["XID", "EXISTING_USP", "USP", "STATUS"])
                    
                    # Process each row
                    for i, row in enumerate(df.itertuples()):
                        try:
                            # Update progress
                            progress = int((i / len(df)) * 100)
                            progress_bar.progress(progress)
                            status_text.text(f"Processing {i+1}/{len(df)}: {row.XID}")
                            
                            # Check if PDF_URL exists for this row
                            if not hasattr(row, 'PDF_URL') or pd.isna(row.PDF_URL) or not row.PDF_URL:
                                # Add error to results if PDF_URL is missing
                                results_df = pd.concat([results_df, pd.DataFrame({
                                    "XID": [row.XID],
                                    "EXISTING_USP": [row.EXISTING_USP if hasattr(row, 'EXISTING_USP') and pd.notna(row.EXISTING_USP) else ""],
                                    "USP": [""],
                                    "STATUS": ["Error: Missing PDF_URL"]
                                })], ignore_index=True)
                                continue
                                
                            # Download PDF from URL
                            try:
                                # Get PDF from URL for this specific row
                                response = requests.get(row.PDF_URL, timeout=30)
                                if response.status_code == 200:
                                    # Create a new BytesIO object for each PDF to avoid reusing the same content
                                    pdf_content = BytesIO(response.content)
                                    
                                    # Process PDF with row-specific existing USP
                                    existing_usp = row.EXISTING_USP if hasattr(row, 'EXISTING_USP') and pd.notna(row.EXISTING_USP) else ""
                                    result = client.process_pdf_for_usp(pdf_content, existing_usp)
                                    
                                    if "error" not in result:
                                        # Add to results dataframe
                                        results_df = pd.concat([results_df, pd.DataFrame({
                                            "XID": [row.XID],
                                            "EXISTING_USP": [existing_usp],
                                            "USP": [result["char_limited_usp"]],
                                            "STATUS": ["Success"]
                                        })], ignore_index=True)
                                    else:
                                        # Add error to results
                                        results_df = pd.concat([results_df, pd.DataFrame({
                                            "XID": [row.XID],
                                            "EXISTING_USP": [existing_usp],
                                            "USP": [""],
                                            "STATUS": [f"Error: {result['error']}"]
                                        })], ignore_index=True)
                                else:
                                    # Add download error to results
                                    results_df = pd.concat([results_df, pd.DataFrame({
                                        "XID": [row.XID],
                                        "EXISTING_USP": [row.EXISTING_USP if hasattr(row, 'EXISTING_USP') and pd.notna(row.EXISTING_USP) else ""],
                                        "USP": [""],
                                        "STATUS": [f"Error downloading PDF: Status code {response.status_code}"]
                                    })], ignore_index=True)
                            except Exception as e:
                                # Add exception to results
                                results_df = pd.concat([results_df, pd.DataFrame({
                                    "XID": [row.XID],
                                    "EXISTING_USP": [row.EXISTING_USP if hasattr(row, 'EXISTING_USP') and pd.notna(row.EXISTING_USP) else ""],
                                    "USP": [""],
                                    "STATUS": [f"Error: {str(e)}"]
                                })], ignore_index=True)
                        except Exception as e:
                            # Add processing exception to results
                            results_df = pd.concat([results_df, pd.DataFrame({
                                "XID": [row.XID if hasattr(row, 'XID') else "Unknown"],
                                "EXISTING_USP": [""],
                                "USP": [""],
                                "STATUS": [f"Processing error: {str(e)}"]
                            })], ignore_index=True)
                    
                    # Complete progress
                    progress_bar.progress(100)
                    status_text.text("Processing complete!")
                    
                    # Display results
                    st.markdown('<h3 style="font-size: 1.3rem; margin-top: 20px; margin-bottom: 10px; color: #a0a8d9;">Processing Results:</h3>', unsafe_allow_html=True)
                    st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                    st.dataframe(results_df, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Prepare download options
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        results_df.to_excel(writer, index=False, sheet_name='Bulk USP Results')
                    buffer.seek(0)
                    
                    st.download_button(
                        label="Download Results as Excel",
                        data=buffer,
                        file_name="Bulk_USP_Results.xlsx",
                        mime="application/vnd.ms-excel"
                    )
            
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer with version info
    st.markdown("""
    <div style="text-align: center; margin-top: 30px; color: #f8f9fa; font-size: 0.9rem; padding: 15px; background-color: #1a1c24; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);">
        <div style="font-weight: 600; margin-bottom: 5px;">USP Generator v1.1 | Developed for 99 acres</div>
    </div>
    """, unsafe_allow_html=True)

    # Clean up temporary files and resources when the app is done
    def cleanup():
        """Clean up temporary resources when the app exits."""
        for item in os.listdir(tempfile.gettempdir()):
            if item.endswith('.pdf'):
                try:
                    os.remove(os.path.join(tempfile.gettempdir(), item))
                except:
                    pass

    # Register cleanup function to run when app exits
    import atexit
    atexit.register(cleanup)
