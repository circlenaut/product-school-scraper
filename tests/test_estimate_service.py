from product_school_scraper.services.estimate_service import estimate_time


def test_estimate_time(mocker):
    mock_urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
    ]
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.estimate_service.parse_sitemap",
        return_value=mock_urls,
    )
    mock_logger = mocker.patch(
        "product_school_scraper.services.estimate_service.logger.info",
    )

    # Mock get_average_request_time to return a specific value
    mock_get_avg_time = mocker.patch(
        "product_school_scraper.services.estimate_service.get_average_request_time",
        return_value=0.5,
    )

    estimate_time("https://example.com/sitemap.xml")
    mock_parse_sitemap.assert_called_once_with("https://example.com/sitemap.xml", None)

    # Assert specific log messages were called
    mock_logger.assert_any_call(
        "Estimating time for sitemap at: https://example.com/sitemap.xml"
    )
    mock_logger.assert_any_call("Average request time from DB: 0.50 seconds")
    mock_logger.assert_any_call("Number of URLs: 3")
    mock_logger.assert_any_call("Rate limit: 10 seconds per request")
    mock_logger.assert_any_call("Average request time: 0.50 seconds")
    mock_logger.assert_any_call("Per request time (max): 10.00 seconds")
    mock_logger.assert_any_call("Estimated total requests time: 30.00 seconds")
    mock_logger.assert_any_call("Total estimated time w/ overhead: 40.00 seconds")


def test_estimate_time_with_directories(mocker):
    mock_urls = [
        "https://example.com/blog/page1",
        "https://example.com/blog/page2",
    ]
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.estimate_service.parse_sitemap",
        return_value=mock_urls,
    )
    mock_logger = mocker.patch(
        "product_school_scraper.services.estimate_service.logger.info",
    )

    # Mock get_average_request_time to return a specific value
    mock_get_avg_time = mocker.patch(
        "product_school_scraper.services.estimate_service.get_average_request_time",
        return_value=0.5,
    )

    directories = ["/blog/"]
    estimate_time("https://example.com/sitemap.xml", directories)
    mock_parse_sitemap.assert_called_once_with(
        "https://example.com/sitemap.xml", directories
    )

    # Assert specific log messages were called
    mock_logger.assert_any_call(
        "Estimating time for sitemap at: https://example.com/sitemap.xml"
    )
    mock_logger.assert_any_call("Average request time from DB: 0.50 seconds")
    mock_logger.assert_any_call("Number of URLs: 2")
    mock_logger.assert_any_call("Rate limit: 10 seconds per request")
    mock_logger.assert_any_call("Average request time: 0.50 seconds")
    mock_logger.assert_any_call("Per request time (max): 10.00 seconds")
    mock_logger.assert_any_call("Estimated total requests time: 20.00 seconds")
    mock_logger.assert_any_call("Total estimated time w/ overhead: 30.00 seconds")


def test_estimate_time_zero_urls(mocker):
    mock_urls = []
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.estimate_service.parse_sitemap",
        return_value=mock_urls,
    )
    mock_logger = mocker.patch(
        "product_school_scraper.services.estimate_service.logger.info",
    )

    # Mock get_average_request_time to return a specific value
    mock_get_avg_time = mocker.patch(
        "product_school_scraper.services.estimate_service.get_average_request_time",
        return_value=0.5,
    )

    estimate_time("https://example.com/sitemap.xml")
    mock_parse_sitemap.assert_called_once_with("https://example.com/sitemap.xml", None)

    # Assert specific log messages were called
    mock_logger.assert_any_call(
        "Estimating time for sitemap at: https://example.com/sitemap.xml"
    )
    mock_logger.assert_any_call("Average request time from DB: 0.50 seconds")
    mock_logger.assert_any_call("Number of URLs: 0")
    mock_logger.assert_any_call("Rate limit: 10 seconds per request")
    mock_logger.assert_any_call("Average request time: 0.50 seconds")
    mock_logger.assert_any_call("Per request time (max): 10.00 seconds")
    mock_logger.assert_any_call("Estimated total requests time: 0.00 seconds")
    mock_logger.assert_any_call("Total estimated time w/ overhead: 10.00 seconds")


def test_estimate_time_with_default_average_time(mocker):
    # Mock sitemap URLs
    mock_urls = ["https://example.com/page1", "https://example.com/page2"]

    # Mock the parse_sitemap function to return mock_urls
    mock_parse_sitemap = mocker.patch(
        "product_school_scraper.services.estimate_service.parse_sitemap",
        return_value=mock_urls,
    )

    # Mock the logger.info method
    mock_logger = mocker.patch(
        "product_school_scraper.services.estimate_service.logger.info",
    )

    # Mock get_average_request_time to return None
    mock_get_avg_time = mocker.patch(
        "product_school_scraper.services.estimate_service.get_average_request_time",
        return_value=None,
    )

    # Define directories if needed, else pass None
    directories = None

    # Call the function under test
    estimate_time("https://example.com/sitemap.xml", directories)

    # Assertions to ensure parse_sitemap was called correctly
    mock_parse_sitemap.assert_called_once_with(
        "https://example.com/sitemap.xml", directories
    )

    # Assert that the default average request time was used
    mock_logger.assert_any_call(
        "No average request time found in DB. Using default: 1.00 seconds"
    )

    # Assert that the number of URLs is correct
    mock_logger.assert_any_call("Number of URLs: 2")

    # Assert other log messages
    mock_logger.assert_any_call("Rate limit: 10 seconds per request")
    mock_logger.assert_any_call("Average request time: 1.00 seconds")
    mock_logger.assert_any_call("Per request time (max): 10.00 seconds")
    mock_logger.assert_any_call("Estimated total requests time: 20.00 seconds")
    mock_logger.assert_any_call("Total estimated time w/ overhead: 30.00 seconds")
