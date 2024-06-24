import os
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Get environment variables
ATLASSIAN_BASE_URL = os.getenv('ATLASSIAN_BASE_URL')
ATLASSIAN_API_TOKEN = os.getenv('ATLASSIAN_API_TOKEN')
ATLASSIAN_USER_EMAIL = os.getenv('ATLASSIAN_USER_EMAIL')
PROJECT_KEY = os.getenv('PROJECT_KEY')

ORG_ID = os.getenv('ORG_ID')  # Load organization ID from environment
ORG_API_TOKEN = os.getenv('ORG_API_TOKEN')  # Load organization API token from environment

# # Debugging statements to check if environment variables are loaded correctly
# print(f"ATLASSIAN_BASE_URL: {ATLASSIAN_BASE_URL}")
# print(f"ATLASSIAN_API_TOKEN: {ATLASSIAN_API_TOKEN}")
# print(f"ATLASSIAN_USER_EMAIL: {ATLASSIAN_USER_EMAIL}")
# print(f"PROJECT_KEY: {PROJECT_KEY}")
# print(f"ORG_ID: {ORG_ID}")
# print(f"ORG_API_TOKEN: {ORG_API_TOKEN}")

def fetch_jira_user_access(project_key):
    url = f"{ATLASSIAN_BASE_URL}/rest/api/3/user/assignable/search"
    auth = HTTPBasicAuth(ATLASSIAN_USER_EMAIL, ATLASSIAN_API_TOKEN)
    headers = {
        "Accept": "application/json"
    }
    params = {
        'project': project_key
    }
    response = requests.get(url, headers=headers, auth=auth, params=params)
    response.raise_for_status()
    return response.json()

def fetch_last_active_date(account_id):
    url = f"https://api.atlassian.com/admin/v1/orgs/{ORG_ID}/directory/users/{account_id}/last-active-dates"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ORG_API_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 401:
        print(f"Unauthorized access for account ID: {account_id}. Check the token and permissions.")
    response.raise_for_status()
    
    last_active_data = response.json()
    
    # Debugging: print the response
    # print(f"Last active date response for account ID {account_id}: {last_active_data}")

    # Extract the most recent last active date
    product_access = last_active_data.get('data', {}).get('product_access', [])
    if product_access:
        last_active_dates = [access['last_active'] for access in product_access]
        most_recent_last_active = max(last_active_dates)
        return most_recent_last_active
    return 'N/A'

def process_and_export_to_csv(jira_users):
    jira_df = pd.DataFrame(jira_users)
    print("Jira DataFrame Head:\n", jira_df.head())  # Debugging statement to print the first few rows

    # Fetch and add last active date for Jira users
    jira_df['last_active_date'] = jira_df['accountId'].apply(lambda x: fetch_last_active_date(x))
    
    jira_df.to_csv('jira_users.csv', index=False)

if __name__ == "__main__":
    jira_users = fetch_jira_user_access(PROJECT_KEY)
    process_and_export_to_csv(jira_users)