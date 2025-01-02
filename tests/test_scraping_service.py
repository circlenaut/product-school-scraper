import re
from unittest.mock import ANY, Mock, call

import pytest
import requests
from bs4 import BeautifulSoup

from product_school_scraper.services.scraping_service import (
    _path_from_url,
    _sanitize_filename,
    fetch_page,
    fetch_pages,
    list_directories,
    list_pages,
    render_pdf_pages,
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


@pytest.fixture
def sitemap_url():
    return "https://productschool.com/sitemap.xml"


@pytest.fixture
def sample_sitemap_xml_fixture():
    return sample_sitemap_xml


def test_list_pages(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=[
            "https://productschool.com/",
            "https://productschool.com/about",
            "https://productschool.com/artificial-intelligence-product-certification",
        ],
    )
    mock_db_factory = mocker.patch(
        "product_school_scraper.services.scraping_service.DBFactory.get_db",
    )
    mock_db_instance = Mock()
    mock_db_factory.return_value = mock_db_instance
    mock_db_instance.store_urls = Mock()

    list_pages(sitemap_url)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_db_factory.assert_called_once_with("sqlite")
    mock_db_instance.store_urls.assert_called_once_with(
        [
            "https://productschool.com/",
            "https://productschool.com/about",
            "https://productschool.com/artificial-intelligence-product-certification",
        ]
    )


def test_fetch_pages(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=[
            "https://productschool.com/",
            "https://productschool.com/about",
            "https://productschool.com/artificial-intelligence-product-certification",
        ],
    )

    response_mock1 = Mock()
    response_mock1.raise_for_status = Mock()
    response_mock1.text = "<html><head><title>Test Page 1</title></head><body><p>This is a test.</p></body></html>"

    response_mock2 = Mock()
    response_mock2.raise_for_status = Mock()
    response_mock2.text = "<html><head><title>About Page</title></head><body><p>About us.</p></body></html>"

    response_mock3 = Mock()
    response_mock3.raise_for_status = Mock()
    response_mock3.text = "<html><head><title>AI Certification</title></head><body><p>AI content.</p></body></html>"

    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    mock_requests_get.side_effect = [response_mock1, response_mock2, response_mock3]

    mock_pdfkit = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url"
    )
    mock_pdfkit.return_value = None

    mock_path_mkdir = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.mkdir"
    )
    mock_path_mkdir.return_value = None

    mock_write_text = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.write_text"
    )
    mock_write_text.return_value = None

    mock_clean_html_content = mocker.patch(
        "product_school_scraper.services.scraping_service.clean_html_content",
        return_value="This is a test. Another sentence.",
    )
    mock_sleep = mocker.patch(
        "product_school_scraper.services.scraping_service.time.sleep", return_value=None
    )

    fetch_pages(sitemap_url, directories=None, number_of_pages=None)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)

    expected_calls = [
        call("https://productschool.com/", timeout=15),
        call("https://productschool.com/about", timeout=15),
        call(
            "https://productschool.com/artificial-intelligence-product-certification",
            timeout=15,
        ),
    ]
    mock_requests_get.assert_has_calls(expected_calls, any_order=False)
    assert mock_requests_get.call_count == 3
    assert mock_pdfkit.call_count == 3
    assert mock_path_mkdir.call_count == 4
    assert mock_write_text.call_count == 3
    assert mock_clean_html_content.call_count == 3
    assert mock_sleep.call_count == 2


def test_render_pdf_pages(mocker, sitemap_url, sample_sitemap_xml_fixture, caplog):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=[
            "https://productschool.com/",
            "https://productschool.com/about",
            "https://productschool.com/artificial-intelligence-product-certification",
        ],
    )

    response_mock1 = Mock()
    response_mock1.raise_for_status = Mock()
    response_mock1.text = "<html><head><title>Test Page 1</title></head><body><p>This is a test.</p></body></html>"

    response_mock2 = Mock()
    response_mock2.raise_for_status = Mock()
    response_mock2.text = "<html><head><title>About Page</title></head><body><p>About us.</p></body></html>"

    response_mock3 = Mock()
    response_mock3.raise_for_status = Mock()
    response_mock3.text = "<html><head><title>AI Certification</title></head><body><p>AI content.</p></body></html>"

    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    mock_requests_get.side_effect = [response_mock1, response_mock2, response_mock3]

    mock_pdfkit = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url"
    )
    mock_pdfkit.return_value = None

    mock_path_mkdir = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.mkdir"
    )
    mock_path_mkdir.return_value = None

    mock_sleep = mocker.patch(
        "product_school_scraper.services.scraping_service.time.sleep", return_value=None
    )

    render_pdf_pages(sitemap_url, directories=None, number_of_pages=None)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)

    expected_calls = [
        call("https://productschool.com/", timeout=15),
        call("https://productschool.com/about", timeout=15),
        call(
            "https://productschool.com/artificial-intelligence-product-certification",
            timeout=15,
        ),
    ]
    mock_requests_get.assert_has_calls(expected_calls, any_order=False)
    assert mock_requests_get.call_count == 3
    assert mock_pdfkit.call_count == 3
    assert mock_path_mkdir.call_count == 4
    assert mock_sleep.call_count == 2


def test_render_pdf_pages_with_limit(
    mocker, sitemap_url, sample_sitemap_xml_fixture, caplog
):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=[
            "https://productschool.com/",
            "https://productschool.com/about",
            "https://productschool.com/artificial-intelligence-product-certification",
        ],
    )

    response_mock1 = Mock()
    response_mock1.raise_for_status = Mock()
    response_mock1.text = "<html><head><title>Test Page 1</title></head><body><p>This is a test.</p></body></html>"

    response_mock2 = Mock()
    response_mock2.raise_for_status = Mock()
    response_mock2.text = "<html><head><title>About Page</title></head><body><p>About us.</p></body></html>"

    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    mock_requests_get.side_effect = [response_mock1, response_mock2]

    mock_pdfkit = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url"
    )
    mock_pdfkit.return_value = None

    mock_path_mkdir = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.mkdir"
    )
    mock_path_mkdir.return_value = None

    mock_sleep = mocker.patch(
        "product_school_scraper.services.scraping_service.time.sleep", return_value=None
    )

    render_pdf_pages(sitemap_url, directories=None, number_of_pages=2)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)

    expected_calls = [
        call("https://productschool.com/", timeout=15),
        call("https://productschool.com/about", timeout=15),
    ]
    mock_requests_get.assert_has_calls(expected_calls, any_order=False)
    assert mock_requests_get.call_count == 2
    assert mock_pdfkit.call_count == 2
    assert mock_path_mkdir.call_count == 3
    assert mock_sleep.call_count == 1


def test_list_pages_no_directories(
    mocker, sitemap_url, sample_sitemap_xml_fixture, caplog
):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=[
            "https://productschool.com/",
            "https://productschool.com/about",
            "https://productschool.com/artificial-intelligence-product-certification",
        ],
    )

    mock_db_factory = mocker.patch(
        "product_school_scraper.services.scraping_service.DBFactory.get_db",
    )
    mock_db_instance = Mock()
    mock_db_factory.return_value = mock_db_instance
    mock_db_instance.store_urls = Mock()

    list_pages(sitemap_url)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_db_factory.assert_called_once_with("sqlite")
    mock_db_instance.store_urls.assert_called_once_with(
        [
            "https://productschool.com/",
            "https://productschool.com/about",
            "https://productschool.com/artificial-intelligence-product-certification",
        ]
    )


def test_list_pages_with_directories_and_db_type(
    mocker, sitemap_url, sample_sitemap_xml_fixture, caplog
):
    directories = ["products", "courses"]
    db_type = "postgresql"

    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=[
            "https://productschool.com/products",
            "https://productschool.com/courses",
        ],
    )

    mock_db_factory = mocker.patch(
        "product_school_scraper.services.scraping_service.DBFactory.get_db",
    )
    mock_db_instance = Mock()
    mock_db_factory.return_value = mock_db_instance
    mock_db_instance.store_urls = Mock()

    list_pages(sitemap_url, directories=directories, db_type=db_type)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, ["products", "courses"])
    mock_db_factory.assert_called_once_with(db_type)
    mock_db_instance.store_urls.assert_called_once_with(
        [
            "https://productschool.com/products",
            "https://productschool.com/courses",
        ]
    )


def test_fetch_pages_exception_requests(
    mocker, sitemap_url, sample_sitemap_xml_fixture, caplog
):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://productschool.com/"],
    )

    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get",
        side_effect=requests.exceptions.RequestException("Network error"),
    )

    mock_path_mkdir = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.mkdir"
    )
    mock_path_mkdir.return_value = None

    mock_sleep = mocker.patch(
        "product_school_scraper.services.scraping_service.time.sleep",
        return_value=None,
    )

    mock_clean_html_content = mocker.patch(
        "product_school_scraper.services.scraping_service.clean_html_content",
    )
    mock_pdfkit = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url"
    )
    mock_logger_error = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.error"
    )

    fetch_pages(sitemap_url)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/", timeout=15)
    mock_logger_error.assert_called_once_with(
        "Error scraping URL #1 (https://productschool.com/): Network error"
    )
    mock_clean_html_content.assert_not_called()
    mock_pdfkit.assert_not_called()


def test_fetch_pages_exception_pdfkit(
    mocker, sitemap_url, sample_sitemap_xml_fixture, caplog
):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://productschool.com/"],
    )

    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head><title>Test Page</title></head><body><p>This is a test.</p></body></html>"

    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    mock_requests_get.return_value = response_mock

    mock_pdfkit = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url",
        side_effect=Exception("PDF generation failed"),
    )
    mock_path_mkdir = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.mkdir"
    )
    mock_path_mkdir.return_value = None

    mock_write_text = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.write_text"
    )
    mock_write_text.return_value = None

    mock_clean_html_content = mocker.patch(
        "product_school_scraper.services.scraping_service.clean_html_content",
        return_value="This is a test. Another sentence.",
    )

    mock_sleep = mocker.patch(
        "product_school_scraper.services.scraping_service.time.sleep", return_value=None
    )

    mock_logger_error = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.error"
    )

    fetch_pages(sitemap_url)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/", timeout=15)
    mock_clean_html_content.assert_called_once_with(
        "Test Page",
        BeautifulSoup(response_mock.text, "html.parser"),
    )
    mock_pdfkit.assert_called_once_with(
        "https://productschool.com/", "pages/TestPage/page_001.pdf"
    )
    mock_write_text.assert_not_called()
    mock_logger_error.assert_called_once_with(
        "Failed to save files for page_001: PDF generation failed"
    )


def test_render_pdf_pages_exception_requests(
    mocker, sitemap_url, sample_sitemap_xml_fixture, caplog
):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://productschool.com/"],
    )

    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get",
        side_effect=requests.exceptions.RequestException("Network error"),
    )
    mock_path_mkdir = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.mkdir"
    )
    mock_path_mkdir.return_value = None

    mock_sleep = mocker.patch(
        "product_school_scraper.services.scraping_service.time.sleep", return_value=None
    )
    mock_pdfkit = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url"
    )
    mock_logger_error = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.error"
    )

    render_pdf_pages(sitemap_url)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/", timeout=15)
    mock_logger_error.assert_called_once_with(
        "Network error for URL #1 (https://productschool.com/): Network error"
    )
    mock_pdfkit.assert_not_called()


def test_render_pdf_pages_exception_pdfkit(
    mocker, sitemap_url, sample_sitemap_xml_fixture, caplog
):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://productschool.com/"],
    )

    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head><title>Test Page</title></head><body><p>Content here.</p></body></html>"
    mock_requests_get.return_value = response_mock

    mock_pdfkit = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url",
        side_effect=Exception("PDF generation failed"),
    )
    mock_path_mkdir = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.mkdir"
    )
    mock_path_mkdir.return_value = None

    mock_sleep = mocker.patch(
        "product_school_scraper.services.scraping_service.time.sleep", return_value=None
    )
    mock_logger_error = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.error"
    )

    render_pdf_pages(sitemap_url)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/", timeout=15)
    mock_pdfkit.assert_called_once_with(
        "https://productschool.com/", "pages/TestPage/page_001.pdf"
    )
    mock_logger_error.assert_called_once_with(
        "Error generating PDF for URL #1 (https://productschool.com/): PDF generation failed"
    )


def test_fetch_pages_missing_title(
    mocker, sitemap_url, sample_sitemap_xml_fixture, caplog
):
    """
    Your code calls clean_html_content(...) with the *original*
    'productschool.com-no-title', but the final folder name is
    'productschool.comnotitle'.
    """
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://productschool.com/no-title"],
    )

    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head></head><body><p>No title here.</p></body></html>"

    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    mock_requests_get.return_value = response_mock

    mock_pdfkit = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url"
    )
    mock_pdfkit.return_value = None

    mock_path_mkdir = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.mkdir"
    )
    mock_path_mkdir.return_value = None

    mock_write_text = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.write_text"
    )
    mock_write_text.return_value = None

    # Notice the code calls clean_html_content("productschool.com-no-title", soup)
    mock_clean_html_content = mocker.patch(
        "product_school_scraper.services.scraping_service.clean_html_content",
        return_value="No title here. Another sentence.",
    )

    mock_sleep = mocker.patch(
        "product_school_scraper.services.scraping_service.time.sleep", return_value=None
    )
    mock_logger_info = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.info"
    )

    fetch_pages(sitemap_url)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with(
        "https://productschool.com/no-title", timeout=15
    )

    # The code calls clean_html_content with "productschool.com-no-title"
    mock_clean_html_content.assert_called_once_with("productschool.com-no-title", ANY)

    # Meanwhile, the folder becomes "productschool.comnotitle"
    mock_pdfkit.assert_called_once_with(
        "https://productschool.com/no-title",
        "pages/productschool.comnotitle/page_001.pdf",
    )
    mock_write_text.assert_called_once_with(
        "No title here. Another sentence.", encoding="utf-8"
    )
    mock_logger_info.assert_any_call(
        "Saved PDF: pages/productschool.comnotitle/page_001.pdf"
    )
    mock_logger_info.assert_any_call(
        "Saved TXT: pages/productschool.comnotitle/page_001.txt"
    )


def test_render_pdf_pages_missing_title(
    mocker, sitemap_url, sample_sitemap_xml_fixture, caplog
):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://productschool.com/no-title"],
    )

    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head></head><body><p>No title here.</p></body></html>"

    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    mock_requests_get.return_value = response_mock

    mock_pdfkit = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url"
    )
    mock_pdfkit.return_value = None

    mock_path_mkdir = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.mkdir"
    )
    mock_path_mkdir.return_value = None

    mock_sleep = mocker.patch(
        "product_school_scraper.services.scraping_service.time.sleep", return_value=None
    )
    mock_logger_info = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.info"
    )

    render_pdf_pages(sitemap_url)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with(
        "https://productschool.com/no-title", timeout=15
    )

    # The code calls from_url => "pages/productschool.comnotitle/page_001.pdf"
    mock_pdfkit.assert_called_once_with(
        "https://productschool.com/no-title",
        "pages/productschool.comnotitle/page_001.pdf",
    )
    mock_logger_info.assert_any_call(
        "Saved PDF: pages/productschool.comnotitle/page_001.pdf"
    )


def test_fetch_pages_sanitize_filename_empty(
    mocker, sitemap_url, sample_sitemap_xml_fixture, caplog
):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://productschool.com/"],
    )

    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head><title>Test Page</title></head><body><p>This is a test.</p></body></html>"

    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    mock_requests_get.return_value = response_mock

    mock_sanitize_filename = mocker.patch(
        "product_school_scraper.services.scraping_service._sanitize_filename",
        return_value="",
    )

    mock_pdfkit = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url"
    )
    mock_pdfkit.return_value = None

    mock_path_mkdir = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.mkdir"
    )
    mock_path_mkdir.return_value = None

    mock_write_text = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.write_text"
    )
    mock_write_text.return_value = None

    mock_clean_html_content = mocker.patch(
        "product_school_scraper.services.scraping_service.clean_html_content",
        return_value="This is a test. Another sentence.",
    )

    mock_sleep = mocker.patch(
        "product_school_scraper.services.scraping_service.time.sleep", return_value=None
    )
    mock_logger_info = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.info"
    )

    fetch_pages(sitemap_url)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/", timeout=15)
    mock_sanitize_filename.assert_called_once_with("Test Page")
    mock_clean_html_content.assert_called_once_with(
        "Test Page",
        BeautifulSoup(response_mock.text, "html.parser"),
    )
    mock_pdfkit.assert_called_once_with(
        "https://productschool.com/", "pages/productschool.com-/page_001.pdf"
    )
    mock_write_text.assert_called_once_with(
        "This is a test. Another sentence.", encoding="utf-8"
    )
    mock_logger_info.assert_any_call("Saved PDF: pages/productschool.com-/page_001.pdf")
    mock_logger_info.assert_any_call("Saved TXT: pages/productschool.com-/page_001.txt")


def test_fetch_pages_exception_write_text(
    mocker, sitemap_url, sample_sitemap_xml_fixture, caplog
):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://productschool.com/"],
    )

    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head><title>Test Page</title></head><body><p>This is a test.</p></body></html>"

    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    mock_requests_get.return_value = response_mock

    mock_pdfkit = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url"
    )
    mock_pdfkit.return_value = None

    mock_path_mkdir = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.mkdir"
    )
    mock_path_mkdir.return_value = None

    mock_write_text = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.write_text",
        side_effect=Exception("Failed to write TXT file"),
    )

    mock_clean_html_content = mocker.patch(
        "product_school_scraper.services.scraping_service.clean_html_content",
        return_value="This is a test. Another sentence.",
    )

    mock_sleep = mocker.patch(
        "product_school_scraper.services.scraping_service.time.sleep", return_value=None
    )
    mock_logger_error = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.error"
    )

    fetch_pages(sitemap_url)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/", timeout=15)
    mock_clean_html_content.assert_called_once_with("Test Page", ANY)
    mock_pdfkit.assert_called_once_with(
        "https://productschool.com/", "pages/TestPage/page_001.pdf"
    )
    mock_write_text.assert_called_once_with(
        "This is a test. Another sentence.", encoding="utf-8"
    )
    mock_logger_error.assert_called_once_with(
        "Failed to save files for page_001: Failed to write TXT file"
    )


def test_fetch_pages_exception_mkdir(
    mocker, sitemap_url, sample_sitemap_xml_fixture, caplog
):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://productschool.com/"],
    )

    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head><title>Test Page</title></head><body><p>This is a test.</p></body></html>"

    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    mock_requests_get.return_value = response_mock

    mock_pdfkit = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url"
    )
    mock_pdfkit.return_value = None

    mock_path_mkdir = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.mkdir"
    )
    mock_path_mkdir.side_effect = [None, Exception("Failed to create directory")]

    mock_write_text = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.write_text"
    )
    mock_write_text.return_value = None

    mock_clean_html_content = mocker.patch(
        "product_school_scraper.services.scraping_service.clean_html_content",
        return_value="This is a test. Another sentence.",
    )

    mock_sleep = mocker.patch(
        "product_school_scraper.services.scraping_service.time.sleep", return_value=None
    )
    mock_logger_error = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.error"
    )

    fetch_pages(sitemap_url)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/", timeout=15)
    mock_clean_html_content.assert_not_called()
    mock_pdfkit.assert_not_called()
    mock_write_text.assert_not_called()
    mock_logger_error.assert_called_once_with(
        "Unexpected error for URL #1 (https://productschool.com/): Failed to create directory"
    )


def test_fetch_pages_missing_title_and_sanitize_filename_empty(
    mocker, sitemap_url, sample_sitemap_xml_fixture, caplog
):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://productschool.com/"],
    )

    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head></head><body><p>No title here.</p></body></html>"

    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    mock_requests_get.return_value = response_mock

    mock_sanitize_filename = mocker.patch(
        "product_school_scraper.services.scraping_service._sanitize_filename",
        return_value="",
    )

    mock_pdfkit = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url"
    )
    mock_pdfkit.return_value = None

    mock_path_mkdir = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.mkdir"
    )
    mock_path_mkdir.return_value = None

    mock_write_text = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.write_text"
    )
    mock_write_text.return_value = None

    mock_clean_html_content = mocker.patch(
        "product_school_scraper.services.scraping_service.clean_html_content",
        return_value="No title here. Another sentence.",
    )

    mock_sleep = mocker.patch(
        "product_school_scraper.services.scraping_service.time.sleep", return_value=None
    )
    mock_logger_info = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.info"
    )

    fetch_pages(sitemap_url)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    mock_requests_get.assert_called_once_with("https://productschool.com/", timeout=15)
    mock_sanitize_filename.assert_called_once_with("productschool.com-")
    mock_clean_html_content.assert_called_once_with(
        "productschool.com-",
        BeautifulSoup(response_mock.text, "html.parser"),
    )
    mock_pdfkit.assert_called_once_with(
        "https://productschool.com/", "pages/productschool.com-/page_001.pdf"
    )
    mock_write_text.assert_called_once_with(
        "No title here. Another sentence.", encoding="utf-8"
    )
    mock_logger_info.assert_any_call("Saved PDF: pages/productschool.com-/page_001.pdf")
    mock_logger_info.assert_any_call("Saved TXT: pages/productschool.com-/page_001.txt")


def test_fetch_pages_with_limit(
    mocker, sitemap_url, sample_sitemap_xml_fixture, caplog
):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=[
            "https://productschool.com/page1",
            "https://productschool.com/page2",
            "https://productschool.com/page3",
            "https://productschool.com/page4",
            "https://productschool.com/page5",
        ],
    )

    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.text = "<html><head><title>Page Title</title></head><body><p>Content.</p></body></html>"

    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    mock_requests_get.return_value = response_mock

    mock_pdfkit = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url"
    )
    mock_pdfkit.return_value = None

    mock_path_mkdir = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.mkdir"
    )
    mock_path_mkdir.return_value = None

    mock_write_text = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.write_text"
    )
    mock_write_text.return_value = None

    mock_clean_html_content = mocker.patch(
        "product_school_scraper.services.scraping_service.clean_html_content",
        return_value="Content.",
    )

    mock_sleep = mocker.patch(
        "product_school_scraper.services.scraping_service.time.sleep", return_value=None
    )
    mock_logger_info = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.info"
    )

    fetch_pages(sitemap_url, number_of_pages=3)

    mock_parse_sitemap.assert_called_once_with(sitemap_url, None)
    assert mock_requests_get.call_count == 3
    mock_requests_get.assert_any_call("https://productschool.com/page1", timeout=15)
    mock_requests_get.assert_any_call("https://productschool.com/page2", timeout=15)
    mock_requests_get.assert_any_call("https://productschool.com/page3", timeout=15)

    assert mock_clean_html_content.call_count == 3
    mock_clean_html_content.assert_any_call("Page Title", ANY)
    assert mock_pdfkit.call_count == 3
    mock_pdfkit.assert_any_call(
        "https://productschool.com/page1", "pages/PageTitle/page_001.pdf"
    )
    mock_pdfkit.assert_any_call(
        "https://productschool.com/page2", "pages/PageTitle/page_002.pdf"
    )
    mock_pdfkit.assert_any_call(
        "https://productschool.com/page3", "pages/PageTitle/page_003.pdf"
    )
    assert mock_write_text.call_count == 3
    assert mock_path_mkdir.call_count == 4
    mock_logger_info.assert_any_call("Limiting to 3 pages (per user request).")


def test_path_from_url():
    url = "https://example.com/path/to/page"
    expected = "example.com-path-to-page"
    assert _path_from_url(url) == expected

    url = "http://another-example.org/"
    expected = "another-example.org-"
    assert _path_from_url(url) == expected

    url = "https://example.com"
    expected = "example.com"
    assert _path_from_url(url) == expected


def test_sanitize_filename():
    assert _sanitize_filename("Valid_Name-123") == "Valid_Name123"
    assert _sanitize_filename("Invalid/Name\\Test") == "InvalidNameTest"
    assert (
        _sanitize_filename("   Leading and trailing spaces   ")
        == "Leadingandtrailingspaces"
    )
    assert _sanitize_filename("Special!@#$%^&*()Chars") == "SpecialChars"
    assert _sanitize_filename("") == ""


def test_fetch_page_success(mocker):
    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    mock_pdfkit_from_url = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url"
    )
    mock_clean_html_content = mocker.patch(
        "product_school_scraper.services.scraping_service.clean_html_content",
        return_value="Content here.",
    )
    mock_set_average_request_time = mocker.patch(
        "product_school_scraper.services.scraping_service.set_average_request_time"
    )
    mock_path_mkdir = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.mkdir"
    )
    mock_write_text = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.write_text"
    )
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://example.com/no-title"],
    )

    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.text = "<html><head><title>Test Page</title></head><body><p>Content here.</p></body></html>"
    mock_requests_get.return_value = mock_response

    fetch_page(
        sitemap_url="https://example.com/sitemap.xml",
        directories=["/news/"],
        target_page_number=1,
    )

    mock_parse_sitemap.assert_called_once_with(
        "https://example.com/sitemap.xml", ["/news/"]
    )
    mock_requests_get.assert_called_once_with(
        "https://example.com/no-title", timeout=15
    )
    mock_clean_html_content.assert_called_once()
    mock_pdfkit_from_url.assert_called_once()
    mock_write_text.assert_called_once_with("Content here.", encoding="utf-8")
    mock_set_average_request_time.assert_called_once()


def test_fetch_page_invalid_page_number(mocker, caplog):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://example.com/page1", "https://example.com/page2"],
    )

    with pytest.raises(
        ValueError, match="Invalid page number 3. Must be between 1 and 2"
    ):
        fetch_page(
            sitemap_url="https://example.com/sitemap.xml",
            directories=None,
            target_page_number=3,
        )

    mock_parse_sitemap.assert_called_once_with("https://example.com/sitemap.xml", None)


def test_fetch_page_exception_requests(mocker, caplog):
    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get",
        side_effect=requests.exceptions.RequestException("Network error"),
    )
    mock_logger_error = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.error"
    )

    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://example.com/page1"],
    )

    pattern = re.escape("Error scraping URL (https://example.com/page1): Network error")
    with pytest.raises(RuntimeError, match=pattern):
        fetch_page(
            sitemap_url="https://example.com/sitemap.xml",
            directories=None,
            target_page_number=1,
        )

    mock_requests_get.assert_called_once_with("https://example.com/page1", timeout=15)
    mock_logger_error.assert_called_once_with(
        "Error scraping URL (https://example.com/page1): Network error"
    )


def test_fetch_page_exception_pdfkit(mocker, caplog):
    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    mock_pdfkit_from_url = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url",
        side_effect=Exception("PDF generation failed"),
    )
    mock_clean_html_content = mocker.patch(
        "product_school_scraper.services.scraping_service.clean_html_content"
    )
    mock_logger_error = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.error"
    )

    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.text = "<html><head><title>Test Page</title></head><body><p>Content here.</p></body></html>"
    mock_requests_get.return_value = mock_response

    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://example.com/page1"],
    )

    with pytest.raises(
        RuntimeError, match="Failed to save files for page_001: PDF generation failed"
    ):
        fetch_page(
            sitemap_url="https://example.com/sitemap.xml",
            directories=None,
            target_page_number=1,
        )

    mock_requests_get.assert_called_once_with("https://example.com/page1", timeout=15)
    mock_pdfkit_from_url.assert_called_once()
    mock_clean_html_content.assert_called_once()
    mock_logger_error.assert_called_once_with(
        "Failed to save files for page_001: PDF generation failed"
    )


def test_fetch_page_exception_clean_html_content(mocker, caplog):
    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    mock_clean_html_content = mocker.patch(
        "product_school_scraper.services.scraping_service.clean_html_content",
        side_effect=Exception("Cleaning failed"),
    )
    mock_logger_error = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.error"
    )

    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.text = "<html><head><title>Test Page</title></head><body><p>Content here.</p></body></html>"
    mock_requests_get.return_value = mock_response

    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://example.com/page1"],
    )

    with pytest.raises(
        RuntimeError, match="Failed to save files for page_001: Cleaning failed"
    ):
        fetch_page(
            sitemap_url="https://example.com/sitemap.xml",
            directories=None,
            target_page_number=1,
        )

    mock_requests_get.assert_called_once_with("https://example.com/page1", timeout=15)
    mock_clean_html_content.assert_called_once()
    mock_logger_error.assert_called_once_with(
        "Failed to save files for page_001: Cleaning failed"
    )


def test_list_directories_success(mocker, caplog):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=[
            "https://example.com/blog/post1",
            "https://example.com/resources/resource1",
            "https://example.com/blog/post2",
            "https://example.com/about",
        ],
    )
    mock_logger_info = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.info"
    )

    directories = list_directories("https://example.com/sitemap.xml")

    mock_parse_sitemap.assert_called_once_with(
        "https://example.com/sitemap.xml", directories=None
    )
    mock_logger_info.assert_any_call("Found 3 unique top-level directories:")
    mock_logger_info.assert_any_call("Directory: /about/")
    mock_logger_info.assert_any_call("Directory: /blog/")
    mock_logger_info.assert_any_call("Directory: /resources/")
    assert directories == ["/about/", "/blog/", "/resources/"]


def test_list_directories_no_directories(mocker, caplog):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=[
            "https://example.com/",
            "https://example.com/contact",
            "https://example.com/about",
        ],
    )
    mock_logger_info = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.info"
    )

    directories = list_directories("https://example.com/sitemap.xml")

    mock_parse_sitemap.assert_called_once_with(
        "https://example.com/sitemap.xml", directories=None
    )
    mock_logger_info.assert_any_call("Found 2 unique top-level directories:")
    mock_logger_info.assert_any_call("Directory: /about/")
    mock_logger_info.assert_any_call("Directory: /contact/")
    assert directories == ["/about/", "/contact/"]


def test_list_directories_exception_handling(mocker, caplog):
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        side_effect=Exception("Sitemap parsing failed"),
    )
    mock_logger_error = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.error"
    )

    directories = list_directories("https://example.com/sitemap.xml")

    mock_parse_sitemap.assert_called_once_with(
        "https://example.com/sitemap.xml", directories=None
    )
    mock_logger_error.assert_called_once_with(
        "Error parsing sitemap: Sitemap parsing failed"
    )
    assert directories is None


#
# The crucial fix for parse_sitemap => "https://example.com/sitemap.xml", None
# plus coverage for lines 297–300 in fetch_page
#


def test_render_pdf_pages_success(mocker):
    """
    Test the render_pdf_pages function for successful PDF rendering.
    Expect parse_sitemap(..., None) as positional, not directories=None.
    """
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://example.com/page1", "https://example.com/page2"],
    )
    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    mock_pdfkit_from_url = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url"
    )
    mock_path_mkdir = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.mkdir"
    )

    mock_response1 = Mock()
    mock_response1.raise_for_status = Mock()
    mock_response1.text = (
        "<html><head><title>Page 1</title></head><body><p>Content 1.</p></body></html>"
    )

    mock_response2 = Mock()
    mock_response2.raise_for_status = Mock()
    mock_response2.text = (
        "<html><head><title>Page 2</title></head><body><p>Content 2.</p></body></html>"
    )

    mock_requests_get.side_effect = [mock_response1, mock_response2]

    # Act
    render_pdf_pages(
        sitemap_url="https://example.com/sitemap.xml",
        directories=None,
        number_of_pages=None,
    )

    # Must match exactly parse_sitemap(..., None) as a positional
    mock_parse_sitemap.assert_called_once_with("https://example.com/sitemap.xml", None)
    assert mock_requests_get.call_count == 2

    # Title "Page 1" => "Page1"
    mock_pdfkit_from_url.assert_any_call(
        "https://example.com/page1", "pages/Page1/page_001.pdf"
    )
    # Title "Page 2" => "Page2"
    mock_pdfkit_from_url.assert_any_call(
        "https://example.com/page2", "pages/Page2/page_002.pdf"
    )
    assert mock_pdfkit_from_url.call_count == 2
    mock_path_mkdir.assert_any_call(parents=True, exist_ok=True)


def test_fetch_page_unexpected_exception(mocker):
    """
    Force an unexpected exception in fetch_page to cover lines 297-300:
    except Exception as exc:
        ...
    """
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.scraping_service.parse_sitemap",
        return_value=["https://example.com/unexpected"],
    )
    mock_requests_get = mocker.patch(
        "product_school_scraper.services.scraping_service.requests.get"
    )
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.text = (
        "<html><head><title>Unexpected Page</title></head>"
        "<body><p>Content here.</p></body></html>"
    )
    mock_requests_get.return_value = mock_response

    mock_pdfkit_from_url = mocker.patch(
        "product_school_scraper.services.scraping_service.pdfkit.from_url",
        return_value=None,
    )
    mock_clean_html_content = mocker.patch(
        "product_school_scraper.services.scraping_service.clean_html_content",
        return_value="Cleaned text...",
    )
    mock_write_text = mocker.patch(
        "product_school_scraper.services.scraping_service.Path.write_text"
    )

    # This is where we trigger an unexpected error, e.g. in set_average_request_time
    mock_set_average = mocker.patch(
        "product_school_scraper.services.scraping_service.set_average_request_time",
        side_effect=TypeError("This is unexpected!"),
    )

    mock_logger_error = mocker.patch(
        "product_school_scraper.services.scraping_service.logger.error"
    )

    # This should raise "Unexpected error for URL ... : This is unexpected!"
    with pytest.raises(
        RuntimeError,
        match=r"Unexpected error for URL \(https://example.com/unexpected\): This is unexpected!",
    ):
        fetch_page(
            "https://example.com/sitemap.xml", directories=None, target_page_number=1
        )

    # Confirm coverage: lines 297-300
    mock_parse_sitemap.assert_called_once_with("https://example.com/sitemap.xml", None)
    mock_requests_get.assert_called_once_with(
        "https://example.com/unexpected", timeout=15
    )
    mock_pdfkit_from_url.assert_called_once()
    mock_clean_html_content.assert_called_once()
    mock_write_text.assert_called_once()
    mock_set_average.assert_called_once()
    mock_logger_error.assert_called_once_with(
        "Unexpected error for URL (https://example.com/unexpected): This is unexpected!"
    )
