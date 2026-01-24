"""Google Sheets client for updating account information."""

import json
import os
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Column headers for the sheet
HEADERS = ["Org ID", "Root Account ID", "Account ID", "Account Name", "Account Email", "Account Status", "Joined Date"]


def get_sheets_client() -> gspread.Client:
    """Get an authenticated gspread client from environment variables."""
    json_str = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    
    if not json_str:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable is required")
    
    creds_dict = json.loads(json_str)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    
    return gspread.authorize(creds)


def format_date(dt: datetime) -> str:
    """Format a datetime for display in the sheet."""
    return dt.strftime("%Y-%m-%d")


def delete_worksheet_if_exists(spreadsheet: gspread.Spreadsheet, tab_name: str) -> None:
    """Delete a worksheet if it exists."""
    try:
        worksheet = spreadsheet.worksheet(tab_name)
        spreadsheet.del_worksheet(worksheet)
    except gspread.WorksheetNotFound:
        pass


def create_worksheet(spreadsheet: gspread.Spreadsheet, tab_name: str, org_info: dict, accounts: list[dict]) -> None:
    """
    Create a worksheet with account data.
    
    Args:
        spreadsheet: The Google Spreadsheet object
        tab_name: Name for the worksheet tab
        org_info: Dictionary with org_id, root_account_id, root_account_name
        accounts: List of account dictionaries from AWS
    """
    org_id = org_info["org_id"]
    root_account_id = org_info["root_account_id"]
    
    # Sort by JoinedTimestamp, newest first
    accounts = sorted(accounts, key=lambda a: a["JoinedTimestamp"], reverse=True)
    
    # Build rows
    rows = [HEADERS]
    for account in accounts:
        rows.append([
            org_id,
            root_account_id,
            account["Id"],
            account["Name"],
            account["Email"],
            account["Status"],
            format_date(account["JoinedTimestamp"])
        ])
    
    if not accounts:
        rows.append(["(none)", "", "", "", "", "", ""])
    
    # Create new worksheet and write data
    worksheet = spreadsheet.add_worksheet(title=tab_name, rows=max(len(rows) + 10, 100), cols=10)
    worksheet.update(range_name="A1", values=rows)
    
    # Get sheet ID for formatting requests
    ws_sheet_id = worksheet._properties['sheetId']
    
    # Set tab color (green for active, red for deleted)
    if tab_name.startswith("ACTIVE"):
        tab_color = {"red": 0.2, "green": 0.8, "blue": 0.2}  # Green
    else:
        tab_color = {"red": 0.9, "green": 0.2, "blue": 0.2}  # Red
    
    # Auto-resize columns and set tab color
    body = {
        "requests": [
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": ws_sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": len(HEADERS)
                    }
                }
            },
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": ws_sheet_id,
                        "tabColor": tab_color
                    },
                    "fields": "tabColor"
                }
            }
        ]
    }
    spreadsheet.batch_update(body)
    
    return len(accounts)


def update_org_sheets(client: gspread.Client, sheet_id: str, org_info: dict, accounts: list[dict]) -> None:
    """
    Create separate worksheets for active and pending deletion accounts.
    
    Creates two sheets:
    1. ACTIVE - <org-id> - <root-account-id> - <friendly-name>
    2. DELETED - <org-id> - <root-account-id> - <friendly-name>
    
    Sheets are deleted and recreated on each run.
    
    Args:
        client: Authenticated gspread client
        sheet_id: Google Sheet ID
        org_info: Dictionary with org_id, root_account_id, root_account_name
        accounts: List of account dictionaries from AWS
    """
    spreadsheet = client.open_by_key(sheet_id)
    
    # Base tab name format: <org-id> - <root-account-id> - <friendly-name>
    base_name = f"{org_info['org_id']} - {org_info['root_account_id']} - {org_info['root_account_name']}"
    
    # Tab names with prefixes (limited to 100 characters)
    active_tab = f"ACTIVE - {base_name}"[:100]
    deleted_tab = f"DELETED - {base_name}"[:100]
    
    # Separate accounts by status
    active_accounts = [a for a in accounts if a["Status"] == "ACTIVE"]
    pending_deletion = [a for a in accounts if a["Status"] in ("SUSPENDED", "PENDING_CLOSURE")]
    
    # Delete existing sheets (nuke and recreate)
    delete_worksheet_if_exists(spreadsheet, active_tab)
    delete_worksheet_if_exists(spreadsheet, deleted_tab)
    
    # Create new sheets
    active_count = create_worksheet(spreadsheet, active_tab, org_info, active_accounts)
    deleted_count = create_worksheet(spreadsheet, deleted_tab, org_info, pending_deletion)
    
    print(f"Created sheets: {active_tab} ({active_count} accounts), {deleted_tab} ({deleted_count} accounts)")


def sync_org(sheet_id: str, org_data: dict) -> None:
    """
    Sync organization data to the Google Sheet.
    
    Args:
        sheet_id: Google Sheet ID
        org_data: Dictionary with org_info and accounts
    """
    client = get_sheets_client()
    
    update_org_sheets(client, sheet_id, org_data["org_info"], org_data["accounts"])
    
    print("Synced organization to sheet")
