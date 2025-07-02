import pytest
import asyncio
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock, AsyncMock

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import mcp, repo_setup, create_file, push_changes, generate_commit_message
from utils.github_api import make_github_request, create_github_repository
from utils.git_operations import run_command, push_to_github, create_file_in_project, commit_and_push_changes

class TestWebsiteGeneratorMCP:
    """Test suite for the website generator MCP server."""
    
    def test_mcp_server_initialization(self):
        """Test that the MCP server is properly initialized."""
        assert mcp.name == "website-generator"
        assert hasattr(mcp, 'tool')
    
    @pytest.mark.asyncio
    async def test_make_github_request_without_token(self):
        """Test GitHub API request fails without token."""
        with patch.dict(os.environ, {}, clear=True):
            result = await make_github_request("GET", "/user")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_make_github_request_success(self):
        """Test successful GitHub API request."""
        mock_response = {"login": "testuser"}
        
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch("httpx.AsyncClient") as mock_client:
                mock_response_obj = MagicMock()
                mock_response_obj.json.return_value = mock_response
                mock_response_obj.raise_for_status.return_value = None
                
                mock_client.return_value.__aenter__.return_value.get.return_value = mock_response_obj
                
                result = await make_github_request("GET", "/user")
                assert result == mock_response
    
    def test_run_command_success(self):
        """Test successful command execution."""
        success, output = run_command(["echo", "test"])
        assert success is True
        assert "test" in output
    
    def test_run_command_failure(self):
        """Test failed command execution."""
        success, output = run_command(["nonexistent_command"])
        assert success is False
        assert output  # Should contain error message
    
    @pytest.mark.asyncio
    async def test_create_github_repository_success(self):
        """Test successful GitHub repository creation."""
        mock_response = {
            "name": "test-project",
            "clone_url": "https://github.com/user/test-project.git"
        }
        
        with patch("utils.github_api.make_github_request", return_value=mock_response):
            success, repo_url = await create_github_repository("test-project", "Test description")
            
            assert success is True
            assert repo_url == "https://github.com/user/test-project.git"
    
    @pytest.mark.asyncio
    async def test_create_github_repository_failure(self):
        """Test failed GitHub repository creation."""
        with patch("utils.github_api.make_github_request", return_value=None):
            success, message = await create_github_repository("test-project")
            
            assert success is False
            assert "Failed to create GitHub repository" in message
    
    @pytest.mark.asyncio
    async def test_push_to_github_success(self):
        """Test successful push to GitHub."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = os.path.join(temp_dir, "test-project")
            os.makedirs(project_path)
            
            with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
                with patch("utils.git_operations.run_command") as mock_run:
                    mock_run.return_value = (True, "Success")
                    
                    success, message = await push_to_github(
                        project_path,
                        "https://github.com/user/test-project.git",
                        "test-project"
                    )
                    
                    assert success is True
                    assert "Successfully pushed to GitHub" in message
    
    @pytest.mark.asyncio
    async def test_push_to_github_failure(self):
        """Test failed push to GitHub."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = os.path.join(temp_dir, "test-project")
            os.makedirs(project_path)
            
            with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
                with patch("utils.git_operations.run_command") as mock_run:
                    mock_run.return_value = (False, "Git command failed")
                    
                    success, message = await push_to_github(
                        project_path,
                        "https://github.com/user/test-project.git",
                        "test-project"
                    )
                    
                    assert success is False
                    assert "Failed to initialize git repository" in message
    
    @pytest.mark.asyncio
    async def test_push_to_github_without_token(self):
        """Test push to GitHub fails without token."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = os.path.join(temp_dir, "test-project")
            os.makedirs(project_path)
            
            with patch.dict(os.environ, {}, clear=True):
                success, message = await push_to_github(
                    project_path,
                    "https://github.com/user/test-project.git",
                    "test-project"
                )
                
                assert success is False
                assert "GitHub token is required" in message
    
    @pytest.mark.asyncio
    async def test_repo_setup_without_github_token(self):
        """Test repo_setup fails without GitHub token."""
        with patch.dict(os.environ, {}, clear=True):
            result = await repo_setup("test-project")
            assert "GitHub Token is missing" in result
    
    @pytest.mark.asyncio
    async def test_repo_setup_empty_project_name(self):
        """Test repo_setup fails with empty project name."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            result = await repo_setup("")
            assert "Project name is required" in result
            
            result = await repo_setup("   ")
            assert "Project name is required" in result
    
    @pytest.mark.asyncio
    async def test_repo_setup_success(self):
        """Test successful complete repo setup."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch("main.clone_template_to_base_directory") as mock_clone:
                with patch("main.create_github_repository") as mock_create:
                    with patch("main.push_to_github") as mock_push:
                        
                        mock_clone.return_value = (True, "./test-project")
                        mock_create.return_value = (True, "https://github.com/user/test-project.git")
                        mock_push.return_value = (True, "Successfully pushed to GitHub")
                        
                        result = await repo_setup("Test Project", "A test project")
                        
                        assert "Repository setup completed successfully!" in result
                        assert "test-project" in result
                        assert "https://github.com/user/test-project" in result
                        assert "✅ Cloned React Vite template repository to base directory" in result
                        assert "✅ Created new GitHub repository" in result
                        assert "✅ Pushed code to GitHub repository" in result
    
    @pytest.mark.asyncio
    async def test_repo_setup_with_amplify_deployment(self):
        """Test repo setup with Amplify deployment option."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch("main.clone_template_to_base_directory") as mock_clone:
                with patch("main.create_github_repository") as mock_create:
                    with patch("main.push_to_github") as mock_push:
                        
                        mock_clone.return_value = (True, "./test-project")
                        mock_create.return_value = (True, "https://github.com/user/test-project.git")
                        mock_push.return_value = (True, "Successfully pushed to GitHub")
                        
                        result = await repo_setup("test-project", deploy_to_amplify=True)
                        
                        assert "Repository setup completed successfully!" in result
                        assert "AWS Amplify deployment is not yet implemented" in result
    
    @pytest.mark.asyncio
    async def test_repo_setup_clone_failure(self):
        """Test repo setup fails at clone step."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch("main.clone_template_to_base_directory") as mock_clone:
                mock_clone.return_value = (False, "Clone failed")
                
                result = await repo_setup("test-project")
                
                assert "Failed at Step 1: Clone failed" in result
    
    @pytest.mark.asyncio
    async def test_repo_setup_create_repo_failure(self):
        """Test repo setup fails at GitHub repo creation step."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch("main.clone_template_to_base_directory") as mock_clone:
                with patch("main.create_github_repository") as mock_create:
                    
                    mock_clone.return_value = (True, "./test-project")
                    mock_create.return_value = (False, "Repo creation failed")
                    
                    result = await repo_setup("test-project")
                    
                    assert "Failed at Step 2: Repo creation failed" in result
    
    @pytest.mark.asyncio
    async def test_repo_setup_push_failure(self):
        """Test repo setup fails at push step."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch("main.clone_template_to_base_directory") as mock_clone:
                with patch("main.create_github_repository") as mock_create:
                    with patch("main.push_to_github") as mock_push:
                        
                        mock_clone.return_value = (True, "./test-project")
                        mock_create.return_value = (True, "https://github.com/user/test-project.git")
                        mock_push.return_value = (False, "Push failed")
                        
                        result = await repo_setup("test-project")
                        
                        assert "Failed at Step 3: Push failed" in result
    
    @pytest.mark.asyncio
    async def test_repo_setup_unexpected_error(self):
        """Test repo setup handles unexpected errors gracefully."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch("main.clone_template_to_base_directory") as mock_clone:
                mock_clone.side_effect = Exception("Unexpected error")
                
                result = await repo_setup("test-project")
                
                assert "Repository setup failed due to unexpected error" in result
                assert "Unexpected error" in result
    
    @pytest.mark.asyncio
    async def test_create_file_success(self):
        """Test successful file creation."""
        with patch("main.create_file_in_project") as mock_create:
            mock_create.return_value = (True, "File created successfully")
            
            result = await create_file("test.txt", "./src", "Hello World")
            
            assert "File created successfully!" in result
            assert "test.txt" in result
            assert "./src" in result
            mock_create.assert_called_once_with("./src", "test.txt", "Hello World")
    
    @pytest.mark.asyncio
    async def test_create_file_empty_filename(self):
        """Test create_file fails with empty filename."""
        result = await create_file("", "./src", "content")
        assert "File name is required and cannot be empty" in result
        
        result = await create_file("   ", "./src", "content")
        assert "File name is required and cannot be empty" in result
    
    @pytest.mark.asyncio
    async def test_create_file_empty_filepath(self):
        """Test create_file fails with empty filepath."""
        result = await create_file("test.txt", "", "content")
        assert "File path is required and cannot be empty" in result
        
        result = await create_file("test.txt", "   ", "content")
        assert "File path is required and cannot be empty" in result
    
    @pytest.mark.asyncio
    async def test_create_file_with_empty_content(self):
        """Test create_file works with empty content."""
        with patch("main.create_file_in_project") as mock_create:
            mock_create.return_value = (True, "File created successfully")
            
            result = await create_file("test.txt", "./src", "")
            
            assert "File created successfully!" in result
            mock_create.assert_called_once_with("./src", "test.txt", "")
    
    @pytest.mark.asyncio
    async def test_create_file_failure(self):
        """Test create_file handles creation failure."""
        with patch("main.create_file_in_project") as mock_create:
            mock_create.return_value = (False, "Permission denied")
            
            result = await create_file("test.txt", "./src", "content")
            
            assert "Failed to create file: Permission denied" in result
    
    @pytest.mark.asyncio
    async def test_create_file_unexpected_error(self):
        """Test create_file handles unexpected errors."""
        with patch("main.create_file_in_project") as mock_create:
            mock_create.side_effect = Exception("Unexpected error")
            
            result = await create_file("test.txt", "./src", "content")
            
            assert "File creation failed due to unexpected error" in result
            assert "Unexpected error" in result
    
    @pytest.mark.asyncio
    async def test_push_changes_success(self):
        """Test successful commit and push."""
        with patch("os.path.exists") as mock_exists:
            with patch("main.commit_and_push_changes") as mock_commit:
                with patch("main.generate_commit_message") as mock_generate:
                    mock_exists.return_value = True
                    mock_commit.return_value = (True, "Successfully committed and pushed changes")
                    mock_generate.return_value = "Auto-commit: Update project files - 2025-01-02 23:05:00"
                    
                    result = await push_changes("project")
                    
                    assert "Changes committed and pushed successfully!" in result
                    assert "Auto-Generated Commit Message:" in result
                    assert "./project" in result
                    mock_commit.assert_called_once_with("./project", "Auto-commit: Update project files - 2025-01-02 23:05:00")
    
    @pytest.mark.asyncio
    async def test_push_changes_no_changes(self):
        """Test push when there are no changes."""
        with patch("os.path.exists") as mock_exists:
            with patch("main.commit_and_push_changes") as mock_commit:
                with patch("main.generate_commit_message") as mock_generate:
                    mock_exists.return_value = True
                    mock_commit.return_value = (True, "No changes to commit.")
                    mock_generate.return_value = "Auto-commit: Update project files - 2025-01-02 23:05:00"
                    
                    result = await push_changes("project")
                    
                    assert "No changes detected in the project" in result
                    assert "The project is already up to date" in result
    
    @pytest.mark.asyncio
    async def test_push_changes_empty_project_name(self):
        """Test push_changes fails with empty project name."""
        result = await push_changes("")
        assert "Project name is required and cannot be empty" in result
        
        result = await push_changes("   ")
        assert "Project name is required and cannot be empty" in result
    
    @pytest.mark.asyncio
    async def test_push_changes_failure(self):
        """Test push_changes handles commit failure."""
        with patch("os.path.exists") as mock_exists:
            with patch("main.commit_and_push_changes") as mock_commit:
                with patch("main.generate_commit_message") as mock_generate:
                    mock_exists.return_value = True
                    mock_commit.return_value = (False, "Git push failed")
                    mock_generate.return_value = "Auto-commit: Update project files - 2025-01-02 23:05:00"
                    
                    result = await push_changes("project")
                    
                    assert "Failed to push changes: Git push failed" in result
    
    @pytest.mark.asyncio
    async def test_push_changes_unexpected_error(self):
        """Test push_changes handles unexpected errors."""
        with patch("os.path.exists") as mock_exists:
            with patch("main.commit_and_push_changes") as mock_commit:
                with patch("main.generate_commit_message") as mock_generate:
                    mock_exists.return_value = True
                    mock_commit.side_effect = Exception("Unexpected error")
                    mock_generate.return_value = "Auto-commit: Update project files - 2025-01-02 23:05:00"
                    
                    result = await push_changes("project")
                    
                    assert "Push operation failed due to unexpected error" in result
                    assert "Unexpected error" in result
    
    def test_generate_commit_message(self):
        """Test that generate_commit_message creates a proper commit message."""
        message = generate_commit_message()
        
        assert "Auto-commit: Update project files -" in message
        assert len(message) > 30  # Should be a reasonable length
        
        # Test that two calls generate different messages (due to timestamp)
        import time
        time.sleep(1)  # Wait 1 second
        message2 = generate_commit_message()
        assert message != message2  # Should be different due to timestamp
    
    @pytest.mark.asyncio
    async def test_create_file_in_project_success(self):
        """Test successful file creation in project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            success, message = await create_file_in_project(temp_dir, "test.txt", "Hello World")
            
            assert success is True
            assert "created successfully" in message
            
            # Verify file was actually created
            file_path = os.path.join(temp_dir, "test.txt")
            assert os.path.exists(file_path)
            
            with open(file_path, 'r') as f:
                content = f.read()
            assert content == "Hello World"
    
    @pytest.mark.asyncio
    async def test_create_file_in_project_creates_directory(self):
        """Test that create_file_in_project creates directories if they don't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = os.path.join(temp_dir, "src", "components")
            
            success, message = await create_file_in_project(nested_path, "Component.js", "export default Component;")
            
            assert success is True
            assert os.path.exists(nested_path)
            assert os.path.exists(os.path.join(nested_path, "Component.js"))
    
    @pytest.mark.asyncio
    async def test_commit_and_push_changes_no_git_repo(self):
        """Test commit_and_push_changes fails when not in a git repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            success, message = await commit_and_push_changes(temp_dir, "Test commit")
            
            assert success is False
            assert "Not a git repository" in message

if __name__ == "__main__":
    pytest.main([__file__, "-v"])