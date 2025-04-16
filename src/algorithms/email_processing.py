# Written by Jocelyn Velarde
# 28 03 2025

"""
Email Processing Module

This module handles the processing of incoming emails containing product orders.
It extracts product information using OpenAI, matches products with costs from a database,
generates invoices as PDFs, and sends them back to the customer.

The module uses OpenAI's GPT models to extract and process product information from email bodies,
and matches this information with a database of products and their costs stored in a CSV file.
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
from src.api.gmail import connect_to_email, fetch_emails, get_body

# OpenAI API Functions
def extract_products_from_email(body):
    """
    Extract products and quantities from the email body using OpenAI.
    
    This function uses OpenAI's GPT model to parse the email body and extract
    product names and quantities. It returns a JSON string containing the extracted
    information in a standardized format.
    
    Args:
        body (str): The email body text containing product information.
        
    Returns:
        str: JSON string containing extracted products and quantities in the format:
             {"productos": [{"nombre": "PRODUCT_NAME", "cantidad": "QUANTITY"}]}
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Extrae los productos de la siguiente cotizacion en json, sin ningun texto adicional en el siguiente formato todo en mayusculas : {\"productos\": [{\"nombre\": \"nombre del producto\", \"cantidad\": \"cantidad del producto\"}]}"},
            {"role": "user", "content": body},
        ],
        stream=False
    )
    return response.choices[0].message.content

def extract_product_names(json_products):
    """
    Extract product names from the JSON response.
    
    This function uses OpenAI's GPT model to extract just the product names
    from a JSON string containing product information.
    
    Args:
        json_products (str): JSON string containing products and quantities.
        
    Returns:
        str: Extracted product names.
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Extrae el nombre de los productos"},
            {"role": "user", "content": json_products},
        ],
        stream=False
    )
    return response.choices[0].message.content

def match_products_with_costs(json_products, products_json_string):
    """
    Match products with costs using OpenAI.
    
    This function uses OpenAI's GPT model to match products extracted from an email
    with products from a database, even if the names are similar or incomplete.
    It adds cost information to the matched products.
    
    Args:
        json_products (str): JSON string containing products from email.
        products_json_string (str): JSON string containing products from database.
        
    Returns:
        str: JSON string containing matched products with costs in the format:
             {"productos": [{"nombre": "PRODUCT_NAME", "cantidad": "QUANTITY", "costo": "COST"}]}
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Se te dara una lista de productos, debes de encontrar los productos de la lista, pueden estar con nombres similares o incompletos, retornalo en el siguiente formato json sin hacer comentarios adicionales: {\"productos\": [{\"nombre\": \"nombre del producto\", \"cantidad\": \"cantidad del producto\", \"costo\": \"costo del producto\"}]"},
            {"role": "user", "content": f"Esta es la lista de productos: {json_products} y estos son los productos de la cotizacion: {products_json_string}"},
        ],
        stream=False
    )
    return response.choices[0].message.content

# CSV Handling Functions
def read_csv_columns(file_path, columns):
    """
    Read specific columns from a CSV file and return as a JSON string.
    
    This function reads a CSV file and extracts specific columns, converting them
    to a JSON string format for further processing.
    
    Args:
        file_path (str): Path to the CSV file.
        columns (list): List of column names to extract.
        
    Returns:
        str: JSON string containing the specified columns.
    """
    try:
        df = pd.read_csv(file_path, usecols=columns)
        products_json = df.to_dict(orient='records')
        return json.dumps(products_json, indent=4)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return ""

def send_email_with_pdf(sender, receiver, password, pdf_path, name):
    """
    Send an email with a PDF attachment.
    
    This function creates and sends an email with a PDF invoice attached.
    It uses SMTP to connect to Gmail and send the email.
    
    Args:
        sender (str): Sender's email address.
        receiver (str): Receiver's email address.
        password (str): Sender's email password.
        pdf_path (str): Path to the PDF file to attach.
        name (str): Receiver's name for personalization.
        
    Returns:
        None
    """
    body = 'Hello,' + name + 'here is the invoice you requested, if it does not meet requirements, please resend the email with the correct information again.'

    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = 'SAMLA - Invoice'

    message.attach(MIMEText(body, 'plain'))

    with open(pdf_path, 'rb') as binary_pdf:
        payload = MIMEBase('application', 'octate-stream', Name=pdf_path)
        payload.set_payload(binary_pdf.read())

    # Encode the binary into base64
    encoders.encode_base64(payload)

    # Add header with PDF name
    payload.add_header('Content-Disposition', 'attachment', filename=pdf_path)
    message.attach(payload)

    # Use Gmail with port
    session = smtplib.SMTP('smtp.gmail.com', 587)

    # Enable security
    session.starttls()

    # Login with email and password
    session.login(sender, password)

    # Send the email
    text = message.as_string()
    session.sendmail(sender, receiver, text)
    session.quit()
    print('Mail Sent')


# Process the latest email
def process_emails():
    """
    Process incoming emails containing product orders.
    
    This is the main function that:
    1. Connects to the email server
    2. Fetches emails with the subject "orden de pedido"
    3. Extracts product information from the email body
    4. Matches products with costs from the CSV file
    5. Generates an invoice PDF
    6. Sends the invoice back to the customer
    
    Returns:
        None
    """
    # Connect to email
    con = connect_to_email()
    if not con:
        return

    # Fetch emails
    msgs = fetch_emails(con, 'SUBJECT', 'orden de pedido')
    if not msgs:
        print("No emails found with 'orden de pedido'.")
        return

    for msg in msgs[0:1]:
        for sent in msg:
            if isinstance(sent, tuple):
                raw_email = sent[1]
                email_message = email.message_from_bytes(raw_email)
                raw_sender = email_message['From']
                name_sender, email_address_to = parseaddr(raw_sender)
                body = get_body(email_message)
                print("Email Body:", body)

                # Extract products and quantities
                json_products = extract_products_from_email(body)
                print("Extracted JSON Products:", json_products)

                # Extract product names
                product_names = extract_product_names(json_products)
                print("Product Names:", product_names)

                # Read product names and costs from CSV
                products_json_string = read_csv_columns(CSV_FILE_PATH, ['Nombre', 'Costo'])
                print("Products JSON String:", products_json_string)

                # Match products with costs
                matched_products = match_products_with_costs(json_products, products_json_string)
                print("Matched Products:", matched_products)

                # Generate invoice PDF
                output_file = "invoice.pdf"
                generate_invoice_pdf(matched_products, output_file=output_file)

                # Send email with PDF attachment
                sender_email = EMAIL_USER
                password = EMAIL_PASSWORD
                send_email_with_pdf(sender_email, email_address_to, password, output_file, name_sender)
                print("SENDER EMAIL:", email_address_to)
