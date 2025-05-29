# 99acres USP Generator

A professional, minimalist Streamlit application that uses Google's Gemini AI to generate Unique Selling Propositions (USPs) from property PDF documents.

## Features

- **PDF Upload**: Upload property PDF documents for analysis
- **Dual Gemini API Processing**: 
  - First API call extracts USPs from the PDF content
  - Second API call converts USPs to 75-character limit format
- **Professional UI**: Clean, responsive interface with dark/light mode support
- **Download Options**: Export results in Excel or CSV format
- **Production-Ready**: Optimized for performance and security

## Requirements

- Python 3.8+
- Streamlit 1.28.0+
- Google Gemini API Key
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository or download the source code
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Streamlit application:

```bash
streamlit run app.py
```

## Usage

1. Configure your Gemini API Key in the sidebar
2. Upload a property PDF document
3. Add any existing USP content (optional)
4. Click "Generate USP"
5. View and download the results

## Project Structure

- `app.py`: Main Streamlit application
- `gemini_client.py`: Backend client for Gemini API integration
- `requirements.txt`: Required dependencies
- `validate.py`: Validation script for checking dependencies and file structure

## Notes

- The application uses the latest Google Gemini SDK (`google-genai`)
- PDF files are processed directly without text extraction
- Maximum file size: 50MB
- Temporary files are automatically cleaned up


## Changelog
### Version 1.1
New version reduces the Rate limit error in the output by introducing Imposed ****Rate limit handling**** which will increase the processing time just a little to stay within LLM request limits.
Version update to tackle the issue caused by multiple request duing bulk processing of brochures.

