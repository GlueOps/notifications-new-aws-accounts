# AWS Organization Account Tracker

Syncs AWS Organization accounts to a Google Sheet with color-coded tabs for active and pending deletion accounts.

## Features

- Fetches all accounts from an AWS Organization
- Creates two sheet tabs per org:
  - 🟢 **ACTIVE** - Active accounts (green tab)
  - 🔴 **DELETED** - Suspended/pending closure accounts (red tab)
- Sorted by joined date (newest first)
- Auto-resizes columns to fit content
- Nukes and recreates sheets on each run (safe for scheduling)

## Requirements

- Docker
- AWS credentials with `AWSOrganizationsReadOnlyAccess` policy
- Google Cloud service account with Sheets API access
- A Google Sheet shared with the service account

## Environment Variables

| Variable | Description |
|----------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |
| `GOOGLE_SHEET_ID` | Google Sheet ID (from URL: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Full JSON content of the Google service account key |

## Setup

### 1. AWS IAM User

Create an IAM user with the `AWSOrganizationsReadOnlyAccess` managed policy attached.

### 2. Google Cloud Service Account

1. Create a Google Cloud project (or use existing)
2. Enable the Google Sheets API
3. Create a service account (IAM & Admin → Service Accounts → Create)
4. Create a JSON key and download it
5. Share your Google Sheet with the service account email as Editor

### 3. Build Docker Image

```bash
docker build -t aws-account-tracker .
```

## Usage

### Run with environment variables

```bash
docker run --rm \
  -e AWS_ACCESS_KEY_ID="your-access-key" \
  -e AWS_SECRET_ACCESS_KEY="your-secret-key" \
  -e GOOGLE_SHEET_ID="your-sheet-id" \
  -e "GOOGLE_SERVICE_ACCOUNT_JSON=$(cat service-account.json)" \
  aws-account-tracker
```

### Run with .env file (for non-JSON vars)

```bash
docker run --rm \
  --env-file .env \
  -e "GOOGLE_SERVICE_ACCOUNT_JSON=$(cat service-account.json)" \
  aws-account-tracker
```

## Sheet Output

Each run creates/recreates two tabs:

**Tab names:**
- `ACTIVE - <org-id> - <root-account-id> - <org-name>`
- `DELETED - <org-id> - <root-account-id> - <org-name>`

**Columns:**
| Org ID | Root Account ID | Account ID | Account Name | Account Email | Account Status | Joined Date |

## Scheduling

This app is designed to run on a schedule (e.g., daily via cron, GitHub Actions, or AWS EventBridge). Each run completely recreates the sheets, so it's safe to run repeatedly.
