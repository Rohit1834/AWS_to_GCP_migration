#!/usr/bin/env python3
"""
AWS Service Analyzer Module
Comprehensive analysis and categorization of AWS services from billing data
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServiceUsage:
    """Data class for AWS service usage"""
    service_category: str
    service_name: str
    service_type: str
    region: str
    usage_quantity: float
    usage_unit: str
    rate_description: str
    cost: Decimal
    raw_line: str
    line_number: int

class AWSServiceAnalyzer:
    """Comprehensive AWS service analyzer and categorizer"""
    
    def __init__(self):
        """Initialize the AWS service analyzer"""
        self.service_patterns = self._initialize_service_patterns()
        self.region_patterns = self._initialize_region_patterns()
        self.cost_patterns = self._initialize_cost_patterns()
        
    def _initialize_service_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize comprehensive AWS service patterns"""
        return {
            'EC2': {
                'keywords': [
                    'elastic compute cloud', 'ec2', 'instance', 'compute',
                    't2.', 't3.', 't3a.', 't4g.', 'm5.', 'm5a.', 'm5n.', 'm5zn.',
                    'c5.', 'c5a.', 'c5n.', 'c6g.', 'c6gn.', 'c6i.',
                    'r5.', 'r5a.', 'r5b.', 'r5n.', 'r6g.', 'r6i.',
                    'x1.', 'x1e.', 'z1d.', 'i3.', 'i3en.', 'i4i.',
                    'f1.', 'g4dn.', 'g4ad.', 'p3.', 'p4d.',
                    'a1.', 'u-', 'mac1.', 'dl1.'
                ],
                'units': ['hours', 'hrs', 'hour', 'instance-hours', 'vcpu-hours']
            },
            'RDS': {
                'keywords': [
                    'relational database service', 'rds', 'database',
                    'db.', 'mysql', 'mariadb', 'postgresql', 'oracle', 'sql server',
                    'aurora', 'backup storage', 'snapshot', 'multi-az'
                ],
                'units': ['hours', 'hrs', 'gb-mo', 'gb-month', 'iops-mo', 'requests']
            },
            'S3': {
                'keywords': [
                    'simple storage service', 's3', 'storage',
                    'requests-tier1', 'requests-tier2', 'timedstorage',
                    'glacier', 'deep archive', 'intelligent tiering',
                    'put', 'get', 'copy', 'post', 'list', 'delete'
                ],
                'units': ['gb-mo', 'gb-month', 'requests', 'gb', 'tb']
            },
            'Lambda': {
                'keywords': [
                    'lambda', 'aws lambda', 'serverless compute',
                    'request', 'duration', 'gb-second'
                ],
                'units': ['requests', 'gb-seconds', 'duration-ms']
            },
            'CloudFront': {
                'keywords': [
                    'cloudfront', 'cdn', 'content delivery',
                    'data transfer', 'requests', 'origin requests'
                ],
                'units': ['gb', 'requests', 'tb']
            },
            'EBS': {
                'keywords': [
                    'elastic block store', 'ebs', 'volume',
                    'gp2', 'gp3', 'io1', 'io2', 'st1', 'sc1',
                    'snapshot', 'provisioned iops'
                ],
                'units': ['gb-mo', 'gb-month', 'iops-mo', 'gb']
            },
            'VPC': {
                'keywords': [
                    'virtual private cloud', 'vpc', 'nat gateway',
                    'vpc endpoint', 'transit gateway', 'vpn',
                    'data transfer', 'elastic ip'
                ],
                'units': ['hours', 'gb', 'connections']
            },
            'ElastiCache': {
                'keywords': [
                    'elasticache', 'redis', 'memcached', 'cache',
                    'cache.', 'node hours'
                ],
                'units': ['hours', 'node-hours', 'gb-mo']
            },
            'SQS': {
                'keywords': [
                    'simple queue service', 'sqs', 'queue',
                    'requests-tier1', 'requests-tier2'
                ],
                'units': ['requests', 'messages']
            },
            'SNS': {
                'keywords': [
                    'simple notification service', 'sns',
                    'notifications', 'messages', 'email', 'sms'
                ],
                'units': ['requests', 'messages', 'notifications']
            },
            'CloudWatch': {
                'keywords': [
                    'cloudwatch', 'monitoring', 'logs', 'metrics',
                    'alarms', 'dashboards', 'insights'
                ],
                'units': ['requests', 'metrics', 'gb', 'alarms']
            },
            'Route53': {
                'keywords': [
                    'route 53', 'route53', 'dns', 'hosted zone',
                    'queries', 'health checks'
                ],
                'units': ['queries', 'hosted zones', 'health checks']
            },
            'API_Gateway': {
                'keywords': [
                    'api gateway', 'apigateway', 'rest api',
                    'websocket', 'http api'
                ],
                'units': ['requests', 'messages', 'minutes']
            },
            'Kinesis': {
                'keywords': [
                    'kinesis', 'data streams', 'firehose',
                    'analytics', 'shard hours', 'records'
                ],
                'units': ['shard-hours', 'records', 'gb', 'hours']
            },
            'DynamoDB': {
                'keywords': [
                    'dynamodb', 'nosql', 'table', 'read capacity',
                    'write capacity', 'on-demand', 'provisioned'
                ],
                'units': ['rcu-hours', 'wcu-hours', 'gb-mo', 'requests']
            },
            'Redshift': {
                'keywords': [
                    'redshift', 'data warehouse', 'cluster',
                    'dc2.', 'ds2.', 'ra3.'
                ],
                'units': ['hours', 'node-hours', 'gb-mo']
            },
            'EMR': {
                'keywords': [
                    'elastic mapreduce', 'emr', 'hadoop',
                    'spark', 'cluster hours'
                ],
                'units': ['hours', 'cluster-hours', 'instance-hours']
            },
            'Glue': {
                'keywords': [
                    'glue', 'etl', 'crawler', 'job runs',
                    'dpu-hours', 'development endpoint'
                ],
                'units': ['dpu-hours', 'hours', 'requests']
            },
            'Athena': {
                'keywords': [
                    'athena', 'query', 'data scanned',
                    'serverless query'
                ],
                'units': ['gb', 'tb', 'queries']
            },
            'ECS': {
                'keywords': [
                    'elastic container service', 'ecs', 'fargate',
                    'container', 'task', 'vcpu-hours', 'gb-hours'
                ],
                'units': ['vcpu-hours', 'gb-hours', 'hours']
            },
            'EKS': {
                'keywords': [
                    'elastic kubernetes service', 'eks',
                    'kubernetes', 'cluster hours'
                ],
                'units': ['hours', 'cluster-hours']
            },
            'EFS': {
                'keywords': [
                    'elastic file system', 'efs', 'file system',
                    'throughput', 'infrequent access', 'one zone'
                ],
                'units': ['gb-mo', 'gb', 'requests']
            },
            'Backup': {
                'keywords': [
                    'aws backup', 'backup storage', 'backup',
                    'warm backup', 'cold backup'
                ],
                'units': ['gb-month', 'gb-mo', 'snapshots']
            },
            'DataTransfer': {
                'keywords': [
                    'data transfer', 'aws data transfer', 'transfer',
                    'cloudfront', 'inter-region', 'internet'
                ],
                'units': ['gb', 'tb', 'bytes']
            },
            'Marketplace': {
                'keywords': [
                    'marketplace', 'aws marketplace', 'claude',
                    'bedrock', 'third-party', 'software usage'
                ],
                'units': ['tokens', 'requests', 'hours', 'units']
            },
            'Other': {
                'keywords': [
                    'support', 'tax', 'credits', 'refunds',
                    'marketplace', 'training', 'certification'
                ],
                'units': ['usd', 'credits', 'hours']
            }
        }
    
    def _initialize_region_patterns(self) -> Dict[str, List[str]]:
        """Initialize AWS region patterns"""
        return {
            'us-east-1': ['us east (n. virginia)', 'us-east-1', 'use1', 'virginia'],
            'us-east-2': ['us east (ohio)', 'us-east-2', 'use2', 'ohio'],
            'us-west-1': ['us west (n. california)', 'us-west-1', 'usw1', 'california'],
            'us-west-2': ['us west (oregon)', 'us-west-2', 'usw2', 'oregon'],
            'eu-west-1': ['eu (ireland)', 'eu-west-1', 'euw1', 'ireland'],
            'eu-west-2': ['eu (london)', 'eu-west-2', 'euw2', 'london'],
            'eu-west-3': ['eu (paris)', 'eu-west-3', 'euw3', 'paris'],
            'eu-central-1': ['eu (frankfurt)', 'eu-central-1', 'euc1', 'frankfurt'],
            'ap-south-1': ['asia pacific (mumbai)', 'ap-south-1', 'aps1', 'mumbai'],
            'ap-southeast-1': ['asia pacific (singapore)', 'ap-southeast-1', 'apse1', 'singapore'],
            'ap-southeast-2': ['asia pacific (sydney)', 'ap-southeast-2', 'apse2', 'sydney'],
            'ap-northeast-1': ['asia pacific (tokyo)', 'ap-northeast-1', 'apne1', 'tokyo'],
            'ap-northeast-2': ['asia pacific (seoul)', 'ap-northeast-2', 'apne2', 'seoul'],
            'ca-central-1': ['canada (central)', 'ca-central-1', 'cac1', 'canada'],
            'sa-east-1': ['south america (são paulo)', 'sa-east-1', 'sae1', 'são paulo'],
            'global': ['global', 'worldwide', 'all regions', 'cloudfront global']
        }
    
    def _initialize_cost_patterns(self) -> List[str]:
        """Initialize cost extraction patterns"""
        return [
            r'USD\s+([\d,]+\.?\d*)',
            r'\$\s*([\d,]+\.?\d*)',
            r'([\d,]+\.?\d*)\s*USD',
            r'Cost:\s*\$?([\d,]+\.?\d*)',
            r'Total:\s*\$?([\d,]+\.?\d*)'
        ]
    
    def categorize_service(self, line: str) -> Tuple[str, str]:
        """
        Categorize AWS service from a line of text
        
        Args:
            line: Text line from AWS bill
            
        Returns:
            Tuple of (service_category, confidence_score)
        """
        line_lower = line.lower()
        
        # Score each service category
        category_scores = {}
        
        for category, patterns in self.service_patterns.items():
            score = 0
            
            # Check keywords
            for keyword in patterns['keywords']:
                if keyword.lower() in line_lower:
                    # Weight longer keywords higher
                    score += len(keyword.split()) * 2
            
            # Check units
            for unit in patterns['units']:
                if unit.lower() in line_lower:
                    score += 1
            
            if score > 0:
                category_scores[category] = score
        
        if not category_scores:
            return 'Other', 0.0
        
        # Return category with highest score
        best_category = max(category_scores.items(), key=lambda x: x[1])
        confidence = min(best_category[1] / 10.0, 1.0)  # Normalize to 0-1
        
        return best_category[0], confidence
    
    def extract_region(self, line: str) -> str:
        """Extract AWS region from line"""
        line_lower = line.lower()
        
        for region_code, patterns in self.region_patterns.items():
            for pattern in patterns:
                if pattern.lower() in line_lower:
                    return region_code
        
        return 'unknown'
    
    def extract_cost(self, line: str) -> Optional[Decimal]:
        """Extract cost from line"""
        for pattern in self.cost_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    cost_str = match.group(1).replace(',', '')
                    return Decimal(cost_str)
                except (InvalidOperation, ValueError):
                    continue
        
        return None
    
    def extract_usage_quantity_and_unit(self, line: str) -> Tuple[Optional[float], str]:
        """Extract usage quantity and unit from line"""
        # Common patterns for usage quantities
        patterns = [
            r'([\d,]+\.?\d*)\s+(hours?|hrs?)\b',
            r'([\d,]+\.?\d*)\s+(gb-mo|gb-month)\b',
            r'([\d,]+\.?\d*)\s+(requests?)\b',
            r'([\d,]+\.?\d*)\s+(gb|tb|mb)\b',
            r'([\d,]+\.?\d*)\s+(instances?)\b',
            r'([\d,]+\.?\d*)\s+(vcpu-hours?)\b',
            r'([\d,]+\.?\d*)\s+(messages?)\b',
            r'([\d,]+\.?\d*)\s+(queries?)\b',
            r'([\d,]+\.?\d*)\s+(events?)\b',
            r'([\d,]+\.?\d*)\s+(notifications?)\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    quantity = float(match.group(1).replace(',', ''))
                    unit = match.group(2).lower()
                    return quantity, unit
                except ValueError:
                    continue
        
        return None, 'unknown'
    
    def extract_service_details(self, line: str) -> Dict[str, Any]:
        """Extract detailed service information from line"""
        # Extract service type (instance type, storage class, etc.)
        service_type_patterns = [
            r'(t[2-4]g?\.[a-z0-9]+)',  # EC2 instance types
            r'(db\.[a-z0-9]+\.[a-z0-9]+)',  # RDS instance types
            r'(cache\.[a-z0-9]+\.[a-z0-9]+)',  # ElastiCache node types
            r'(gp[2-3]|io[1-2]|st1|sc1)',  # EBS volume types
            r'(standard|glacier|deep archive|intelligent)',  # S3 storage classes
        ]
        
        service_type = 'standard'
        for pattern in service_type_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                service_type = match.group(1)
                break
        
        return {
            'service_type': service_type,
            'rate_description': self._extract_rate_description(line)
        }
    
    def _extract_rate_description(self, line: str) -> str:
        """Extract rate description from line"""
        # Look for pricing information
        rate_patterns = [
            r'\$[\d,]+\.?\d*\s+per\s+[^,\n]+',
            r'USD[\d,]+\.?\d*\s+per\s+[^,\n]+',
            r'First\s+[\d,]+[^,\n]+',
            r'Additional\s+[^,\n]+',
        ]
        
        for pattern in rate_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return 'Standard rate'
    
    def analyze_aws_invoice(self, text: str, filename: str) -> Dict[str, Any]:
        """
        Comprehensive analysis of AWS invoice text
        
        Args:
            text: Raw invoice text
            filename: Source filename
            
        Returns:
            Dictionary with categorized services and analysis
        """
        logger.info(f"🔍 Starting comprehensive AWS invoice analysis for {filename}")
        
        lines = text.split('\n')
        service_usages = []
        total_cost = Decimal('0')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or len(line) < 10:  # Skip very short lines
                continue
            
            # Extract cost first
            cost = self.extract_cost(line)
            if cost is None or cost == 0:
                continue  # Skip lines without cost
            
            # Categorize service
            category, confidence = self.categorize_service(line)
            if confidence < 0.1:  # Skip low confidence matches
                continue
            
            # Extract other details
            region = self.extract_region(line)
            quantity, unit = self.extract_usage_quantity_and_unit(line)
            service_details = self.extract_service_details(line)
            
            # Create service usage record
            usage = ServiceUsage(
                service_category=category,
                service_name=self._extract_service_name(line, category),
                service_type=service_details['service_type'],
                region=region,
                usage_quantity=quantity or 0.0,
                usage_unit=unit,
                rate_description=service_details['rate_description'],
                cost=cost,
                raw_line=line,
                line_number=line_num
            )
            
            service_usages.append(usage)
            total_cost += cost
        
        # Group and analyze services
        analysis_result = self._group_and_analyze_services(service_usages, total_cost, filename)
        
        logger.info(f"✅ Analysis complete: {len(service_usages)} service entries, total cost: ${total_cost}")
        
        return analysis_result
    
    def _extract_service_name(self, line: str, category: str) -> str:
        """Extract specific service name from line"""
        line_lower = line.lower()
        
        # Service name patterns by category
        name_patterns = {
            'EC2': r'(elastic compute cloud|ec2|compute)',
            'RDS': r'(relational database service|rds|database)',
            'S3': r'(simple storage service|s3|storage)',
            'Lambda': r'(aws lambda|lambda)',
            'CloudFront': r'(cloudfront|cdn)',
            'EBS': r'(elastic block store|ebs)',
            'VPC': r'(virtual private cloud|vpc|nat gateway)',
            'ElastiCache': r'(elasticache)',
            'SQS': r'(simple queue service|sqs)',
            'SNS': r'(simple notification service|sns)',
            'CloudWatch': r'(cloudwatch)',
            'Route53': r'(route 53|route53)',
            'API_Gateway': r'(api gateway)',
            'Kinesis': r'(kinesis)',
            'DynamoDB': r'(dynamodb)',
            'Redshift': r'(redshift)',
            'EMR': r'(elastic mapreduce|emr)',
            'Glue': r'(glue)',
            'Athena': r'(athena)',
            'ECS': r'(elastic container service|ecs|fargate)',
            'EKS': r'(elastic kubernetes service|eks)'
        }
        
        pattern = name_patterns.get(category, category.lower())
        match = re.search(pattern, line_lower)
        
        if match:
            return match.group(1).title()
        
        return category
    
    def _group_and_analyze_services(self, service_usages: List[ServiceUsage], 
                                  total_cost: Decimal, filename: str) -> Dict[str, Any]:
        """Group services and create analysis summary"""
        
        # Group by service category
        services_by_category = {}
        category_totals = {}
        
        for usage in service_usages:
            category = usage.service_category
            
            if category not in services_by_category:
                services_by_category[category] = []
                category_totals[category] = Decimal('0')
            
            services_by_category[category].append(usage)
            category_totals[category] += usage.cost
        
        # Create summary
        analysis = {
            'filename': filename,
            'total_cost': float(total_cost),
            'total_entries': len(service_usages),
            'service_categories': list(services_by_category.keys()),
            'services_by_category': services_by_category,
            'category_totals': {k: float(v) for k, v in category_totals.items()},
            'cost_validation': {
                'calculated_total': float(total_cost),
                'category_sum': float(sum(category_totals.values())),
                'validation_passed': True  # Will be updated with actual invoice total
            }
        }
        
        return analysis
