# tests/test_scraping_service.py

from bs4 import BeautifulSoup
import pytest
from unittest.mock import Mock, call, ANY

import requests
from product_school_scraper.services.scraping_service import (
    list_pages,
    fetch_pages,
    render_pdf_pages
)

# Sample sitemap XML for testing
sample_sitemap_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://productschool.com/</loc>
        <lastmod>2023-10-10</lastmod>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://productschool.com/about</loc>
        <lastmod>2023-10-12</lastmod>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://productschool.com/artificial-intelligence-product-certification</loc>
        <lastmod>2023-10-15</lastmod>
        <priority>0.7</priority>
    </url>
    <!-- Add more URLs as needed for testing -->
</urlset>
"""

# Fixtures for reuse
@pytest.fixture
def sitemap_url():
    return "https://productschool.com/sitemap.xml"

@pytest.fixture
def sample_sitemap_xml_fixture():
    return sample_sitemap_xml

def test_list_pages(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test the list_pages function by mocking external dependencies.
    """
    # Mock 'parse_sitemap' to return a list of URLs
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=[
            "https://productschool.com/",
            "https://productschool.com/about",
            "https://productschool.com/artificial-intelligence-product-certification"
        ]
    )

    # Mock 'DBFactory.get_db' to return a mock db object
    mock_db_factory = mocker.patch(
        'product_school_scraper.services.scraping_service.DBFactory.get_db'
    )
    mock_db_instance = Mock()
    mock_db_factory.return_value = mock_db_instance
    mock_db_instance.store_urls = Mock()

    # Call the function under test
    list_pages(sitemap_url)

    # Assertions to ensure that the mocked methods were called as expected
    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_db_factory.assert_called_once_with("sqlite")
    mock_db_instance.store_urls.assert_called_once_with([
        "https://productschool.com/",
        "https://productschool.com/about",
        "https://productschool.com/artificial-intelligence-product-certification"
    ])

def test_fetch_pages(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test the fetch_pages function by mocking external dependencies.
    """
    # Mock 'parse_sitemap' to return a list of URLs
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=[
            "https://productschool.com/",
            "https://productschool.com/about",
            "https://productschool.com/artificial-intelligence-product-certification"
        ]
    )

    # Create separate response mocks for each 'requests.get' call
    response_mock1 = Mock()
    response_mock1.raise_for_status = Mock()
    response_mock1.text = "<html><head><title>Test Page 1</title></head><body><p>This is a test.</p></body></html>"

    response_mock2 = Mock()
    response_mock2.raise_for_status = Mock()
    response_mock2.text = "<html><head><title>About Page</title></head><body><p>About us.</p></body></html>"

    response_mock3 = Mock()
    response_mock3.raise_for_status = Mock()
    response_mock3.text = "<html><head><title>AI Certification</title></head><body><p>AI content.</p></body></html>"

    # Mock 'requests.get' to return the response mocks
    mock_requests_get = mocker.patch('product_school_scraper.services.scraping_service.requests.get')
    mock_requests_get.side_effect = [response_mock1, response_mock2, response_mock3]

    # Mock 'pdfkit.from_url' to prevent actual PDF generation
    mock_pdfkit = mocker.patch('product_school_scraper.services.scraping_service.pdfkit.from_url')
    mock_pdfkit.return_value = None  # Assuming from_url doesn't return anything meaningful

    # Mock 'Path.mkdir' to prevent actual directory creation
    mock_path_mkdir = mocker.patch('product_school_scraper.services.scraping_service.Path.mkdir')
    mock_path_mkdir.return_value = None

    # Mock 'Path.write_text' to prevent actual file writing
    mock_write_text = mocker.patch('product_school_scraper.services.scraping_service.Path.write_text')
    mock_write_text.return_value = None

    # Mock 'clean_html_content' to return cleaned text
    mock_clean_html_content = mocker.patch(
        'product_school_scraper.services.scraping_service.clean_html_content',
        return_value="This is a test. Another sentence."
    )

    # Mock 'time.sleep' to speed up tests
    mock_sleep = mocker.patch('product_school_scraper.services.scraping_service.time.sleep', return_value=None)

    # Call the function under test
    fetch_pages(sitemap_url, directories=None, number_of_pages=None)

    # Assertions to ensure that the mocked methods were called as expected
    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)

    # Assert 'requests.get' was called three times with the expected URLs and timeout
    expected_calls = [
        call("https://productschool.com/", timeout=15),
        call("https://productschool.com/about", timeout=15),
        call("https://productschool.com/artificial-intelligence-product-certification", timeout=15)
    ]
    mock_requests_get.assert_has_calls(expected_calls, any_order=False)
    assert mock_requests_get.call_count == 3

    # Assert 'pdfkit.from_url' was called three times
    assert mock_pdfkit.call_count == 3

    # Assert 'Path.mkdir' was called four times (1 for base 'pages' + 3 for each page)
    assert mock_path_mkdir.call_count == 4

    # Assert 'Path.write_text' was called three times (1 for each page)
    assert mock_write_text.call_count == 3

    # Assert 'clean_html_content' was called three times (1 for each page)
    assert mock_clean_html_content.call_count == 3

    # Assert 'time.sleep' was called two times (between 3 requests)
    assert mock_sleep.call_count == 2

def test_render_pdf_pages(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test the render_pdf_pages function by mocking external dependencies.
    """
    # Mock 'parse_sitemap' to return a list of URLs
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=[
            "https://productschool.com/",
            "https://productschool.com/about",
            "https://productschool.com/artificial-intelligence-product-certification"
        ]
    )

    # Create separate response mocks for each 'requests.get' call
    response_mock1 = Mock()
    response_mock1.raise_for_status = Mock()
    response_mock1.text = "<html><head><title>Test Page 1</title></head><body><p>This is a test.</p></body></html>"

    response_mock2 = Mock()
    response_mock2.raise_for_status = Mock()
    response_mock2.text = "<html><head><title>About Page</title></head><body><p>About us.</p></body></html>"

    response_mock3 = Mock()
    response_mock3.raise_for_status = Mock()
    response_mock3.text = "<html><head><title>AI Certification</title></head><body><p>AI content.</p></body></html>"

    # Mock 'requests.get' to return the response mocks
    mock_requests_get = mocker.patch('product_school_scraper.services.scraping_service.requests.get')
    mock_requests_get.side_effect = [response_mock1, response_mock2, response_mock3]

    # Mock 'pdfkit.from_url' to prevent actual PDF generation
    mock_pdfkit = mocker.patch('product_school_scraper.services.scraping_service.pdfkit.from_url')
    mock_pdfkit.return_value = None  # Assuming from_url doesn't return anything meaningful

    # Mock 'Path.mkdir' to prevent actual directory creation
    mock_path_mkdir = mocker.patch('product_school_scraper.services.scraping_service.Path.mkdir')
    mock_path_mkdir.return_value = None

    # Mock 'time.sleep' to speed up tests
    mock_sleep = mocker.patch('product_school_scraper.services.scraping_service.time.sleep', return_value=None)

    # Call the function under test
    render_pdf_pages(sitemap_url, directories=None, number_of_pages=None)

    # Assertions to ensure that the mocked methods were called as expected
    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)

    # Assert 'requests.get' was called three times with the expected URLs and timeout
    expected_calls = [
        call("https://productschool.com/", timeout=15),
        call("https://productschool.com/about", timeout=15),
        call("https://productschool.com/artificial-intelligence-product-certification", timeout=15)
    ]
    mock_requests_get.assert_has_calls(expected_calls, any_order=False)
    assert mock_requests_get.call_count == 3

    # Assert 'pdfkit.from_url' was called three times
    assert mock_pdfkit.call_count == 3

    # Assert 'Path.mkdir' was called four times (1 for base 'pages' + 3 for each page)
    assert mock_path_mkdir.call_count == 4

    # Assert 'time.sleep' was called two times (between 3 requests)
    assert mock_sleep.call_count == 2

def test_render_pdf_pages_with_limit(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test the render_pdf_pages function with a limit on the number of pages.
    """
    # Mock 'parse_sitemap' to return a list of URLs
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=[
            "https://productschool.com/",
            "https://productschool.com/about",
            "https://productschool.com/artificial-intelligence-product-certification"
        ]
    )

    # Create separate response mocks for each 'requests.get' call
    response_mock1 = Mock()
    response_mock1.raise_for_status = Mock()
    response_mock1.text = "<html><head><title>Test Page 1</title></head><body><p>This is a test.</p></body></html>"

    response_mock2 = Mock()
    response_mock2.raise_for_status = Mock()
    response_mock2.text = "<html><head><title>About Page</title></head><body><p>About us.</p></body></html>"

    # Mock 'requests.get' to return the response mocks
    mock_requests_get = mocker.patch('product_school_scraper.services.scraping_service.requests.get')
    mock_requests_get.side_effect = [response_mock1, response_mock2]

    # Mock 'pdfkit.from_url' to prevent actual PDF generation
    mock_pdfkit = mocker.patch('product_school_scraper.services.scraping_service.pdfkit.from_url')
    mock_pdfkit.return_value = None  # Assuming from_url doesn't return anything meaningful

    # Mock 'Path.mkdir' to prevent actual directory creation
    mock_path_mkdir = mocker.patch('product_school_scraper.services.scraping_service.Path.mkdir')
    mock_path_mkdir.return_value = None

    # Mock 'time.sleep' to speed up tests
    mock_sleep = mocker.patch('product_school_scraper.services.scraping_service.time.sleep', return_value=None)

    # Call the function under test with a limit
    render_pdf_pages(sitemap_url, directories=None, number_of_pages=2)

    # Assertions to ensure that the mocked methods were called as expected
    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)

    # Assert 'requests.get' was called two times with the expected URLs and timeout
    expected_calls = [
        call("https://productschool.com/", timeout=15),
        call("https://productschool.com/about", timeout=15)
    ]
    mock_requests_get.assert_has_calls(expected_calls, any_order=False)
    assert mock_requests_get.call_count == 2

    # Assert 'pdfkit.from_url' was called two times
    assert mock_pdfkit.call_count == 2

    # Assert 'Path.mkdir' was called three times (1 for base 'pages' + 2 for each page)
    assert mock_path_mkdir.call_count == 3

    # Assert 'time.sleep' was called once (between 2 requests)
    assert mock_sleep.call_count == 1

def test_list_pages_no_directories(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test the list_pages function without specifying directories and with default db_type.
    """
    # Mock 'parse_sitemap' to return a list of URLs
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=[
            "https://productschool.com/",
            "https://productschool.com/about",
            "https://productschool.com/artificial-intelligence-product-certification"
        ]
    )

    # Mock 'DBFactory.get_db' to return a mock db object
    mock_db_factory = mocker.patch(
        'product_school_scraper.services.scraping_service.DBFactory.get_db'
    )
    mock_db_instance = Mock()
    mock_db_factory.return_value = mock_db_instance
    mock_db_instance.store_urls = Mock()

    # Call the function under test
    list_pages(sitemap_url)

    # Assertions to ensure that the mocked methods were called as expected
    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_db_factory.assert_called_once_with("sqlite")
    mock_db_instance.store_urls.assert_called_once_with([
        "https://productschool.com/",
        "https://productschool.com/about",
        "https://productschool.com/artificial-intelligence-product-certification"
    ])

def test_list_pages_with_directories_and_db_type(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test the list_pages function with specified directories and a different db_type.
    """
    directories = ["products", "courses"]
    db_type = "postgresql"

    # Mock 'parse_sitemap' to return a list of URLs filtered by directories
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=[
            "https://productschool.com/products",
            "https://productschool.com/courses"
        ]
    )

    # Mock 'DBFactory.get_db' to return a mock db object
    mock_db_factory = mocker.patch(
        'product_school_scraper.services.scraping_service.DBFactory.get_db'
    )
    mock_db_instance = Mock()
    mock_db_factory.return_value = mock_db_instance
    mock_db_instance.store_urls = Mock()

    # Call the function under test
    list_pages(sitemap_url, directories=directories, db_type=db_type)

    # Assertions to ensure that the mocked methods were called as expected
    mock_parse_sitemap.assert_called_once_with(sitemap_url, directories)
    mock_db_factory.assert_called_once_with(db_type)
    mock_db_instance.store_urls.assert_called_once_with([
        "https://productschool.com/products",
        "https://productschool.com/courses"
    ])

def test_fetch_pages_exception_requests(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test that fetch_pages handles requests.exceptions.RequestException and logs an error.
    """
    # Mock 'parse_sitemap' to return a list of URLs
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=["https://productschool.com/"]
    )

    # Mock 'requests.get' to raise a RequestException
    mock_requests_get = mocker.patch('product_school_scraper.services.scraping_service.requests.get')
    mock_requests_get.side_effect = requests.exceptions.RequestException("Network error")

    # Mock 'Path.mkdir' to prevent actual directory creation
    mock_path_mkdir = mocker.patch('product_school_scraper.services.scraping_service.Path.mkdir')
    mock_path_mkdir.return_value = None

    # Mock 'time.sleep' to speed up tests
    mock_sleep = mocker.patch('product_school_scraper.services.scraping_service.time.sleep', return_value=None)

    # Mock 'clean_html_content' as it should not be called due to exception
    mock_clean_html_content = mocker.patch(
        'product_school_scraper.services.scraping_service.clean_html_content'
    )

    # Mock 'pdfkit.from_url' as it should not be called due to exception
    mock_pdfkit = mocker.patch('product_school_scraper.services.scraping_service.pdfkit.from_url')

    # Mock the logger
    mock_logger_error = mocker.patch('product_school_scraper.services.scraping_service.logger.error')

    # Call the function under test
    fetch_pages(sitemap_url)

    # Assertions
    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/", timeout=15)
    mock_logger_error.assert_called_once_with("Error scraping URL #1 (https://productschool.com/): Network error")
    mock_clean_html_content.assert_not_called()
    mock_pdfkit.assert_not_called()

def test_fetch_pages_exception_pdfkit(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test that fetch_pages handles exceptions raised by pdfkit.from_url and logs an error.
    """
    # Mock 'parse_sitemap' to return a list of URLs
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=["https://productschool.com/"]
    )

    # Create a mock response for 'requests.get'
    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head><title>Test Page</title></head><body><p>This is a test.</p></body></html>"

    # Mock 'requests.get' to return the response mock
    mock_requests_get = mocker.patch('product_school_scraper.services.scraping_service.requests.get')
    mock_requests_get.return_value = response_mock

    # Mock 'pdfkit.from_url' to raise an exception
    mock_pdfkit = mocker.patch('product_school_scraper.services.scraping_service.pdfkit.from_url')
    mock_pdfkit.side_effect = Exception("PDF generation failed")

    # Mock 'Path.mkdir' to prevent actual directory creation
    mock_path_mkdir = mocker.patch('product_school_scraper.services.scraping_service.Path.mkdir')
    mock_path_mkdir.return_value = None

    # Mock 'Path.write_text' to prevent actual file writing
    mock_write_text = mocker.patch('product_school_scraper.services.scraping_service.Path.write_text')
    mock_write_text.return_value = None

    # Mock 'clean_html_content' to return cleaned text
    mock_clean_html_content = mocker.patch(
        'product_school_scraper.services.scraping_service.clean_html_content',
        return_value="This is a test. Another sentence."
    )

    # Mock 'time.sleep' to speed up tests
    mock_sleep = mocker.patch('product_school_scraper.services.scraping_service.time.sleep', return_value=None)

    # Mock the logger's error method
    mock_logger_error = mocker.patch('product_school_scraper.services.scraping_service.logger.error')

    # Call the function under test
    fetch_pages(sitemap_url)

    # Assertions
    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/", timeout=15)
    mock_clean_html_content.assert_called_once_with(
        "Test Page", BeautifulSoup(response_mock.text, "html.parser")
    )
    mock_pdfkit.assert_called_once_with("https://productschool.com/", "pages/Test Page/page_001.pdf")
    mock_write_text.assert_not_called()  # Changed from assert_called_once_with to assert_not_called
    mock_logger_error.assert_called_once_with("Failed to save files for page_001: PDF generation failed")

def test_render_pdf_pages_exception_requests(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test that render_pdf_pages handles requests.exceptions.RequestException and logs an error.
    """
    # Mock 'parse_sitemap' to return a list of URLs
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=["https://productschool.com/"]
    )

    # Mock 'requests.get' to raise a RequestException
    mock_requests_get = mocker.patch('product_school_scraper.services.scraping_service.requests.get')
    mock_requests_get.side_effect = requests.exceptions.RequestException("Network error")

    # Mock 'Path.mkdir' to prevent actual directory creation
    mock_path_mkdir = mocker.patch('product_school_scraper.services.scraping_service.Path.mkdir')
    mock_path_mkdir.return_value = None

    # Mock 'time.sleep' to speed up tests
    mock_sleep = mocker.patch('product_school_scraper.services.scraping_service.time.sleep', return_value=None)

    # Mock 'pdfkit.from_url' as it should not be called due to exception
    mock_pdfkit = mocker.patch('product_school_scraper.services.scraping_service.pdfkit.from_url')

    # Mock the logger
    mock_logger_error = mocker.patch('product_school_scraper.services.scraping_service.logger.error')

    # Call the function under test
    render_pdf_pages(sitemap_url)

    # Assertions
    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/", timeout=15)
    mock_logger_error.assert_called_once_with("Network error for URL #1 (https://productschool.com/): Network error")
    mock_pdfkit.assert_not_called()

def test_render_pdf_pages_exception_pdfkit(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test that render_pdf_pages handles exceptions raised by pdfkit.from_url and logs an error.
    """
    # Mock 'parse_sitemap' to return a list of URLs
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=["https://productschool.com/"]
    )

    # Create a mock response for 'requests.get'
    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head><title>Test Page</title></head><body><p>This is a test.</p></body></html>"

    # Mock 'requests.get' to return the response mock
    mock_requests_get = mocker.patch('product_school_scraper.services.scraping_service.requests.get')
    mock_requests_get.return_value = response_mock

    # Mock 'pdfkit.from_url' to raise an exception
    mock_pdfkit = mocker.patch('product_school_scraper.services.scraping_service.pdfkit.from_url')
    mock_pdfkit.side_effect = Exception("PDF generation failed")

    # Mock 'Path.mkdir' to prevent actual directory creation
    mock_path_mkdir = mocker.patch('product_school_scraper.services.scraping_service.Path.mkdir')
    mock_path_mkdir.return_value = None

    # Mock 'time.sleep' to speed up tests
    mock_sleep = mocker.patch('product_school_scraper.services.scraping_service.time.sleep', return_value=None)

    # Mock the logger
    mock_logger_error = mocker.patch('product_school_scraper.services.scraping_service.logger.error')

    # Call the function under test
    render_pdf_pages(sitemap_url)

    # Assertions
    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/", timeout=15)
    mock_pdfkit.assert_called_once_with("https://productschool.com/", "pages/Test Page/page_001.pdf")
    mock_logger_error.assert_called_once_with("Error generating PDF for URL #1 (https://productschool.com/): PDF generation failed")

def test_fetch_pages_missing_title(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test fetch_pages when the HTML content lacks a <title> tag.
    Ensures that _path_from_url is used for directory naming.
    """
    # Mock 'parse_sitemap' to return a list with one URL
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=["https://productschool.com/no-title"]
    )

    # Mock 'requests.get' to return HTML without a <title> tag
    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head></head><body><p>No title here.</p></body></html>"

    mock_requests_get = mocker.patch('product_school_scraper.services.scraping_service.requests.get')
    mock_requests_get.return_value = response_mock

    # Mock 'pdfkit.from_url' to succeed
    mock_pdfkit = mocker.patch('product_school_scraper.services.scraping_service.pdfkit.from_url')
    mock_pdfkit.return_value = None

    # Mock 'Path.mkdir' to succeed
    mock_path_mkdir = mocker.patch('product_school_scraper.services.scraping_service.Path.mkdir')
    mock_path_mkdir.return_value = None

    # Mock 'Path.write_text' to prevent actual file writing
    mock_write_text = mocker.patch('product_school_scraper.services.scraping_service.Path.write_text')
    mock_write_text.return_value = None

    # Mock 'clean_html_content' to return cleaned text
    mock_clean_html_content = mocker.patch(
        'product_school_scraper.services.scraping_service.clean_html_content',
        return_value="No title here. Another sentence."
    )

    # Mock 'time.sleep' to speed up tests
    mock_sleep = mocker.patch('product_school_scraper.services.scraping_service.time.sleep', return_value=None)

    # Mock the logger's info method
    mock_logger_info = mocker.patch('product_school_scraper.services.scraping_service.logger.info')

    # Call the function under test
    fetch_pages(sitemap_url)

    # Assertions
    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/no-title", timeout=15)
    mock_clean_html_content.assert_called_once_with(
        "productschool.com-no-title", BeautifulSoup(response_mock.text, "html.parser")
    )
    mock_pdfkit.assert_called_once_with("https://productschool.com/no-title", "pages/productschool.com-no-title/page_001.pdf")
    mock_write_text.assert_called_once_with("No title here. Another sentence.", encoding="utf-8")
    mock_logger_info.assert_any_call("Saved PDF: pages/productschool.com-no-title/page_001.pdf")
    mock_logger_info.assert_any_call("Saved TXT: pages/productschool.com-no-title/page_001.txt")

def test_render_pdf_pages_missing_title(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test render_pdf_pages when the HTML content lacks a <title> tag.
    Ensures that _path_from_url is used for directory naming.
    """
    # Mock 'parse_sitemap' to return a list with one URL
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=["https://productschool.com/no-title"]
    )

    # Mock 'requests.get' to return HTML without a <title> tag
    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head></head><body><p>No title here.</p></body></html>"

    mock_requests_get = mocker.patch('product_school_scraper.services.scraping_service.requests.get')
    mock_requests_get.return_value = response_mock

    # Mock 'pdfkit.from_url' to succeed
    mock_pdfkit = mocker.patch('product_school_scraper.services.scraping_service.pdfkit.from_url')
    mock_pdfkit.return_value = None

    # Mock 'Path.mkdir' to succeed
    mock_path_mkdir = mocker.patch('product_school_scraper.services.scraping_service.Path.mkdir')
    mock_path_mkdir.return_value = None

    # Mock 'time.sleep' to speed up tests
    mock_sleep = mocker.patch('product_school_scraper.services.scraping_service.time.sleep', return_value=None)

    # Mock the logger's info method
    mock_logger_info = mocker.patch('product_school_scraper.services.scraping_service.logger.info')

    # Call the function under test
    render_pdf_pages(sitemap_url)

    # Assertions
    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/no-title", timeout=15)
    mock_pdfkit.assert_called_once_with("https://productschool.com/no-title", "pages/productschool.com-no-title/page_001.pdf")
    mock_logger_info.assert_any_call("Saved PDF: pages/productschool.com-no-title/page_001.pdf")

def test_fetch_pages_sanitize_filename_empty(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test fetch_pages when _sanitize_filename returns an empty string, forcing safe_dir_name to use _path_from_url.
    """
    # Mock 'parse_sitemap' to return a list with one URL
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=["https://productschool.com/"]
    )

    # Mock 'requests.get' to return standard HTML with a <title> tag
    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head><title>Test Page</title></head><body><p>This is a test.</p></body></html>"

    mock_requests_get = mocker.patch('product_school_scraper.services.scraping_service.requests.get')
    mock_requests_get.return_value = response_mock

    # Mock '_sanitize_filename' to return an empty string
    mock_sanitize_filename = mocker.patch(
        'product_school_scraper.services.scraping_service._sanitize_filename',
        return_value=""
    )

    # Mock 'pdfkit.from_url' to succeed
    mock_pdfkit = mocker.patch('product_school_scraper.services.scraping_service.pdfkit.from_url')
    mock_pdfkit.return_value = None

    # Mock 'Path.mkdir' to prevent actual directory creation
    mock_path_mkdir = mocker.patch('product_school_scraper.services.scraping_service.Path.mkdir')
    mock_path_mkdir.return_value = None

    # Mock 'Path.write_text' to prevent actual file writing
    mock_write_text = mocker.patch('product_school_scraper.services.scraping_service.Path.write_text')
    mock_write_text.return_value = None

    # Mock 'clean_html_content' to return cleaned text
    mock_clean_html_content = mocker.patch(
        'product_school_scraper.services.scraping_service.clean_html_content',
        return_value="This is a test. Another sentence."
    )

    # Mock 'time.sleep' to speed up tests
    mock_sleep = mocker.patch('product_school_scraper.services.scraping_service.time.sleep', return_value=None)

    # Mock the logger's info method
    mock_logger_info = mocker.patch('product_school_scraper.services.scraping_service.logger.info')

    # Call the function under test
    fetch_pages(sitemap_url)

    # Assertions
    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/", timeout=15)
    mock_sanitize_filename.assert_called_once_with("Test Page")
    mock_clean_html_content.assert_called_once_with(
        "Test Page", BeautifulSoup(response_mock.text, "html.parser")
    )
    mock_pdfkit.assert_called_once_with("https://productschool.com/", "pages/productschool.com-/page_001.pdf")
    mock_write_text.assert_called_once_with("This is a test. Another sentence.", encoding="utf-8")
    mock_logger_info.assert_any_call("Saved PDF: pages/productschool.com-/page_001.pdf")
    mock_logger_info.assert_any_call("Saved TXT: pages/productschool.com-/page_001.txt")

def test_fetch_pages_exception_write_text(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test that fetch_pages handles exceptions raised by txt_path.write_text and logs an error.
    """
    # Mock 'parse_sitemap' to return a list with one URL
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=["https://productschool.com/"]
    )

    # Mock 'requests.get' to return standard HTML with a <title> tag
    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head><title>Test Page</title></head><body><p>This is a test.</p></body></html>"

    mock_requests_get = mocker.patch('product_school_scraper.services.scraping_service.requests.get')
    mock_requests_get.return_value = response_mock

    # Mock 'pdfkit.from_url' to succeed
    mock_pdfkit = mocker.patch('product_school_scraper.services.scraping_service.pdfkit.from_url')
    mock_pdfkit.return_value = None

    # Mock 'Path.mkdir' to prevent actual directory creation
    mock_path_mkdir = mocker.patch('product_school_scraper.services.scraping_service.Path.mkdir')
    mock_path_mkdir.return_value = None

    # Mock 'Path.write_text' to raise an exception
    mock_write_text = mocker.patch('product_school_scraper.services.scraping_service.Path.write_text')
    mock_write_text.side_effect = Exception("Failed to write TXT file")

    # Mock 'clean_html_content' to return cleaned text
    mock_clean_html_content = mocker.patch(
        'product_school_scraper.services.scraping_service.clean_html_content',
        return_value="This is a test. Another sentence."
    )

    # Mock 'time.sleep' to speed up tests
    mock_sleep = mocker.patch('product_school_scraper.services.scraping_service.time.sleep', return_value=None)

    # Mock the logger's error method
    mock_logger_error = mocker.patch('product_school_scraper.services.scraping_service.logger.error')

    # Call the function under test
    fetch_pages(sitemap_url)

    # Assertions
    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/", timeout=15)
    mock_clean_html_content.assert_called_once_with(
        "Test Page", BeautifulSoup(response_mock.text, "html.parser")
    )
    mock_pdfkit.assert_called_once_with("https://productschool.com/", "pages/Test Page/page_001.pdf")
    mock_write_text.assert_called_once_with("This is a test. Another sentence.", encoding="utf-8")
    mock_logger_error.assert_called_once_with("Failed to save files for page_001: Failed to write TXT file")

def test_fetch_pages_exception_mkdir(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test that fetch_pages handles exceptions raised by Path.mkdir and logs an error.
    """
    # Mock 'parse_sitemap' to return a list with one URL
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=["https://productschool.com/"]
    )

    # Mock 'requests.get' to return standard HTML with a <title> tag
    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head><title>Test Page</title></head><body><p>This is a test.</p></body></html>"

    mock_requests_get = mocker.patch('product_school_scraper.services.scraping_service.requests.get')
    mock_requests_get.return_value = response_mock

    # Mock 'pdfkit.from_url' to succeed
    mock_pdfkit = mocker.patch('product_school_scraper.services.scraping_service.pdfkit.from_url')
    mock_pdfkit.return_value = None

    # Mock 'Path.mkdir' to raise an exception when creating the output_subdir
    mock_path_mkdir = mocker.patch('product_school_scraper.services.scraping_service.Path.mkdir')
    # First call succeeds (for "pages"), second call fails (for output_subdir)
    mock_path_mkdir.side_effect = [None, Exception("Failed to create directory")]

    # Mock 'Path.write_text' to prevent actual file writing
    mock_write_text = mocker.patch('product_school_scraper.services.scraping_service.Path.write_text')
    mock_write_text.return_value = None

    # Mock 'clean_html_content' to return cleaned text
    mock_clean_html_content = mocker.patch(
        'product_school_scraper.services.scraping_service.clean_html_content',
        return_value="This is a test. Another sentence."
    )

    # Mock 'time.sleep' to speed up tests
    mock_sleep = mocker.patch('product_school_scraper.services.scraping_service.time.sleep', return_value=None)

    # Mock the logger's error method
    mock_logger_error = mocker.patch('product_school_scraper.services.scraping_service.logger.error')

    # Call the function under test
    fetch_pages(sitemap_url)

    # Assertions
    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/", timeout=15)
    mock_clean_html_content.assert_not_called()  # Correctly not called due to mkdir failure
    mock_pdfkit.assert_not_called()  # Should not be called because mkdir failed
    mock_write_text.assert_not_called()  # Should not be called because mkdir failed

    # Updated assertion for logger.error
    mock_logger_error.assert_called_once_with("Unexpected error for URL #1 (https://productschool.com/): Failed to create directory")

def test_fetch_pages_missing_title_and_sanitize_filename_empty(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test fetch_pages when the HTML content lacks a <title> tag and _sanitize_filename returns an empty string.
    """
    # Mock 'parse_sitemap' to return a list with one URL
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=["https://productschool.com/"]
    )

    # Mock 'requests.get' to return HTML without a <title> tag
    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head></head><body><p>No title here.</p></body></html>"

    mock_requests_get = mocker.patch('product_school_scraper.services.scraping_service.requests.get')
    mock_requests_get.return_value = response_mock

    # Mock '_sanitize_filename' to return an empty string
    mock_sanitize_filename = mocker.patch(
        'product_school_scraper.services.scraping_service._sanitize_filename',
        return_value=""
    )

    # Mock 'pdfkit.from_url' to succeed
    mock_pdfkit = mocker.patch('product_school_scraper.services.scraping_service.pdfkit.from_url')
    mock_pdfkit.return_value = None

    # Mock 'Path.mkdir' to prevent actual directory creation
    mock_path_mkdir = mocker.patch('product_school_scraper.services.scraping_service.Path.mkdir')
    mock_path_mkdir.return_value = None

    # Mock 'Path.write_text' to prevent actual file writing
    mock_write_text = mocker.patch('product_school_scraper.services.scraping_service.Path.write_text')
    mock_write_text.return_value = None

    # Mock 'clean_html_content' to return cleaned text
    mock_clean_html_content = mocker.patch(
        'product_school_scraper.services.scraping_service.clean_html_content',
        return_value="No title here. Another sentence."
    )

    # Mock 'time.sleep' to speed up tests
    mock_sleep = mocker.patch('product_school_scraper.services.scraping_service.time.sleep', return_value=None)

    # Mock the logger's info method
    mock_logger_info = mocker.patch('product_school_scraper.services.scraping_service.logger.info')

    # Call the function under test
    fetch_pages(sitemap_url)

    # Assertions
    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/", timeout=15)
    mock_sanitize_filename.assert_called_once_with("productschool.com-")  # Updated expectation
    mock_clean_html_content.assert_called_once_with(
        "productschool.com-", BeautifulSoup(response_mock.text, "html.parser")
    )
    mock_pdfkit.assert_called_once_with("https://productschool.com/", "pages/productschool.com-/page_001.pdf")
    mock_write_text.assert_called_once_with("No title here. Another sentence.", encoding="utf-8")
    mock_logger_info.assert_any_call("Saved PDF: pages/productschool.com-/page_001.pdf")
    mock_logger_info.assert_any_call("Saved TXT: pages/productschool.com-/page_001.txt")

def test_fetch_pages_with_limit(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    """
    Test fetch_pages with number_of_pages set to limit the number of URLs.
    Ensures that only the specified number of URLs are processed.
    """
    # Arrange

    # Mock 'parse_sitemap' to return multiple URLs
    mock_parse_sitemap = mocker.patch(
        'product_school_scraper.services.scraping_service.parse_sitemap',
        return_value=[
            "https://productschool.com/page1",
            "https://productschool.com/page2",
            "https://productschool.com/page3",
            "https://productschool.com/page4",
            "https://productschool.com/page5",
        ]
    )

    # Mock 'requests.get' to return HTML with a <title> tag
    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head><title>Page Title</title></head><body><p>Content.</p></body></html>"

    mock_requests_get = mocker.patch('product_school_scraper.services.scraping_service.requests.get')
    mock_requests_get.return_value = response_mock

    # Mock 'pdfkit.from_url' to succeed
    mock_pdfkit = mocker.patch('product_school_scraper.services.scraping_service.pdfkit.from_url')
    mock_pdfkit.return_value = None

    # Mock 'Path.mkdir' to succeed
    mock_path_mkdir = mocker.patch('product_school_scraper.services.scraping_service.Path.mkdir')
    mock_path_mkdir.return_value = None

    # Mock 'Path.write_text' to prevent actual file writing
    mock_write_text = mocker.patch('product_school_scraper.services.scraping_service.Path.write_text')
    mock_write_text.return_value = None

    # Mock 'clean_html_content' to return cleaned text
    mock_clean_html_content = mocker.patch(
        'product_school_scraper.services.scraping_service.clean_html_content',
        return_value="Content."
    )

    # Mock 'time.sleep' to speed up tests
    mock_sleep = mocker.patch('product_school_scraper.services.scraping_service.time.sleep', return_value=None)

    # Mock the logger's info method
    mock_logger_info = mocker.patch('product_school_scraper.services.scraping_service.logger.info')

    # Act

    # Call the function under test with number_of_pages=3
    fetch_pages(sitemap_url, number_of_pages=3)

    # Assert

    # Ensure 'parse_sitemap' was called correctly
    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)

    # Ensure only the first URL was fetched due to rate-limiting and looping
    # However, since 'fetch_pages' processes URLs sequentially, we need to verify multiple calls

    # Since number_of_pages=3, it should process 3 URLs
    assert mock_requests_get.call_count == 3
    mock_requests_get.assert_any_call("https://productschool.com/page1", timeout=15)
    mock_requests_get.assert_any_call("https://productschool.com/page2", timeout=15)
    mock_requests_get.assert_any_call("https://productschool.com/page3", timeout=15)

    # Ensure 'clean_html_content' was called three times with correct arguments
    assert mock_clean_html_content.call_count == 3
    mock_clean_html_content.assert_any_call("Page Title", ANY)

    # Ensure 'pdfkit.from_url' was called three times
    assert mock_pdfkit.call_count == 3
    mock_pdfkit.assert_any_call("https://productschool.com/page1", "pages/Page Title/page_001.pdf")
    mock_pdfkit.assert_any_call("https://productschool.com/page2", "pages/Page Title/page_002.pdf")
    mock_pdfkit.assert_any_call("https://productschool.com/page3", "pages/Page Title/page_003.pdf")

    # Ensure 'write_text' was called three times
    assert mock_write_text.call_count == 3
    mock_write_text.assert_any_call("Content.", encoding="utf-8")

    # Ensure 'Path.mkdir' was called for each subdirectory
    assert mock_path_mkdir.call_count == 4  # 1 for 'pages' and 3 for each subdir

    # Ensure the rate-limiting log was recorded
    mock_logger_info.assert_any_call("Limiting to 3 pages (per user request).")