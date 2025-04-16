import pytest
import os
import pandas as pd
import json
import sys

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

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

# Create a temporary PDF file for testing
@pytest.fixture
def temp_pdf_file(tmp_path):
    pdf_file = tmp_path / "test_invoice.pdf"
    with open(pdf_file, 'wb') as f:
        f.write(b'PDF content')
    return pdf_file

# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("EMAIL_USER", "test@example.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "password")
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.setenv("CHECKING_INTERVAL", "180") 