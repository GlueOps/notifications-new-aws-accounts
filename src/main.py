#!/usr/bin/env python3
"""
AWS Organization Account Tracker

Fetches accounts from an AWS Organization and syncs them to a Google Sheet.
Creates two color-coded sheet tabs per organization:
1. ACTIVE (green) - Active accounts sorted by joined date, newest first
2. DELETED (red) - SUSPENDED and PENDING_CLOSURE accounts
"""

import os
import sys

from dotenv import load_dotenv

from aws_client import fetch_org_data
from sheets_client import sync_org


def main():
    # Load environment variables from .env file if present
    load_dotenv()
    
    # Get configuration from environment
    sheet_id = os.environ.get("GOOGLE_SHEET_ID", "")
    
    # Validate AWS credentials are present
    if not os.environ.get("AWS_ACCESS_KEY_ID") or not os.environ.get("AWS_SECRET_ACCESS_KEY"):
        print("ERROR: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables are required")
        sys.exit(1)
    
    if not sheet_id:
        print("ERROR: GOOGLE_SHEET_ID environment variable is required")
        sys.exit(1)
    
    if not os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"):
        print("ERROR: GOOGLE_SERVICE_ACCOUNT_JSON environment variable is required")
        sys.exit(1)
    
    print("Starting sync...")
    
    # Fetch accounts from the org
    org_data = fetch_org_data()
    
    # Sync to Google Sheets
    sync_org(sheet_id, org_data)
    
    print("Done!")


if __name__ == "__main__":
    main()
