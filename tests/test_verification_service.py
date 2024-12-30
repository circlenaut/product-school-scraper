import logging
from pathlib import Path
import pytest
from unittest.mock import Mock, mock_open

from product_school_scraper.services.verification_service import verify_pages
from product_school_scraper.utils.logger import logger

def test_verify_pages_with_files(mocker, caplog):
    """
    Test the verify_pages function by mocking external dependencies.
    """
    # Set caplog to capture DEBUG and above logs
    caplog.set_level(logging.DEBUG)

    # Set the logger's level to DEBUG to ensure DEBUG messages are emitted
    logger.setLevel(logging.DEBUG)

    # Mock Path.exists and Path.is_dir to return True
    mocker.patch('product_school_scraper.services.verification_service.Path.exists', return_value=True)
    mocker.patch('product_school_scraper.services.verification_service.Path.is_dir', return_value=True)

    # Create a mock subdirectory
    mock_subdir = Mock(spec=Path)
    mock_subdir.name = "Page1"

    # Create mock PDF and TXT files
    mock_pdf = Mock(spec=Path)
    mock_pdf.exists.return_value = True
    mock_pdf.stat.return_value.st_size = 1024  # Size in bytes

    mock_txt = Mock(spec=Path)
    mock_txt.exists.return_value = True
    mock_txt.read_text.return_value = "Valid text."

    # Mock the 'glob' method for PDFs and TXTs
    # First call to glob("*.pdf") returns [mock_pdf]
    # Second call to glob("*.txt") returns [mock_txt]
    mock_subdir.glob.side_effect = [
        [mock_pdf],  # PDF files
        [mock_txt]    # TXT files
    ]

    # Mock Path.iterdir to return the mock_subdir
    mocker.patch('product_school_scraper.services.verification_service.Path.iterdir', return_value=[mock_subdir])

    # Mock PdfReader to return a reader with one page
    mock_pdf_reader = mocker.patch('product_school_scraper.services.verification_service.pypdf.PdfReader')
    mock_pdf_reader_instance = Mock()
    mock_pdf_reader_instance.pages = [Mock()]  # Simulate one page
    mock_pdf_reader.return_value = mock_pdf_reader_instance

    # Mock the 'open' function to return a mock file object for PDF
    # The 'verify_pages' function calls 'open(pdf_path, 'rb')'
    # So, we need to mock 'open' when it's called with 'rb' and the pdf_path.

    # Create a mock for the PDF file object
    mock_pdf_file = mock_open(read_data=b"%PDF-1.4 mock pdf data").return_value
    mock_pdf_file.__enter__.return_value = mock_pdf_file

    # Assign the mock to 'open' when called with 'rb'
    def open_mock(path, mode='r', *args, **kwargs):
        if mode == 'rb':
            return mock_pdf_file
        else:
            raise ValueError("Unexpected mode for open: {}".format(mode))

    mocker.patch('product_school_scraper.services.verification_service.open', side_effect=open_mock)

    # Run the verification
    verify_pages("pages_dir")

    # Assert log messages using caplog
    assert "Starting verification of pages in 'pages_dir'..." in caplog.text
    assert "Checking directory: Page1" in caplog.text
    assert "Valid PDF: " in caplog.text  # The actual path will be a Mock object, so not checking exact path
    assert "Non-empty text file: " in caplog.text
    assert "Verification summary:" in caplog.text
    assert "Directories checked: 1" in caplog.text
    assert "PDF files found: 1, Invalid: 0" in caplog.text
    assert "TXT files found: 1, Empty: 0" in caplog.text
    assert "Verification complete." in caplog.text


def test_verify_pages_invalid_directory(mocker, caplog):
    """
    Test verify_pages when the provided pages_dir does not exist or is not a directory.
    """
    # Arrange
    caplog.set_level(logging.ERROR)
    
    # Mock Path.exists() and Path.is_dir() to return False
    mock_path = mocker.patch('product_school_scraper.services.verification_service.Path')
    mock_instance = mock_path.return_value
    mock_instance.exists.return_value = False
    mock_instance.is_dir.return_value = False
    
    # Mock logger.error to monitor error logs
    mock_logger_error = mocker.patch('product_school_scraper.services.verification_service.logger.error')
    
    # Act
    verify_pages("invalid_pages_dir")
    
    # Assert
    mock_logger_error.assert_called_once_with("Directory 'invalid_pages_dir' does not exist or is not a directory.")

def test_verify_pages_with_invalid_pdf(mocker, caplog):
    """
    Test verify_pages when a PDF file is invalid (cannot be parsed by PyPDF).
    """
    from unittest.mock import MagicMock, mock_open

    # Arrange
    caplog.set_level(logging.DEBUG)

    # Mock Path.exists() and Path.is_dir() to return True
    mock_path = mocker.patch('product_school_scraper.services.verification_service.Path')
    mock_instance = mock_path.return_value
    mock_instance.exists.return_value = True
    mock_instance.is_dir.return_value = True

    # Create a mock subdirectory
    mock_subdir = MagicMock(spec=Path)
    mock_subdir.name = "Page1"

    # Mock glob to return one PDF file and no TXT files
    mock_pdf = MagicMock(spec=Path)
    mock_pdf_file_path = Path("pages/Page1/page_001.pdf")
    mock_pdf.__str__.return_value = str(mock_pdf_file_path)
    mock_pdf.exists.return_value = True
    mock_pdf.stat.return_value.st_size = 2048  # Non-zero size

    # Set side_effect to return [mock_pdf] for "*.pdf" and [] for "*.txt"
    mock_subdir.glob.side_effect = [ [mock_pdf], [] ]

    # Mock iterdir to return the subdirectory
    mock_instance.iterdir.return_value = [mock_subdir]

    # Mock PdfReader to raise an exception (invalid PDF)
    mock_pypdf = mocker.patch('product_school_scraper.services.verification_service.pypdf.PdfReader')
    mock_pypdf.side_effect = Exception("Invalid PDF content")

    # Mock the 'open' function to return a mock file object for PDF
    mock_pdf_file = mock_open(read_data=b"%PDF-1.4 mock pdf data").return_value
    mock_pdf_file.__enter__.return_value = mock_pdf_file
    mocker.patch('product_school_scraper.services.verification_service.open', return_value=mock_pdf_file)

    # Mock logger.debug to monitor debug logs
    mock_logger_debug = mocker.patch('product_school_scraper.services.verification_service.logger.debug')

    # Act
    verify_pages("pages")

    # Assert
    mock_pypdf.assert_called_once()
    mock_logger_debug.assert_any_call(f"PDF read error on '{mock_pdf_file_path}': Invalid PDF content")
    mock_logger_debug.assert_any_call(f"Invalid PDF: {mock_pdf}")

def test_verify_pages_with_empty_txt(mocker, caplog):
    """
    Test verify_pages when a TXT file is empty or below the minimum length.
    """
    from unittest.mock import MagicMock

    # Arrange
    caplog.set_level(logging.DEBUG)

    # Mock Path.exists() and Path.is_dir() to return True
    mock_path = mocker.patch('product_school_scraper.services.verification_service.Path')
    mock_instance = mock_path.return_value
    mock_instance.exists.return_value = True
    mock_instance.is_dir.return_value = True

    # Create a mock subdirectory
    mock_subdir = MagicMock(spec=Path)
    mock_subdir.name = "Page2"

    # Mock glob to return no PDF files and one TXT file
    mock_txt = MagicMock(spec=Path)
    mock_txt_file_path = Path("pages/Page2/page_002.txt")
    mock_txt.__str__.return_value = str(mock_txt_file_path)
    mock_txt.exists.return_value = True

    # Set side_effect to return [] for "*.pdf" and [mock_txt] for "*.txt"
    mock_subdir.glob.side_effect = [ [], [mock_txt] ]

    # Mock iterdir to return the subdirectory
    mock_instance.iterdir.return_value = [mock_subdir]

    # Mock logger.debug to monitor debug logs
    mock_logger_debug = mocker.patch('product_school_scraper.services.verification_service.logger.debug')

    # Act
    verify_pages("pages")

    # Assert
    mock_logger_debug.assert_any_call(f"Empty or very small text file: {mock_txt}")

def test_is_valid_pdf_nonexistent_or_empty(mocker):
    """
    Test _is_valid_pdf returns False when the PDF does not exist or has zero size.
    """
    from product_school_scraper.services.verification_service import _is_valid_pdf
    
    # Arrange
    mock_pdf_path = Mock(spec=Path)
    mock_pdf_path.exists.return_value = False
    mock_pdf_path.stat.return_value.st_size = 0
    
    # Act
    result = _is_valid_pdf(mock_pdf_path)
    
    # Assert
    assert result == False

def test_is_valid_pdf_exception(mocker):
    """
    Test _is_valid_pdf handles exceptions raised by PdfReader and returns False.
    """
    from product_school_scraper.services.verification_service import _is_valid_pdf
    
    # Arrange
    mock_pdf_path = Mock(spec=Path)
    mock_pdf_path.exists.return_value = True
    mock_pdf_path.stat.return_value.st_size = 1024
    
    # Mock open to raise an exception
    mock_open = mocker.patch('builtins.open', side_effect=Exception("Read error"))
    
    # Mock logger.debug to monitor debug logs
    mock_logger_debug = mocker.patch('product_school_scraper.services.verification_service.logger.debug')
    
    # Act
    result = _is_valid_pdf(mock_pdf_path)
    
    # Assert
    assert result == False
    mock_logger_debug.assert_called_once_with(f"PDF read error on '{mock_pdf_path}': Read error")

def test_has_content_nonexistent_txt():
    """
    Test _has_content returns False when the TXT file does not exist.
    """
    from product_school_scraper.services.verification_service import _has_content
    
    # Arrange
    mock_txt_path = Mock(spec=Path)
    mock_txt_path.exists.return_value = False
    
    # Act
    result = _has_content(mock_txt_path)
    
    # Assert
    assert result == False