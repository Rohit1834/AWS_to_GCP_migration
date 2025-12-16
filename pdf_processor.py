#!/usr/bin/env python3
"""
PDF Processing Module
Handles PDF text extraction and data processing for AWS billing documents
"""

import os
import io
import logging
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import pdfplumber
import PyPDF2
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF processor for AWS billing documents"""
    
    def __init__(self):
        """Initialize PDF processor"""
        self.supported_formats = ['.pdf']
        
    def validate_pdf_file(self, file_path: str) -> bool:
        """
        Validate if file is a valid PDF
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.supported_formats:
                logger.error(f"❌ Unsupported file format: {file_ext}")
                return False
                
            # Check if file exists and is readable
            if not os.path.exists(file_path):
                logger.error(f"❌ File not found: {file_path}")
                return False
                
            # Try to open with PyPDF2 to validate
            with open(file_path, 'rb') as file:
                PyPDF2.PdfReader(file)
                
            logger.info(f"✅ Valid PDF file: {Path(file_path).name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ PDF validation failed for {file_path}: {e}")
            return False
    
    def extract_text_pdfplumber(self, file_path: str) -> str:
        """
        Extract text using pdfplumber (better for tables)
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            text_content = ""
            
            with pdfplumber.open(file_path) as pdf:
                logger.info(f"📄 Processing {len(pdf.pages)} pages with pdfplumber")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        # Extract tables first (better for structured data)
                        tables = page.extract_tables()
                        
                        if tables:
                            logger.info(f"📊 Found {len(tables)} tables on page {page_num}")
                            for table in tables:
                                for row in table:
                                    if row:  # Skip empty rows
                                        row_text = "\t".join([str(cell) if cell else "" for cell in row])
                                        text_content += row_text + "\n"
                        
                        # Also extract regular text
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Error processing page {page_num}: {e}")
                        continue
            
            logger.info(f"✅ Extracted {len(text_content)} characters using pdfplumber")
            return text_content
            
        except Exception as e:
            logger.error(f"❌ pdfplumber extraction failed: {e}")
            return ""
    
    def extract_text_pypdf2(self, file_path: str) -> str:
        """
        Extract text using PyPDF2 (fallback method)
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            text_content = ""
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                logger.info(f"📄 Processing {len(pdf_reader.pages)} pages with PyPDF2")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"⚠️ Error processing page {page_num}: {e}")
                        continue
            
            logger.info(f"✅ Extracted {len(text_content)} characters using PyPDF2")
            return text_content
            
        except Exception as e:
            logger.error(f"❌ PyPDF2 extraction failed: {e}")
            return ""
    
    def extract_text_from_uploaded_file(self, uploaded_file) -> Tuple[str, str]:
        """
        Extract text from Streamlit uploaded file
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Tuple of (extracted_text, filename)
        """
        try:
            filename = uploaded_file.name
            logger.info(f"🔄 Processing uploaded file: {filename}")
            
            # Read file content
            file_content = uploaded_file.read()
            
            # Try pdfplumber first (better for tables)
            try:
                with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                    text_content = ""
                    
                    for page_num, page in enumerate(pdf.pages, 1):
                        try:
                            # Extract tables first
                            tables = page.extract_tables()
                            
                            if tables:
                                for table in tables:
                                    for row in table:
                                        if row:
                                            row_text = "\t".join([str(cell) if cell else "" for cell in row])
                                            text_content += row_text + "\n"
                            
                            # Also extract regular text
                            page_text = page.extract_text()
                            if page_text:
                                text_content += page_text + "\n"
                                
                        except Exception as e:
                            logger.warning(f"⚠️ Error processing page {page_num}: {e}")
                            continue
                
                if text_content.strip():
                    logger.info(f"✅ Extracted {len(text_content)} characters from {filename}")
                    return text_content, filename
                    
            except Exception as e:
                logger.warning(f"⚠️ pdfplumber failed for {filename}: {e}")
            
            # Fallback to PyPDF2
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                text_content = ""
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
                
                if text_content.strip():
                    logger.info(f"✅ Extracted {len(text_content)} characters from {filename} (PyPDF2)")
                    return text_content, filename
                    
            except Exception as e:
                logger.error(f"❌ PyPDF2 also failed for {filename}: {e}")
            
            logger.error(f"❌ All extraction methods failed for {filename}")
            return "", filename
            
        except Exception as e:
            logger.error(f"❌ File processing error: {e}")
            return "", uploaded_file.name if hasattr(uploaded_file, 'name') else "unknown"
    
    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from PDF file using multiple methods
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        if not self.validate_pdf_file(file_path):
            return ""
        
        # Try pdfplumber first (better for structured data)
        text_content = self.extract_text_pdfplumber(file_path)
        
        # If pdfplumber fails or returns empty, try PyPDF2
        if not text_content.strip():
            logger.info("🔄 Trying PyPDF2 as fallback...")
            text_content = self.extract_text_pypdf2(file_path)
        
        if not text_content.strip():
            logger.error(f"❌ Failed to extract any text from {file_path}")
            return ""
        
        logger.info(f"✅ Successfully extracted text from {Path(file_path).name}")
        return text_content
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess extracted text for better LLM processing
        
        Args:
            text: Raw extracted text
            
        Returns:
            Preprocessed text
        """
        if not text:
            return ""
        
        # Basic text cleaning
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                # Remove excessive whitespace
                line = ' '.join(line.split())
                cleaned_lines.append(line)
        
        cleaned_text = '\n'.join(cleaned_lines)
        
        logger.info(f"✅ Preprocessed text: {len(cleaned_text)} characters")
        return cleaned_text
