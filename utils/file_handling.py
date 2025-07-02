"""
File handling utilities for the website generator MCP server.

This module provides tools for reading, writing, listing, and updating files
that can be used by the MCP server to interact with the file system.
"""

import os
import logging
from typing import Tuple, List, Optional


async def read_file(file_path: str) -> Tuple[bool, str]:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file to read

    Returns:
        Tuple of (success: bool, content_or_error: str)
    """
    try:
        if not file_path or not file_path.strip():
            return False, "File path is required and cannot be empty."

        file_path = file_path.strip()

        if not os.path.exists(file_path):
            return False, f"File '{file_path}' does not exist."

        if not os.path.isfile(file_path):
            return False, f"Path '{file_path}' is not a file."

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        logging.info(f"Successfully read file: {file_path}")
        return True, content

    except PermissionError:
        error_msg = f"Permission denied when reading file: {file_path}"
        logging.error(error_msg)
        return False, error_msg
    except UnicodeDecodeError:
        error_msg = f"Unable to decode file as UTF-8: {file_path}"
        logging.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error reading file '{file_path}': {str(e)}"
        logging.error(error_msg)
        return False, error_msg


async def list_files(directory_path: str) -> Tuple[bool, List[str]]:
    """
    List all files and directories in the specified directory.

    Args:
        directory_path: Path to the directory to list

    Returns:
        Tuple of (success: bool, files_list_or_error: List[str] or str)
    """
    try:
        if not directory_path or not directory_path.strip():
            return False, "Directory path is required and cannot be empty."

        directory_path = directory_path.strip()

        if not os.path.exists(directory_path):
            return False, f"Directory '{directory_path}' does not exist."

        if not os.path.isdir(directory_path):
            return False, f"Path '{directory_path}' is not a directory."

        items = []
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path):
                items.append(f"[DIR] {item}")
            else:
                items.append(f"[FILE] {item}")

        items.sort()  # Sort alphabetically

        logging.info(f"Successfully listed directory: {directory_path}")
        return True, items

    except PermissionError:
        error_msg = f"Permission denied when listing directory: {directory_path}"
        logging.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error listing directory '{directory_path}': {str(e)}"
        logging.error(error_msg)
        return False, error_msg


async def update_file(file_path: str, new_content: str) -> Tuple[bool, str]:
    """
    Update the contents of an existing file.

    Args:
        file_path: Path to the file to update
        new_content: New content to write to the file

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        if not file_path or not file_path.strip():
            return False, "File path is required and cannot be empty."

        file_path = file_path.strip()

        if not os.path.exists(file_path):
            return (
                False,
                f"File '{file_path}' does not exist. Use new_file to create a new file.",
            )

        if not os.path.isfile(file_path):
            return False, f"Path '{file_path}' is not a file."

        # Create backup of original content
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                original_content = file.read()
        except Exception:
            original_content = None

        # Write new content
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(new_content)

        success_msg = f"Successfully updated file: {file_path}"
        logging.info(success_msg)
        return True, success_msg

    except PermissionError:
        error_msg = f"Permission denied when updating file: {file_path}"
        logging.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error updating file '{file_path}': {str(e)}"
        logging.error(error_msg)
        return False, error_msg
