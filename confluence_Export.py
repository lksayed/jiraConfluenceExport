import os
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment variables
ATLASSIAN_BASE_URL = os.getenv('ATLASSIAN_BASE_URL')
ATLASSIAN_API_TOKEN = os.getenv('ATLASSIAN_API_TOKEN')
ATLASSIAN_USER_EMAIL = os.getenv('ATLASSIAN_USER_EMAIL')
ORG_ID = os.getenv('ORG_ID')  # Load organization ID from environment
ORG_API_TOKEN = os.getenv('ORG_API_TOKEN')  # Load organization API token from environment

def fetch_confluence_groups():
    url = f"{ATLASSIAN_BASE_URL}/wiki/rest/api/group"
    auth = HTTPBasicAuth(ATLASSIAN_USER_EMAIL, ATLASSIAN_API_TOKEN)
    headers = {
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers, auth=auth)
    response.raise_for_status()
    confluence_groups = response.json()
    return confluence_groups['results']

def fetch_group_members(group_name):
    url = f"{ATLASSIAN_BASE_URL}/wiki/rest/api/group/{group_name}/member"
    auth = HTTPBasicAuth(ATLASSIAN_USER_EMAIL, ATLASSIAN_API_TOKEN)
    headers = {
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers, auth=auth)
    response.raise_for_status()
    group_members = response.json()
    return group_members['results']

def fetch_last_active_date(account_id):
    url = f"https://api.atlassian.com/admin/v1/orgs/{ORG_ID}/directory/users/{account_id}/last-active-dates"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ORG_API_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 401:
        pass  # Unauthorized access for account ID: {account_id}. Check the token and permissions.
    response.raise_for_status()
    
    last_active_data = response.json()

    # Extract the most recent last active date for Confluence
    product_access = last_active_data.get('data', {}).get('product_access', [])
    if product_access:
        confluence_dates = [access['last_active'] for access in product_access if access['key'] == 'confluence']
        if confluence_dates:
            return max(confluence_dates)
    return 'N/A'

def process_and_export_to_csv(confluence_groups):
    all_members = []

    for group in confluence_groups:
        group_name = group['name']
        members = fetch_group_members(group_name)
        for member in members:
            member['group'] = group_name
            member['last_active_date'] = fetch_last_active_date(member['accountId'])
            # Remove unwanted fields
            member.pop('profilePicture', None)
            all_members.append(member)

    confluence_df = pd.DataFrame(all_members)

    # Specify the columns to keep
    columns_to_keep = [
        'type', 'accountId', 'accountType', 'email', 'publicName', 
        'displayName', 'isExternalCollaborator', 'group', 'last_active_date'
    ]
    confluence_df = confluence_df[columns_to_keep]

    confluence_df.to_csv('confluence_users.csv', index=False)

if __name__ == "__main__":
    confluence_groups = fetch_confluence_groups()
    process_and_export_to_csv(confluence_groups)