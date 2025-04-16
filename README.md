# Valora

## Overview

Valora is an automated system that processes incoming emails containing product orders, extracts product information using AI, matches products with their costs from a database, generates invoices as PDFs, and sends them back to the customer. The system runs continuously, checking for new emails at regular intervals.

## Features

- **Email Monitoring**: Automatically checks for new emails with specific subject lines
- **AI-Powered Product Extraction**: Uses OpenAI's GPT models to extract product information from email bodies
- **Product Matching**: Matches extracted products with a database of products and their costs
- **Invoice Generation**: Creates professional PDF invoices with company branding
- **Automated Response**: Sends generated invoices back to customers via email

## System Architecture

The system is organized into the following components:

- **Email Processing Module**: Handles email retrieval, parsing, and response
- **AI Processing Module**: Extracts and processes product information using OpenAI
- **Invoice Generation Module**: Creates PDF invoices from processed data
- **Configuration Module**: Manages environment variables and settings

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/SAMLA-io/valora.git
   cd valora
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with the following variables:
   ```
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   OPENAI_API_KEY=your_openai_api_key
   ```

   Note: For Gmail, you'll need to use an App Password instead of your regular password. See [Google's documentation](https://support.google.com/accounts/answer/185833) for details.

4. Create a `products.csv` file with your product catalog in the following format:
   ```
   Nombre,Costo
   Product1,$10.00
   Product2,$20.00
   ```

5. Add your company logo as `bunker_logo.jpg` in the root directory.

## Usage

Run the application:

```
python src/app.py
```

The application will:
1. Check for new emails with the subject "orden de pedido"
2. Process the first email found
3. Extract product information using AI
4. Match products with costs from the CSV file
5. Generate an invoice PDF
6. Send the invoice back to the customer
7. Wait for 180 seconds before checking for new emails

## API Documentation

### Email Processing Module (`src/algorithms/email_processing.py`)

#### `extract_products_from_email(body)`
Extracts products and quantities from an email body using OpenAI.

**Parameters:**
- `body` (str): The email body text

**Returns:**
- `str`: JSON string containing extracted products and quantities

#### `extract_product_names(json_products)`
Extracts product names from a JSON response.

**Parameters:**
- `json_products` (str): JSON string containing products

**Returns:**
- `str`: Extracted product names

#### `match_products_with_costs(json_products, products_json_string)`
Matches products with their costs using OpenAI.

**Parameters:**
- `json_products` (str): JSON string containing products from email
- `products_json_string` (str): JSON string containing products from database

**Returns:**
- `str`: JSON string containing matched products with costs

#### `read_csv_columns(file_path, columns)`
Reads specific columns from a CSV file and returns as a JSON string.

**Parameters:**
- `file_path` (str): Path to the CSV file
- `columns` (list): List of column names to extract

**Returns:**
- `str`: JSON string containing the specified columns

#### `send_email_with_pdf(sender, receiver, password, pdf_path, name)`
Sends an email with a PDF attachment.

**Parameters:**
- `sender` (str): Sender's email address
- `receiver` (str): Receiver's email address
- `password` (str): Sender's email password
- `pdf_path` (str): Path to the PDF file
- `name` (str): Receiver's name

#### `process_emails()`
Main function that processes incoming emails, extracts products, generates invoices, and sends responses.

### Invoice Generation Module (`src/algorithms/invoice.py`)

#### `generate_invoice_pdf(matched_products, output_file="orden_de_servicio.pdf")`
Generates a PDF invoice from matched products.

**Parameters:**
- `matched_products` (str or dict): JSON string or dictionary containing matched products
- `output_file` (str): Path for the output PDF file

### Gmail API Module (`src/api/gmail.py`)

#### `connect_to_email()`
Establishes a connection to the email server.

**Returns:**
- `imaplib.IMAP4_SSL` or `None`: Connection object or None if connection fails

#### `get_body(msg)`
Extracts the plain text body from an email message.

**Parameters:**
- `msg` (email.message.Message): Email message object

**Returns:**
- `str`: Email body text

#### `search_emails(con, key, value)`
Searches for emails based on a specific key and value.

**Parameters:**
- `con` (imaplib.IMAP4_SSL): Email connection
- `key` (str): Search key (e.g., 'SUBJECT')
- `value` (str): Search value

**Returns:**
- `list`: List of email IDs matching the search criteria

#### `fetch_emails(con, search_key, search_value)`
Fetches emails matching the search criteria.

**Parameters:**
- `con` (imaplib.IMAP4_SSL): Email connection
- `search_key` (str): Search key (e.g., 'SUBJECT')
- `search_value` (str): Search value

**Returns:**
- `list`: List of email messages

## Configuration

The system uses the following environment variables:

- `EMAIL_USER`: Gmail address for sending/receiving emails
- `EMAIL_PASSWORD`: App password for Gmail authentication
- `OPENAI_API_KEY`: API key for OpenAI services
- `CSV_FILE_PATH`: Path to the products CSV file

## Dependencies

- Python 3.8+
- OpenAI API
- ReportLab (for PDF generation)
- Pandas (for CSV handling)
- Python-dotenv (for environment variables)

## License

This project is licensed under the terms included in the LICENSE file.

## Contributors

- [@JocelynVelarde](https://github.com/JocelynVelarde)
- [@jpgtzg](https://github.com/JuanPabloGutierrez)
