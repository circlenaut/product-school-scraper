from bs4 import BeautifulSoup

from product_school_scraper.services.cleaning_service import (
    clean_html_content,
    fix_missing_space_after_period,
    remove_boilerplate_phrases,
)


def test_remove_boilerplate_phrases_middle():
    """
    Test removing a boilerplate phrase located in the middle of the text.
    """
    text = "This is a test. Subscribe to The Product Blog. Another sentence."
    cleaned = remove_boilerplate_phrases(text)

    # After removal, expect single space replacing the phrase and punctuation
    expected = "This is a test. Another sentence."
    assert "Subscribe to The Product Blog" not in cleaned
    assert cleaned == expected


def test_remove_boilerplate_phrases_start():
    """
    Test removing a boilerplate phrase located at the beginning of the text.
    """
    text = "Subscribe to The Product Blog. This is a test. Another sentence."
    cleaned = remove_boilerplate_phrases(text)

    # After removal, expect the phrase and following punctuation to be removed
    expected = "This is a test. Another sentence."
    assert "Subscribe to The Product Blog" not in cleaned
    assert cleaned == expected


def test_remove_boilerplate_phrases_end():
    """
    Test removing a boilerplate phrase located at the end of the text.
    """
    text = "This is a test. Another sentence. Subscribe to The Product Blog."
    cleaned = remove_boilerplate_phrases(text)

    # After removal, expect the phrase and preceding punctuation to be removed
    expected = "This is a test. Another sentence."
    assert "Subscribe to The Product Blog" not in cleaned
    assert cleaned == expected


def test_remove_boilerplate_phrases_multiple_occurrences():
    """
    Test removing multiple occurrences of a boilerplate phrase in the text.
    """
    text = (
        "Subscribe to The Product Blog. This is a test. "
        "Subscribe to The Product Blog. Another sentence."
    )
    cleaned = remove_boilerplate_phrases(text)

    # After removal, expect both phrases and their punctuation to be removed
    expected = "This is a test. Another sentence."
    assert "Subscribe to The Product Blog" not in cleaned
    assert cleaned == expected


def test_remove_boilerplate_phrases_case_insensitive():
    """
    Test removing a boilerplate phrase regardless of its case.
    """
    text = "This is a test. subscribe to the product blog. Another sentence."
    cleaned = remove_boilerplate_phrases(text)

    # Since the function is case-insensitive, the phrase should be removed
    expected = "This is a test. Another sentence."
    assert "subscribe to the product blog" not in cleaned
    assert cleaned == expected


def test_remove_boilerplate_phrases_with_punctuation():
    """
    Test removing a boilerplate phrase followed by different punctuation.
    """
    text = "This is a test! Subscribe to The Product Blog? Another sentence."
    cleaned = remove_boilerplate_phrases(text)

    # After removal, expect the phrase and its punctuation to be removed
    expected = "This is a test! Another sentence."
    assert "Subscribe to The Product Blog" not in cleaned
    assert cleaned == expected


def test_fix_missing_space_after_period():
    """
    Test fixing missing space after a period.
    """
    text = "This is a sentence.Another sentence without space."
    fixed = fix_missing_space_after_period(text)
    expected = "This is a sentence. Another sentence without space."
    assert fixed == expected


def test_fix_missing_space_after_period_already_correct():
    """
    Test that text with correct spacing remains unchanged.
    """
    text = "This is a sentence. Another sentence with space."
    fixed = fix_missing_space_after_period(text)
    expected = "This is a sentence. Another sentence with space."
    assert fixed == expected


def test_clean_html_content():
    """
    Test cleaning HTML content by removing boilerplate elements and phrases.
    """
    html_content = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <header><nav>Navigation Bar</nav></header>
            <main>
                <p>This is a test. Subscribe to The Product Blog. Another sentence.</p>
            </main>
            <footer>Footer Content</footer>
        </body>
    </html>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    cleaned = clean_html_content("Test Page", soup)

    # After removal, expect the phrase and its punctuation to be removed
    expected = "This is a test. Another sentence."
    assert "Subscribe to The Product Blog" not in cleaned
    assert cleaned == expected


def test_clean_html_content_with_missing_main():
    """
    Test cleaning HTML content when <main> tag is missing.
    """
    html_content = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <header><nav>Navigation Bar</nav></header>
            <div>
                <p>This is a test. Subscribe to The Product Blog. Another sentence.</p>
            </div>
            <footer>Footer Content</footer>
        </body>
    </html>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    cleaned = clean_html_content("Test Page", soup)

    # After removal, expect the phrase and its punctuation to be removed
    # Including the page title since <main> is missing and <head> is not excluded
    expected = "Test Page This is a test. Another sentence."
    assert "Subscribe to The Product Blog" not in cleaned
    assert cleaned == expected


def test_clean_html_content_empty():
    """
    Test cleaning HTML content that has no main content.
    """
    html_content = """
    <html>
        <head><title>Empty Page</title></head>
        <body>
            <header><nav>Navigation Bar</nav></header>
            <main></main>
            <footer>Footer Content</footer>
        </body>
    </html>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    cleaned = clean_html_content("Empty Page", soup)
    expected = ""
    assert cleaned == expected


def test_clean_html_content_empty():
    """
    Test cleaning HTML content that has no main content.
    """
    html_content = """
    <html>
        <head><title>Empty Page</title></head>
        <body>
            <header><nav>Navigation Bar</nav></header>
            <main></main>
            <footer>Footer Content</footer>
        </body>
    </html>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    cleaned = clean_html_content("Empty Page", soup)
    expected = ""
    assert cleaned == expected


def test_clean_html_content_exception(mocker):
    """
    Test that clean_html_content handles exceptions and returns an empty string.
    """
    # Create a mock BeautifulSoup object
    mock_soup = mocker.Mock(spec=BeautifulSoup)

    # Configure the mock to raise an exception when find_all is called
    mock_soup.find_all.side_effect = Exception("Test exception")

    # Patch the logger's error method
    mock_logger_error = mocker.patch(
        "product_school_scraper.services.cleaning_service.logger.error"
    )

    # Call the function with the mocked soup
    cleaned = clean_html_content("Test Page", mock_soup)

    # Assert that the function returns an empty string
    assert cleaned == ""

    # Assert that logger.error was called with the correct message
    mock_logger_error.assert_called_once_with(
        "Error cleaning page 'Test Page': Test exception"
    )
