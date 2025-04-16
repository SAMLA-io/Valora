import pytest
import json
import os
import pandas as pd
from unittest.mock import patch, MagicMock
from src.algorithms.email_processing import (
    extract_products_from_email,
    extract_product_names,
    match_products_with_costs,
    read_csv_columns,
    send_email_with_pdf,
    process_emails
)

# Sample data for testing
SAMPLE_EMAIL_BODY = """
Hola, necesito cotizar los siguientes productos:
- 5 laptops HP
- 3 impresoras Epson
- 2 monitores Dell
Gracias.
"""

SAMPLE_JSON_PRODUCTS = '''
{
    "productos": [
        {"nombre": "LAPTOP HP", "cantidad": "5"},
        {"nombre": "IMPRESORA EPSON", "cantidad": "3"},
        {"nombre": "MONITOR DELL", "cantidad": "2"}
    ]
}
'''

SAMPLE_PRODUCT_NAMES = "LAPTOP HP, IMPRESORA EPSON, MONITOR DELL"

SAMPLE_PRODUCTS_JSON_STRING = '''
[
    {"Nombre": "LAPTOP HP", "Costo": "$800.00"},
    {"Nombre": "IMPRESORA EPSON", "Costo": "$200.00"},
    {"Nombre": "MONITOR DELL", "Costo": "$300.00"}
]
'''

SAMPLE_MATCHED_PRODUCTS = '''
{
    "productos": [
        {"nombre": "LAPTOP HP", "cantidad": "5", "costo": "$800.00"},
        {"nombre": "IMPRESORA EPSON", "cantidad": "3", "costo": "$200.00"},
        {"nombre": "MONITOR DELL", "cantidad": "2", "costo": "$300.00"}
    ]
}
'''

# Create a temporary CSV file for testing
@pytest.fixture
def temp_csv_file(tmp_path):
    csv_file = tmp_path / "test_products.csv"
    df = pd.DataFrame({
        'Nombre': ['LAPTOP HP', 'IMPRESORA EPSON', 'MONITOR DELL'],
        'Costo': ['$800.00', '$200.00', '$300.00']
    })
    df.to_csv(csv_file, index=False)
    return csv_file

# Test extract_products_from_email
@patch('src.algorithms.email_processing.OpenAI')
def test_extract_products_from_email(mock_openai):
    # Setup mock
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = SAMPLE_JSON_PRODUCTS
    mock_client.chat.completions.create.return_value = mock_response
    
    # Call function
    result = extract_products_from_email(SAMPLE_EMAIL_BODY)
    
    # Assert
    assert result == SAMPLE_JSON_PRODUCTS
    mock_client.chat.completions.create.assert_called_once()

# Test extract_product_names
@patch('src.algorithms.email_processing.OpenAI')
def test_extract_product_names(mock_openai):
    # Setup mock
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = SAMPLE_PRODUCT_NAMES
    mock_client.chat.completions.create.return_value = mock_response
    
    # Call function
    result = extract_product_names(SAMPLE_JSON_PRODUCTS)
    
    # Assert
    assert result == SAMPLE_PRODUCT_NAMES
    mock_client.chat.completions.create.assert_called_once()

# Test match_products_with_costs
@patch('src.algorithms.email_processing.OpenAI')
def test_match_products_with_costs(mock_openai):
    # Setup mock
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = SAMPLE_MATCHED_PRODUCTS
    mock_client.chat.completions.create.return_value = mock_response
    
    # Call function
    result = match_products_with_costs(SAMPLE_JSON_PRODUCTS, SAMPLE_PRODUCTS_JSON_STRING)
    
    # Assert
    assert result == SAMPLE_MATCHED_PRODUCTS
    mock_client.chat.completions.create.assert_called_once()

# Test read_csv_columns
def test_read_csv_columns(temp_csv_file):
    # Call function
    result = read_csv_columns(temp_csv_file, ['Nombre', 'Costo'])
    
    # Assert
    assert isinstance(result, str)
    data = json.loads(result)
    assert len(data) == 3
    assert data[0]['Nombre'] == 'LAPTOP HP'
    assert data[0]['Costo'] == '$800.00'

# Test send_email_with_pdf
@patch('src.algorithms.email_processing.smtplib.SMTP')
def test_send_email_with_pdf(mock_smtp, tmp_path):
    # Create a temporary PDF file
    pdf_file = tmp_path / "test_invoice.pdf"
    with open(pdf_file, 'wb') as f:
        f.write(b'PDF content')
    
    # Setup mock
    mock_session = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_session
    
    # Call function
    send_email_with_pdf(
        sender="test@example.com",
        receiver="customer@example.com",
        password="password",
        pdf_path=str(pdf_file),
        name="John Doe"
    )
    
    # Assert
    mock_session.starttls.assert_called_once()
    mock_session.login.assert_called_once_with("test@example.com", "password")
    mock_session.sendmail.assert_called_once()

# Test process_emails
@patch('src.algorithms.email_processing.connect_to_email')
@patch('src.algorithms.email_processing.fetch_emails')
@patch('src.algorithms.email_processing.extract_products_from_email')
@patch('src.algorithms.email_processing.extract_product_names')
@patch('src.algorithms.email_processing.read_csv_columns')
@patch('src.algorithms.email_processing.match_products_with_costs')
@patch('src.algorithms.email_processing.generate_invoice_pdf')
@patch('src.algorithms.email_processing.send_email_with_pdf')
def test_process_emails(
    mock_send_email, mock_generate_invoice, mock_match_products,
    mock_read_csv, mock_extract_names, mock_extract_products,
    mock_fetch_emails, mock_connect
):
    # Setup mocks
    mock_connect.return_value = MagicMock()
    mock_fetch_emails.return_value = [[(b'', b'email content')]]
    mock_extract_products.return_value = SAMPLE_JSON_PRODUCTS
    mock_extract_names.return_value = SAMPLE_PRODUCT_NAMES
    mock_read_csv.return_value = SAMPLE_PRODUCTS_JSON_STRING
    mock_match_products.return_value = SAMPLE_MATCHED_PRODUCTS
    
    # Mock email message
    mock_email_message = MagicMock()
    mock_email_message.__getitem__.return_value = "John Doe <john@example.com>"
    mock_email_message.is_multipart.return_value = False
    mock_email_message.get_payload.return_value = SAMPLE_EMAIL_BODY
    
    # Mock email parsing
    with patch('src.algorithms.email_processing.email.message_from_bytes', return_value=mock_email_message):
        with patch('src.algorithms.email_processing.parseaddr', return_value=("John Doe", "john@example.com")):
            with patch('src.algorithms.email_processing.get_body', return_value=SAMPLE_EMAIL_BODY):
                # Call function
                process_emails()
    
    # Assert
    mock_connect.assert_called_once()
    mock_fetch_emails.assert_called_once()
    mock_extract_products.assert_called_once()
    mock_extract_names.assert_called_once()
    mock_read_csv.assert_called_once()
    mock_match_products.assert_called_once()
    mock_generate_invoice.assert_called_once()
    mock_send_email.assert_called_once()

if __name__ == '__main__':
    pytest.main([__file__]) 