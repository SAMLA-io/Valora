import pytest
from unittest.mock import patch, MagicMock
from src.api.gmail import (
    connect_to_email,
    get_body,
    search_emails,
    fetch_emails
)

# Sample data for testing
SAMPLE_EMAIL_BODY = "This is a sample email body for testing."

# Test connect_to_email successful connection
@patch('src.api.gmail.imaplib.IMAP4_SSL')
def test_connect_to_email_success(mock_imap):
    # Setup mock
    mock_con = MagicMock()
    mock_imap.return_value = mock_con
    
    # Call function
    result = connect_to_email()
    
    # Assert
    assert result == mock_con
    mock_imap.assert_called_once_with('imap.gmail.com')
    mock_con.login.assert_called_once()

# Test connect_to_email failed connection
@patch('src.api.gmail.imaplib.IMAP4_SSL')
def test_connect_to_email_failure(mock_imap):
    # Setup mock to raise an exception
    mock_imap.side_effect = Exception("Connection failed")
    
    # Call function
    result = connect_to_email()
    
    # Assert
    assert result is None

# Test get_body with multipart message
def test_get_body_multipart():
    # Setup mock
    mock_msg = MagicMock()
    mock_msg.is_multipart.return_value = True
    
    # Create a mock part with text/plain content
    mock_part = MagicMock()
    mock_part.get_content_type.return_value = "text/plain"
    mock_part.get_payload.return_value = b"Sample email body"
    
    # Setup walk to return the mock part
    mock_msg.walk.return_value = [mock_part]
    
    # Call function
    result = get_body(mock_msg)
    
    # Assert
    assert result == "Sample email body"
    mock_msg.is_multipart.assert_called_once()
    mock_msg.walk.assert_called_once()
    mock_part.get_content_type.assert_called_once()
    mock_part.get_payload.assert_called_once_with(decode=True)

# Test get_body with single-part message
def test_get_body_single_part():
    # Setup mock
    mock_msg = MagicMock()
    mock_msg.is_multipart.return_value = False
    mock_msg.get_payload.return_value = b"Sample email body"
    
    # Call function
    result = get_body(mock_msg)
    
    # Assert
    assert result == "Sample email body"
    mock_msg.is_multipart.assert_called_once()
    mock_msg.get_payload.assert_called_once_with(decode=True)

# Test get_body with UnicodeDecodeError
def test_get_body_decode_error():
    # Setup mock
    mock_msg = MagicMock()
    mock_msg.is_multipart.return_value = False
    mock_msg.get_payload.side_effect = [
        UnicodeDecodeError("utf-8", b"", 0, 1, "Invalid UTF-8"),
        b"Sample email body"
    ]
    
    # Call function
    result = get_body(mock_msg)
    
    # Assert
    assert result == "Sample email body"
    mock_msg.is_multipart.assert_called_once()
    assert mock_msg.get_payload.call_count == 2

# Test search_emails
def test_search_emails():
    # Setup mock
    mock_con = MagicMock()
    mock_con.search.return_value = ("OK", [b"1 2 3"])
    
    # Call function
    result = search_emails(mock_con, "SUBJECT", "test")
    
    # Assert
    assert result == [b"1 2 3"]
    mock_con.search.assert_called_once_with(None, "SUBJECT", '"test"')

# Test fetch_emails successful
def test_fetch_emails_success():
    # Setup mock
    mock_con = MagicMock()
    mock_con.select.return_value = ("OK", [b"1"])
    mock_con.search.return_value = ("OK", [b"1 2 3"])
    mock_con.fetch.side_effect = [
        ("OK", [(b"1", b"email content")]),
        ("OK", [(b"2", b"email content")]),
        ("OK", [(b"3", b"email content")])
    ]
    
    # Call function
    result = fetch_emails(mock_con, "SUBJECT", "test")
    
    # Assert
    assert len(result) == 3
    mock_con.select.assert_called_once_with('Inbox')
    mock_con.search.assert_called_once_with(None, "SUBJECT", '"test"')
    assert mock_con.fetch.call_count == 3

# Test fetch_emails failure
def test_fetch_emails_failure():
    # Setup mock to raise an exception
    mock_con = MagicMock()
    mock_con.select.side_effect = Exception("Failed to select inbox")
    
    # Call function
    result = fetch_emails(mock_con, "SUBJECT", "test")
    
    # Assert
    assert result == []
    mock_con.select.assert_called_once_with('Inbox')

if __name__ == '__main__':
    pytest.main([__file__]) 