"""
Git operations module for the website generator MCP server.
"""
import os
import logging
import subprocess
import shutil
import tempfile
from typing import Optional

# Default Timeouts
CLONE_TIMEOUT = 60.0


def run_command(command: list[str], cwd: Optional[str] = None) -> tuple[bool, str]:
    """
    Run a shell command and return success status and output.
    
    Args:
        command: List of command parts
        cwd: Working directory for the command
        
    Returns:
        Tuple of (success, output/error_message)
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=CLONE_TIMEOUT
        )
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {CLONE_TIMEOUT} seconds"
    except Exception as e:
        return False, f"Command failed: {str(e)}"


async def clone_template_repository(project_name: str, temp_dir: str, template_repo: str) -> tuple[bool, str]:
    """
    Clone the template repository to a temporary directory.
    
    Args:
        project_name: Name of the project
        temp_dir: Temporary directory path
        template_repo: URL of the template repository
        
    Returns:
        Tuple of (success, message)
    """
    project_path = os.path.join(temp_dir, project_name)
    
    # Clone the repository
    success, output = run_command([
        "git", "clone", template_repo, project_path
    ])
    
    if not success:
        return False, f"Failed to clone template repository: {output}"
    
    # Remove .git folder
    git_path = os.path.join(project_path, ".git")
    if os.path.exists(git_path):
        try:
            shutil.rmtree(git_path)
            logging.info(f"Removed .git folder from {project_path}")
        except Exception as e:
            return False, f"Failed to remove .git folder: {str(e)}"
    
    return True, project_path


async def push_to_github(project_path: str, repo_url: str, project_name: str) -> tuple[bool, str]:
    """
    Initialize git and push the project to GitHub.
    
    Args:
        project_path: Local path to the project
        repo_url: GitHub repository URL
        project_name: Name of the project
        
    Returns:
        Tuple of (success, message)
    """
    # Get GitHub token for authentication
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        return False, "GitHub token is required for pushing to repository"
    
    # Convert HTTPS URL to include token for authentication
    # Format: https://token@github.com/user/repo.git
    if repo_url.startswith("https://github.com/"):
        authenticated_url = repo_url.replace("https://github.com/", f"https://{github_token}@github.com/")
    else:
        return False, f"Unsupported repository URL format: {repo_url}"
    
    # Initialize git repository
    success, output = run_command(["git", "init"], cwd=project_path)
    if not success:
        return False, f"Failed to initialize git repository: {output}"
    
    # Add all files
    success, output = run_command(["git", "add", "."], cwd=project_path)
    if not success:
        return False, f"Failed to add files to git: {output}"
    
    # Commit files
    success, output = run_command([
        "git", "commit", "-m", f"Initial commit for {project_name}"
    ], cwd=project_path)
    if not success:
        return False, f"Failed to commit files: {output}"
    
    # Add remote origin with authenticated URL
    success, output = run_command([
        "git", "remote", "add", "origin", authenticated_url
    ], cwd=project_path)
    if not success:
        return False, f"Failed to add remote origin: {output}"
    
    # Set default branch to main
    success, output = run_command([
        "git", "branch", "-M", "main"
    ], cwd=project_path)
    if not success:
        return False, f"Failed to set main branch: {output}"
    
    # Push to GitHub using authenticated URL
    success, output = run_command([
        "git", "push", "-u", "origin", "main"
    ], cwd=project_path)
    if not success:
        return False, f"Failed to push to GitHub: {output}"
    
    return True, "Successfully pushed to GitHub"


async def create_file_in_project(file_path: str, file_name: str, content: str) -> tuple[bool, str]:
    """
    Create a new file with the given content at the specified path.
    
    Args:
        file_path: Directory path where the file should be created
        file_name: Name of the file to create
        content: Content to write to the file
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Ensure the directory exists
        if not os.path.exists(file_path):
            os.makedirs(file_path, exist_ok=True)
            logging.info(f"Created directory: {file_path}")
        
        # Create the full file path
        full_file_path = os.path.join(file_path, file_name)
        
        # Write content to the file
        with open(full_file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        logging.info(f"Successfully created file: {full_file_path}")
        return True, f"File '{file_name}' created successfully at '{file_path}'"
        
    except Exception as e:
        error_msg = f"Failed to create file '{file_name}' at '{file_path}': {str(e)}"
        logging.error(error_msg)
        return False, error_msg


async def commit_and_push_changes(project_path: str, commit_message: str) -> tuple[bool, str]:
    """
    Check for changes, commit them, and push to the remote repository.
    
    Args:
        project_path: Local path to the project repository
        commit_message: Message for the commit
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Check if we're in a git repository
        if not os.path.exists(os.path.join(project_path, ".git")):
            return False, "Not a git repository. Please ensure the project is initialized with git."
        
        # Check for changes
        success, output = run_command(["git", "status", "--porcelain"], cwd=project_path)
        if not success:
            return False, f"Failed to check git status: {output}"
        
        # If no changes, return early
        if not output.strip():
            return True, "No changes to commit."
        
        # Stage all changes
        success, output = run_command(["git", "add", "."], cwd=project_path)
        if not success:
            return False, f"Failed to stage changes: {output}"
        
        # Commit changes
        success, output = run_command([
            "git", "commit", "-m", commit_message
        ], cwd=project_path)
        if not success:
            return False, f"Failed to commit changes: {output}"
        
        # Push changes to remote
        success, output = run_command(["git", "push"], cwd=project_path)
        if not success:
            return False, f"Failed to push changes: {output}"
        
        return True, f"Successfully committed and pushed changes with message: '{commit_message}'"
        
    except Exception as e:
        error_msg = f"Failed to commit and push changes: {str(e)}"
        logging.error(error_msg)
        return False, error_msg