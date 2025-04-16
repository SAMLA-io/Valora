# Written by Juan Pablo Gutiérrez
# 15 04 2025

"""
Main Application Module

This module serves as the entry point for the Valora application.
It runs a continuous loop that processes incoming emails at regular intervals.

The application checks for new emails containing product orders, processes them,
and sends back invoices automatically without requiring manual intervention.
"""

import time
from src.algorithms.email_processing import process_emails
from src.setup import CHECKING_INTERVAL

def main():
    """
    Main application function.
    
    This function runs an infinite loop that:
    1. Processes any incoming emails with product orders
    2. Waits for a specified interval (180 seconds)
    3. Repeats the process
    
    The function uses the process_emails() function from the email_processing
    module to handle the email processing workflow.
    
    Returns:
        None
    """
    while True:
        process_emails()
        print("Waiting for 180 seconds before checking for new emails...")
        time.sleep(CHECKING_INTERVAL)  

if __name__ == "__main__":
    main()