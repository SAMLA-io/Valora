import pytest
from unittest.mock import patch, MagicMock
from src.app import main

# Test main function
@patch('src.app.process_emails')
@patch('src.app.time.sleep')
def test_main(mock_sleep, mock_process_emails):
    # Setup mock to raise KeyboardInterrupt after first iteration
    mock_sleep.side_effect = KeyboardInterrupt()
    
    # Call function
    with pytest.raises(KeyboardInterrupt):
        main()
    
    # Assert
    mock_process_emails.assert_called_once()
    mock_sleep.assert_called_once_with(180)

# Test main function with multiple iterations
@patch('src.app.process_emails')
@patch('src.app.time.sleep')
def test_main_multiple_iterations(mock_sleep, mock_process_emails):
    # Setup mock to raise KeyboardInterrupt after second iteration
    mock_sleep.side_effect = [None, KeyboardInterrupt()]
    
    # Call function
    with pytest.raises(KeyboardInterrupt):
        main()
    
    # Assert
    assert mock_process_emails.call_count == 2
    assert mock_sleep.call_count == 2

# Test main function with process_emails exception
@patch('src.app.process_emails')
@patch('src.app.time.sleep')
def test_main_process_emails_exception(mock_sleep, mock_process_emails):
    # Setup mock to raise an exception in process_emails
    mock_process_emails.side_effect = Exception("Process emails failed")
    mock_sleep.side_effect = KeyboardInterrupt()
    
    # Call function
    with pytest.raises(KeyboardInterrupt):
        main()
    
    # Assert
    mock_process_emails.assert_called_once()
    mock_sleep.assert_called_once_with(180)

if __name__ == '__main__':
    pytest.main([__file__]) 