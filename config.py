"""
Configuration for the Repository Dashboard.

This module centralizes everything that the application needs to know at
startup: the GitHub API endpoint, the target repository, and the secret
token used to authenticate GitHub requests.

All values can be overridden from a ``.env`` file in the project root
(via ``python-dotenv``), which is the recommended way to keep secrets
out of source control.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env (if present) before reading them.
# This allows you to keep GITHUB_TOKEN secret without hardcoding it.
load_dotenv()

# GitHub Personal Access Token — used to authenticate API requests.
# Public repos like apache/superset work without a token, but a token
# raises the rate limit from 60 to 5000 requests/hour and enables
# access to private repositories.
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Base URL for the GitHub REST API (v3).
GITHUB_API_URL = "https://api.github.com"

# The repository this dashboard monitors.
# Change these two values to point at a different repo.
REPO_OWNER = "apache"
REPO_NAME = "superset"
