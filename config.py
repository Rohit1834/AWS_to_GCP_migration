#!/usr/bin/env python3
"""
Configuration Module
Central configuration for AWS Billing Data Extractor
"""

import os
from pathlib import Path

# Project Configuration
PROJECT_NAME = "AWS Billing Data Extractor"
VERSION = "1.0.0"

# Directory Configuration
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

# Claude LLM Configuration
CLAUDE_CONFIG = {
    "project_id": "paradigm-gpt",
    "location": "us-east5",
    "model_name": "claude-sonnet-4@20250514",
    "max_tokens": 4000,
    "temperature": 0.1,
    "credentials_file": "paradigm-gpt-9c0deac797aa.json"
}

# PDF Processing Configuration
PDF_CONFIG = {
    "supported_formats": ['.pdf'],
    "max_file_size_mb": 50,
    "extraction_methods": ['pdfplumber', 'pypdf2']
}

# Excel Output Configuration
EXCEL_CONFIG = {
    "max_sheet_name_length": 31,
    "default_columns": ["AWS", "OS", "Region", "Hours", "Cores", "RAM", "Cost"],
    "column_widths": {
        "AWS": 15,
        "OS": 12,
        "Region": 12,
        "Hours": 12,
        "Cores": 8,
        "RAM": 8,
        "Cost": 12
    }
}

# Streamlit Configuration
STREAMLIT_CONFIG = {
    "page_title": "AWS Billing Data Extractor",
    "page_icon": "📊",
    "layout": "wide",
    "max_upload_size_mb": 200
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_handler": True,
    "console_handler": True
}

# Error Messages
ERROR_MESSAGES = {
    "claude_init_failed": "Failed to initialize Claude LLM. Please check your credentials.",
    "pdf_extraction_failed": "Failed to extract text from PDF file.",
    "no_data_extracted": "No billing data found in the PDF.",
    "excel_save_failed": "Failed to save data to Excel file.",
    "file_too_large": "File size exceeds maximum limit.",
    "invalid_file_format": "Invalid file format. Only PDF files are supported.",
    "processing_error": "An error occurred during processing."
}

# Success Messages
SUCCESS_MESSAGES = {
    "claude_initialized": "Claude LLM initialized successfully!",
    "pdf_processed": "PDF processed successfully.",
    "excel_saved": "Data saved to Excel file successfully.",
    "processing_complete": "All files processed successfully."
}

def ensure_directories():
    """Ensure required directories exist"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

def get_credentials_path():
    """Get path to Claude credentials file"""
    return BASE_DIR / CLAUDE_CONFIG["credentials_file"]

def validate_environment():
    """Validate environment setup"""
    issues = []
    
    # Check credentials file
    if not get_credentials_path().exists():
        issues.append(f"Credentials file not found: {get_credentials_path()}")
    
    # Check required environment variables
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(get_credentials_path())
    
    return issues
