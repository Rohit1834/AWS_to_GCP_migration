#!/usr/bin/env python3
"""
Setup Test Script
Verify that all components are working correctly
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError:
        print("❌ Streamlit import failed")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError:
        print("❌ Pandas import failed")
        return False
    
    try:
        import pdfplumber
        print("✅ PDFplumber imported successfully")
    except ImportError:
        print("❌ PDFplumber import failed")
        return False
    
    try:
        from anthropic import Anthropic
        print("✅ Anthropic imported successfully")
    except ImportError:
        print("❌ Anthropic import failed")
        return False
    
    return True

def test_custom_modules():
    """Test if custom modules can be imported"""
    print("\n🔍 Testing custom modules...")
    
    try:
        from claude_llm import ClaudeLLMProcessor
        print("✅ Claude LLM module imported successfully")
    except ImportError as e:
        print(f"❌ Claude LLM module import failed: {e}")
        return False
    
    try:
        from pdf_processor import PDFProcessor
        print("✅ PDF Processor module imported successfully")
    except ImportError as e:
        print(f"❌ PDF Processor module import failed: {e}")
        return False
    
    try:
        from excel_handler import ExcelHandler
        print("✅ Excel Handler module imported successfully")
    except ImportError as e:
        print(f"❌ Excel Handler module import failed: {e}")
        return False
    
    try:
        from error_handler import ErrorHandler
        print("✅ Error Handler module imported successfully")
    except ImportError as e:
        print(f"❌ Error Handler module import failed: {e}")
        return False
    
    return True

def test_directories():
    """Test if required directories exist"""
    print("\n🔍 Testing directories...")
    
    output_dir = Path("output")
    if output_dir.exists():
        print("✅ Output directory exists")
    else:
        print("❌ Output directory missing")
        return False
    
    logs_dir = Path("logs")
    if logs_dir.exists():
        print("✅ Logs directory exists")
    else:
        print("❌ Logs directory missing")
        return False
    
    return True

def test_credentials():
    """Test if credentials file exists"""
    print("\n🔍 Testing credentials...")
    
    creds_file = Path("paradigm-gpt-9c0deac797aa.json")
    if creds_file.exists():
        print("✅ Credentials file found")
        return True
    else:
        print("❌ Credentials file missing")
        print("Please place 'paradigm-gpt-9c0deac797aa.json' in the project directory")
        return False

def test_pdf_file():
    """Test if sample PDF exists"""
    print("\n🔍 Testing sample PDF...")
    
    pdf_file = Path("AWS1_April.pdf")
    if pdf_file.exists():
        print("✅ Sample PDF file found")
        return True
    else:
        print("⚠️ Sample PDF file not found (optional)")
        return True  # Not critical for setup

def main():
    """Run all tests"""
    print("🚀 AWS Billing Data Extractor - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("Custom Modules", test_custom_modules),
        ("Directories", test_directories),
        ("Credentials", test_credentials),
        ("Sample PDF", test_pdf_file)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nTo run the application:")
        print("  python run.py")
        print("  OR")
        print("  streamlit run app.py")
    else:
        print("⚠️ Some tests failed. Please fix the issues before running the application.")
        
        if not any(result for name, result in results if name == "Credentials"):
            print("\n🔑 IMPORTANT: Make sure to place your Google Cloud credentials file:")
            print("  paradigm-gpt-9c0deac797aa.json")
            print("  in the project directory before running the application.")

if __name__ == "__main__":
    main()
