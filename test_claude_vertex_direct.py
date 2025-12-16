#!/usr/bin/env python3
"""
Claude LLM Access Test via Google Cloud Vertex AI Direct
Tests Claude Sonnet 4 access using Google Cloud Vertex AI client directly
"""

import os
import json
import time
from datetime import datetime

# Set service account credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "paradigm-gpt-9c0deac797aa.json"

try:
    from google.cloud import aiplatform
    from google.cloud.aiplatform import gapic
    print("✅ Google Cloud AI Platform imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Google Cloud AI Platform: {e}")
    exit(1)

# Configuration
PROJECT_ID = "paradigm-gpt"
LOCATION = "us-east5"  # Claude models are available in us-east5
MODEL_NAME = "claude-3-5-sonnet@20241022"  # Claude 3.5 Sonnet latest version

def test_vertex_ai_claude():
    """Test Claude access via Vertex AI direct client"""
    
    print("🚀 CLAUDE VIA VERTEX AI DIRECT TEST")
    print("=" * 50)
    print(f" Model: {MODEL_NAME}")
    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print("=" * 50)
    
    try:
        # Initialize Vertex AI
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        print("✅ Vertex AI initialized successfully")
        
        # Create prediction client
        client_options = {"api_endpoint": f"{LOCATION}-aiplatform.googleapis.com"}
        client = gapic.PredictionServiceClient(client_options=client_options)
        print("✅ Prediction client created successfully")
        
        # Prepare the request
        endpoint = f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/anthropic/models/{MODEL_NAME}"
        
        # Test prompt
        test_prompt = "Hello! Please introduce yourself in one sentence."
        
        # Prepare the request payload
        instance = {
            "messages": [
                {
                    "role": "user",
                    "content": test_prompt
                }
            ],
            "max_tokens": 100,
            "temperature": 0.0
        }
        
        instances = [instance]
        
        print("\n🤖 Testing Claude accessibility...")
        start_time = time.time()
        
        # Make the prediction request
        response = client.predict(
            endpoint=endpoint,
            instances=instances
        )
        
        processing_time = time.time() - start_time
        
        if response.predictions:
            prediction = response.predictions[0]
            print(f"✅ Claude responded successfully in {processing_time:.2f}s")
            print(f"📝 Response: {prediction}")
            print("\n🎉 SUCCESS: Claude LLM is accessible via Vertex AI!")
            return True
        else:
            print("❌ No predictions in response")
            return False
            
    except Exception as e:
        print(f"❌ Vertex AI Claude test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_anthropic_direct():
    """Test if we can use Anthropic client directly with API key"""
    
    print("\n🧪 TESTING ANTHROPIC DIRECT CLIENT")
    print("=" * 50)
    
    try:
        from anthropic import Anthropic
        
        # Check if API key is available
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("⚠️ ANTHROPIC_API_KEY not found in environment variables")
            print("This test requires a direct Anthropic API key")
            return False
        
        client = Anthropic(api_key=api_key)
        print("✅ Anthropic client initialized successfully")
        
        # Test prompt
        test_prompt = "Hello! Please introduce yourself in one sentence."
        
        print("🤖 Testing Anthropic direct access...")
        start_time = time.time()
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",  # Use available model
            max_tokens=100,
            temperature=0.0,
            messages=[{
                "role": "user",
                "content": test_prompt
            }]
        )
        
        processing_time = time.time() - start_time
        
        if response and response.content:
            response_text = response.content[0].text
            print(f"✅ Anthropic responded successfully in {processing_time:.2f}s")
            print(f"📝 Response: {response_text}")
            print("\n🎉 SUCCESS: Anthropic direct client working!")
            return True
        else:
            print("❌ No response from Anthropic")
            return False
            
    except Exception as e:
        print(f"❌ Anthropic direct test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Claude LLM access methods...")
    
    # Test 1: Vertex AI direct
    vertex_success = test_vertex_ai_claude()
    
    # Test 2: Anthropic direct (if API key available)
    anthropic_success = test_anthropic_direct()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    print(f"Vertex AI Claude: {'✅ SUCCESS' if vertex_success else '❌ FAILED'}")
    print(f"Anthropic Direct: {'✅ SUCCESS' if anthropic_success else '❌ FAILED'}")
    
    if vertex_success or anthropic_success:
        print("\n🎉 At least one Claude access method is working!")
    else:
        print("\n❌ No Claude access methods are working.")
        print("Please check your credentials and configuration.")
    
    print("=" * 50)
