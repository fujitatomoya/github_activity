import os
import subprocess
import requests
import argparse


def clone_repositories(org_name, token, clone_dir):
    # Base URL for GitHub API
    base_url = f"https://api.github.com/orgs/{org_name}/repos"

    # Create the directory if it doesn't exist
    os.makedirs(clone_dir, exist_ok=True)

    # Headers for authentication (if token is provided)
    headers = {"Authorization": f"token {token}"} if token else {}

    # Paginate through all repositories
    page = 1
    while True:
        response = requests.get(base_url, headers=headers, params={"page": page, "per_page": 100})
        repos = response.json()

        # Check for errors or no more repositories
        if not repos or "message" in repos:
            if "message" in repos:
                print(f"Error: {repos['message']}")
            break

        # Clone each repository
        for repo in repos:
            clone_url = repo["clone_url"]
            repo_name = repo["name"]
            print(f"Cloning {repo_name}...")
            subprocess.run(["git", "clone", clone_url], cwd=clone_dir)

        page += 1

    print("All repositories cloned.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clone all repositories of a GitHub organization.")
    parser.add_argument(
        "organization", type=str, help="The name of the GitHub organization.")
    parser.add_argument(
        "--token", type=str, default=None,
        help="Personal Access Token for authentication (optional).")
    parser.add_argument(
        "--clone_dir", type=str, default="./cloned_repos",
        help="Directory to store the cloned repositories.")

    args = parser.parse_args()
    clone_repositories(args.organization, args.token, args.clone_dir)
