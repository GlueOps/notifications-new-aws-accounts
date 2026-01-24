"""AWS Organizations client for fetching account information."""

import boto3


def get_org_info() -> dict:
    """
    Get organization information including the management (root) account.
    
    Returns:
        Dictionary with:
        - org_id: Organization ID (e.g., o-abc123)
        - root_account_id: Management account ID
        - root_account_name: Management account friendly name
    """
    org_client = boto3.client("organizations")
    org = org_client.describe_organization()["Organization"]
    
    # Get management account details
    mgmt_account_id = org["MasterAccountId"]
    mgmt_account = org_client.describe_account(AccountId=mgmt_account_id)["Account"]
    
    return {
        "org_id": org["Id"],
        "root_account_id": mgmt_account_id,
        "root_account_name": mgmt_account["Name"]
    }


def list_accounts() -> list[dict]:
    """
    List all accounts in the organization.
    
    Returns a list of account dictionaries with keys:
    - Id: Account ID
    - Name: Account name
    - Email: Account email
    - Status: ACTIVE, SUSPENDED, or PENDING_CLOSURE
    - JoinedTimestamp: When the account joined the org
    """
    org_client = boto3.client("organizations")
    paginator = org_client.get_paginator("list_accounts")
    
    accounts = []
    for page in paginator.paginate():
        accounts.extend(page["Accounts"])
    
    return accounts


def fetch_org_data() -> dict:
    """
    Fetch accounts from the AWS Organization.
    
    Uses credentials from environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY).
        
    Returns:
        Dictionary with org_info and accounts
    """
    org_info = get_org_info()
    print(f"Fetching accounts for org: {org_info['org_id']} ({org_info['root_account_name']})")
    
    accounts = list_accounts()
    print(f"Found {len(accounts)} accounts")
    
    return {
        "org_info": org_info,
        "accounts": accounts
    }
