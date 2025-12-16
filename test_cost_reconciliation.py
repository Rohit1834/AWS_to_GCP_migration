#!/usr/bin/env python3
"""
Test script to demonstrate cost reconciliation functionality
"""

import os
import sys
sys.path.append('/Users/admin/Downloads/BOT')

from claude_aws_enhanced import EnhancedClaudeAWSAnalyzer

def test_cost_reconciliation():
    """Test the cost reconciliation with the AWS April PDF"""
    
    # Initialize the enhanced analyzer
    analyzer = EnhancedClaudeAWSAnalyzer()
    
    # Read the extracted text
    text_file = "/Users/admin/Downloads/BOT/output/AWS1_April_extracted.txt"
    
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            pdf_text = f.read()
        
        print("🔍 Testing Enhanced AWS Analysis with Cost Reconciliation")
        print("=" * 60)
        
        # First analysis
        print("📊 Step 1: Initial comprehensive analysis...")
        analysis_data = analyzer.extract_comprehensive_aws_data(pdf_text, "AWS1_April.pdf")
        
        if analysis_data:
            enhanced_analysis = analyzer.validate_and_enhance_analysis(analysis_data)
            
            # Show initial results
            cost_validation = enhanced_analysis.get('cost_validation', {})
            calculated_total = cost_validation.get('calculated_total', 0.0)
            invoice_total = cost_validation.get('invoice_total', 0.0)
            difference = cost_validation.get('difference', 0.0)
            
            print(f"✅ Initial Analysis Results:")
            print(f"   📋 Service Items Found: {len(enhanced_analysis.get('service_line_items', []))}")
            print(f"   💰 Invoice Total: ${invoice_total:,.2f}")
            print(f"   🧮 Calculated Total: ${calculated_total:,.2f}")
            print(f"   ⚠️  Difference: ${difference:,.2f}")
            
            # Cost reconciliation if needed
            if abs(difference) > 1.0:
                print(f"\n🔍 Step 2: Cost reconciliation (finding missing ${abs(difference):.2f})...")
                reconciled_analysis = analyzer.reconcile_missing_costs(
                    pdf_text, "AWS1_April.pdf", enhanced_analysis
                )
                
                # Show reconciled results
                final_cost_validation = reconciled_analysis.get('cost_validation', {})
                final_calculated = final_cost_validation.get('calculated_total', 0.0)
                final_difference = final_cost_validation.get('difference', 0.0)
                
                print(f"✅ Reconciliation Results:")
                print(f"   📋 Total Service Items: {len(reconciled_analysis.get('service_line_items', []))}")
                print(f"   🧮 Final Calculated Total: ${final_calculated:,.2f}")
                print(f"   ✨ Final Difference: ${final_difference:,.2f}")
                
                if abs(final_difference) < 1.0:
                    print(f"   🎉 SUCCESS: Cost difference minimized to ${abs(final_difference):.2f}!")
                else:
                    print(f"   ⚠️  Still ${abs(final_difference):.2f} difference remaining")
            else:
                print(f"✅ No reconciliation needed - difference already minimal!")
        
        else:
            print("❌ Failed to extract analysis data")
    
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_cost_reconciliation()
