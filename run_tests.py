#!/usr/bin/env python
"""
Test Runner Script

This script runs all tests in the tests directory using pytest.
It provides a convenient way to run tests with various options.
"""

import os
import sys
import pytest

def main():
    """
    Run all tests in the tests directory.
    
    This function runs pytest with the following options:
    - Verbose output
    - Short traceback format
    - Coverage report
    """
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the script directory
    os.chdir(script_dir)
    
    # Run pytest with options
    args = [
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--cov=src",  # Coverage for src directory
        "--cov-report=term",  # Terminal coverage report
        "tests"  # Test directory
    ]
    
    # Add any command line arguments
    args.extend(sys.argv[1:])
    
    # Run pytest
    return pytest.main(args)

if __name__ == "__main__":
    sys.exit(main()) 