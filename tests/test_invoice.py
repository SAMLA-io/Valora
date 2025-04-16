import pytest
import json
import os
from unittest.mock import patch, MagicMock
from src.algorithms.invoice import generate_invoice_pdf

# Sample data for testing
SAMPLE_MATCHED_PRODUCTS_JSON = '''
{
    "productos": [
        {"nombre": "LAPTOP HP", "cantidad": "5", "costo": "$800.00"},
        {"nombre": "IMPRESORA EPSON", "cantidad": "3", "costo": "$200.00"},
        {"nombre": "MONITOR DELL", "cantidad": "2", "costo": "$300.00"}
    ]
}
'''

SAMPLE_MATCHED_PRODUCTS_DICT = {
    "productos": [
        {"nombre": "LAPTOP HP", "cantidad": "5", "costo": "$800.00"},
        {"nombre": "IMPRESORA EPSON", "cantidad": "3", "costo": "$200.00"},
        {"nombre": "MONITOR DELL", "cantidad": "2", "costo": "$300.00"}
    ]
}

# Test generate_invoice_pdf with JSON string input
@patch('src.algorithms.invoice.canvas.Canvas')
def test_generate_invoice_pdf_json_string(mock_canvas, tmp_path):
    # Setup
    output_file = tmp_path / "test_invoice.pdf"
    
    # Mock canvas methods
    mock_c = MagicMock()
    mock_canvas.return_value = mock_c
    
    # Mock drawImage to avoid file not found error
    with patch('src.algorithms.invoice.canvas.Canvas.drawImage'):
        # Call function
        generate_invoice_pdf(SAMPLE_MATCHED_PRODUCTS_JSON, str(output_file))
    
    # Assert
    mock_canvas.assert_called_once_with(str(output_file), pagesize=mock_canvas.letter)
    # Check that save was called
    mock_c.save.assert_called_once()

# Test generate_invoice_pdf with dictionary input
@patch('src.algorithms.invoice.canvas.Canvas')
def test_generate_invoice_pdf_dict(mock_canvas, tmp_path):
    # Setup
    output_file = tmp_path / "test_invoice.pdf"
    
    # Mock canvas methods
    mock_c = MagicMock()
    mock_canvas.return_value = mock_c
    
    # Mock drawImage to avoid file not found error
    with patch('src.algorithms.invoice.canvas.Canvas.drawImage'):
        # Call function
        generate_invoice_pdf(SAMPLE_MATCHED_PRODUCTS_DICT, str(output_file))
    
    # Assert
    mock_canvas.assert_called_once_with(str(output_file), pagesize=mock_canvas.letter)
    # Check that save was called
    mock_c.save.assert_called_once()

# Test generate_invoice_pdf with invalid JSON
def test_generate_invoice_pdf_invalid_json():
    # Setup
    invalid_json = "This is not a valid JSON string"
    
    # Assert that ValueError is raised
    with pytest.raises(ValueError):
        generate_invoice_pdf(invalid_json)

# Test generate_invoice_pdf with table too large
@patch('src.algorithms.invoice.canvas.Canvas')
def test_generate_invoice_pdf_table_too_large(mock_canvas, tmp_path):
    # Setup
    output_file = tmp_path / "test_invoice.pdf"
    
    # Create a large product list that would make the table too large
    large_products = {"productos": [{"nombre": f"Product {i}", "cantidad": "1", "costo": "$10.00"} for i in range(100)]}
    
    # Mock canvas methods
    mock_c = MagicMock()
    mock_canvas.return_value = mock_c
    
    # Mock drawImage to avoid file not found error
    with patch('src.algorithms.invoice.canvas.Canvas.drawImage'):
        # Assert that ValueError is raised
        with pytest.raises(ValueError):
            generate_invoice_pdf(large_products, str(output_file))

# Test generate_invoice_pdf with default output file
@patch('src.algorithms.invoice.canvas.Canvas')
def test_generate_invoice_pdf_default_output(mock_canvas):
    # Mock canvas methods
    mock_c = MagicMock()
    mock_canvas.return_value = mock_c
    
    # Mock drawImage to avoid file not found error
    with patch('src.algorithms.invoice.canvas.Canvas.drawImage'):
        # Call function with default output file
        generate_invoice_pdf(SAMPLE_MATCHED_PRODUCTS_DICT)
    
    # Assert
    mock_canvas.assert_called_once_with("orden_de_servicio.pdf", pagesize=mock_canvas.letter)
    # Check that save was called
    mock_c.save.assert_called_once()

if __name__ == '__main__':
    pytest.main([__file__]) 