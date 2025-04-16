# Written by Jocelyn Velarde
# 28 03 2025

"""
Invoice Generation Module

This module handles the generation of PDF invoices from product data.
It creates professional-looking invoices with company branding, product details,
and cost calculations including subtotal, tax, and total amounts.

The module uses ReportLab to generate PDF documents with proper formatting,
tables, and styling to create a professional invoice document.
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import json

def generate_invoice_pdf(matched_products, output_file="orden_de_servicio.pdf"):
    """
    Generate a PDF invoice from matched products.
    
    This function creates a professional PDF invoice with the following sections:
    - Company logo
    - Invoice title and header
    - Customer information
    - Company information
    - Product table with details (name, quantity, price, total)
    - Cost summary (subtotal, tax, total)
    
    Args:
        matched_products (str or dict): JSON string or dictionary containing matched products
                                      with names, quantities, and costs.
        output_file (str): Path for the output PDF file.
        
    Returns:
        None
        
    Raises:
        ValueError: If matched_products is not a valid JSON string or if the table
                   is too large to fit on one page.
    """
    if isinstance(matched_products, str):
        matched_products = matched_products.strip("```json")
        try:
            matched_products = json.loads(matched_products)  
        except json.JSONDecodeError:
            raise ValueError("matched_products is not a valid JSON string")
    productos = matched_products.get("productos", [])

    # Create a canvas for the PDF
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter

    # Add an image at the top right
    image_path = "bunker_logo.jpg" 
    image_width = 100 
    image_height = 50 
    c.drawImage(image_path, width - image_width - 20, height - image_height - 20, 
                width=image_width, height=image_height, preserveAspectRatio=True, mask='auto')


    # Add title and header
    title_y_position = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, title_y_position, "Orden de Servicio")
    c.setFont("Helvetica", 12)
    c.drawString(50, title_y_position - 30, "Nombre de la empresa")

    # Add "Issued To" section
    issued_to_y_position = title_y_position - 60
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, issued_to_y_position, "Issued To:")
    c.setFont("Helvetica", 12)
    c.drawString(50, issued_to_y_position - 20, "Nombre del Cliente: John Doe")
    c.drawString(50, issued_to_y_position - 40, "Dirección: 123 Main Street")
    c.drawString(50, issued_to_y_position - 60, "Teléfono: +1 234 567 890")

    # Add "Pay To" section
    pay_to_y_position = issued_to_y_position - 100
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, pay_to_y_position, "Pay To:")
    c.setFont("Helvetica", 12)
    c.drawString(50, pay_to_y_position - 20, "Nombre de la Empresa: Bunker Inc.")
    c.drawString(50, pay_to_y_position - 40, "Dirección: 456 Business Road")
    c.drawString(50, pay_to_y_position - 60, "Teléfono: +1 987 654 321")

    table_y_position = (height / 2) - 50

    # Prepare table data
    table_data = [["Producto", "Cantidad", "Precio", "Total"]] 
    for product in productos:
        nombre = product.get("nombre", "")
        cantidad = product.get("cantidad", 0)
        costo = product.get("costo", "0").replace("$", "")
        try:
            cantidad = int(cantidad)
        except ValueError:
            cantidad = 1  
        try:
            costo = float(costo)
        except ValueError:
            costo = 1.0 
        costo = float(costo)
        cantidad = int(cantidad)
        total = cantidad * costo 
        table_data.append([nombre, cantidad, f"${costo:.2f}", f"${total:.2f}"]) 

    # Create the table
    table = Table(table_data, colWidths=[200, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Calculate table height
    row_height = 20 
    table_height = len(table_data) * row_height

    # Adjust table position dynamically
    table_y_position = title_y_position - 60  
    if table_y_position - table_height < 50:  
        raise ValueError("Table is too large to fit on one page. Consider splitting it into multiple pages.")

    subtotal = sum(float(row[3].replace("$", "")) for row in table_data[1:])  
    subtotal_y_position = table_y_position - 300 - table_height - 20 
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, subtotal_y_position, "Subtotal:")
    c.setFont("Helvetica", 12)
    c.drawString(500, subtotal_y_position, f"${subtotal:.2f}")

    # Add IVA
    iva = subtotal * 0.16
    iva_y_position = subtotal_y_position - 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, iva_y_position, "IVA:")
    c.setFont("Helvetica", 12)
    c.drawString(500, iva_y_position, f"${iva:.2f}")

    # Add IVA + Subtotal
    total_y_position = iva_y_position - 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, total_y_position, "Total:")
    c.setFont("Helvetica", 12)
    c.drawString(500, total_y_position, f"${subtotal + iva:.2f}")
    # Draw the table
    table.wrapOn(c, width, height)
    table.drawOn(c, 50, table_y_position - 300)

    # Save the PDF
    c.save()