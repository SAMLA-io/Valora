# Written by Jocelyn Velarde
# 15 04 2025

"""
Gmail API Module

This module provides functions for interacting with Gmail via the IMAP protocol.
It handles email connection, searching, fetching, and body extraction.

The module uses Python's built-in imaplib and email libraries to connect to Gmail
servers, search for specific emails, and extract email content.
"""

import os
import time
import imaplib
import email
import pandas as pd
import json
import smtplib, ssl
from openai import OpenAI
from dotenv import load_dotenv
from invoice import generate_invoice_pdf
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import parseaddr

from src.setup import IMAP_URL, EMAIL_USER, EMAIL_PASSWORD, OPENAI_API_KEY, CSV_FILE_PATH

# Load environment variables
load_dotenv()

def connect_to_email():
    """
    Establish a connection to the email server.
    
    This function connects to the Gmail IMAP server using SSL and logs in
    with the provided credentials from environment variables.
    
    Returns:
        imaplib.IMAP4_SSL or None: Connection object if successful, None if connection fails.
    """
    try:
        con = imaplib.IMAP4_SSL(IMAP_URL)
        print("Connection established with GMAIL")
        con.login(EMAIL_USER, EMAIL_PASSWORD)
        print("Login successful")
        return con
    except Exception as e:
        print(f"Error connecting to email: {e}")
        return None

def get_body(msg):
    """
    Extract the plain text body from an email message.
    
    This function handles both multipart and single-part email messages,
    attempting to extract the plain text content. It handles different
    character encodings to ensure proper text extraction.
    
    Args:
        msg (email.message.Message): Email message object.
        
    Returns:
        str: Extracted email body text.
    """
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    return part.get_payload(decode=True).decode('utf-8')
                except UnicodeDecodeError:
                    return part.get_payload(decode=True).decode('latin-1', errors='ignore')
    else:
        try:
            return msg.get_payload(decode=True).decode('utf-8')
        except UnicodeDecodeError:
            return msg.get_payload(decode=True).decode('latin-1', errors='ignore')

def search_emails(con, key, value):
    """
    Search for emails based on a specific key and value.
    
    This function uses IMAP search criteria to find emails matching
    the specified key-value pair (e.g., subject, sender, etc.).
    
    Args:
        con (imaplib.IMAP4_SSL): Email connection object.
        key (str): Search key (e.g., 'SUBJECT', 'FROM').
        value (str): Search value to match.
        
    Returns:
        list: List of email IDs matching the search criteria.
    """
    result, data = con.search(None, key, f'"{value}"')
    return data

def fetch_emails(con, search_key, search_value):
    """
    Fetch emails matching the search criteria.
    
    This function searches for emails matching the specified criteria and
    fetches their full content. It selects the 'Inbox' folder, searches
    for matching emails, and retrieves their content.
    
    Args:
        con (imaplib.IMAP4_SSL): Email connection object.
        search_key (str): Search key (e.g., 'SUBJECT', 'FROM').
        search_value (str): Search value to match.
        
    Returns:
        list: List of email messages matching the search criteria.
    """
    try:
        con.select('Inbox')
        print("Fetching emails...")
        result_bytes = search_emails(con, search_key, search_value)
        msgs = []
        for num in result_bytes[0].split()[::-1]:
            typ, data = con.fetch(num, '(RFC822)')
            msgs.append(data)
        print("Fetching done")
        return msgs
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []

