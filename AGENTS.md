# Agent Instructions

This document provides context for AI coding agents working on this project.

## Project Overview

A Python application that syncs AWS Organization accounts to a Google Sheet. It creates color-coded tabs (green for active, red for pending deletion) and is designed to run on a schedule.

## Architecture

```
src/
├── main.py           # Entry point, env var validation, orchestration
├── aws_client.py     # AWS Organizations API calls (boto3)
├── sheets_client.py  # Google Sheets API calls (gspread)
└── __init__.py
```

## Key Design Decisions

1. **Nuke and recreate** - Sheets are deleted and recreated on each run (no incremental updates)
2. **Single org per run** - Designed to run multiple times with different AWS credentials for multiple orgs
3. **Env vars only** - All configuration via environment variables (no config files)
4. **Docker-first** - Primary execution method is via Docker container

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AWS_ACCESS_KEY_ID` | Yes | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS secret key |
| `GOOGLE_SHEET_ID` | Yes | Target Google Sheet ID |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Yes | Full JSON string of service account key |

## Dependencies

- `boto3` - AWS SDK
- `gspread` - Google Sheets API wrapper
- `google-auth` - Google authentication
- `python-dotenv` - Local .env file support

## Common Tasks

### Build and run locally

```bash
docker build -t aws-account-tracker .
docker run --rm \
  --env-file .env \
  -e "GOOGLE_SERVICE_ACCOUNT_JSON=$(cat service-account.json)" \
  aws-account-tracker
```

### Add a new column

1. Add to `HEADERS` list in `sheets_client.py`
2. Add to row append in `create_worksheet()` function
3. Update empty row placeholder to match column count

### Change tab naming

Modify `update_org_sheets()` in `sheets_client.py` - look for `active_tab` and `deleted_tab` variables.

### Change sorting

Modify the `sorted()` call in `create_worksheet()` in `sheets_client.py`.

## Testing

No automated tests currently. Test manually by running with valid credentials and checking the Google Sheet output.

