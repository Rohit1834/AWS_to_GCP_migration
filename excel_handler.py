#!/usr/bin/env python3
"""
Excel Output Handler
Manages Excel file creation and data export for AWS billing data
"""

import os
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path
import xlsxwriter
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelHandler:
    """Excel file handler for AWS billing data export"""
    
    def __init__(self, base_directory: str = None):
        """
        Initialize Excel handler
        
        Args:
            base_directory: Base directory for output files
        """
        self.base_directory = base_directory or os.getcwd()
        self.output_directory = os.path.join(self.base_directory, "output")
        self.ensure_output_directory()
    
    def ensure_output_directory(self) -> bool:
        """
        Ensure output directory exists
        
        Returns:
            True if directory exists or was created successfully
        """
        try:
            os.makedirs(self.output_directory, exist_ok=True)
            logger.info(f"✅ Output directory ready: {self.output_directory}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create output directory: {e}")
            return False
    
    def sanitize_sheet_name(self, filename: str) -> str:
        """
        Sanitize filename for use as Excel sheet name
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized sheet name
        """
        # Remove file extension
        sheet_name = Path(filename).stem
        
        # Excel sheet name restrictions
        invalid_chars = ['\\', '/', '?', '*', '[', ']', ':']
        for char in invalid_chars:
            sheet_name = sheet_name.replace(char, '_')
        
        # Limit to 31 characters (Excel limit)
        if len(sheet_name) > 31:
            sheet_name = sheet_name[:28] + "..."
        
        return sheet_name
    
    def create_dataframe(self, extracted_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Create pandas DataFrame from extracted data
        
        Args:
            extracted_data: List of dictionaries with billing data
            
        Returns:
            Pandas DataFrame
        """
        if not extracted_data:
            logger.warning("⚠️ No data to create DataFrame")
            return pd.DataFrame()
        
        try:
            # Define column order
            columns = ["AWS", "OS", "Region", "Hours", "Cores", "RAM", "Cost"]
            
            # Create DataFrame
            df = pd.DataFrame(extracted_data)
            
            # Ensure all columns exist
            for col in columns:
                if col not in df.columns:
                    df[col] = None
            
            # Reorder columns
            df = df[columns]
            
            logger.info(f"✅ Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to create DataFrame: {e}")
            return pd.DataFrame()
    
    def save_to_excel_single(self, extracted_data: List[Dict[str, Any]], 
                           filename: str,
                           non_instance_lines: Optional[List[str]] = None) -> Optional[str]:
        """
        Save extracted data to a single Excel file
        
        Args:
            extracted_data: List of dictionaries with billing data
            filename: Original PDF filename
            
        Returns:
            Path to created Excel file or None if failed
        """
        try:
            if not extracted_data:
                logger.warning(f"⚠️ No data to save for {filename}")
                return None
            
            # Create DataFrame
            df = self.create_dataframe(extracted_data)
            if df.empty:
                logger.warning(f"⚠️ Empty DataFrame for {filename}")
                return None
            
            # Generate output filename
            base_name = Path(filename).stem
            excel_filename = f"{base_name}_extracted.xlsx"
            excel_path = os.path.join(self.output_directory, excel_filename)
            
            # Save to Excel
            with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
                sheet_name = self.sanitize_sheet_name(filename)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Get workbook and worksheet for formatting
                workbook = writer.book
                worksheet = writer.sheets[sheet_name]
                
                # Add formatting to main sheet
                self.format_worksheet(workbook, worksheet, df)

                # Optionally add a second sheet with non-instance lines
                if non_instance_lines:
                    other_sheet_name = sheet_name
                    if len(other_sheet_name) > 28:
                        other_sheet_name = other_sheet_name[:28]
                    other_sheet_name = f"{other_sheet_name}_oth"

                    # Ensure sheet name length <= 31
                    other_sheet_name = other_sheet_name[:31]

                    other_df = pd.DataFrame({"Text": non_instance_lines})
                    other_df.to_excel(writer, sheet_name=other_sheet_name, index=False)
                    logger.info(f"✅ Added non-instance lines sheet '{other_sheet_name}' with {len(other_df)} rows")
            
            logger.info(f"✅ Saved Excel file: {excel_path}")
            return excel_path
            
        except Exception as e:
            logger.error(f"❌ Failed to save Excel file for {filename}: {e}")
            return None
    
    def save_to_excel_multiple(self, results: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """
        Save multiple PDF results to a single Excel file with multiple sheets
        
        Args:
            results: Dictionary mapping filename to extracted data
            
        Returns:
            Path to created Excel file or None if failed
        """
        try:
            if not results:
                logger.warning("⚠️ No results to save")
                return None
            
            # Generate output filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_filename = f"AWS_Billing_Extract_{timestamp}.xlsx"
            excel_path = os.path.join(self.output_directory, excel_filename)
            
            with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                for filename, result in results.items():
                    extracted_data = result.get('data') if isinstance(result, dict) else result
                    non_instance_lines = None
                    if isinstance(result, dict):
                        non_instance_lines = result.get('non_instance_lines')

                    if not extracted_data:
                        logger.warning(f"⚠️ No data for {filename}, skipping sheet")
                        continue

                    # Create DataFrame for main data
                    df = self.create_dataframe(extracted_data)
                    if df.empty:
                        logger.warning(f"⚠️ Empty DataFrame for {filename}, skipping sheet")
                        continue
                    
                    # Create sheet
                    sheet_name = self.sanitize_sheet_name(filename)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    # Format worksheet
                    worksheet = writer.sheets[sheet_name]
                    self.format_worksheet(workbook, worksheet, df)

                    logger.info(f"✅ Added sheet '{sheet_name}' with {len(df)} rows")

                    # Optionally add second sheet with non-instance lines
                    if non_instance_lines:
                        other_sheet_name = sheet_name
                        if len(other_sheet_name) > 28:
                            other_sheet_name = other_sheet_name[:28]
                        other_sheet_name = f"{other_sheet_name}_oth"

                        other_sheet_name = other_sheet_name[:31]

                        other_df = pd.DataFrame({"Text": non_instance_lines})
                        other_df.to_excel(writer, sheet_name=other_sheet_name, index=False)
                        logger.info(f"✅ Added non-instance lines sheet '{other_sheet_name}' with {len(other_df)} rows")
            
            logger.info(f"✅ Saved multi-sheet Excel file: {excel_path}")
            return excel_path
            
        except Exception as e:
            logger.error(f"❌ Failed to save multi-sheet Excel file: {e}")
            return None
    
    def format_worksheet(self, workbook, worksheet, df: pd.DataFrame):
        """
        Apply formatting to Excel worksheet
        
        Args:
            workbook: xlsxwriter workbook object
            worksheet: xlsxwriter worksheet object
            df: DataFrame with data
        """
        try:
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            currency_format = workbook.add_format({
                'num_format': '$#,##0.00',
                'border': 1
            })
            
            number_format = workbook.add_format({
                'num_format': '#,##0.00',
                'border': 1
            })
            
            text_format = workbook.add_format({
                'border': 1,
                'text_wrap': True
            })
            
            # Apply header formatting
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Set column widths and apply data formatting
            column_widths = {
                'AWS': 15,
                'OS': 12,
                'Region': 12,
                'Hours': 12,
                'Cores': 8,
                'RAM': 8,
                'Cost': 12
            }
            
            for col_num, column in enumerate(df.columns):
                # Set column width
                width = column_widths.get(column, 10)
                worksheet.set_column(col_num, col_num, width)
                
                # Apply data formatting based on column type
                if column == 'Cost':
                    # Format cost column as currency
                    for row_num in range(1, len(df) + 1):
                        worksheet.write(row_num, col_num, df.iloc[row_num-1, col_num], currency_format)
                elif column in ['Hours', 'Cores', 'RAM']:
                    # Format numeric columns
                    for row_num in range(1, len(df) + 1):
                        worksheet.write(row_num, col_num, df.iloc[row_num-1, col_num], number_format)
                else:
                    # Format text columns
                    for row_num in range(1, len(df) + 1):
                        worksheet.write(row_num, col_num, df.iloc[row_num-1, col_num], text_format)
            
            # Freeze header row
            worksheet.freeze_panes(1, 0)
            
            logger.info("✅ Applied Excel formatting")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to apply Excel formatting: {e}")
    
    def get_output_files(self) -> List[str]:
        """
        Get list of output Excel files
        
        Returns:
            List of Excel file paths in output directory
        """
        try:
            if not os.path.exists(self.output_directory):
                return []
            
            excel_files = []
            for file in os.listdir(self.output_directory):
                if file.endswith(('.xlsx', '.xls')):
                    excel_files.append(os.path.join(self.output_directory, file))
            
            return sorted(excel_files, key=os.path.getmtime, reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Failed to get output files: {e}")
            return []
