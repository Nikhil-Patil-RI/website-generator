"""
Tests for file handling utilities.

This module contains tests for the file handling tools to ensure they work correctly.
"""

import os
import tempfile
import pytest
from utils.file_handling import read_file, list_files, update_file


class TestFileHandling:
    """Test class for file handling utilities."""

    @pytest.mark.asyncio
    async def test_read_file(self):
        """Test reading a file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test_read.txt")
            content = "Test content for reading"
            
            # Create file first
            with open(file_path, 'w') as f:
                f.write(content)
            
            success, read_content = await read_file(file_path)
            
            assert success is True
            assert read_content == content

    @pytest.mark.asyncio
    async def test_update_file(self):
        """Test updating an existing file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test_update.txt")
            original_content = "Original content"
            new_content = "Updated content"
            
            # Create file first
            with open(file_path, 'w') as f:
                f.write(original_content)
            
            success, message = await update_file(file_path, new_content)
            
            assert success is True
            assert "Successfully updated file" in message
            
            # Verify updated content
            with open(file_path, 'r') as f:
                assert f.read() == new_content

    @pytest.mark.asyncio
    async def test_list_files(self):
        """Test listing files in a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files and directories
            test_file = os.path.join(temp_dir, "test.txt")
            test_dir = os.path.join(temp_dir, "test_dir")
            
            with open(test_file, 'w') as f:
                f.write("test")
            os.makedirs(test_dir)
            
            success, items = await list_files(temp_dir)
            
            assert success is True
            assert isinstance(items, list)
            assert "[FILE] test.txt" in items
            assert "[DIR] test_dir" in items

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for invalid operations."""
        # Test reading non-existent file
        success, error = await read_file("non_existent_file.txt")
        assert success is False
        assert "does not exist" in error
        
        # Test updating non-existent file
        success, error = await update_file("non_existent_file.txt", "content")
        assert success is False
        assert "does not exist" in error

    @pytest.mark.asyncio
    async def test_empty_parameters(self):
        """Test handling of empty parameters."""
        # Test empty file path
        success, error = await read_file("")
        assert success is False
        assert "required and cannot be empty" in error
        
        success, error = await list_files("")
        assert success is False
        assert "required and cannot be empty" in error
        
        success, error = await update_file("", "content")
        assert success is False
        assert "required and cannot be empty" in error