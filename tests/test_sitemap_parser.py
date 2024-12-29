# tests/test_sitemap_parser.py
import pytest
from unittest.mock import Mock
from product_school_scraper.parsing.sitemap_parser import parse_sitemap
import requests

@pytest.fixture
def mock_sitemap_xml():
    return """
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://example.com/blog/page1</loc>
        </url>
        <url>
            <loc>https://example.com/blog/page2</loc>
        </url>
        <url>
            <loc>https://example.com/contact</loc>
        </url>
    </urlset>
    """

def test_parse_sitemap_all_urls(mocker, mock_sitemap_xml):
    mock_response = Mock()
    mock_response.content = mock_sitemap_xml.encode('utf-8')
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)

    urls = parse_sitemap("https://example.com/sitemap.xml")
    assert len(urls) == 3
    assert "https://example.com/blog/page1" in urls
    assert "https://example.com/blog/page2" in urls
    assert "https://example.com/contact" in urls

def test_parse_sitemap_filtered(mocker, mock_sitemap_xml):
    mock_response = Mock()
    mock_response.content = mock_sitemap_xml.encode('utf-8')
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)

    directories = ["/blog/"]
    urls = parse_sitemap("https://example.com/sitemap.xml", directories)
    assert len(urls) == 2
    assert "https://example.com/blog/page1" in urls
    assert "https://example.com/blog/page2" in urls
    assert "https://example.com/contact" not in urls

def test_parse_sitemap_no_urls(mocker):
    mock_response = Mock()
    mock_response.content = "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'></urlset>".encode('utf-8')
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)

    urls = parse_sitemap("https://example.com/empty_sitemap.xml")
    assert urls == []

def test_parse_sitemap_request_failure(mocker):
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Failed to fetch"))
    with pytest.raises(requests.exceptions.RequestException):
        parse_sitemap("https://example.com/invalid_sitemap.xml")