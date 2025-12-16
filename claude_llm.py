#!/usr/bin/env python3
"""
Claude LLM Integration Module
Handles Claude Sonnet 4 via Google Cloud Vertex AI for PDF data extraction
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Set service account credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "paradigm-gpt-9c0deac797aa.json"

from anthropic import AnthropicVertex

# Configuration
PROJECT_ID = "paradigm-gpt"
LOCATION = "us-east5"
MODEL_NAME = "claude-sonnet-4@20250514"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaudeLLMProcessor:
    """Claude LLM processor for AWS billing data extraction"""
    
    def __init__(self):
        """Initialize Claude LLM client"""
        self.client = None
        self.initialize_client()
    
    def initialize_client(self) -> bool:
        """Initialize Anthropic Vertex AI client"""
        try:
            self.client = AnthropicVertex(
                region=LOCATION,
                project_id=PROJECT_ID
            )
            logger.info("✅ Claude LLM client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Claude LLM: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test Claude LLM connectivity"""
        if not self.client:
            return False
            
        try:
            response = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=50,
                temperature=0.0,
                messages=[{
                    "role": "user",
                    "content": "Respond with 'OK' if you can process AWS billing data."
                }]
            )
            
            if response and response.content:
                logger.info("✅ Claude LLM connection test successful")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Claude LLM connection test failed: {e}")
            return False
    
    def extract_billing_data(self, pdf_text: str, filename: str) -> List[Dict[str, Any]]:
        """
        Extract AWS billing data from PDF text using Claude LLM
        
        Args:
            pdf_text: Raw text extracted from PDF
            filename: Name of the PDF file for context
            
        Returns:
            List of dictionaries containing extracted billing data
        """
        if not self.client:
            logger.error("Claude LLM client not initialized")
            return []
        
        extraction_prompt = f"""
You are an expert at extracting AWS billing data from text.

I have AWS billing data from the file: {filename}

Your task is to scan the text LINE BY LINE and identify every line that
represents an AWS compute instance usage entry. A line should be treated as an
instance row if it either:
- clearly contains an instance type (for example: t3a.small, t2.micro,
  m5.xlarge, r6g.4xlarge, etc.), OR
- explicitly mentions the word "instance" together with other billing details.

For EVERY such instance line you detect, you must create ONE JSON record and
populate the following fields using information from that line and any
immediately associated context (such as the same row or very close columns in
the extracted text):
- "AWS": Service / instance type (e.g., "t3a.small", "t2.micro")
- "OS": Operating System (e.g., "Linux/UNIX", "Windows")
- "Region": AWS Region (e.g., "Mumbai", "us-east-1")
- "Hours": Usage hours as number (e.g., 744, 2231.51)
- "Cores": Number of CPU cores as integer (e.g., 2, 4)
- "RAM": RAM in GB as integer (e.g., 2, 4, 8)
- "Cost": Cost in USD as string with $ (e.g., "$9.15", "$27.67")

IMPORTANT RULES:
1. You MUST return one JSON object per instance line you detect. Do not skip
   any instance rows.
2. If any field is missing or cannot be confidently determined for a given
   instance, set that field to null in that record.
3. Convert numeric values appropriately (Hours as float, Cores/RAM as int).
4. Keep Cost as a string including the $ symbol.
5. Ignore headers, footers, subtotals, and grand totals (for example, rows like
   "TOTAL"), unless they themselves look like a normal instance line.
6. Return ONLY a valid JSON array of these records, with no additional text
   before or after.

Text to process:
{pdf_text}

Return JSON array:
"""

        try:
            start_time = time.time()
            
            response = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=4000,
                temperature=0.1,
                messages=[{
                    "role": "user", 
                    "content": extraction_prompt
                }]
            )
            
            processing_time = time.time() - start_time
            
            if response and response.content:
                response_text = response.content[0].text.strip()
                logger.info(f"✅ Claude processed {filename} in {processing_time:.2f}s")
                
                # Try to parse JSON response
                try:
                    # Clean response text to extract JSON
                    if "```json" in response_text:
                        json_start = response_text.find("```json") + 7
                        json_end = response_text.find("```", json_start)
                        json_text = response_text[json_start:json_end].strip()
                    elif "[" in response_text:
                        json_start = response_text.find("[")
                        json_end = response_text.rfind("]") + 1
                        json_text = response_text[json_start:json_end]
                    else:
                        json_text = response_text
                    
                    extracted_data = json.loads(json_text)
                    
                    if isinstance(extracted_data, list):
                        logger.info(f"✅ Extracted {len(extracted_data)} billing records from {filename}")
                        return extracted_data
                    else:
                        logger.warning(f"⚠️ Unexpected data format from Claude for {filename}")
                        return []
                        
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse JSON response for {filename}: {e}")
                    logger.debug(f"Raw response: {response_text}")
                    return []
            else:
                logger.error(f"❌ No response from Claude for {filename}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Claude processing error for {filename}: {e}")
            return []
    
    def validate_extracted_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and clean extracted data
        
        Args:
            data: Raw extracted data from Claude
            
        Returns:
            Cleaned and validated data
        """
        validated_data = []
        
        for item in data:
            # Ensure all required fields exist
            validated_item = {
                "AWS": item.get("AWS"),
                "OS": item.get("OS"), 
                "Region": item.get("Region"),
                "Hours": item.get("Hours"),
                "Cores": item.get("Cores"),
                "RAM": item.get("RAM"),
                "Cost": item.get("Cost")
            }
            
            # Type conversions and validations
            try:
                if validated_item["Hours"] is not None:
                    validated_item["Hours"] = float(validated_item["Hours"])
                    
                if validated_item["Cores"] is not None:
                    validated_item["Cores"] = int(validated_item["Cores"])
                    
                if validated_item["RAM"] is not None:
                    validated_item["RAM"] = int(validated_item["RAM"])
                    
            except (ValueError, TypeError) as e:
                logger.warning(f"⚠️ Data validation warning: {e}")
            
            validated_data.append(validated_item)
        
        return validated_data
