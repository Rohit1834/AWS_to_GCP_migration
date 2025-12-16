#!/usr/bin/env python3
"""
Simple run script for AWS Billing Data Extractor
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if requirements are installed"""
    try:
        import streamlit
        import pandas
        import pdfplumber
        import anthropic
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_credentials():
    """Check if credentials file exists"""
    creds_file = Path("paradigm-gpt-9c0deac797aa.json")
    if creds_file.exists():
        print("✅ Credentials file found")
        return True
    else:
        print("❌ Credentials file not found: paradigm-gpt-9c0deac797aa.json")
        print("Please place your Google Cloud service account credentials file in this directory")
        return False

def main():
    """Main function to run the application"""
    print("🚀 AWS Billing Data Extractor")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check credentials
    if not check_credentials():
        sys.exit(1)
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    print(f"✅ Output directory ready: {output_dir.absolute()}")
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print(f"✅ Logs directory ready: {logs_dir.absolute()}")
    
    print("\n🌐 Starting Streamlit application...")
    print("The application will open in your default web browser")
    print("If it doesn't open automatically, go to: http://localhost:8501")
    print("\nPress Ctrl+C to stop the application")
    print("=" * 50)
    
    try:
        # Run Streamlit app
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
