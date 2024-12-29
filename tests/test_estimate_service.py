# tests/test_estimate_service.py
import pytest
from unittest.mock import Mock
from product_school_scraper.services.estimate_service import estimate_time
from product_school_scraper.parsing.sitemap_parser import parse_sitemap
from product_school_scraper.utils.logger import logger

def test_estimate_time(mocker):
    mock_urls = ["https://example.com/page1", "https://example.com/page2", "https://example.com/page3"]
    mock_parse_sitemap = mocker.patch('product_school_scraper.services.estimate_service.parse_sitemap', return_value=mock_urls)
    mock_logger = mocker.patch.object(logger, 'info')

    estimate_time("https://example.com/sitemap.xml")
    mock_parse_sitemap.assert_called_once_with("https://example.com/sitemap.xml", None)
    assert "Number of URLs: 3" in mock_logger.call_args_list[-3][0][0]
    assert "Best-case time: 0.30 seconds" in mock_logger.call_args_list[-2][0][0]
    assert "Total time w/ overhead: 1.30 seconds" in mock_logger.call_args_list[-1][0][0]

def test_estimate_time_with_directories(mocker):
    mock_urls = ["https://example.com/blog/page1", "https://example.com/blog/page2"]
    mock_parse_sitemap = mocker.patch('product_school_scraper.services.estimate_service.parse_sitemap', return_value=mock_urls)
    mock_logger = mocker.patch.object(logger, 'info')

    directories = ["/blog/"]
    estimate_time("https://example.com/sitemap.xml", directories)
    mock_parse_sitemap.assert_called_once_with("https://example.com/sitemap.xml", directories)
    assert "Number of URLs: 2" in mock_logger.call_args_list[-3][0][0]
    assert "Best-case time: 0.20 seconds" in mock_logger.call_args_list[-2][0][0]
    assert "Total time w/ overhead: 1.20 seconds" in mock_logger.call_args_list[-1][0][0]