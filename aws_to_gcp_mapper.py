#!/usr/bin/env python3
"""
AWS to GCP Resource Mapping Module
Maps AWS services to equivalent GCP services for cost comparison analysis
"""

import pandas as pd
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSToGCPMapper:
    """Maps AWS services to equivalent GCP services"""
    
    def __init__(self):
        """Initialize the AWS to GCP mapper"""
        self.service_mappings = self._initialize_service_mappings()
        self.instance_mappings = self._initialize_instance_mappings()
        self.region_mappings = self._initialize_region_mappings()
        self.database_mappings = self._initialize_database_mappings()
        
    def _initialize_service_mappings(self) -> Dict[str, Dict[str, str]]:
        """Initialize AWS to GCP service mappings with accurate GCP service names"""
        return {
            # Compute Services
            "EC2": {
                "gcp_service_category": "Compute",
                "gcp_service_name": "Compute Engine",
                "gcp_service_type": "Virtual Machines"
            },
            
            # Database Services
            "RDS": {
                "gcp_service_category": "Databases",
                "gcp_service_name": "Cloud SQL",
                "gcp_service_type": "Relational Database Service"
            },
            
            # Storage Services
            "S3": {
                "gcp_service_category": "Storage",
                "gcp_service_name": "Cloud Storage",
                "gcp_service_type": "Object Storage"
            },
            
            "EBS": {
                "gcp_service_category": "Compute",
                "gcp_service_name": "Persistent Disk",
                "gcp_service_type": "Block Storage"
            },
            
            "EFS": {
                "gcp_service_category": "Storage",
                "gcp_service_name": "Filestore",
                "gcp_service_type": "Managed NFS"
            },
            
            # Monitoring Services
            "CloudWatch": {
                "gcp_service_category": "Operations",
                "gcp_service_name": "Cloud Operations Suite",
                "gcp_service_type": "Monitoring and Logging"
            },
            
            # Networking Services
            "DataTransfer": {
                "gcp_service_category": "Networking",
                "gcp_service_name": "Cloud CDN",
                "gcp_service_type": "Content Delivery Network"
            },
            
            "VPC": {
                "gcp_service_category": "Networking",
                "gcp_service_name": "Virtual Private Cloud",
                "gcp_service_type": "Private Network"
            },
            
            # Backup Services
            "Backup": {
                "gcp_service_category": "Storage",
                "gcp_service_name": "Cloud Storage",
                "gcp_service_type": "Backup and Archive"
            },
            
            # Marketplace Services
            "Marketplace": {
                "gcp_service_category": "AI and Machine Learning",
                "gcp_service_name": "Vertex AI",
                "gcp_service_type": "AI Platform"
            }
        }
    
    def _initialize_instance_mappings(self) -> Dict[str, str]:
        """Initialize AWS to GCP instance type mappings"""
        return {
            # General Purpose
            "t2.micro": "e2-micro",
            "t2.small": "e2-small", 
            "t2.medium": "e2-medium",
            "t3.micro": "e2-micro",
            "t3.small": "e2-small",
            "t3.medium": "e2-medium",
            "t3.large": "e2-standard-2",
            "t3.xlarge": "e2-standard-4",
            "t3a.micro": "e2-micro",
            "t3a.small": "e2-small",
            "t3a.medium": "e2-medium",
            "t3a.large": "e2-standard-2",
            "t3a.xlarge": "e2-standard-4",
            
            # Compute Optimized
            "c5.large": "c2-standard-4",
            "c5.xlarge": "c2-standard-8",
            "c5.2xlarge": "c2-standard-16",
            "c5.4xlarge": "c2-standard-30",
            
            # Memory Optimized
            "r5.large": "n2-highmem-2",
            "r5.xlarge": "n2-highmem-4",
            "r5.2xlarge": "n2-highmem-8",
            "r5.4xlarge": "n2-highmem-16",
            "r6g.large": "n2-highmem-2",
            "r6g.xlarge": "n2-highmem-4",
            "r6g.2xlarge": "n2-highmem-8",
            "r6g.4xlarge": "n2-highmem-16",
            
            # Storage Optimized
            "i3.large": "n2-standard-2",
            "i3.xlarge": "n2-standard-4",
            "i3.2xlarge": "n2-standard-8",
            
            # General Purpose (M series)
            "m5.large": "n2-standard-2",
            "m5.xlarge": "n2-standard-4",
            "m5.2xlarge": "n2-standard-8",
            "m5.4xlarge": "n2-standard-16"
        }
    
    def _initialize_region_mappings(self) -> Dict[str, str]:
        """Initialize AWS to GCP region mappings"""
        return {
            # US Regions
            "US East (N. Virginia)": "us-east1",
            "US East (Ohio)": "us-east4", 
            "US West (Oregon)": "us-west1",
            "US West (N. California)": "us-west2",
            
            # Asia Pacific Regions
            "Asia Pacific (Mumbai)": "asia-south1",
            "Asia Pacific (Singapore)": "asia-southeast1",
            "Asia Pacific (Sydney)": "australia-southeast1",
            "Asia Pacific (Tokyo)": "asia-northeast1",
            "Asia Pacific (Seoul)": "asia-northeast3",
            "Asia Pacific (Hong Kong)": "asia-east2",
            
            # Europe Regions
            "EU (Ireland)": "europe-west1",
            "EU (London)": "europe-west2",
            "EU (Frankfurt)": "europe-west3",
            "EU (Paris)": "europe-west9",
            "EU (Stockholm)": "europe-north1",
            
            # Canada
            "Canada (Central)": "northamerica-northeast1",
            
            # South America
            "South America (Sao Paulo)": "southamerica-east1",
            
            # Global/Any
            "Any": "global",
            "Global": "global"
        }
    
    def _initialize_database_mappings(self) -> Dict[str, str]:
        """Initialize AWS to GCP database mappings"""
        return {
            "MariaDB": "MariaDB",
            "MySQL": "MySQL", 
            "PostgreSQL": "PostgreSQL",
            "Oracle": "SQL Server",  # GCP doesn't have Oracle, map to SQL Server
            "SQL Server": "SQL Server",
            "Aurora": "MySQL"  # Aurora MySQL maps to MySQL
        }
    
    def map_aws_service_to_gcp(self, aws_service_category: str, aws_service_name: str = "", 
                              aws_instance: str = "", aws_region: str = "", 
                              aws_db: str = "") -> Dict[str, str]:
        """
        Map AWS service details to equivalent GCP services
        
        Args:
            aws_service_category: AWS service category (EC2, RDS, S3, etc.)
            aws_service_name: AWS service name
            aws_instance: AWS instance type
            aws_region: AWS region
            aws_db: AWS database type
            
        Returns:
            Dictionary with GCP service mappings
        """
        # Get base service mapping
        gcp_mapping = self.service_mappings.get(aws_service_category, {
            "gcp_service_category": None,
            "gcp_service_name": None,
            "gcp_service_type": None
        }).copy()
        
        # Map instance type (handle both string and float)
        gcp_instance = ""
        if aws_instance:
            if isinstance(aws_instance, str):
                gcp_instance = self.instance_mappings.get(aws_instance.lower(), aws_instance)
            else:
                # Handle float/numeric data - convert to string and keep as-is
                gcp_instance = str(aws_instance)
        
        # Map region (handle both string and float)
        gcp_region = ""
        if aws_region:
            if isinstance(aws_region, str):
                gcp_region = self.region_mappings.get(aws_region, "us-central1")
            else:
                # Handle float/numeric data - convert to string and keep as-is
                gcp_region = str(aws_region)
        
        # Map database (handle both string and float)
        gcp_db = ""
        if aws_db:
            if isinstance(aws_db, str):
                gcp_db = self.database_mappings.get(aws_db, aws_db)
            else:
                # Handle float/numeric data - convert to string and keep as-is
                gcp_db = str(aws_db)
        
        # Add mapped values
        gcp_mapping.update({
            "gcp_instance": gcp_instance,
            "gcp_region": gcp_region,
            "gcp_db": gcp_db,
            "gcp_usage_quantity": "",  # Empty for now
            "gcp_usage_unit": "",      # Empty for now
            "gcp_rate_description": "", # Empty for now
            "gcp_cost_usd": "",        # Empty for now
            "gcp_original_line_text": "" # Empty for now
        })
        
        return gcp_mapping
    
    def process_aws_analysis_file(self, aws_excel_path: str, output_path: str = None) -> str:
        """
        Process AWS analysis Excel file and create clean organized AWS-GCP mapping
        
        Args:
            aws_excel_path: Path to AWS analysis Excel file
            output_path: Optional output path for mapped file
            
        Returns:
            Path to the output file with GCP mappings
        """
        try:
            logger.info(f"🔄 Processing AWS analysis file: {aws_excel_path}")
            
            # Read the Raw Data sheet
            df = pd.read_excel(aws_excel_path, sheet_name='Raw Data')
            logger.info(f"📊 Loaded {len(df)} AWS service line items")
            
            # Create organized layout
            organized_data = self._create_organized_layout(df)
            
            # Generate output path
            if not output_path:
                input_path = Path(aws_excel_path)
                output_path = input_path.parent / f"{input_path.stem}_AWS_GCP_Comparison.xlsx"
            
            # Save to Excel with formatting
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Create the organized comparison sheet
                organized_df = pd.DataFrame(organized_data)
                organized_df.to_excel(writer, sheet_name='AWS_GCP_Comparison', index=False)
                
                # Copy other sheets from original file if they exist
                try:
                    original_file = pd.ExcelFile(aws_excel_path)
                    for sheet_name in original_file.sheet_names:
                        if sheet_name != 'Raw Data':
                            original_sheet = pd.read_excel(aws_excel_path, sheet_name=sheet_name)
                            original_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
                except Exception as e:
                    logger.warning(f"⚠️ Could not copy original sheets: {e}")
            
            logger.info(f"✅ AWS to GCP comparison completed: {output_path}")
            logger.info(f"📋 Organized {len(df)} service line items by category")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ Error processing AWS analysis file: {e}")
            raise
    
    def _create_organized_layout(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Create organized layout with AWS and GCP services grouped by category
        
        Args:
            df: DataFrame with AWS service data
            
        Returns:
            List of dictionaries representing organized rows
        """
        organized_rows = []
        
        # Group by AWS service category
        service_groups = df.groupby('Service Category')
        
        for aws_service_category, group_df in service_groups:
            # Add service category header
            organized_rows.append({
                'AWS Service Name': f"=== {aws_service_category.upper()} SERVICES ===",
                'AWS Service Type': '',
                'AWS Region': '',
                'AWS Usage Quantity': '',
                'AWS Usage Unit': '',
                'AWS Rate Description': '',
                'AWS Cost (USD)': '',
                'AWS OS': '',
                'AWS Instance': '',
                'AWS DB': '',
                'SPACER_1': '',
                'SPACER_2': '',
                'GCP Service Name': f"=== EQUIVALENT GCP SERVICES ===",
                'GCP Service Type': '',
                'GCP Region': '',
                'GCP Usage Quantity': '',
                'GCP Usage Unit': '',
                'GCP Rate Description': '',
                'GCP Cost (USD)': '',
                'GCP OS': '',
                'GCP Instance': '',
                'GCP DB': ''
            })
            
            # Add individual service mappings
            aws_total_cost = 0
            for idx, row in group_df.iterrows():
                # Get AWS service details (handle float data properly)
                aws_service_category = row.get('Service Category', '')
                aws_service_name = row.get('Service Name', '')
                aws_instance = row.get('Instance', '')
                aws_region = row.get('Region', '')
                aws_db = row.get('DB', '')
                aws_cost = row.get('Cost (USD)', 0.0)
                
                # Handle float cost data
                try:
                    aws_total_cost += float(aws_cost) if aws_cost else 0.0
                except (ValueError, TypeError):
                    aws_total_cost += 0.0
                
                # Map to GCP
                gcp_mapping = self.map_aws_service_to_gcp(
                    aws_service_category, aws_service_name, 
                    aws_instance, aws_region, aws_db
                )
                
                # Create organized row (handle float data properly)
                def safe_convert(value):
                    """Safely convert value to string, handling float/NaN"""
                    if value is None or (isinstance(value, float) and pd.isna(value)):
                        return ''
                    return str(value)
                
                organized_rows.append({
                    'AWS Service Name': safe_convert(row.get('Service Name', '')),
                    'AWS Service Type': safe_convert(row.get('Service Type', '')),
                    'AWS Region': safe_convert(row.get('Region', '')),
                    'AWS Usage Quantity': safe_convert(row.get('Usage Quantity', '')),
                    'AWS Usage Unit': safe_convert(row.get('Usage Unit', '')),
                    'AWS Rate Description': safe_convert(row.get('Rate Description', '')),
                    'AWS Cost (USD)': safe_convert(row.get('Cost (USD)', '')),
                    'AWS OS': safe_convert(row.get('OS', '')),
                    'AWS Instance': safe_convert(row.get('Instance', '')),
                    'AWS DB': safe_convert(row.get('DB', '')),
                    'SPACER_1': '',
                    'SPACER_2': '',
                    'GCP Service Name': gcp_mapping.get('gcp_service_name', '') or '',
                    'GCP Service Type': gcp_mapping.get('gcp_service_type', '') or '',
                    'GCP Region': gcp_mapping.get('gcp_region', '') or '',
                    'GCP Usage Quantity': '',  # Empty for now
                    'GCP Usage Unit': '',      # Empty for now
                    'GCP Rate Description': '', # Empty for now
                    'GCP Cost (USD)': '',      # Empty for now
                    'GCP OS': gcp_mapping.get('gcp_db', '') or '',
                    'GCP Instance': gcp_mapping.get('gcp_instance', '') or '',
                    'GCP DB': gcp_mapping.get('gcp_db', '') or ''
                })
            
            # Add subtotal row
            organized_rows.append({
                'AWS Service Name': f"SUBTOTAL - {aws_service_category.upper()}",
                'AWS Service Type': '',
                'AWS Region': 'All Regions',
                'AWS Usage Quantity': '',
                'AWS Usage Unit': 'Mixed',
                'AWS Rate Description': '',
                'AWS Cost (USD)': f"{aws_total_cost:.2f}",
                'AWS OS': '',
                'AWS Instance': '',
                'AWS DB': '',
                'SPACER_1': '',
                'SPACER_2': '',
                'GCP Service Name': f"SUBTOTAL - {gcp_mapping.get('gcp_service_name', 'GCP Service')}",
                'GCP Service Type': '',
                'GCP Region': '',
                'GCP Usage Quantity': '',
                'GCP Usage Unit': '',
                'GCP Rate Description': '',
                'GCP Cost (USD)': '',  # Empty for now
                'GCP OS': '',
                'GCP Instance': '',
                'GCP DB': ''
            })
            
            # Add empty row for spacing
            organized_rows.append({
                'AWS Service Name': '',
                'AWS Service Type': '',
                'AWS Region': '',
                'AWS Usage Quantity': '',
                'AWS Usage Unit': '',
                'AWS Rate Description': '',
                'AWS Cost (USD)': '',
                'AWS OS': '',
                'AWS Instance': '',
                'AWS DB': '',
                'SPACER_1': '',
                'SPACER_2': '',
                'GCP Service Name': '',
                'GCP Service Type': '',
                'GCP Region': '',
                'GCP Usage Quantity': '',
                'GCP Usage Unit': '',
                'GCP Rate Description': '',
                'GCP Cost (USD)': '',
                'GCP OS': '',
                'GCP Instance': '',
                'GCP DB': ''
            })
        
        # Add grand total
        total_aws_cost = df['Cost (USD)'].sum()
        organized_rows.append({
            'AWS Service Name': 'GRAND TOTAL - AWS',
            'AWS Service Type': '',
            'AWS Region': 'All Regions',
            'AWS Usage Quantity': '',
            'AWS Usage Unit': 'Mixed',
            'AWS Rate Description': '',
            'AWS Cost (USD)': f"{total_aws_cost:.2f}",
            'AWS OS': '',
            'AWS Instance': '',
            'AWS DB': '',
            'SPACER_1': '',
            'SPACER_2': '',
            'GCP Service Name': 'GRAND TOTAL - GCP',
            'GCP Service Type': '',
            'GCP Region': '',
            'GCP Usage Quantity': '',
            'GCP Usage Unit': '',
            'GCP Rate Description': '',
            'GCP Cost (USD)': '',  # Empty for now
            'GCP OS': '',
            'GCP Instance': '',
            'GCP DB': ''
        })
        
        return organized_rows
    
    def generate_mapping_report(self, mapped_excel_path: str) -> Dict[str, Any]:
        """
        Generate a summary report of AWS to GCP mappings
        
        Args:
            mapped_excel_path: Path to the mapped Excel file
            
        Returns:
            Dictionary with mapping statistics
        """
        try:
            df = pd.read_excel(mapped_excel_path, sheet_name='AWS_GCP_Comparison')
            
            # Filter out header rows and empty rows for accurate counting
            service_rows = df[
                (df['AWS Service Name'].notna()) & 
                (~df['AWS Service Name'].str.contains('===', na=False)) &
                (~df['AWS Service Name'].str.contains('SUBTOTAL', na=False)) &
                (~df['AWS Service Name'].str.contains('GRAND TOTAL', na=False)) &
                (df['AWS Service Name'] != '')
            ]
            
            report = {
                'total_services': len(service_rows),
                'aws_service_breakdown': service_rows['AWS Service Name'].value_counts().head(10).to_dict(),
                'gcp_service_breakdown': service_rows[service_rows['GCP Service Name'].notna()]['GCP Service Name'].value_counts().to_dict(),
                'mapped_services': len(service_rows[service_rows['GCP Service Name'].notna()]),
                'unmapped_services': len(service_rows[service_rows['GCP Service Name'].isna()])
            }
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating mapping report: {e}")
            return {}

def main():
    """Test the AWS to GCP mapper"""
    
    # Initialize mapper
    mapper = AWSToGCPMapper()
    
    # Find AWS analysis files
    output_dir = Path("/Users/admin/Downloads/BOT/output")
    aws_files = list(output_dir.glob("*AWS_Analysis.xlsx"))
    
    if not aws_files:
        logger.error("❌ No AWS analysis files found in output directory")
        return
    
    # Process the first AWS file found
    aws_file = aws_files[0]
    logger.info(f"🔍 Processing: {aws_file}")
    
    try:
        # Create AWS to GCP mapping
        mapped_file = mapper.process_aws_analysis_file(str(aws_file))
        
        # Generate mapping report
        report = mapper.generate_mapping_report(mapped_file)
        
        print("\n" + "="*60)
        print("🎯 AWS TO GCP MAPPING COMPLETED")
        print("="*60)
        print(f"📁 Output File: {mapped_file}")
        print(f"📊 Total Services: {report.get('total_services', 0)}")
        print(f"✅ Mapped Services: {report.get('mapped_services', 0)}")
        print(f"⚠️  Unmapped Services: {report.get('unmapped_services', 0)}")
        print("\n🎯 GCP Service Mappings:")
        for service, count in report.get('gcp_service_breakdown', {}).items():
            print(f"   {service}: {count} items")
        print("\n🔄 Top AWS Services:")
        for service, count in list(report.get('aws_service_breakdown', {}).items())[:5]:
            print(f"   {service}: {count} items")
        
    except Exception as e:
        logger.error(f"❌ Mapping failed: {e}")

if __name__ == "__main__":
    main()
