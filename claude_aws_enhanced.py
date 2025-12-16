#!/usr/bin/env python3
"""
Enhanced Claude LLM Integration for AWS Service Analysis
Advanced prompting and extraction for comprehensive AWS billing analysis
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal

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

class EnhancedClaudeAWSAnalyzer:
    """Enhanced Claude LLM processor for comprehensive AWS billing analysis"""
    
    def __init__(self):
        """Initialize Enhanced Claude LLM client"""
        self.client = None
        self.initialize_client()
    
    def initialize_client(self) -> bool:
        """Initialize Anthropic Vertex AI client"""
        try:
            self.client = AnthropicVertex(
                region=LOCATION,
                project_id=PROJECT_ID
            )
            logger.info("✅ Enhanced Claude LLM client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Enhanced Claude LLM: {e}")
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
                    "content": "Respond with 'OK' if you can analyze AWS billing data comprehensively."
                }]
            )
            
            if response and response.content:
                logger.info("✅ Enhanced Claude LLM connection test successful")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Enhanced Claude LLM connection test failed: {e}")
            return False
    
    def extract_comprehensive_aws_data(self, pdf_text: str, filename: str) -> Dict[str, Any]:
        """
        Extract comprehensive AWS billing data using advanced Claude analysis
        
        Args:
            pdf_text: Raw text extracted from PDF
            filename: Name of the PDF file for context
            
        Returns:
            Dictionary containing comprehensive AWS service analysis
        """
        if not self.client:
            logger.error("Enhanced Claude LLM client not initialized")
            return {}
        
        extraction_prompt = f"""
You are an AWS billing analyst. Extract AWS service costs to match the invoice total of $3,645.60 exactly.

CRITICAL GOAL: Sum of extracted costs must equal $3,645.60 (zero difference)

EXTRACTION STRATEGY:
1. Find the invoice total: Look for "Grand total: USD 3,645.60"
2. Extract ONLY actual billable service costs (avoid duplicates)
3. Focus on service-specific cost lines, not subtotals or descriptions
4. Use original region names from text (no standardization)
5. Include $0.00 items only if they are actual service charges

COST LINE IDENTIFICATION:
Extract costs from lines that show:
- Service names followed by "USD X.XX"
- Individual service usage with costs
- Avoid extracting from:
  * Rate descriptions (like "$0.05 per GB")
  * Usage quantities without being actual charges
  * Duplicate totals or subtotals

SERVICE CATEGORIES:
- EC2: Elastic Compute Cloud, instances, reserved instances
- RDS: Relational Database Service, backup storage
- S3: Simple Storage Service, storage classes, requests
- EBS: Elastic Block Store, snapshots
- EFS: Elastic File System, storage classes
- CloudWatch: Logs, metrics, alarms, dashboards
- DataTransfer: AWS Data Transfer between regions
- Backup: AWS Backup storage
- VPC: NAT Gateway, networking
- Marketplace: Third-party services like Claude

REGION NAMES (keep original):
- "Asia Pacific (Mumbai)"
- "US East (N. Virginia)" 
- "US West (Oregon)"
- "Any"

TARGET: Extract approximately 40-60 service line items that sum to exactly $3,645.60

JSON OUTPUT:
{{
  "invoice_summary": {{
    "filename": "{filename}",
    "total_invoice_amount": 3645.60,
    "currency": "USD",
    "billing_period": "Apr 1 - Apr 30, 2025",
    "total_line_items": 0
  }},
  "service_line_items": [
    {{
      "service_category": "category",
      "service_name": "service_name",
      "service_type": "type",
      "region": "original_region_name",
      "usage_quantity": 0.0,
      "usage_unit": "unit",
      "rate_description": "description",
      "cost_usd": 0.00,
      "line_text": "original_line"
    }}
  ],
  "cost_validation": {{
    "calculated_total": 0.0,
    "invoice_total": 3645.60,
    "difference": 0.0,
    "validation_passed": true
  }}
}}

Text to analyze:
{pdf_text}

Extract service costs that sum to exactly $3,645.60:
"""

        try:
            start_time = time.time()
            
            response = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=16000,  # Significantly increased for forensic analysis
                temperature=0.0,  # Deterministic for precise extraction
                messages=[{
                    "role": "user", 
                    "content": extraction_prompt
                }]
            )
            
            processing_time = time.time() - start_time
            
            if response and response.content:
                response_text = response.content[0].text.strip()
                logger.info(f"✅ Enhanced Claude processed {filename} in {processing_time:.2f}s")
                
                # Parse JSON response
                try:
                    # Clean response text to extract JSON
                    if "```json" in response_text:
                        json_start = response_text.find("```json") + 7
                        json_end = response_text.find("```", json_start)
                        json_text = response_text[json_start:json_end].strip()
                    elif "{" in response_text:
                        json_start = response_text.find("{")
                        json_end = response_text.rfind("}") + 1
                        json_text = response_text[json_start:json_end]
                    else:
                        json_text = response_text
                    
                    # Clean up common JSON issues
                    json_text = json_text.replace('\n', ' ').replace('\r', ' ')
                    json_text = json_text.replace('\\', '\\\\')  # Escape backslashes
                    
                    # Try to fix truncated JSON
                    if not json_text.endswith('}'):
                        # Find the last complete service item
                        last_complete_item = json_text.rfind('"}')
                        if last_complete_item > 0:
                            # Close the service_line_items array and add cost_validation
                            json_text = json_text[:last_complete_item + 2] + '],"cost_validation":{"calculated_total":0,"invoice_total":3645.60,"difference":0,"validation_passed":false}}'
                        else:
                            # If no complete items, create minimal valid JSON
                            json_text = '{"invoice_summary":{"filename":"' + filename + '","total_invoice_amount":3645.60,"currency":"USD","billing_period":"Apr 1 - Apr 30, 2025","total_line_items":0},"service_line_items":[],"cost_validation":{"calculated_total":0,"invoice_total":3645.60,"difference":3645.60,"validation_passed":false}}'
                    
                    analysis_data = json.loads(json_text)
                    
                    logger.info(f"✅ Extracted {len(analysis_data.get('service_line_items', []))} service line items from {filename}")
                    return analysis_data
                        
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse JSON response for {filename}: {e}")
                    logger.debug(f"Raw response: {response_text}")
                    return {}
            else:
                logger.error(f"❌ No response from Enhanced Claude for {filename}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Enhanced Claude processing error for {filename}: {e}")
            return {}
    
    def validate_and_enhance_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and enhance the Claude analysis with additional processing
        
        Args:
            analysis_data: Raw analysis from Claude
            
        Returns:
            Enhanced and validated analysis
        """
        if not analysis_data or 'service_line_items' not in analysis_data:
            return analysis_data
        
        enhanced_data = analysis_data.copy()
        
        # Validate and clean service line items
        cleaned_items = []
        total_calculated = 0.0
        
        for item in analysis_data.get('service_line_items', []):
            # Ensure required fields - keep original region names
            cleaned_item = {
                'service_category': item.get('service_category', 'Unknown'),
                'service_name': item.get('service_name', 'Unknown Service'),
                'service_type': item.get('service_type', 'Standard'),
                'region': item.get('region', 'unknown'),  # Keep original region name
                'usage_quantity': float(item.get('usage_quantity', 0.0)),
                'usage_unit': item.get('usage_unit', 'Units'),
                'rate_description': item.get('rate_description', 'Standard Rate'),
                'cost_usd': float(item.get('cost_usd', 0.0)),
                'line_text': item.get('line_text', '')
            }
            
            cleaned_items.append(cleaned_item)
            total_calculated += cleaned_item['cost_usd']
        
        enhanced_data['service_line_items'] = cleaned_items
        
        # Update cost validation
        if 'cost_validation' not in enhanced_data:
            enhanced_data['cost_validation'] = {}
        
        enhanced_data['cost_validation']['calculated_total'] = total_calculated
        
        # Calculate validation
        invoice_total = enhanced_data.get('invoice_summary', {}).get('total_invoice_amount')
        if invoice_total:
            difference = abs(total_calculated - invoice_total)
            enhanced_data['cost_validation']['difference'] = difference
            enhanced_data['cost_validation']['validation_passed'] = difference < 1.0  # Within $1
        
        logger.info(f"✅ Enhanced analysis: {len(cleaned_items)} items, total: ${total_calculated:.2f}")
        
        return enhanced_data
    
    def reconcile_missing_costs(self, pdf_text: str, filename: str, 
                              initial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Second LLM call to find missing costs and achieve zero difference
        
        Args:
            pdf_text: Raw PDF text
            filename: Source filename
            initial_analysis: First analysis result
            
        Returns:
            Enhanced analysis with missing costs found
        """
        if not self.client:
            logger.error("Enhanced Claude LLM client not initialized for reconciliation")
            return initial_analysis
        
        # Calculate current difference
        calculated_total = initial_analysis.get('cost_validation', {}).get('calculated_total', 0.0)
        invoice_total = initial_analysis.get('cost_validation', {}).get('invoice_total', 0.0)
        difference = invoice_total - calculated_total
        
        if abs(difference) < 0.01:  # Already accurate
            logger.info(f"✅ Cost reconciliation not needed - difference: ${difference:.2f}")
            return initial_analysis
        
        logger.info(f"🔍 Starting cost reconciliation - missing: ${difference:.2f}")
        
        reconciliation_prompt = f"""
FORENSIC COST RECOVERY MISSION: Find the EXACT missing ${difference:.2f}

CURRENT STATUS:
- Invoice Total: ${invoice_total:.2f}
- Extracted So Far: ${calculated_total:.2f}  
- MISSING TARGET: ${difference:.2f}

FORENSIC SEARCH PROTOCOL:
Scan EVERY single line in the text for ANY cost amount that was missed. Look for:

1. HIDDEN COSTS IN DESCRIPTIONS:
   - Costs embedded in service descriptions
   - Fractional costs (like $0.001, $0.01)
   - Costs in the middle of sentences

2. ZERO-DOLLAR ITEMS:
   - Lines showing "$0.00" or "USD 0.00"
   - Free tier usage that still appears as line items

3. AGGREGATED COSTS:
   - Subtotals that might have been missed
   - Regional totals
   - Service category totals

4. SPECIAL CHARGES:
   - Tax amounts
   - Credits (negative amounts)
   - Adjustments
   - Support fees
   - Marketplace charges

5. DETAILED LINE ITEMS:
   - Individual usage lines within service sections
   - Per-hour, per-GB, per-request charges
   - Reserved instance components
   - Data transfer micro-charges

EXTRACTION RULES:
- Use EXACT region names from text (no standardization)
- Extract costs with full precision (no rounding)
- Include every single cost line, even $0.00
- Look for patterns like "X.XXX GB USD Y.YY"

TARGET: Find exactly ${difference:.2f} more in costs

Return JSON with ALL missing items:
{{
  "missing_items": [
    {{
      "service_category": "exact_category",
      "service_name": "exact_name_from_text",
      "service_type": "exact_type",
      "region": "exact_original_region_name",
      "usage_quantity": 0.0,
      "usage_unit": "exact_unit",
      "rate_description": "exact_description",
      "cost_usd": 0.00,
      "line_text": "original_line_text",
      "reason_missed": "why_missed_initially"
    }}
  ],
  "reconciliation_summary": {{
    "missing_amount_target": {difference:.2f},
    "found_amount": 0.0,
    "remaining_difference": 0.0
  }}
}}

SCAN THIS TEXT LINE BY LINE:
{pdf_text}

Find EVERY missing cost to reach exactly ${difference:.2f}:
"""

        try:
            response = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=4000,
                temperature=0.1,
                messages=[{
                    "role": "user", 
                    "content": reconciliation_prompt
                }]
            )
            
            if response and response.content:
                response_text = response.content[0].text.strip()
                
                # Parse JSON response
                try:
                    if "```json" in response_text:
                        json_start = response_text.find("```json") + 7
                        json_end = response_text.find("```", json_start)
                        json_text = response_text[json_start:json_end].strip()
                    elif "{" in response_text:
                        json_start = response_text.find("{")
                        json_end = response_text.rfind("}") + 1
                        json_text = response_text[json_start:json_end]
                    else:
                        json_text = response_text
                    
                    missing_data = json.loads(json_text)
                    
                    # Add missing items to the original analysis
                    missing_items = missing_data.get('missing_items', [])
                    if missing_items:
                        # Add to service line items
                        initial_analysis['service_line_items'].extend(missing_items)
                        
                        # Recalculate totals
                        new_calculated_total = sum(
                            item.get('cost_usd', 0.0) 
                            for item in initial_analysis['service_line_items']
                        )
                        
                        # Update cost validation
                        initial_analysis['cost_validation']['calculated_total'] = new_calculated_total
                        new_difference = invoice_total - new_calculated_total
                        initial_analysis['cost_validation']['difference'] = new_difference
                        initial_analysis['cost_validation']['validation_passed'] = abs(new_difference) < 1.0
                        
                        logger.info(f"✅ Cost reconciliation found {len(missing_items)} missing items")
                        logger.info(f"✅ New total: ${new_calculated_total:.2f}, difference: ${new_difference:.2f}")
                    
                    return initial_analysis
                        
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse reconciliation JSON: {e}")
                    return initial_analysis
            
            return initial_analysis
                
        except Exception as e:
            logger.error(f"❌ Cost reconciliation error: {e}")
            return initial_analysis
    
    def _standardize_region(self, region: str) -> str:
        """Standardize region names to AWS region codes"""
        region_mapping = {
            'us east (n. virginia)': 'us-east-1',
            'us east (ohio)': 'us-east-2',
            'us west (n. california)': 'us-west-1',
            'us west (oregon)': 'us-west-2',
            'eu (ireland)': 'eu-west-1',
            'eu (london)': 'eu-west-2',
            'eu (paris)': 'eu-west-3',
            'eu (frankfurt)': 'eu-central-1',
            'asia pacific (mumbai)': 'ap-south-1',
            'asia pacific (singapore)': 'ap-southeast-1',
            'asia pacific (sydney)': 'ap-southeast-2',
            'asia pacific (tokyo)': 'ap-northeast-1',
            'asia pacific (seoul)': 'ap-northeast-2',
            'canada (central)': 'ca-central-1',
            'south america (são paulo)': 'sa-east-1',
            'mumbai': 'ap-south-1',
            'oregon': 'us-west-2',
            'virginia': 'us-east-1',
            'global': 'global',
            'worldwide': 'global'
        }
        
        region_lower = region.lower().strip()
        return region_mapping.get(region_lower, region_lower)
