#!/usr/bin/env python3
"""
Test the fixed AWS cost extraction
"""

import os
import sys
sys.path.append('/Users/admin/Downloads/BOT')

from claude_aws_enhanced import EnhancedClaudeAWSAnalyzer
from pdf_processor import PDFProcessor

def test_fixed_extraction():
    """Test the corrected extraction system"""
    
    # Initialize components
    analyzer = EnhancedClaudeAWSAnalyzer()
    pdf_processor = PDFProcessor()
    
    # Extract text from PDF
    pdf_file = "/Users/admin/Downloads/BOT/AWS1_April.pdf"
    
    try:
        pdf_text = pdf_processor.extract_text_from_file(pdf_file)
        
        print("🔍 Testing Fixed AWS Cost Extraction")
        print("=" * 50)
        
        # Test the corrected analysis
        print("📊 Step 1: Initial analysis with corrected prompt...")
        analysis_data = analyzer.extract_comprehensive_aws_data(pdf_text, "AWS1_April.pdf")
        
        if analysis_data:
            enhanced_analysis = analyzer.validate_and_enhance_analysis(analysis_data)
            
            # Show results
            cost_validation = enhanced_analysis.get('cost_validation', {})
            calculated_total = cost_validation.get('calculated_total', 0.0)
            invoice_total = cost_validation.get('invoice_total', 0.0)
            difference = cost_validation.get('difference', 0.0)
            
            print(f"✅ Corrected Analysis Results:")
            print(f"   📋 Service Items Found: {len(enhanced_analysis.get('service_line_items', []))}")
            print(f"   💰 Invoice Total: ${invoice_total:,.2f}")
            print(f"   🧮 Calculated Total: ${calculated_total:,.2f}")
            print(f"   ⚠️  Difference: ${difference:,.2f}")
            
            # Test reconciliation if needed
            if abs(difference) > 1.0:
                print(f"\n🔍 Step 2: Cost reconciliation...")
                reconciled_analysis = analyzer.reconcile_missing_costs(
                    pdf_text, "AWS1_April.pdf", enhanced_analysis
                )
                
                final_cost_validation = reconciled_analysis.get('cost_validation', {})
                final_calculated = final_cost_validation.get('calculated_total', 0.0)
                final_difference = final_cost_validation.get('difference', 0.0)
                
                print(f"✅ Final Results:")
                print(f"   📋 Total Service Items: {len(reconciled_analysis.get('service_line_items', []))}")
                print(f"   🧮 Final Calculated Total: ${final_calculated:,.2f}")
                print(f"   ✨ Final Difference: ${final_difference:,.2f}")
                
                if abs(final_difference) < 50.0:  # Within $50
                    print(f"   🎉 SUCCESS: Much better accuracy!")
                else:
                    print(f"   ⚠️  Still needs work: ${abs(final_difference):.2f} difference")
            else:
                print(f"✅ Excellent! Difference already minimal: ${abs(difference):.2f}")
        
        else:
            print("❌ Failed to extract analysis data")
    
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_fixed_extraction()
