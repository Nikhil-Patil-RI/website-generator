"""
GitHub API integration module for the website generator MCP server.
"""

import os
import logging
from typing import Any, Optional, Literal
import httpx

# GitHub API Configuration
GITHUB_API_BASE = "https://api.github.com"
USER_AGENT = "website-generator-mcp/1.0.0"
DEFAULT_TIMEOUT = 30.0


async def make_github_request(
    method: Literal["GET", "POST", "PUT", "DELETE"],
    endpoint: str,
    payload: Optional[dict[str, Any]] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Optional[dict[str, Any]]:
    """
    Makes an HTTP request to the GitHub API.

    Args:
        method: HTTP method ('GET', 'POST', 'PUT', 'DELETE').
        endpoint: API endpoint path (e.g., '/user/repos').
        payload: JSON payload for POST/PUT requests. Ignored for GET/DELETE.
        timeout: Request timeout in seconds.

    Returns:
        The parsed JSON response as a dictionary on success, None on failure.
    """
    # Check for token at request time, not import time
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        logging.error("GitHub Token is missing. Cannot make API request.")
        return None

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {github_token}",
    }

    # Construct full URL
    url = f"{GITHUB_API_BASE}{endpoint}"

    async with httpx.AsyncClient() as client:
        try:
            if method == "POST":
                response = await client.post(
                    url, json=payload, headers=headers, timeout=timeout
                )
            elif method == "PUT":
                response = await client.put(
                    url, json=payload, headers=headers, timeout=timeout
                )
            elif method == "DELETE":
                response = await client.delete(url, headers=headers, timeout=timeout)
            else:  # Default to GET
                response = await client.get(url, headers=headers, timeout=timeout)

            response.raise_for_status()  # Raise exception for 4xx or 5xx status codes
            return response.json()

        except httpx.HTTPStatusError as e:
            logging.error(
                f"HTTP error calling {method} {url}: {e.response.status_code} - {e.response.text}"
            )
        except httpx.RequestError as e:
            logging.error(f"Request error calling {method} {url}: {str(e)}")
        except Exception as e:
            logging.error(
                f"An unexpected error occurred calling {method} {url}: {str(e)}"
            )

        return None


async def create_github_repository(
    project_name: str, description: str = ""
) -> tuple[bool, str]:
    """
    Create a new repository on GitHub.

    Args:
        project_name: Name of the repository
        description: Repository description

    Returns:
        Tuple of (success, repo_url_or_error)
    """
    payload = {
        "name": project_name,
        "description": description or f"Website project: {project_name}",
        "private": False,
        "auto_init": False,
    }

    result = await make_github_request("POST", "/user/repos", payload=payload)

    if not result:
        return False, "Failed to create GitHub repository"

    repo_url = result.get("clone_url", "")
    if not repo_url:
        return False, "Repository created but clone URL not found"

    return True, repo_url
