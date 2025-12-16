#!/usr/bin/env python3
"""
Advanced Excel Handler for AWS Service Analysis
Creates comprehensive multi-sheet Excel reports with service breakdowns
"""

import os
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
from pathlib import Path
import xlsxwriter
from datetime import datetime
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedAWSExcelHandler:
    """Advanced Excel handler for comprehensive AWS service analysis"""
    
    def __init__(self, base_directory: str = None):
        """
        Initialize Advanced Excel handler
        
        Args:
            base_directory: Base directory for output files
        """
        self.base_directory = base_directory or os.getcwd()
        self.output_directory = os.path.join(self.base_directory, "output")
        self.ensure_output_directory()
    
    def ensure_output_directory(self) -> bool:
        """Ensure output directory exists"""
        try:
            os.makedirs(self.output_directory, exist_ok=True)
            logger.info(f"✅ Advanced output directory ready: {self.output_directory}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create output directory: {e}")
            return False
    
    def create_comprehensive_aws_report(self, analysis_data: Dict[str, Any], 
                                     filename: str) -> Optional[str]:
        """
        Create comprehensive AWS service analysis Excel report
        
        Args:
            analysis_data: Comprehensive analysis data from Claude
            filename: Original PDF filename
            
        Returns:
            Path to created Excel file or None if failed
        """
        try:
            if not analysis_data or 'service_line_items' not in analysis_data:
                logger.warning(f"⚠️ No analysis data for {filename}")
                return None
            
            # Generate output filename
            base_name = Path(filename).stem
            excel_filename = f"{base_name}_AWS_Analysis.xlsx"
            excel_path = os.path.join(self.output_directory, excel_filename)
            
            # Group services by category
            services_by_category = self._group_services_by_category(
                analysis_data['service_line_items']
            )
            
            # Create Excel workbook
            with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Create summary sheet
                self._create_summary_sheet(writer, workbook, analysis_data, services_by_category)
                
                # Create service category sheets
                for category, items in services_by_category.items():
                    if items:  # Only create sheet if there are items
                        self._create_service_category_sheet(
                            writer, workbook, category, items
                        )
                
                # Create regional breakdown sheet
                self._create_regional_breakdown_sheet(
                    writer, workbook, analysis_data['service_line_items']
                )
                
                # Create cost validation sheet
                self._create_cost_validation_sheet(writer, workbook, analysis_data)
                
                # Create detailed usage breakdown sheet
                self._create_detailed_usage_breakdown_sheet(
                    writer, workbook, analysis_data['service_line_items']
                )
                
                # Create raw data sheet
                self._create_raw_data_sheet(
                    writer, workbook, analysis_data['service_line_items']
                )
            
            logger.info(f"✅ Created comprehensive AWS analysis report: {excel_path}")
            return excel_path
            
        except Exception as e:
            logger.error(f"❌ Failed to create AWS analysis report for {filename}: {e}")
            return None
    
    def _group_services_by_category(self, service_items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group services by category"""
        services_by_category = defaultdict(list)
        
        for item in service_items:
            category = item.get('service_category', 'Other')
            services_by_category[category].append(item)
        
        return dict(services_by_category)
    
    def _create_summary_sheet(self, writer, workbook, analysis_data: Dict[str, Any], 
                            services_by_category: Dict[str, List[Dict[str, Any]]]):
        """Create executive summary sheet"""
        
        # Calculate summary statistics
        total_cost = analysis_data.get('cost_validation', {}).get('calculated_total', 0.0)
        total_items = len(analysis_data.get('service_line_items', []))
        
        category_totals = {}
        for category, items in services_by_category.items():
            category_totals[category] = sum(item.get('cost_usd', 0.0) for item in items)
        
        # Create summary data
        summary_data = []
        
        # Invoice overview
        summary_data.append(['INVOICE OVERVIEW', '', '', ''])
        summary_data.append(['Filename', analysis_data.get('invoice_summary', {}).get('filename', ''), '', ''])
        summary_data.append(['Total Cost (USD)', f"${total_cost:,.2f}", '', ''])
        summary_data.append(['Total Line Items', total_items, '', ''])
        summary_data.append(['Billing Period', analysis_data.get('invoice_summary', {}).get('billing_period', 'N/A'), '', ''])
        summary_data.append(['', '', '', ''])
        
        # Service category breakdown
        summary_data.append(['SERVICE CATEGORY BREAKDOWN', '', '', ''])
        summary_data.append(['Category', 'Items', 'Total Cost (USD)', 'Percentage'])
        
        for category, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            item_count = len(services_by_category[category])
            percentage = (total / total_cost * 100) if total_cost > 0 else 0
            summary_data.append([
                category, 
                item_count, 
                f"${total:,.2f}", 
                f"{percentage:.1f}%"
            ])
        
        summary_data.append(['', '', '', ''])
        summary_data.append(['TOTAL', total_items, f"${total_cost:,.2f}", '100.0%'])
        
        # Create DataFrame and write to Excel
        summary_df = pd.DataFrame(summary_data, columns=['Item', 'Value', 'Cost', 'Percentage'])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Format summary sheet
        worksheet = writer.sheets['Summary']
        self._format_summary_sheet(workbook, worksheet, len(summary_data))
    
    def _create_service_category_sheet(self, writer, workbook, category: str, 
                                     items: List[Dict[str, Any]]):
        """Create detailed sheet for each service category with granular breakdown"""
        
        # Group items by unique combination of service_type, usage_unit, and region
        grouped_items = defaultdict(list)
        
        for item in items:
            # Create unique key for grouping
            key = (
                item.get('service_type', 'Standard'),
                item.get('usage_unit', 'Units'),
                item.get('region', 'unknown')
            )
            grouped_items[key].append(item)
        
        # Prepare granular data for DataFrame
        sheet_data = []
        
        for (service_type, usage_unit, region), group_items in grouped_items.items():
            # Sum quantities and costs for this unique combination
            total_quantity = sum(item.get('usage_quantity', 0.0) for item in group_items)
            total_cost = sum(item.get('cost_usd', 0.0) for item in group_items)
            
            # Get representative service name and rate description
            service_name = group_items[0].get('service_name', category)
            rate_description = group_items[0].get('rate_description', 'Standard Rate')
            
            # Create row for this unique usage pattern
            sheet_data.append({
                'Service Name': service_name,
                'Service Type': service_type,
                'Region': region,
                'Usage Quantity': total_quantity,
                'Usage Unit': usage_unit,
                'Rate Description': rate_description,
                'Cost (USD)': total_cost,
                'Line Items': len(group_items)  # Number of original line items grouped
            })
        
        # Create DataFrame
        df = pd.DataFrame(sheet_data)
        
        # Sort by region first, then by cost (descending)
        df = df.sort_values(['Region', 'Cost (USD)'], ascending=[True, False])
        
        # Add region subtotals
        df_with_subtotals = []
        current_region = None
        region_total = 0.0
        region_quantity = 0.0
        
        for _, row in df.iterrows():
            if current_region != row['Region']:
                # Add subtotal for previous region
                if current_region is not None:
                    df_with_subtotals.append({
                        'Service Name': f'SUBTOTAL - {current_region.upper()}',
                        'Service Type': '',
                        'Region': current_region,
                        'Usage Quantity': region_quantity,
                        'Usage Unit': 'Mixed',
                        'Rate Description': '',
                        'Cost (USD)': region_total,
                        'Line Items': ''
                    })
                    df_with_subtotals.append({
                        'Service Name': '',
                        'Service Type': '',
                        'Region': '',
                        'Usage Quantity': '',
                        'Usage Unit': '',
                        'Rate Description': '',
                        'Cost (USD)': '',
                        'Line Items': ''
                    })  # Empty row for spacing
                
                current_region = row['Region']
                region_total = 0.0
                region_quantity = 0.0
            
            df_with_subtotals.append(row.to_dict())
            region_total += row['Cost (USD)']
            region_quantity += row['Usage Quantity']
        
        # Add final region subtotal
        if current_region is not None:
            df_with_subtotals.append({
                'Service Name': f'SUBTOTAL - {current_region.upper()}',
                'Service Type': '',
                'Region': current_region,
                'Usage Quantity': region_quantity,
                'Usage Unit': 'Mixed',
                'Rate Description': '',
                'Cost (USD)': region_total,
                'Line Items': ''
            })
        
        # Add grand total
        df_with_subtotals.append({
            'Service Name': '',
            'Service Type': '',
            'Region': '',
            'Usage Quantity': '',
            'Usage Unit': '',
            'Rate Description': '',
            'Cost (USD)': '',
            'Line Items': ''
        })  # Empty row
        
        df_with_subtotals.append({
            'Service Name': f'GRAND TOTAL - {category.upper()}',
            'Service Type': '',
            'Region': 'All Regions',
            'Usage Quantity': df['Usage Quantity'].sum(),
            'Usage Unit': 'Mixed',
            'Rate Description': '',
            'Cost (USD)': df['Cost (USD)'].sum(),
            'Line Items': df['Line Items'].sum()
        })
        
        # Create final DataFrame
        final_df = pd.DataFrame(df_with_subtotals)
        
        # Write to Excel
        sheet_name = self._sanitize_sheet_name(category)
        final_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Format sheet
        worksheet = writer.sheets[sheet_name]
        self._format_service_sheet_granular(workbook, worksheet, final_df, category)
    
    def _create_regional_breakdown_sheet(self, writer, workbook, service_items: List[Dict[str, Any]]):
        """Create regional cost breakdown sheet"""
        
        # Group by region
        regional_data = defaultdict(lambda: defaultdict(float))
        
        for item in service_items:
            region = item.get('region', 'unknown')
            category = item.get('service_category', 'Other')
            cost = item.get('cost_usd', 0.0)
            
            regional_data[region][category] += cost
        
        # Create pivot-style data
        all_categories = set()
        for region_data in regional_data.values():
            all_categories.update(region_data.keys())
        
        all_categories = sorted(all_categories)
        
        # Prepare data
        pivot_data = []
        for region in sorted(regional_data.keys()):
            row = {'Region': region}
            region_total = 0.0
            
            for category in all_categories:
                cost = regional_data[region].get(category, 0.0)
                row[category] = cost
                region_total += cost
            
            row['Total'] = region_total
            pivot_data.append(row)
        
        # Add totals row
        totals_row = {'Region': 'TOTAL'}
        grand_total = 0.0
        
        for category in all_categories:
            category_total = sum(row.get(category, 0.0) for row in pivot_data)
            totals_row[category] = category_total
            grand_total += category_total
        
        totals_row['Total'] = grand_total
        pivot_data.append(totals_row)
        
        # Create DataFrame
        columns = ['Region'] + all_categories + ['Total']
        df = pd.DataFrame(pivot_data, columns=columns)
        
        # Write to Excel
        df.to_excel(writer, sheet_name='Regional Breakdown', index=False)
        
        # Format sheet
        worksheet = writer.sheets['Regional Breakdown']
        self._format_regional_sheet(workbook, worksheet, df)
    
    def _create_cost_validation_sheet(self, writer, workbook, analysis_data: Dict[str, Any]):
        """Create cost validation and reconciliation sheet"""
        
        cost_validation = analysis_data.get('cost_validation', {})
        invoice_summary = analysis_data.get('invoice_summary', {})
        
        validation_data = [
            ['COST VALIDATION REPORT', ''],
            ['', ''],
            ['Calculated Total (from line items)', f"${cost_validation.get('calculated_total', 0.0):,.2f}"],
            ['Invoice Total (if available)', f"${cost_validation.get('invoice_total', 0.0):,.2f}"],
            ['Difference', f"${cost_validation.get('difference', 0.0):,.2f}"],
            ['Validation Status', 'PASSED' if cost_validation.get('validation_passed', False) else 'REVIEW NEEDED'],
            ['', ''],
            ['INVOICE DETAILS', ''],
            ['Filename', invoice_summary.get('filename', 'N/A')],
            ['Total Line Items Processed', len(analysis_data.get('service_line_items', []))],
            ['Billing Period', invoice_summary.get('billing_period', 'N/A')],
            ['Currency', invoice_summary.get('currency', 'USD')],
            ['', ''],
            ['ANALYSIS NOTES', ''],
            ['• All billable line items have been extracted and categorized'],
            ['• Costs are grouped by AWS service category and region'],
            ['• Small discrepancies may be due to rounding or tax calculations'],
            ['• Review "Raw Data" sheet for complete line-by-line details']
        ]
        
        # Create DataFrame
        validation_df = pd.DataFrame(validation_data, columns=['Item', 'Value'])
        validation_df.to_excel(writer, sheet_name='Cost Validation', index=False)
        
        # Format sheet
        worksheet = writer.sheets['Cost Validation']
        self._format_validation_sheet(workbook, worksheet, len(validation_data))
    
    def _create_detailed_usage_breakdown_sheet(self, writer, workbook, service_items: List[Dict[str, Any]]):
        """Create detailed usage breakdown sheet - every usage line separately"""
        
        # Prepare detailed usage data - each row is a unique usage pattern
        usage_data = []
        
        for item in service_items:
            usage_data.append({
                'Service Category': item.get('service_category', 'Unknown'),
                'Service Name': item.get('service_name', 'Unknown'),
                'Service Type': item.get('service_type', 'Standard'),
                'Region': item.get('region', 'unknown'),
                'Usage Quantity': item.get('usage_quantity', 0.0),
                'Usage Unit': item.get('usage_unit', 'Units'),
                'Rate Description': item.get('rate_description', 'Standard Rate'),
                'Cost (USD)': item.get('cost_usd', 0.0)
            })
        
        # Create DataFrame
        df = pd.DataFrame(usage_data)
        
        # Sort by Service Category, then Region, then Cost
        df = df.sort_values(['Service Category', 'Region', 'Cost (USD)'], 
                           ascending=[True, True, False])
        
        # Add running totals and subtotals
        df_with_totals = []
        current_service = None
        current_region = None
        service_total = 0.0
        region_total = 0.0
        grand_total = 0.0
        
        for _, row in df.iterrows():
            service_category = row['Service Category']
            region = row['Region']
            cost = row['Cost (USD)']
            
            # Check for service category change
            if current_service != service_category:
                # Add service subtotal for previous service
                if current_service is not None:
                    # Add region subtotal if needed
                    if current_region is not None:
                        df_with_totals.append({
                            'Service Category': f'  → {current_region.upper()} SUBTOTAL',
                            'Service Name': '',
                            'Service Type': '',
                            'Region': current_region,
                            'Usage Quantity': '',
                            'Usage Unit': '',
                            'Rate Description': '',
                            'Cost (USD)': region_total
                        })
                    
                    df_with_totals.append({
                        'Service Category': f'🔹 {current_service.upper()} TOTAL',
                        'Service Name': '',
                        'Service Type': '',
                        'Region': 'All Regions',
                        'Usage Quantity': '',
                        'Usage Unit': '',
                        'Rate Description': '',
                        'Cost (USD)': service_total
                    })
                    
                    # Add spacing
                    df_with_totals.append({
                        'Service Category': '',
                        'Service Name': '',
                        'Service Type': '',
                        'Region': '',
                        'Usage Quantity': '',
                        'Usage Unit': '',
                        'Rate Description': '',
                        'Cost (USD)': ''
                    })
                
                current_service = service_category
                current_region = None
                service_total = 0.0
                region_total = 0.0
            
            # Check for region change within same service
            if current_region != region:
                # Add region subtotal for previous region
                if current_region is not None and current_service == service_category:
                    df_with_totals.append({
                        'Service Category': f'  → {current_region.upper()} SUBTOTAL',
                        'Service Name': '',
                        'Service Type': '',
                        'Region': current_region,
                        'Usage Quantity': '',
                        'Usage Unit': '',
                        'Rate Description': '',
                        'Cost (USD)': region_total
                    })
                
                current_region = region
                region_total = 0.0
            
            # Add the actual data row
            df_with_totals.append(row.to_dict())
            
            # Update totals
            service_total += cost
            region_total += cost
            grand_total += cost
        
        # Add final subtotals
        if current_region is not None:
            df_with_totals.append({
                'Service Category': f'  → {current_region.upper()} SUBTOTAL',
                'Service Name': '',
                'Service Type': '',
                'Region': current_region,
                'Usage Quantity': '',
                'Usage Unit': '',
                'Rate Description': '',
                'Cost (USD)': region_total
            })
        
        if current_service is not None:
            df_with_totals.append({
                'Service Category': f'🔹 {current_service.upper()} TOTAL',
                'Service Name': '',
                'Service Type': '',
                'Region': 'All Regions',
                'Usage Quantity': '',
                'Usage Unit': '',
                'Rate Description': '',
                'Cost (USD)': service_total
            })
        
        # Add grand total
        df_with_totals.append({
            'Service Category': '',
            'Service Name': '',
            'Service Type': '',
            'Region': '',
            'Usage Quantity': '',
            'Usage Unit': '',
            'Rate Description': '',
            'Cost (USD)': ''
        })
        
        df_with_totals.append({
            'Service Category': '🏆 GRAND TOTAL - ALL SERVICES',
            'Service Name': '',
            'Service Type': '',
            'Region': 'All Regions',
            'Usage Quantity': len(usage_data),
            'Usage Unit': 'Line Items',
            'Rate Description': '',
            'Cost (USD)': grand_total
        })
        
        # Create final DataFrame
        final_df = pd.DataFrame(df_with_totals)
        
        # Write to Excel
        final_df.to_excel(writer, sheet_name='Detailed Usage', index=False)
        
        # Format sheet
        worksheet = writer.sheets['Detailed Usage']
        self._format_detailed_usage_sheet(workbook, worksheet, final_df)
    
    def _extract_os_from_text(self, text: str) -> str:
        """Extract Operating System from line text"""
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Common OS patterns
        if 'linux/unix' in text_lower or 'linux' in text_lower:
            return 'Linux/UNIX'
        elif 'windows' in text_lower:
            return 'Windows'
        elif 'rhel' in text_lower:
            return 'RHEL'
        elif 'suse' in text_lower:
            return 'SUSE'
        elif 'ubuntu' in text_lower:
            return 'Ubuntu'
        
        return None
    
    def _extract_instance_from_text(self, text: str) -> str:
        """Extract Instance type from line text"""
        if not text:
            return None
        
        import re
        # Pattern for AWS instance types (e.g., t3a.small, m5.xlarge, r6g.4xlarge)
        instance_pattern = r'\b([a-z][0-9][a-z]?\.[a-z0-9]+)\b'
        match = re.search(instance_pattern, text.lower())
        
        if match:
            return match.group(1)
        
        return None
    
    def _extract_db_from_text(self, text: str) -> str:
        """Extract Database type from line text"""
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Common database patterns
        if 'mariadb' in text_lower:
            return 'MariaDB'
        elif 'mysql' in text_lower:
            return 'MySQL'
        elif 'postgresql' in text_lower or 'postgres' in text_lower:
            return 'PostgreSQL'
        elif 'oracle' in text_lower:
            return 'Oracle'
        elif 'sql server' in text_lower or 'sqlserver' in text_lower:
            return 'SQL Server'
        elif 'aurora' in text_lower:
            return 'Aurora'
        
        return None

    def _create_raw_data_sheet(self, writer, workbook, service_items: List[Dict[str, Any]]):
        """Create raw data sheet with all extracted information"""
        
        # Prepare comprehensive data
        raw_data = []
        for i, item in enumerate(service_items, 1):
            line_text = item.get('line_text', '')
            
            raw_data.append({
                'Line #': i,
                'Service Category': item.get('service_category', ''),
                'Service Name': item.get('service_name', ''),
                'Service Type': item.get('service_type', ''),
                'Region': item.get('region', ''),
                'Usage Quantity': item.get('usage_quantity', 0.0),
                'Usage Unit': item.get('usage_unit', ''),
                'Rate Description': item.get('rate_description', ''),
                'Cost (USD)': item.get('cost_usd', 0.0),
                'Original Line Text': line_text,
                'OS': self._extract_os_from_text(line_text),
                'Instance': self._extract_instance_from_text(line_text),
                'DB': self._extract_db_from_text(line_text)
            })
        
        # Create DataFrame
        df = pd.DataFrame(raw_data)
        
        # Write to Excel
        df.to_excel(writer, sheet_name='Raw Data', index=False)
        
        # Format sheet
        worksheet = writer.sheets['Raw Data']
        self._format_raw_data_sheet(workbook, worksheet, df)
    
    def _sanitize_sheet_name(self, name: str) -> str:
        """Sanitize name for Excel sheet"""
        # Remove invalid characters
        invalid_chars = ['\\', '/', '?', '*', '[', ']', ':']
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Limit length
        return name[:31]
    
    def _format_summary_sheet(self, workbook, worksheet, row_count: int):
        """Format summary sheet"""
        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#1f4e79',
            'font_color': 'white',
            'border': 1
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#d9e2f3',
            'border': 1
        })
        
        currency_format = workbook.add_format({
            'num_format': '$#,##0.00',
            'border': 1
        })
        
        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 12)
        
        # Apply formatting (basic example)
        worksheet.conditional_format(f'A1:D{row_count}', {
            'type': 'no_blanks',
            'format': workbook.add_format({'border': 1})
        })
    
    def _format_service_sheet(self, workbook, worksheet, df: pd.DataFrame, category: str):
        """Format service category sheet"""
        # Set column widths
        worksheet.set_column('A:A', 20)  # Service Name
        worksheet.set_column('B:B', 15)  # Service Type
        worksheet.set_column('C:C', 15)  # Region
        worksheet.set_column('D:D', 12)  # Usage Quantity
        worksheet.set_column('E:E', 12)  # Usage Unit
        worksheet.set_column('F:F', 30)  # Rate Description
        worksheet.set_column('G:G', 12)  # Cost
        
        # Format currency column
        currency_format = workbook.add_format({'num_format': '$#,##0.00'})
        worksheet.set_column('G:G', 12, currency_format)
    
    def _format_service_sheet_granular(self, workbook, worksheet, df: pd.DataFrame, category: str):
        """Format granular service category sheet with enhanced styling"""
        # Set column widths
        worksheet.set_column('A:A', 25)  # Service Name
        worksheet.set_column('B:B', 18)  # Service Type
        worksheet.set_column('C:C', 15)  # Region
        worksheet.set_column('D:D', 15)  # Usage Quantity
        worksheet.set_column('E:E', 12)  # Usage Unit
        worksheet.set_column('F:F', 35)  # Rate Description
        worksheet.set_column('G:G', 15)  # Cost
        worksheet.set_column('H:H', 12)  # Line Items
        
        # Define formats
        currency_format = workbook.add_format({
            'num_format': '$#,##0.00',
            'border': 1
        })
        
        subtotal_format = workbook.add_format({
            'bold': True,
            'bg_color': '#E6F3FF',
            'border': 1,
            'num_format': '$#,##0.00'
        })
        
        total_format = workbook.add_format({
            'bold': True,
            'bg_color': '#1f4e79',
            'font_color': 'white',
            'border': 1,
            'num_format': '$#,##0.00'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#d9e2f3',
            'border': 1,
            'text_wrap': True
        })
        
        # Format header row
        for col_num, value in enumerate(df.columns):
            worksheet.write(0, col_num, value, header_format)
        
        # Format data rows
        for row_num, row_data in enumerate(df.itertuples(index=False), start=1):
            service_name = str(row_data[0]) if row_data[0] is not None else ''
            
            # Determine format based on row type
            if 'SUBTOTAL' in service_name:
                row_format = subtotal_format
            elif 'GRAND TOTAL' in service_name:
                row_format = total_format
            else:
                row_format = workbook.add_format({'border': 1})
            
            # Write each cell with appropriate formatting
            for col_num, cell_value in enumerate(row_data):
                if col_num == 6:  # Cost column
                    if isinstance(cell_value, (int, float)) and cell_value != '':
                        worksheet.write(row_num, col_num, cell_value, 
                                      subtotal_format if 'SUBTOTAL' in service_name 
                                      else total_format if 'GRAND TOTAL' in service_name 
                                      else currency_format)
                    else:
                        worksheet.write(row_num, col_num, cell_value, row_format)
                else:
                    worksheet.write(row_num, col_num, cell_value, row_format)
    
    def _format_detailed_usage_sheet(self, workbook, worksheet, df: pd.DataFrame):
        """Format detailed usage breakdown sheet"""
        # Set column widths
        worksheet.set_column('A:A', 30)  # Service Category
        worksheet.set_column('B:B', 25)  # Service Name
        worksheet.set_column('C:C', 20)  # Service Type
        worksheet.set_column('D:D', 15)  # Region
        worksheet.set_column('E:E', 15)  # Usage Quantity
        worksheet.set_column('F:F', 12)  # Usage Unit
        worksheet.set_column('G:G', 40)  # Rate Description
        worksheet.set_column('H:H', 15)  # Cost
        
        # Define formats
        currency_format = workbook.add_format({
            'num_format': '$#,##0.00',
            'border': 1
        })
        
        region_subtotal_format = workbook.add_format({
            'bold': True,
            'bg_color': '#FFF2CC',
            'border': 1,
            'num_format': '$#,##0.00'
        })
        
        service_total_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D5E8D4',
            'border': 1,
            'num_format': '$#,##0.00'
        })
        
        grand_total_format = workbook.add_format({
            'bold': True,
            'bg_color': '#1f4e79',
            'font_color': 'white',
            'border': 1,
            'num_format': '$#,##0.00'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#d9e2f3',
            'border': 1,
            'text_wrap': True
        })
        
        # Format header row
        for col_num, value in enumerate(df.columns):
            worksheet.write(0, col_num, value, header_format)
        
        # Format data rows
        for row_num, row_data in enumerate(df.itertuples(index=False), start=1):
            service_category = str(row_data[0]) if row_data[0] is not None else ''
            
            # Determine format based on row type
            if '→' in service_category and 'SUBTOTAL' in service_category:
                row_format = region_subtotal_format
            elif '🔹' in service_category and 'TOTAL' in service_category:
                row_format = service_total_format
            elif '🏆' in service_category and 'GRAND TOTAL' in service_category:
                row_format = grand_total_format
            else:
                row_format = workbook.add_format({'border': 1})
            
            # Write each cell with appropriate formatting
            for col_num, cell_value in enumerate(row_data):
                if col_num == 7:  # Cost column
                    if isinstance(cell_value, (int, float)) and cell_value != '':
                        if '→' in service_category and 'SUBTOTAL' in service_category:
                            worksheet.write(row_num, col_num, cell_value, region_subtotal_format)
                        elif '🔹' in service_category and 'TOTAL' in service_category:
                            worksheet.write(row_num, col_num, cell_value, service_total_format)
                        elif '🏆' in service_category and 'GRAND TOTAL' in service_category:
                            worksheet.write(row_num, col_num, cell_value, grand_total_format)
                        else:
                            worksheet.write(row_num, col_num, cell_value, currency_format)
                    else:
                        worksheet.write(row_num, col_num, cell_value, row_format)
                else:
                    worksheet.write(row_num, col_num, cell_value, row_format)
    
    def _format_regional_sheet(self, workbook, worksheet, df: pd.DataFrame):
        """Format regional breakdown sheet"""
        # Set column widths
        worksheet.set_column('A:A', 20)  # Region
        
        # Format currency columns
        currency_format = workbook.add_format({'num_format': '$#,##0.00'})
        for col_num in range(1, len(df.columns)):
            worksheet.set_column(col_num, col_num, 12, currency_format)
    
    def _format_validation_sheet(self, workbook, worksheet, row_count: int):
        """Format cost validation sheet"""
        worksheet.set_column('A:A', 35)
        worksheet.set_column('B:B', 20)
    
    def _format_raw_data_sheet(self, workbook, worksheet, df: pd.DataFrame):
        """Format raw data sheet"""
        # Set column widths
        worksheet.set_column('A:A', 8)   # Line #
        worksheet.set_column('B:B', 15)  # Service Category
        worksheet.set_column('C:C', 20)  # Service Name
        worksheet.set_column('D:D', 15)  # Service Type
        worksheet.set_column('E:E', 15)  # Region
        worksheet.set_column('F:F', 12)  # Usage Quantity
        worksheet.set_column('G:G', 12)  # Usage Unit
        worksheet.set_column('H:H', 35)  # Rate Description
        worksheet.set_column('I:I', 12)  # Cost
        worksheet.set_column('J:J', 50)  # Original Line Text
        
        # Format currency column
        currency_format = workbook.add_format({'num_format': '$#,##0.00'})
        worksheet.set_column('I:I', 12, currency_format)
