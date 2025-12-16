#!/usr/bin/env python3
"""
Simple Claude LLM Access Test
Tests if Google Cloud Vertex AI Claude Sonnet 4 is accessible and responding
"""

import os
import sys
import json
import time
from datetime import datetime

# Set service account credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "paradigm-gpt-9c0deac797aa.json"

from anthropic import AnthropicVertex

# Configuration
PROJECT_ID = "paradigm-gpt"
LOCATION = "us-east5"  # Claude models are available in us-east5
MODEL_NAME = "claude-sonnet-4@20250514"  # Claude Sonnet 4 model

def test_claude_access():
    """Test basic Claude LLM accessibility with a simple prompt"""
    
    # Initialize Anthropic Vertex AI client
    try:
        client = AnthropicVertex(
            region=LOCATION,
            project_id=PROJECT_ID
        )
    except Exception as e:
        return False
        
    # Simple test prompt
    test_prompt = "Hello! Please introduce yourself"
    
    try:
        start_time = time.time()
        
        # Generate content with Claude
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=100,
            temperature=0.0,  # Deterministic response
            messages=[
                {
                    "role": "user",
                    "content": test_prompt
                }
            ]
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Check if we got a response
        if response and response.content and len(response.content) > 0:
            return True
        else:
            return False
            
    except Exception as e:
        return False

def test_claude_with_details():
    """Test Claude access with detailed output"""
    
    print("🚀 CLAUDE LLM ACCESSIBILITY TEST")
    print("=" * 50)
    print(f" Model: {MODEL_NAME}")
    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print("=" * 50)
    
    # Initialize Anthropic Vertex AI client
    try:
        client = AnthropicVertex(
            region=LOCATION,
            project_id=PROJECT_ID
        )
        print("✅ Anthropic Vertex AI initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Anthropic Vertex AI: {e}")
        return False
        
    print("\n🤖 Testing Claude accessibility...")
    
    # Simple test prompt
    test_prompt = "Hello! Please introduce yourself"
    
    try:
        start_time = time.time()
        
        # Generate content with Claude
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=100,
            temperature=0.0,  # Deterministic response
            messages=[
                {
                    "role": "user",
                    "content": test_prompt
                }
            ]
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Check if we got a response
        if response and response.content and len(response.content) > 0:
            response_text = response.content[0].text
            print(f"✅ Claude responded successfully in {processing_time:.2f}s")
            print(f"📝 Response: {response_text}")
            print("\n🎉 SUCCESS: Claude LLM is accessible and working!")
            return True
        else:
            print("❌ No response content from Claude")
            print("\n❌ FAILED: Claude LLM is not accessible")
            return False
            
    except Exception as e:
        print(f"❌ Claude access error: {e}")
        print("\n❌ FAILED: Claude LLM is not accessible")
        return False

def test_aws_billing_extraction():
    """Test Claude with AWS billing data extraction"""
    
    print("\n🧪 TESTING AWS BILLING DATA EXTRACTION")
    print("=" * 50)
    
    # Sample AWS billing text (similar to what would be extracted from PDF)
    sample_billing_text = """
    AWS Service Usage Report - April 2024
    
    Service: t3a.small
    Operating System: Linux/UNIX
    Region: Mumbai
    Usage Hours: 744
    CPU Cores: 2
    RAM: 2 GB
    Cost: $9.15
    
    Service: t2.micro
    Operating System: Linux/UNIX
    Region: Mumbai
    Usage Hours: 2,231.51
    CPU Cores: 1
    RAM: 1 GB
    Cost: $27.67
    
    Service: t3.medium
    Operating System: Linux/UNIX
    Region: Mumbai
    Usage Hours: 744
    CPU Cores: 2
    RAM: 4 GB
    Cost: $33.33
    """
    
    extraction_prompt = f"""
You are an expert at extracting AWS billing data from text. 

Please extract ALL billing line items from this text and return them as a JSON array. 
Each item should have these exact fields:
- "AWS": Service type (e.g., "t3a.small", "t2.micro")
- "OS": Operating System (e.g., "Linux/UNIX", "Windows")  
- "Region": AWS Region (e.g., "Mumbai", "us-east-1")
- "Hours": Usage hours as number (e.g., 744, 2231.51)
- "Cores": Number of CPU cores as integer (e.g., 2, 4)
- "RAM": RAM in GB as integer (e.g., 2, 4, 8)
- "Cost": Cost in USD as string with $ (e.g., "$9.15", "$27.67")

IMPORTANT RULES:
1. If any field is missing or unclear, use null
2. Convert numeric values appropriately (Hours as float, Cores/RAM as int)
3. Keep Cost as string with $ symbol
4. Extract EVERY billing line, ignore headers and totals
5. Return ONLY valid JSON array, no other text

Text to process:
{sample_billing_text}

Return JSON array:
"""
    
    try:
        client = AnthropicVertex(
            region=LOCATION,
            project_id=PROJECT_ID
        )
        
        print("🔄 Testing AWS billing data extraction...")
        start_time = time.time()
        
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=2000,
            temperature=0.1,
            messages=[{
                "role": "user",
                "content": extraction_prompt
            }]
        )
        
        processing_time = time.time() - start_time
        
        if response and response.content:
            response_text = response.content[0].text.strip()
            print(f"✅ Claude processed billing data in {processing_time:.2f}s")
            print(f"📝 Raw Response:\n{response_text}")
            
            # Try to parse JSON
            try:
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
                print(f"\n✅ Successfully parsed {len(extracted_data)} billing records:")
                for i, record in enumerate(extracted_data, 1):
                    print(f"  {i}. {record}")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON: {e}")
                return False
        else:
            print("❌ No response from Claude")
            return False
            
    except Exception as e:
        print(f"❌ AWS billing extraction test failed: {e}")
        return False

if __name__ == "__main__":
    # Run detailed test
    success = test_claude_with_details()
    
    if success:
        # Test AWS billing extraction
        test_aws_billing_extraction()
    
    print("=" * 50)
