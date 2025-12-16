#!/usr/bin/env python3
"""
AWS Billing Data Extractor - Streamlit MVP
Main application for processing AWS billing PDFs using Claude LLM
"""

import streamlit as st
import os
import logging
from typing import List, Dict, Any, Optional
import time
from pathlib import Path
import pandas as pd

# Import custom modules
from claude_llm import ClaudeLLMProcessor
from pdf_processor import PDFProcessor
from excel_handler import ExcelHandler
from claude_aws_enhanced import EnhancedClaudeAWSAnalyzer
from excel_aws_advanced import AdvancedAWSExcelHandler
from forensic_extractor import ForensicAWSExtractor
from aws_to_gcp_mapper import AWSToGCPMapper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AWS Billing Data Extractor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AWSBillingExtractor:
    """Main application class for AWS billing data extraction"""
    
    def __init__(self):
        """Initialize the application"""
        self.claude_processor = None
        self.enhanced_claude = None
        self.forensic_extractor = ForensicAWSExtractor()
        self.aws_gcp_mapper = AWSToGCPMapper()
        self.pdf_processor = PDFProcessor()
        self.excel_handler = ExcelHandler(base_directory=os.getcwd())
        self.advanced_excel_handler = AdvancedAWSExcelHandler(base_directory=os.getcwd())
        self.initialize_session_state()
        
        # Auto-initialize Claude LLM if not already done
        if not st.session_state.claude_initialized:
            self.initialize_claude()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'processing_results' not in st.session_state:
            st.session_state.processing_results = {}
        if 'claude_initialized' not in st.session_state:
            st.session_state.claude_initialized = False
        if 'processing_complete' not in st.session_state:
            st.session_state.processing_complete = False
        if 'analysis_mode' not in st.session_state:
            st.session_state.analysis_mode = 'Basic'
        if 'aws_analysis_results' not in st.session_state:
            st.session_state.aws_analysis_results = {}
    
    def initialize_claude(self) -> bool:
        """Initialize Claude LLM processor"""
        if st.session_state.claude_initialized and self.claude_processor:
            return True
        
        # Reset session state if processor is None
        if not self.claude_processor:
            st.session_state.claude_initialized = False
        
        try:
            with st.spinner("🔄 Initializing Claude LLM..."):
                self.claude_processor = ClaudeLLMProcessor()
                self.enhanced_claude = EnhancedClaudeAWSAnalyzer()
                
                if self.claude_processor.test_connection() and self.enhanced_claude.test_connection():
                    st.session_state.claude_initialized = True
                    st.success("✅ Claude LLM and Enhanced AWS Analyzer initialized successfully!")
                    return True
                else:
                    st.error("❌ Failed to connect to Claude LLM")
                    return False
                    
        except Exception as e:
            st.error(f"❌ Claude initialization error: {e}")
            logger.error(f"Claude initialization error: {e}")
            return False
    
    def process_single_pdf(self, uploaded_file) -> Dict[str, Any]:
        """
        Process a single PDF file
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Dictionary with processing results
        """
        result = {
            'filename': uploaded_file.name,
            'success': False,
            'data': [],
            'error': None,
            'processing_time': 0,
            'non_instance_lines': []
        }
        
        try:
            start_time = time.time()
            
            # Check if Claude LLM is initialized, auto-initialize if needed
            if not self.claude_processor or not self.enhanced_claude:
                logger.info("🔄 Auto-initializing Claude LLM...")
                if not self.initialize_claude():
                    result['error'] = "Failed to initialize Claude LLM automatically."
                    return result
            
            # Extract text from PDF
            with st.spinner(f"📄 Extracting text from {uploaded_file.name}..."):
                extracted_text, filename = self.pdf_processor.extract_text_from_uploaded_file(uploaded_file)
            
            if not extracted_text.strip():
                result['error'] = "Failed to extract text from PDF"
                return result
            
            # Save extracted text to output directory for inspection
            try:
                from pathlib import Path
                output_dir = self.excel_handler.output_directory
                base_name = Path(filename).stem
                text_output_path = os.path.join(output_dir, f"{base_name}_extracted.txt")
                with open(text_output_path, "w", encoding="utf-8") as f:
                    f.write(extracted_text)
                logger.info(f"✅ Saved extracted text to {text_output_path}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to save extracted text for {filename}: {e}")
            
            # Process with Claude LLM
            with st.spinner(f"🤖 Processing with Claude LLM..."):
                extracted_data = self.claude_processor.extract_billing_data(extracted_text, filename)
            
            if not extracted_data:
                result['error'] = "No billing data extracted by Claude LLM"
                return result
            
            # Validate data
            validated_data = self.claude_processor.validate_extracted_data(extracted_data)
            
            # Derive non-instance lines: all lines that do NOT correspond to an instance row
            try:
                lines = extracted_text.split("\n")
                instance_flags = [False] * len(lines)
                # Mark lines that contain an AWS instance type string
                for item in validated_data:
                    aws_type = item.get("AWS")
                    if not aws_type:
                        continue
                    for idx, line in enumerate(lines):
                        if aws_type in line:
                            instance_flags[idx] = True
                non_instance_lines = [
                    line for idx, line in enumerate(lines)
                    if line.strip() and not instance_flags[idx]
                ]
                result['non_instance_lines'] = non_instance_lines
                logger.info(f"✅ Identified {len(non_instance_lines)} non-instance lines for {filename}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to compute non-instance lines for {filename}: {e}")
            
            result['data'] = validated_data
            result['success'] = True
            result['processing_time'] = time.time() - start_time
            
            logger.info(f"✅ Successfully processed {filename}: {len(validated_data)} records")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"❌ Error processing {uploaded_file.name}: {e}")
        
        return result
    
    def process_comprehensive_aws_analysis(self, uploaded_file) -> Dict[str, Any]:
        """
        Process PDF with comprehensive AWS service analysis
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Dictionary with comprehensive AWS analysis results
        """
        result = {
            'filename': uploaded_file.name,
            'success': False,
            'analysis_data': {},
            'error': None,
            'processing_time': 0
        }
        
        try:
            start_time = time.time()
            
            # Check if Enhanced Claude is initialized
            if not self.enhanced_claude:
                logger.info("🔄 Auto-initializing Enhanced Claude...")
                if not self.initialize_claude():
                    result['error'] = "Failed to initialize Enhanced Claude automatically."
                    return result
            
            # Extract text from PDF
            with st.spinner(f"📄 Extracting text from {uploaded_file.name}..."):
                extracted_text, filename = self.pdf_processor.extract_text_from_uploaded_file(uploaded_file)
            
            if not extracted_text.strip():
                result['error'] = "Failed to extract text from PDF"
                return result
            
            # Save extracted text
            try:
                output_dir = self.advanced_excel_handler.output_directory
                base_name = Path(filename).stem
                text_output_path = os.path.join(output_dir, f"{base_name}_extracted.txt")
                with open(text_output_path, "w", encoding="utf-8") as f:
                    f.write(extracted_text)
                logger.info(f"✅ Saved extracted text to {text_output_path}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to save extracted text for {filename}: {e}")
            
            # Comprehensive AWS analysis with Enhanced Claude
            with st.spinner(f"🔍 Performing comprehensive AWS service analysis..."):
                analysis_data = self.enhanced_claude.extract_comprehensive_aws_data(extracted_text, filename)
            
            if not analysis_data:
                result['error'] = "No AWS service data extracted by Enhanced Claude"
                return result
            
            # Validate and enhance analysis
            enhanced_analysis = self.enhanced_claude.validate_and_enhance_analysis(analysis_data)
            
            # Perform cost reconciliation if there's a significant difference
            cost_validation = enhanced_analysis.get('cost_validation', {})
            difference = abs(cost_validation.get('difference', 0.0))
            
            if difference > 1.0:  # If difference > $1, try to reconcile
                with st.spinner(f"🔍 Reconciling ${difference:.2f} cost difference..."):
                    enhanced_analysis = self.enhanced_claude.reconcile_missing_costs(
                        extracted_text, filename, enhanced_analysis
                    )
                
                # Log final difference after reconciliation
                final_difference = abs(enhanced_analysis.get('cost_validation', {}).get('difference', 0.0))
                logger.info(f"✅ Final cost difference after reconciliation: ${final_difference:.2f}")
            
            # Create comprehensive Excel report
            with st.spinner(f"📊 Creating comprehensive AWS analysis report..."):
                excel_path = self.advanced_excel_handler.create_comprehensive_aws_report(
                    enhanced_analysis, filename
                )
            
            if not excel_path:
                result['error'] = "Failed to create comprehensive AWS analysis report"
                return result
            
            # Create AWS-to-GCP mapping
            with st.spinner(f"🔄 Creating AWS-to-GCP comparison report..."):
                gcp_comparison_path = self.aws_gcp_mapper.process_aws_analysis_file(excel_path)
            
            if not gcp_comparison_path:
                logger.warning("⚠️ Failed to create AWS-to-GCP comparison report")
                result['gcp_comparison_path'] = None
            else:
                result['gcp_comparison_path'] = gcp_comparison_path
                logger.info(f"✅ AWS-to-GCP comparison completed: {gcp_comparison_path}")
            
            result['analysis_data'] = enhanced_analysis
            result['excel_path'] = excel_path
            result['success'] = True
            result['processing_time'] = time.time() - start_time
            
            logger.info(f"✅ Comprehensive AWS analysis completed for {filename}: {len(enhanced_analysis.get('service_line_items', []))} services analyzed")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"❌ Error in comprehensive AWS analysis for {uploaded_file.name}: {e}")
        
        return result
    
    def display_results_table(self, data: List[Dict[str, Any]], filename: str):
        """
        Display extracted data in a table
        
        Args:
            data: Extracted billing data
            filename: Source filename
        """
        if not data:
            st.warning(f"⚠️ No data extracted from {filename}")
            return
        
        # Create DataFrame for display
        df = pd.DataFrame(data)
        
        # Ensure all columns exist
        columns = ["AWS", "OS", "Region", "Hours", "Cores", "RAM", "Cost"]
        for col in columns:
            if col not in df.columns:
                df[col] = None
        
        # Reorder columns
        df = df[columns]
        
        st.subheader(f"📊 Extracted Data from {filename}")
        st.dataframe(df, use_container_width=True)
        
        # Show summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", len(df))
        
        with col2:
            total_hours = df['Hours'].sum() if 'Hours' in df.columns and df['Hours'].notna().any() else 0
            st.metric("Total Hours", f"{total_hours:,.2f}")
        
        with col3:
            # Calculate total cost (remove $ and convert to float)
            total_cost = 0
            if 'Cost' in df.columns:
                for cost in df['Cost'].dropna():
                    try:
                        if isinstance(cost, str) and cost.startswith('$'):
                            total_cost += float(cost.replace('$', '').replace(',', ''))
                        elif isinstance(cost, (int, float)):
                            total_cost += float(cost)
                    except (ValueError, TypeError):
                        continue
            
            st.metric("Total Cost", f"${total_cost:,.2f}")
    
    def run_application(self):
        """Run the main Streamlit application"""
        
        # Header
        st.title("📊 AWS Billing Data Extractor")
        st.markdown("Extract structured data from AWS billing PDFs using Claude LLM")
        
        # Sidebar
        with st.sidebar:
            st.header("🔧 Configuration")
            
            # Claude LLM status
            if st.button("🔄 Initialize Claude LLM"):
                self.initialize_claude()
            
            if st.session_state.claude_initialized:
                st.success("✅ Claude LLM Ready")
            else:
                st.warning("⚠️ Claude LLM Not Initialized")
            
            st.markdown("---")
            
            # Output directory info
            st.subheader("📁 Output Directory")
            st.code(self.excel_handler.output_directory)
            
            # Show existing output files
            output_files = self.excel_handler.get_output_files()
            if output_files:
                st.subheader("📄 Recent Output Files")
                for file_path in output_files[:5]:  # Show last 5 files
                    filename = Path(file_path).name
                    st.text(f"• {filename}")
        
        # Main content
        if not st.session_state.claude_initialized:
            st.warning("⚠️ Please initialize Claude LLM first using the sidebar button.")
            st.stop()
        
        # File upload section
        st.header("📤 Upload PDF Files")
        
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload one or more AWS billing PDF files for processing"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
            
            # Processing options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                analysis_mode = st.radio(
                    "Analysis Mode",
                    ["Basic Instance Extraction", "🚀 Comprehensive AWS Analysis"],
                    help="Choose analysis depth"
                )
            
            with col2:
                if analysis_mode == "Basic Instance Extraction":
                    process_mode = st.radio(
                        "Processing Mode",
                        ["Single Excel per PDF", "Combined Excel file"],
                        help="Choose how to save the results"
                    )
                else:
                    st.info("📊 Comprehensive mode creates detailed multi-sheet reports per PDF")
                    process_mode = "Comprehensive Analysis"
            
            with col3:
                if analysis_mode == "Basic Instance Extraction":
                    if st.button("🚀 Process Files (Basic)", type="primary"):
                        self.process_files(uploaded_files, process_mode)
                else:
                    if st.button("🔍 Comprehensive AWS Analysis", type="primary"):
                        self.process_comprehensive_analysis(uploaded_files)
        
        # Display results if available
        if st.session_state.processing_results:
            st.header("📋 Processing Results")
            
            for filename, result in st.session_state.processing_results.items():
                with st.expander(f"📄 {filename} - {'✅ Success' if result['success'] else '❌ Failed'}"):
                    if result['success']:
                        st.success(f"✅ Processed in {result['processing_time']:.2f} seconds")
                        self.display_results_table(result['data'], filename)

                        # Display non-instance lines (lines where no instance was detected)
                        non_instance_lines = result.get('non_instance_lines') or []
                        if non_instance_lines:
                            st.subheader("📄 Non-instance lines (no instance detected)")
                            non_df = pd.DataFrame({"Text": non_instance_lines})
                            st.dataframe(non_df, use_container_width=True)
                    else:
                        st.error(f"❌ Error: {result['error']}")
        
        # Display comprehensive AWS analysis results
        if st.session_state.aws_analysis_results:
            st.header("🔍 Comprehensive AWS Analysis Results")
            
            for filename, result in st.session_state.aws_analysis_results.items():
                with st.expander(f"📊 {filename} - {'✅ Success' if result['success'] else '❌ Failed'}"):
                    if result['success']:
                        st.success(f"✅ Analysis completed in {result['processing_time']:.2f} seconds")
                        self.display_comprehensive_analysis(result['analysis_data'], filename)
                        
                        if 'excel_path' in result:
                            st.success(f"📊 AWS Analysis report saved: {Path(result['excel_path']).name}")
                        
                        if 'gcp_comparison_path' in result and result['gcp_comparison_path']:
                            st.success(f"🔄 AWS-to-GCP Comparison report saved: {Path(result['gcp_comparison_path']).name}")
                    else:
                        st.error(f"❌ Error: {result['error']}")
    
    def process_files(self, uploaded_files, process_mode: str):
        """
        Process uploaded files
        
        Args:
            uploaded_files: List of uploaded files
            process_mode: Processing mode ("Single Excel per PDF" or "Combined Excel file")
        """
        st.session_state.processing_results = {}
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Process each file
            for i, uploaded_file in enumerate(uploaded_files):
                progress = (i + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                status_text.text(f"Processing {uploaded_file.name}... ({i+1}/{len(uploaded_files)})")
                
                # Process the file
                result = self.process_single_pdf(uploaded_file)
                st.session_state.processing_results[uploaded_file.name] = result
                
                # Debug logging
                logger.info(f"🔍 Processing result for {uploaded_file.name}: success={result['success']}, data_count={len(result['data']) if result['data'] else 0}, error={result['error']}")
            
            # Save results to Excel
            status_text.text("💾 Saving results to Excel...")
            
            if process_mode == "Single Excel per PDF":
                # Save each PDF to separate Excel file
                saved_files = []
                logger.info(f"🔍 Processing {len(st.session_state.processing_results)} files for Excel export")
                
                for filename, result in st.session_state.processing_results.items():
                    logger.info(f"🔍 Checking {filename}: success={result['success']}, has_data={bool(result['data'])}")
                    if result['success'] and result['data']:
                        logger.info(f"📊 Saving Excel for {filename} with {len(result['data'])} records")
                        excel_path = self.excel_handler.save_to_excel_single(
                            result['data'],
                            filename,
                            non_instance_lines=result.get('non_instance_lines')
                        )
                        if excel_path:
                            saved_files.append(excel_path)
                            logger.info(f"✅ Excel saved: {excel_path}")
                        else:
                            logger.error(f"❌ Failed to save Excel for {filename}")
                    else:
                        logger.warning(f"⚠️ Skipping {filename}: success={result['success']}, error={result.get('error', 'Unknown')}")
                
                if saved_files:
                    st.success(f"✅ Saved {len(saved_files)} Excel files to output directory")
                    logger.info(f"✅ Successfully saved {len(saved_files)} Excel files")
                else:
                    st.warning("⚠️ No Excel files were created")
                    logger.warning("⚠️ No Excel files were created - check processing results above")
            
            else:  # Combined Excel file
                # Combine all results into one Excel file
                combined_results = {}
                for filename, result in st.session_state.processing_results.items():
                    if result['success'] and result['data']:
                        combined_results[filename] = result
                
                if combined_results:
                    excel_path = self.excel_handler.save_to_excel_multiple(combined_results)
                    if excel_path:
                        st.success(f"✅ Saved combined Excel file: {Path(excel_path).name}")
                    else:
                        st.error("❌ Failed to save combined Excel file")
                else:
                    st.warning("⚠️ No data to save")
            
            progress_bar.progress(1.0)
            status_text.text("✅ Processing complete!")
            st.session_state.processing_complete = True
            
        except Exception as e:
            st.error(f"❌ Processing error: {e}")
            logger.error(f"Processing error: {e}")
        
        finally:
            progress_bar.empty()
            status_text.empty()
    
    def process_comprehensive_analysis(self, uploaded_files):
        """
        Process uploaded files with comprehensive AWS analysis
        
        Args:
            uploaded_files: List of uploaded files
        """
        st.session_state.aws_analysis_results = {}
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Process each file
            for i, uploaded_file in enumerate(uploaded_files):
                progress = (i + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                status_text.text(f"Analyzing {uploaded_file.name}... ({i+1}/{len(uploaded_files)})")
                
                # Process the file with comprehensive analysis
                result = self.process_comprehensive_aws_analysis(uploaded_file)
                st.session_state.aws_analysis_results[uploaded_file.name] = result
                
                # Debug logging
                logger.info(f"🔍 Comprehensive analysis result for {uploaded_file.name}: success={result['success']}")
            
            progress_bar.progress(1.0)
            status_text.text("✅ Comprehensive analysis complete!")
            
        except Exception as e:
            st.error(f"❌ Comprehensive analysis error: {e}")
            logger.error(f"Comprehensive analysis error: {e}")
        
        finally:
            progress_bar.empty()
            status_text.empty()
    
    def display_comprehensive_analysis(self, analysis_data: Dict[str, Any], filename: str):
        """
        Display comprehensive AWS analysis results
        
        Args:
            analysis_data: Comprehensive analysis data
            filename: Source filename
        """
        if not analysis_data or 'service_line_items' not in analysis_data:
            st.warning(f"⚠️ No comprehensive analysis data for {filename}")
            return
        
        # Invoice summary
        invoice_summary = analysis_data.get('invoice_summary', {})
        cost_validation = analysis_data.get('cost_validation', {})
        service_items = analysis_data.get('service_line_items', [])
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Services", len(service_items))
        
        with col2:
            total_cost = cost_validation.get('calculated_total', 0.0)
            st.metric("Total Cost", f"${total_cost:,.2f}")
        
        with col3:
            # Count unique service categories
            categories = set(item.get('service_category', 'Unknown') for item in service_items)
            st.metric("Service Categories", len(categories))
        
        with col4:
            # Count unique regions
            regions = set(item.get('region', 'unknown') for item in service_items if item.get('region', 'unknown') != 'unknown')
            st.metric("Regions", len(regions))
        
        # Cost validation status
        validation_passed = cost_validation.get('validation_passed', False)
        if validation_passed:
            st.success("✅ Cost validation passed - all services accounted for")
        else:
            difference = cost_validation.get('difference', 0.0)
            st.warning(f"⚠️ Cost validation needs review - difference: ${difference:.2f}")
        
        # Service category breakdown
        st.subheader("📊 Service Category Breakdown")
        
        # Group by category
        category_totals = {}
        for item in service_items:
            category = item.get('service_category', 'Unknown')
            cost = item.get('cost_usd', 0.0)
            if category not in category_totals:
                category_totals[category] = {'cost': 0.0, 'count': 0}
            category_totals[category]['cost'] += cost
            category_totals[category]['count'] += 1
        
        # Create category summary DataFrame
        category_data = []
        for category, data in sorted(category_totals.items(), key=lambda x: x[1]['cost'], reverse=True):
            percentage = (data['cost'] / total_cost * 100) if total_cost > 0 else 0
            category_data.append({
                'Service Category': category,
                'Line Items': data['count'],
                'Total Cost (USD)': f"${data['cost']:,.2f}",
                'Percentage': f"{percentage:.1f}%"
            })
        
        category_df = pd.DataFrame(category_data)
        st.dataframe(category_df, use_container_width=True)
        
        # Regional breakdown
        st.subheader("🌍 Regional Cost Distribution")
        
        # Group by region
        regional_totals = {}
        for item in service_items:
            region = item.get('region', 'unknown')
            cost = item.get('cost_usd', 0.0)
            if region not in regional_totals:
                regional_totals[region] = 0.0
            regional_totals[region] += cost
        
        # Create regional summary
        regional_data = []
        for region, cost in sorted(regional_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            regional_data.append({
                'Region': region,
                'Total Cost (USD)': f"${cost:,.2f}",
                'Percentage': f"{percentage:.1f}%"
            })
        
        regional_df = pd.DataFrame(regional_data)
        st.dataframe(regional_df, use_container_width=True)
        
        # Top 10 most expensive services
        st.subheader("💰 Top 10 Most Expensive Services")
        
        # Sort services by cost
        sorted_services = sorted(service_items, key=lambda x: x.get('cost_usd', 0.0), reverse=True)[:10]
        
        top_services_data = []
        for item in sorted_services:
            top_services_data.append({
                'Service': item.get('service_name', 'Unknown'),
                'Type': item.get('service_type', 'Standard'),
                'Region': item.get('region', 'unknown'),
                'Usage': f"{item.get('usage_quantity', 0)} {item.get('usage_unit', 'units')}",
                'Cost (USD)': f"${item.get('cost_usd', 0.0):,.2f}"
            })
        
        top_services_df = pd.DataFrame(top_services_data)
        st.dataframe(top_services_df, use_container_width=True)

def main():
    """Main application entry point"""
    try:
        app = AWSBillingExtractor()
        app.run_application()
        
    except Exception as e:
        st.error(f"❌ Application error: {e}")
        logger.error(f"Application error: {e}")

if __name__ == "__main__":
    main()
