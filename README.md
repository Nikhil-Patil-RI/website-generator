# Website Generator MCP Server

A Model Context Protocol (MCP) server for automated website generation using GitHub repository setup, file creation, and deployment management.

## Overview

This MCP server provides comprehensive tools for AI agents to manage website projects:

### `repo_setup` Tool
Automates the process of creating a new website project by:
1. Cloning a React Vite template repository
2. Removing the .git folder from the template
3. Creating a new GitHub repository
4. Pushing the code to the new repository
5. **Cloning the repository to the base directory for local development**
6. Optionally deploying to AWS Amplify (planned feature)

### `create_file` Tool
Creates new files with AI-generated content:
1. Creates files at specified paths with given content
2. Automatically creates directories if they don't exist
3. Handles various file types and content

### `commit_changes` Tool
Manages git operations for project updates:
1. Checks for changes in the project
2. Stages all changes automatically
3. Commits with provided message
4. Pushes changes to remote repository

## Features

- **Complete Project Lifecycle**: From setup to deployment
- **Template-based Setup**: Uses a pre-configured React Vite template
- **GitHub Integration**: Automatically creates and pushes to GitHub repositories
- **Local Development**: Clones repositories to base directory for immediate development
- **File Management**: AI-driven file creation and content generation
- **Git Operations**: Automated commit and push functionality
- **Error Handling**: Comprehensive error handling and logging
- **Test Coverage**: Full test suite with pytest
- **MCP Compliant**: Follows Model Context Protocol standards

## Prerequisites

- Python 3.12+
- Git installed and configured
- GitHub Personal Access Token
- uv package manager

## Installation

1. Navigate to the website-generator directory:
```bash
cd website-generator
```

2. Install dependencies:
```bash
uv sync
```

3. Set up your GitHub token:
```bash
export GITHUB_TOKEN="your_github_personal_access_token"
```

## Usage

### Running the Server

```bash
uv run python main.py
```

The server will start and listen for MCP protocol messages via stdio.

### Available Tools

#### `repo_setup`

Setup a new repository for a website project and clone it locally.

**Parameters:**
- `project_name` (string, required): Name of the project and GitHub repository
- `description` (string, optional): Description for the GitHub repository
- `deploy_to_amplify` (boolean, optional): Whether to deploy to AWS Amplify (not yet implemented)

**Example:**
```json
{
  "tool": "repo_setup",
  "arguments": {
    "project_name": "my-awesome-website",
    "description": "A new website project",
    "deploy_to_amplify": false
  }
}
```

**Returns:**
A status message with repository URL, local clone path, and setup information.

#### `create_file`

Create a new file in the project with AI-generated content.

**Parameters:**
- `file_name` (string, required): Name of the file to create (e.g., "component.tsx", "styles.css")
- `file_path` (string, required): Directory path where the file should be created (e.g., "./src", "./public")
- `content` (string, required): Content to write to the file

**Example:**
```json
{
  "tool": "create_file",
  "arguments": {
    "file_name": "HelloWorld.tsx",
    "file_path": "./my-awesome-website/src/components",
    "content": "import React from 'react';\n\nconst HelloWorld = () => {\n  return <h1>Hello World!</h1>;\n};\n\nexport default HelloWorld;"
  }
}
```

**Returns:**
A status message indicating success or failure of file creation.

#### `commit_changes`

Commit and push changes made to the project.

**Parameters:**
- `commit_message` (string, required): Message to use for the commit
- `project_path` (string, optional): Path to the project directory (defaults to current directory)

**Example:**
```json
{
  "tool": "commit_changes",
  "arguments": {
    "commit_message": "Add new HelloWorld component",
    "project_path": "./my-awesome-website"
  }
}
```

**Returns:**
A status message indicating success or failure of the commit and push operation.

## Configuration

### Environment Variables

- `GITHUB_TOKEN`: GitHub Personal Access Token with repository creation permissions

### Template Repository

The server uses `https://github.com/Jeetanshu18/react-vite` as the template repository. This can be modified in the `TEMPLATE_REPO` constant in `main.py`.

## Development

### Running Tests

```bash
uv run python -m pytest test_main.py -v
```

### Test Coverage

The test suite covers:
- MCP server initialization
- GitHub API requests
- Command execution
- Repository cloning
- GitHub repository creation
- Git operations
- Error handling
- Edge cases

### Adding New Features

1. Write tests first (TDD approach)
2. Implement the feature
3. Ensure all tests pass
4. Update documentation

## Architecture

The server follows the FastMCP pattern and includes:

- **`main.py`**: Main MCP server implementation with all tools
- **`utils/github_api.py`**: GitHub API integration utilities
- **`utils/git_operations.py`**: Git operations and file management utilities
- **`tests/test_main.py`**: Comprehensive test suite
- **`pyproject.toml`**: Project configuration and dependencies

### Key Components

#### Main Tools
- **`repo_setup()`**: Orchestrates repository creation and local cloning
- **`create_file()`**: Handles AI-driven file creation
- **`commit_changes()`**: Manages git commit and push operations

#### Utility Functions
- **`make_github_request()`**: Handles GitHub API communication
- **`create_github_repository()`**: Creates new GitHub repositories
- **`run_command()`**: Executes shell commands safely
- **`clone_template_repository()`**: Clones and prepares templates
- **`clone_existing_repository()`**: Clones repositories preserving git history
- **`push_to_github()`**: Initializes git and pushes code
- **`create_file_in_project()`**: Creates files with directory handling
- **`commit_and_push_changes()`**: Handles git operations for commits

## Implementation Details

### Complete Workflow Process

#### Repository Setup (`repo_setup`)
1. **Validation**: Check for GitHub token and project name
2. **Clone Template**: Clone the React Vite template to a temporary directory
3. **Clean Template**: Remove .git folder from cloned template
4. **Create Repository**: Create new GitHub repository via API
5. **Initialize Git**: Set up git repository in project directory
6. **Push Code**: Push the code to the new GitHub repository
7. **Local Clone**: Clone the repository to the base directory for development
8. **Return Results**: Provide success message with repository details and local path

#### File Creation (`create_file`)
1. **Validation**: Check file name and path parameters
2. **Directory Creation**: Create directories if they don't exist
3. **File Writing**: Write content to the specified file
4. **Confirmation**: Return success status and file details

#### Change Management (`commit_changes`)
1. **Repository Check**: Verify the directory is a git repository
2. **Change Detection**: Check for uncommitted changes
3. **Staging**: Stage all changes automatically
4. **Commit**: Commit changes with provided message
5. **Push**: Push changes to remote repository
6. **Confirmation**: Return operation status

### Error Handling

- Comprehensive error checking at each step
- Detailed error messages for debugging
- Graceful failure handling
- Timeout protection for long-running operations

### Local Development Integration

The `repo_setup` tool automatically clones repositories to the base directory, enabling immediate local development:

- **Base Directory Cloning**: Projects are cloned directly to the current working directory
- **Git Integration**: Full git history is preserved for version control
- **Immediate Development**: No additional setup required after repository creation
- **Gitignore Management**: Cloned repositories are automatically excluded from version control

### Gitignore Configuration

The `.gitignore` file is configured to exclude common project patterns while preserving the core MCP server files:

```gitignore
# Cloned repositories (created by repo_setup tool)
*-website*/
*-app*/
*-project*/
test-*/
```

This ensures that:
- Cloned project directories are not committed to the MCP server repository
- Core utilities (`utils/`, `tests/`) remain tracked
- Development workflow is clean and organized

### Security

- GitHub token is checked at runtime, not stored
- Temporary directories are automatically cleaned up
- No sensitive information is logged
- Local repositories are excluded from version control

## Future Enhancements

- AWS Amplify deployment integration
- Support for multiple template repositories
- Custom deployment configurations
- Webhook setup for CI/CD
- Domain configuration support

## Troubleshooting

### Common Issues

1. **GitHub Token Missing**: Ensure `GITHUB_TOKEN` environment variable is set
2. **Git Not Found**: Install Git and ensure it's in your PATH
3. **Permission Denied**: Check GitHub token has repository creation permissions
4. **Network Issues**: Verify internet connection and GitHub API access
5. **Authentication Prompts**: The server automatically handles GitHub authentication using your token - no manual username/password input required

### Authentication Details

The server uses token-based authentication for GitHub operations:
- GitHub API calls use the token in Authorization headers
- Git push operations use the token embedded in the repository URL
- No interactive authentication prompts should appear during operation

### Debugging

Enable debug logging by setting the log level:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Implement the feature
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License.