import streamlit as st
import requests
import requests_cache
from collections import defaultdict

# Enable caching
requests_cache.install_cache('github_cache', expire_after=18000)  # Cache for 5 hours

# Your personal access token and headers
# Warning: It is not safe to store tokens in source code.
# It would be better to use environment variables or Streamlit's Secret Management.
headers = {'Authorization': f'token {st.secrets.GH_TOKEN}'}

# Base URL for GitHub API
base_url = "https://api.github.com"

def fetch_repositories(query):
    # Search for repositories with the user-specified query
    search_url = f"{base_url}/search/repositories?q={query}&sort=stars&order=desc"
    response = requests.get(search_url, headers=headers)
    data = response.json()
    return data['items']

def fetch_contributor_info(repo_full_name):
    contributors_url = f"{base_url}/repos/{repo_full_name}/contributors"
    response = requests.get(contributors_url, headers=headers)
    return response.json()

def fetch_profile_data(contributor_login):
    contributor_profile_url = f"{base_url}/users/{contributor_login}"
    profile_response = requests.get(contributor_profile_url, headers=headers)
    return profile_response.json()

def main():
    st.title("GitHub Repository and Contributor Analysis")

    # Input field for query topic
    query = st.text_input("Enter a GitHub topic to search for repositories", "topic:llm")

    if st.button("Search"):
        repositories = fetch_repositories(query)
        all_contributors = defaultdict(lambda: {'contributions': 0, 'followers': 0, 'public_repos': 0, 'location': '', 'url': ''})

        for repo in repositories:
            contributors = fetch_contributor_info(repo['full_name'])

            for contributor in contributors:
                contributor_login = contributor['login']
                profile_data = fetch_profile_data(contributor_login)

                all_contributors[contributor_login]['contributions'] += contributor['contributions']
                all_contributors[contributor_login]['followers'] = profile_data.get('followers', 0)
                all_contributors[contributor_login]['public_repos'] = profile_data.get('public_repos', 0)
                all_contributors[contributor_login]['location'] = profile_data.get('location', 'Unknown')
                all_contributors[contributor_login]['url'] = profile_data.get('html_url', '')

        # Sorting contributors based on total contributions
        sorted_contributors = sorted(all_contributors.items(), key=lambda x: x[1]['contributions'], reverse=True)

        # Displaying ranked contributors
        for contributor_login, data in sorted_contributors:
            st.write(f"""
            - Contributor: {contributor_login}, 
            Total Contributions: {data['contributions']}, 
            Followers: {data['followers']}, 
            Public Repos: {data['public_repos']}, 
            Location: {data['location']}, 
            URL: {data['url']}
            """)

if __name__ == "__main__":
    main()
