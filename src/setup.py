# Written by Juan Pablo Gutiérrez
# 15 04 2025

"""
Configuration Module

This module handles the loading and management of environment variables and
configuration settings for the Valora application.

It uses python-dotenv to load sensitive information from a .env file,
including email credentials and API keys, and provides these values
to other modules in the application.
"""

import os
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Environment variables for sensitive data
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_URL = 'imap.gmail.com'
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CSV_FILE_PATH = 'products.csv'
CHECKING_INTERVAL = os.getenv("CHECKING_INTERVAL")