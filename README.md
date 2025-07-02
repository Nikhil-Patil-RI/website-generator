# Website Generator MCP Server

A Model Context Protocol (MCP) server for automated website generation using GitHub repository setup, file creation, and deployment management.

## Overview

This MCP server provides comprehensive tools for AI agents to manage website projects:

### `repo_setup` Tool
Automates the process of creating a new website project by:
1. **Cloning a React Vite template repository directly to the base directory**
2. Removing the .git folder from the template
3. Creating a new GitHub repository
4. Pushing the code to the new repository
5. Optionally deploying to AWS Amplify (planned feature)

### `create_file` Tool
Creates new files with AI-generated content:
1. Creates files at specified paths with given content
2. Automatically creates directories if they don't exist
3. Handles various file types and content

### `push_changes` Tool
Manages git operations for project updates:
1. Checks for changes in the project
2. Stages all changes automatically
3. Commits with provided message
4. Pushes changes to remote repository

### File Handling Tools
Additional tools for file system operations:

#### `read_file_tool`
Reads the contents of any file in the project or system:
1. Reads file contents with proper encoding
2. Provides file statistics (lines, characters)
3. Handles various file types and formats

#### `list_files_tool`
Lists all files and directories in a specified directory:
1. Shows files and directories with clear prefixes
2. Provides organized directory listings
3. Handles empty directories gracefully

#### `update_file_tool`
Updates the contents of existing files:
1. Overwrites entire file content with new content
2. Validates file existence before updating
3. Provides detailed operation feedback

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

#### `push_changes`

Commit and push changes made to the project.

**Parameters:**
- `commit_message` (string, required): Message to use for the commit
- `project_name` (string, required): Name of the project (same as used in repo_setup)

**Example:**
```json
{
  "tool": "push_changes",
  "arguments": {
    "commit_message": "Add new HelloWorld component",
    "project_name": "my-awesome-website"
  }
}
```

**Returns:**
A status message indicating success or failure of the commit and push operation.

#### `read_file_tool`

Read the contents of any file in the project or system.

**Parameters:**
- `file_path` (string, required): Path to the file to read (can be relative or absolute)

**Example:**
```json
{
  "tool": "read_file_tool",
  "arguments": {
    "file_path": "./my-awesome-website/src/App.tsx"
  }
}
```

**Returns:**
File contents with metadata including character count and line count.

#### `list_files_tool`

List all files and directories in the specified directory.

**Parameters:**
- `directory_path` (string, required): Path to the directory to list (can be relative or absolute)

**Example:**
```json
{
  "tool": "list_files_tool",
  "arguments": {
    "directory_path": "./my-awesome-website/src"
  }
}
```

**Returns:**
Directory listing with files marked as [FILE] and directories as [DIR].

#### `update_file_tool`

Update the contents of an existing file.

**Parameters:**
- `file_path` (string, required): Path to the file to update (can be relative or absolute)
- `new_content` (string, required): New content to write to the file

**Example:**
```json
{
  "tool": "update_file_tool",
  "arguments": {
    "file_path": "./my-awesome-website/src/App.tsx",
    "new_content": "import React from 'react';\nimport HelloWorld from './components/HelloWorld';\n\nfunction App() {\n  return <HelloWorld />;\n}\n\nexport default App;"
  }
}
```

**Returns:**
A status message indicating success or failure of the file update operation.

## Configuration

### Environment Variables

- `GITHUB_TOKEN`: GitHub Personal Access Token with repository creation permissions

### Template Repository

The server uses `https://github.com/Jeetanshu18/react-vite` as the template repository. This can be modified in the `TEMPLATE_REPO` constant in `main.py`.

## Development

### Running Tests

```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run specific test files
uv run python -m pytest tests/test_main.py -v
uv run python -m pytest tests/test_file_handling.py -v
```

### Test Coverage

The test suite covers:
- MCP server initialization
- GitHub API requests
- Command execution
- Repository cloning
- GitHub repository creation
- Git operations
- File handling operations (read, list, update)
- Error handling and validation
- Edge cases and empty parameters

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
- **`utils/file_handling.py`**: File system operations and utilities
- **`tests/test_main.py`**: Comprehensive test suite for main functionality
- **`tests/test_file_handling.py`**: Test suite for file handling operations
- **`pyproject.toml`**: Project configuration and dependencies

### Key Components

#### Main Tools
- **`repo_setup()`**: Orchestrates repository creation with optimized workflow
- **`create_file()`**: Handles AI-driven file creation
- **`push_changes()`**: Manages git commit and push operations
- **`read_file_tool()`**: Reads file contents with metadata
- **`list_files_tool()`**: Lists directory contents with clear formatting
- **`update_file_tool()`**: Updates existing file contents

#### Utility Functions
- **`make_github_request()`**: Handles GitHub API communication
- **`create_github_repository()`**: Creates new GitHub repositories
- **`run_command()`**: Executes shell commands safely
- **`clone_template_to_base_directory()`**: Optimized template cloning to base directory
- **`clone_existing_repository()`**: Clones repositories preserving git history
- **`push_to_github()`**: Initializes git and pushes code
- **`create_file_in_project()`**: Creates files with directory handling
- **`commit_and_push_changes()`**: Handles git operations for commits
- **`read_file()`**: Reads file contents with error handling
- **`list_files()`**: Lists directory contents with type identification
- **`update_file()`**: Updates existing files with validation

## Implementation Details

### Complete Workflow Process

#### Repository Setup (`repo_setup`) - Optimized Workflow
1. **Validation**: Check for GitHub token and project name
2. **Clone Template**: Clone the React Vite template directly to the base directory
3. **Clean Template**: Remove .git folder from cloned template
4. **Create Repository**: Create new GitHub repository via API
5. **Initialize Git**: Set up git repository in project directory
6. **Push Code**: Push the code to the new GitHub repository
7. **Return Results**: Provide success message with repository details and local path

**Optimization Benefits:**
- Eliminates redundant cloning step
- Reduces temporary file usage
- Faster setup process
- Direct local development readiness

#### File Creation (`create_file`)
1. **Validation**: Check file name and path parameters
2. **Directory Creation**: Create directories if they don't exist
3. **File Writing**: Write content to the specified file
4. **Confirmation**: Return success status and file details

#### Change Management (`push_changes`)
1. **Project Location**: Construct project path from project name (`./{project_name}`)
2. **Directory Validation**: Verify the project directory exists
3. **Repository Check**: Verify the directory is a git repository
4. **Change Detection**: Check for uncommitted changes
5. **Staging**: Stage all changes automatically
6. **Commit**: Commit changes with provided message
7. **Push**: Push changes to remote repository
8. **Confirmation**: Return operation status

### Error Handling

- Comprehensive error checking at each step
- Detailed error messages for debugging
- Graceful failure handling
- Timeout protection for long-running operations

### Local Development Integration

The `repo_setup` tool uses an optimized workflow for immediate local development:

- **Direct Base Directory Setup**: Template is cloned directly to the current working directory
- **Optimized Workflow**: Eliminates redundant cloning steps for faster setup
- **Git Integration**: Full git history is established and connected to GitHub
- **Immediate Development**: Project is ready for development immediately after setup
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