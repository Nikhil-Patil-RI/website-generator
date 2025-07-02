# Website Generator MCP Server

A Model Context Protocol (MCP) server for automated website generation using GitHub repository setup and deployment.

## Overview

This MCP server provides a `repo_setup` tool that automates the process of creating a new website project by:

1. Cloning a React Vite template repository
2. Removing the .git folder from the template
3. Creating a new GitHub repository
4. Pushing the code to the new repository
5. Optionally deploying to AWS Amplify (planned feature)

## Features

- **Template-based Setup**: Uses a pre-configured React Vite template
- **GitHub Integration**: Automatically creates and pushes to GitHub repositories
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

Setup a new repository for a website project.

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
A status message with repository URL and setup information.

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

- **`main.py`**: Main MCP server implementation
- **`test_main.py`**: Comprehensive test suite
- **`pyproject.toml`**: Project configuration and dependencies

### Key Components

- **`_make_github_request()`**: Handles GitHub API communication
- **`_run_command()`**: Executes shell commands safely
- **`_clone_template_repository()`**: Clones and prepares template
- **`_create_github_repository()`**: Creates new GitHub repository
- **`_push_to_github()`**: Initializes git and pushes code
- **`repo_setup()`**: Main tool that orchestrates the entire process

## Implementation Details

### Step-by-Step Process

1. **Validation**: Check for GitHub token and project name
2. **Clone Template**: Clone the React Vite template to a temporary directory
3. **Clean Template**: Remove .git folder from cloned template
4. **Create Repository**: Create new GitHub repository via API
5. **Initialize Git**: Set up git repository in project directory
6. **Push Code**: Push the code to the new GitHub repository
7. **Return Results**: Provide success message with repository details

### Error Handling

- Comprehensive error checking at each step
- Detailed error messages for debugging
- Graceful failure handling
- Timeout protection for long-running operations

### Security

- GitHub token is checked at runtime, not stored
- Temporary directories are automatically cleaned up
- No sensitive information is logged

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