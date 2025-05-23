import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("gemini_usp_app")

def create_test_directory():
    """Create test directory structure if it doesn't exist."""
    test_dir = Path("tests")
    test_dir.mkdir(exist_ok=True)
    return test_dir

def validate_dependencies():
    """Validate that all required dependencies are installed."""
    try:
        import streamlit
        import pandas
        import google.generativeai
        import fitz  # PyMuPDF
        logger.info("All dependencies validated successfully")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {str(e)}")
        return False

def validate_file_structure():
    """Validate that all required files exist."""
    required_files = [
        "app.py",
        "gemini_client.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Missing files: {', '.join(missing_files)}")
        return False
    
    logger.info("All required files exist")
    return True

def run_validation():
    """Run all validation checks."""
    logger.info("Starting validation...")
    
    # Create test directory
    test_dir = create_test_directory()
    logger.info(f"Test directory created at {test_dir}")
    
    # Validate dependencies
    deps_valid = validate_dependencies()
    
    # Validate file structure
    files_valid = validate_file_structure()
    
    # Overall validation result
    if deps_valid and files_valid:
        logger.info("Validation completed successfully")
        return True
    else:
        logger.error("Validation failed")
        return False

if __name__ == "__main__":
    run_validation()
