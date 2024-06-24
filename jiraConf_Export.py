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
PROJECT_KEY = os.getenv('PROJECT_KEY')  # Load project key from environment

# Debugging statements to check if environment variables are loaded correctly
print(f"ATLASSIAN_BASE_URL: {ATLASSIAN_BASE_URL}")
print(f"ATLASSIAN_API_TOKEN: {ATLASSIAN_API_TOKEN}")
print(f"ATLASSIAN_USER_EMAIL: {ATLASSIAN_USER_EMAIL}")
print(f"PROJECT_KEY: {PROJECT_KEY}")

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

def fetch_confluence_user_access(group_name):
    url = f"{ATLASSIAN_BASE_URL}/wiki/rest/api/group"
    auth = HTTPBasicAuth(ATLASSIAN_USER_EMAIL, ATLASSIAN_API_TOKEN)
    headers = {
        "Accept": "application/json"
    }
    params = {
        'name': group_name
    }
    response = requests.get(url, headers=headers, auth=auth, params=params)
    response.raise_for_status()
    confluence_data = response.json()
    print(confluence_data)  # Print the full response for debugging
    return confluence_data

def process_and_export_to_csv(jira_users, confluence_users):
    jira_df = pd.DataFrame(jira_users)
    
    # Adjust based on the actual response structure
    if 'results' in confluence_users:
        confluence_df = pd.DataFrame(confluence_users['results'])
    else:
        confluence_df = pd.DataFrame(confluence_users)
    
    jira_df.to_csv('jira_users.csv', index=False)
    confluence_df.to_csv('confluence_users.csv', index=False)

if __name__ == "__main__":
    group_name = 'TestDev'
    jira_users = fetch_jira_user_access(PROJECT_KEY)
    confluence_users = fetch_confluence_user_access(group_name)
    process_and_export_to_csv(jira_users, confluence_users)