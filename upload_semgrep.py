#!/usr/bin/env python3
import argparse
import json
import logging
import os
import requests
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('semgrep-uploader')

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Upload Semgrep scan results to AppSec Dashboard')
    parser.add_argument('--report', required=True, help='Path to the Semgrep JSON report file')
    parser.add_argument('--api-url', required=True, help='URL of the AppSec Dashboard API')
    parser.add_argument('--project-id', required=True, help='GitLab project ID')
    parser.add_argument('--pipeline-id', required=True, help='GitLab pipeline ID')
    parser.add_argument('--job-id', required=True, help='GitLab job ID')
    parser.add_argument('--branch', required=True, help='Git branch name')
    parser.add_argument('--commit-sha', required=True, help='Git commit SHA')
    # parser.add_argument('--api-token', help='API token for authentication')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--project-path', help='Full path of the GitLab project')
    parser.add_argument('--project-name', help='Name of the GitLab project')
    return parser.parse_args()

# This function is no longer needed as we're using Semgrep's native GitLab SAST output format
# Keeping this as a comment for reference
# def convert_semgrep_to_gitlab_format(semgrep_data):
#     """Convert Semgrep report format to GitLab SAST format"""
#     # Function removed as we now use Semgrep's native GitLab SAST output

def upload_report(args, gitlab_report):
    """Upload the converted report to the AppSec Dashboard API"""
    # Prepare API request
    url = f"{args.api_url.rstrip('/')}/api/reports/upload/"
    
    # Prepare request data
    request_data = {
        "project_id": args.project_id,
        "scan_type": "SAST", 
        "pipeline_id": args.pipeline_id,
        "job_id": args.job_id,
        "branch": args.branch,
        "commit_sha": args.commit_sha,
        "report": gitlab_report
    }
    
    # Add project path and name if provided
    if hasattr(args, 'project_path') and args.project_path:
        request_data["project_path"] = args.project_path
    
    if hasattr(args, 'project_name') and args.project_name:
        request_data["project_name"] = args.project_name
    
    # Prepare headers
    headers = {}
    # if args.api_token:
    #     headers["Authorization"] = f"Token {args.api_token}"
    
    # Send request
    try:
        logger.info(f"Uploading Semgrep report to {url}")
        response = requests.post(url, json=request_data, headers=headers)
        
        # Check response
        if response.status_code in (200, 201):
            logger.info("Report uploaded successfully")
            logger.info(f"Response: {response.json()}")
            return True
        else:
            logger.error(f"Failed to upload report. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error uploading report: {str(e)}")
        return False

def main():
    # Parse arguments
    args = parse_arguments()
    
    # Set debug logging if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Load Semgrep report (already in GitLab SAST format)
    try:
        logger.info(f"Loading Semgrep GitLab SAST report from {args.report}")
        with open(args.report, 'r') as f:
            gitlab_report = json.load(f)
    except Exception as e:
        logger.error(f"Error loading Semgrep report: {str(e)}")
        return 1
    
    # Upload report directly (no conversion needed)
    if upload_report(args, gitlab_report):
        logger.info("Report processing completed successfully")
        return 0
    else:
        logger.error("Report processing failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())