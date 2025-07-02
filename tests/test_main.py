import pytest
import asyncio
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock, AsyncMock

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import mcp, repo_setup
from utils.github_api import make_github_request, create_github_repository
from utils.git_operations import run_command, clone_template_repository, push_to_github

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
    async def test_clone_template_repository_success(self):
        """Test successful template repository cloning."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("utils.git_operations.run_command") as mock_run:
                mock_run.side_effect = [
                    (True, "Cloning into 'test-project'..."),  # git clone
                ]
                
                with patch("os.path.exists", return_value=True):
                    with patch("shutil.rmtree") as mock_rmtree:
                        success, project_path = await clone_template_repository("test-project", temp_dir, "https://github.com/test/template.git")
                        
                        assert success is True
                        assert "test-project" in project_path
                        mock_rmtree.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_clone_template_repository_failure(self):
        """Test failed template repository cloning."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("utils.git_operations.run_command") as mock_run:
                mock_run.return_value = (False, "Repository not found")
                
                success, message = await clone_template_repository("test-project", temp_dir, "https://github.com/test/template.git")
                
                assert success is False
                assert "Failed to clone template repository" in message
    
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
            with patch("main.clone_template_repository") as mock_clone:
                with patch("main.create_github_repository") as mock_create:
                    with patch("main.push_to_github") as mock_push:
                        
                        mock_clone.return_value = (True, "/tmp/test-project")
                        mock_create.return_value = (True, "https://github.com/user/test-project.git")
                        mock_push.return_value = (True, "Successfully pushed to GitHub")
                        
                        result = await repo_setup("Test Project", "A test project")
                        
                        assert "Repository setup completed successfully!" in result
                        assert "test-project" in result
                        assert "https://github.com/user/test-project.git" in result
                        assert "✅ Cloned React Vite template repository" in result
                        assert "✅ Created new GitHub repository" in result
                        assert "✅ Pushed code to GitHub repository" in result
    
    @pytest.mark.asyncio
    async def test_repo_setup_with_amplify_deployment(self):
        """Test repo setup with Amplify deployment option."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch("main.clone_template_repository") as mock_clone:
                with patch("main.create_github_repository") as mock_create:
                    with patch("main.push_to_github") as mock_push:
                        
                        mock_clone.return_value = (True, "/tmp/test-project")
                        mock_create.return_value = (True, "https://github.com/user/test-project.git")
                        mock_push.return_value = (True, "Successfully pushed to GitHub")
                        
                        result = await repo_setup("test-project", deploy_to_amplify=True)
                        
                        assert "Repository setup completed successfully!" in result
                        assert "AWS Amplify deployment is not yet implemented" in result
    
    @pytest.mark.asyncio
    async def test_repo_setup_clone_failure(self):
        """Test repo setup fails at clone step."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch("main.clone_template_repository") as mock_clone:
                mock_clone.return_value = (False, "Clone failed")
                
                result = await repo_setup("test-project")
                
                assert "Failed at Step 1: Clone failed" in result
    
    @pytest.mark.asyncio
    async def test_repo_setup_create_repo_failure(self):
        """Test repo setup fails at GitHub repo creation step."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch("main.clone_template_repository") as mock_clone:
                with patch("main.create_github_repository") as mock_create:
                    
                    mock_clone.return_value = (True, "/tmp/test-project")
                    mock_create.return_value = (False, "Repo creation failed")
                    
                    result = await repo_setup("test-project")
                    
                    assert "Failed at Step 2: Repo creation failed" in result
    
    @pytest.mark.asyncio
    async def test_repo_setup_push_failure(self):
        """Test repo setup fails at push step."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch("main.clone_template_repository") as mock_clone:
                with patch("main.create_github_repository") as mock_create:
                    with patch("main.push_to_github") as mock_push:
                        
                        mock_clone.return_value = (True, "/tmp/test-project")
                        mock_create.return_value = (True, "https://github.com/user/test-project.git")
                        mock_push.return_value = (False, "Push failed")
                        
                        result = await repo_setup("test-project")
                        
                        assert "Failed at Step 3: Push failed" in result
    
    @pytest.mark.asyncio
    async def test_repo_setup_unexpected_error(self):
        """Test repo setup handles unexpected errors gracefully."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            with patch("main.clone_template_repository") as mock_clone:
                mock_clone.side_effect = Exception("Unexpected error")
                
                result = await repo_setup("test-project")
                
                assert "Repository setup failed due to unexpected error" in result
                assert "Unexpected error" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])