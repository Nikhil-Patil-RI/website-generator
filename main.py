import os
import logging
import tempfile
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Import helper modules
from utils.github_api import create_github_repository
from utils.git_operations import clone_template_repository, push_to_github

load_dotenv()

# --- Configuration & Constants ---

# Initialize FastMCP server
mcp = FastMCP("website-generator")

# Template Repository
TEMPLATE_REPO = "https://github.com/Jeetanshu18/react-vite"

# Get GitHub token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    logging.warning("GITHUB_TOKEN environment variable not set.")


@mcp.tool()
async def repo_setup(
    project_name: str, description: str = "", deploy_to_amplify: bool = False
) -> str:
    """
    Setup a new repository for a website project by cloning a template, creating a GitHub repo, and pushing the code.

    This tool performs the following steps:
    1. Clone the React Vite template repository
    2. Remove the .git folder from the cloned repository
    3. Create a new repository on GitHub with the given project name
    4. Push the cloned repository to the new GitHub repository
    5. Optionally deploy to AWS Amplify (if requested)

    Args:
        project_name: Name of the project and GitHub repository
        description: Optional description for the GitHub repository
        deploy_to_amplify: Whether to deploy to AWS Amplify (optional, not implemented yet)

    Returns:
        Status message with repository URL and deployment information
    """
    # Check for token at function call time
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        return "GitHub Token is missing. Cannot process repository setup requests."

    if not project_name or not project_name.strip():
        return "Project name is required and cannot be empty."

    # Sanitize project name for GitHub
    project_name = project_name.strip().replace(" ", "-").lower()

    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            logging.info(f"Starting repository setup for project: {project_name}")

            # Step 1: Clone template repository
            logging.info("Step 1: Cloning template repository...")
            success, project_path = await clone_template_repository(
                project_name, temp_dir, TEMPLATE_REPO
            )
            if not success:
                return f"Failed at Step 1: {project_path}"

            # Step 2: Create GitHub repository
            logging.info("Step 2: Creating GitHub repository...")
            success, repo_url = await create_github_repository(
                project_name, description
            )
            if not success:
                return f"Failed at Step 2: {repo_url}"

            # Step 3: Push to GitHub
            logging.info("Step 3: Pushing code to GitHub...")
            success, message = await push_to_github(
                project_path, repo_url, project_name
            )
            if not success:
                return f"Failed at Step 3: {message}"

            # Prepare success message
            result_message = f"""
Repository setup completed successfully!

Project Name: {project_name}
Repository URL: {repo_url.replace('.git', '')}
Template Used: {TEMPLATE_REPO}

Steps Completed:
✅ Cloned React Vite template repository
✅ Removed .git folder from template
✅ Created new GitHub repository
✅ Pushed code to GitHub repository

Your website project is now ready! You can:
1. Clone the repository locally: git clone {repo_url}
2. Install dependencies: npm install
3. Start development server: npm run dev
4. Build for production: npm run build
"""

            # Step 4: Optional Amplify deployment
            if deploy_to_amplify:
                result_message += "\n⚠️  AWS Amplify deployment is not yet implemented but can be added in future updates."

            return result_message.strip()

        except Exception as e:
            logging.error(f"Unexpected error during repository setup: {str(e)}")
            return f"Repository setup failed due to unexpected error: {str(e)}"


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Check for GitHub Token at startup
    if not GITHUB_TOKEN:
        logging.critical(
            "GITHUB_TOKEN is not set. The server cannot communicate with GitHub API."
        )
        logging.info(
            "Please set the GITHUB_TOKEN environment variable with a valid GitHub personal access token."
        )
        # Note: We don't exit here to allow the server to start, but operations will fail

    # Initialize and run the server
    mcp.run(transport="stdio")
