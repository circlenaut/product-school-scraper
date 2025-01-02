from pathlib import Path
from unittest.mock import MagicMock

from bs4 import BeautifulSoup

from product_school_scraper.services.cleaning_service import (
    clean_html_content,
    fix_missing_space_after_period,
    merge_text_files,
    remove_boilerplate_phrases,
    rename_and_organize_files,
    sanitize_filename,
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


def test_fix_missing_space_after_period_multiple():
    """
    Test fix_missing_space_after_period with multiple missing spaces.
    """
    text = "This is sentence one.This is sentence two.Another one."
    fixed = fix_missing_space_after_period(text)
    expected = "This is sentence one. This is sentence two. Another one."
    assert fixed == expected


def test_sanitize_filename():
    """
    Test the sanitize_filename function with various inputs.
    """
    # Assuming the function replaces invalid chars with '_' and lowercases the filename
    assert sanitize_filename("Valid_Filename-123") == "valid_filename_123"
    assert sanitize_filename("Invalid/Name\\Test") == "invalid_name_test"
    assert sanitize_filename("   Spaces   ") == "spaces"
    assert sanitize_filename("Special!@#$%^&*()Chars") == "special_chars"
    assert sanitize_filename("") == ""


def test_rename_and_organize_files(mocker):
    """
    Test the rename_and_organize_files function.
    """
    # Mock Path and shutil.copy2
    mock_path_cls = mocker.patch(
        "product_school_scraper.services.cleaning_service.Path", autospec=True
    )
    mock_shutil_copy2 = mocker.patch(
        "product_school_scraper.services.cleaning_service.shutil.copy2"
    )

    # Setup mock directories and files
    mock_pages_path = MagicMock(spec=Path)
    mock_result_path = MagicMock(spec=Path)
    mock_cleaned_pages_path = MagicMock(spec=Path)
    mock_page_dir = MagicMock(spec=Path)
    mock_page_dir.is_dir.return_value = True
    mock_page_dir.name = "TestDir"
    mock_page_dir.glob.return_value = [
        MagicMock(name="file1.txt"),
        MagicMock(name="file2.txt"),
    ]

    mock_pages_path.iterdir.return_value = [mock_page_dir]

    # Define side effect for Path constructor
    def path_side_effect(arg, *args, **kwargs):
        if arg == "pages":
            return mock_pages_path
        if arg == "result":
            return mock_result_path
        if arg == "result/cleaned_pages":
            return mock_cleaned_pages_path
        return MagicMock(spec=Path)

    mock_path_cls.side_effect = path_side_effect

    # Mock the division (/) operator for Path("result") / "cleaned_pages"
    mock_result_path.__truediv__.return_value = mock_cleaned_pages_path

    # Call the function
    rename_and_organize_files(pages_dir="pages", output_dir="cleaned_pages")

    # Assertions
    mock_path_cls.assert_any_call("pages")
    mock_path_cls.assert_any_call("result")
    # Removed assertion for "result/cleaned_pages"

    # Instead, assert that Path("result") / "cleaned_pages" was called
    mock_result_path.__truediv__.assert_called_once_with("cleaned_pages")

    # Assert that mkdir was called on both 'result_path' and 'cleaned_pages_path'
    mock_result_path.mkdir.assert_called_once_with(exist_ok=True)
    mock_cleaned_pages_path.mkdir.assert_called_once_with(exist_ok=True)

    mock_page_dir.glob.assert_called_once_with("*.txt")

    assert mock_shutil_copy2.call_count == 2
    mock_shutil_copy2.assert_any_call(
        mock_page_dir.glob.return_value[0], mock_cleaned_pages_path / "testdir_0.txt"
    )
    mock_shutil_copy2.assert_any_call(
        mock_page_dir.glob.return_value[1], mock_cleaned_pages_path / "testdir_1.txt"
    )


def test_merge_text_files(mocker):
    """
    Test the merge_text_files function.
    """
    # Mock Path and file operations
    mock_path_cls = mocker.patch(
        "product_school_scraper.services.cleaning_service.Path", autospec=True
    )
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    # Setup mock directories and files
    mock_pages_path = MagicMock(spec=Path)
    mock_result_path = MagicMock(spec=Path)
    mock_merged_content_path = MagicMock(spec=Path)
    mock_page_dir = MagicMock(spec=Path)
    mock_page_dir.is_dir.return_value = True
    mock_page_dir.name = "TestDir"
    mock_page_dir.glob.return_value = [
        MagicMock(name="file1.txt"),
        MagicMock(name="file2.txt"),
    ]

    mock_pages_path.iterdir.return_value = [mock_page_dir]

    # Define side effect for Path constructor
    def path_side_effect(arg, *args, **kwargs):
        if arg == "pages":
            return mock_pages_path
        if arg == "result":
            return mock_result_path
        if arg == "result/merged_content.txt":
            return mock_merged_content_path
        return MagicMock(spec=Path)

    mock_path_cls.side_effect = path_side_effect

    # Mock the division (/) operator for Path("result") / "merged_content.txt"
    mock_result_path.__truediv__.return_value = mock_merged_content_path

    # Mock file reads
    mock_file1 = mocker.mock_open(read_data="Content of file1.\n")
    mock_file2 = mocker.mock_open(read_data="Content of file2.\n")
    # The third open call is for writing; use the original mock_open
    mock_open.side_effect = [
        mock_file1.return_value,
        mock_file2.return_value,
        mock_open.return_value,
    ]

    # Call the function
    merge_text_files(pages_dir="pages", output_filename="merged_content.txt")

    # Assertions
    mock_path_cls.assert_any_call("pages")
    mock_path_cls.assert_any_call("result")
    # Removed assertion for "result/merged_content.txt"

    # Instead, assert that Path("result") / "merged_content.txt" was called
    mock_result_path.__truediv__.assert_called_once_with("merged_content.txt")

    mock_result_path.mkdir.assert_called_once_with(exist_ok=True)
    mock_merged_content_path.mkdir.assert_not_called()

    mock_page_dir.glob.assert_called_once_with("*.txt")

    # Now, expect three open calls: two for reading, one for writing
    assert mock_open.call_count == 3
    mock_open.assert_any_call(mock_page_dir.glob.return_value[0], encoding="utf-8")
    mock_open.assert_any_call(mock_page_dir.glob.return_value[1], encoding="utf-8")
    mock_open.assert_any_call(mock_merged_content_path, "w", encoding="utf-8")

    # Assert that write was called correctly
    write_handle = mock_open.return_value.__enter__.return_value
    expected_content = (
        "=== TestDir ===\n\nContent of file1.\n=== TestDir ===\n\nContent of file2.\n"
    )
    write_handle.write.assert_called_once_with(expected_content)


def test_clean_html_content_no_boilerplate():
    """
    Test clean_html_content where there are no boilerplate elements or phrases.
    """
    html_content = """
    <html>
        <head><title>Clean Page</title></head>
        <body>
            <main>
                <p>This is a clean paragraph without boilerplate.</p>
            </main>
        </body>
    </html>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    cleaned = clean_html_content("Clean Page", soup)
    expected = "This is a clean paragraph without boilerplate."
    assert cleaned == expected


def test_clean_html_content_with_boilerplate_and_missing_space():
    """
    Test clean_html_content with boilerplate phrases and missing spaces after periods.
    """
    html_content = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <header><nav>Navigation</nav></header>
            <main>
                <p>This is a test.Subscribe to The Product Blog.Another sentence!</p>
            </main>
            <footer>Footer content</footer>
        </body>
    </html>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    cleaned = clean_html_content("Test Page", soup)
    expected = "This is a test. Another sentence!"
    assert cleaned == expected


def test_clean_html_content_exception_handling(mocker):
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


def test_rename_and_organize_files_skips_files(mocker):
    """
    Test that rename_and_organize_files gracefully skips any path items
    that are not directories, thereby hitting 'if not page_dir.is_dir(): continue'.
    """
    from pathlib import Path

    from product_school_scraper.services.cleaning_service import (
        rename_and_organize_files,
    )

    mock_path_cls = mocker.patch(
        "product_school_scraper.services.cleaning_service.Path", autospec=True
    )
    mock_shutil_copy2 = mocker.patch(
        "product_school_scraper.services.cleaning_service.shutil.copy2"
    )

    # Create a mock "file" (not a directory)
    mock_file_item = mocker.MagicMock(spec=Path)
    mock_file_item.is_dir.return_value = False  # So we skip it

    # Create a mock "directory"
    mock_directory = mocker.MagicMock(spec=Path)
    mock_directory.is_dir.return_value = True
    mock_directory.name = "TestDir"
    mock_directory.glob.return_value = []

    # Mock pages/ result/ cleaned_pages
    mock_pages_path = mocker.MagicMock(spec=Path)
    mock_result_path = mocker.MagicMock(spec=Path)
    mock_cleaned_pages_path = mocker.MagicMock(spec=Path)

    # pages_path.iterdir() returns one file and one dir
    mock_pages_path.iterdir.return_value = [mock_file_item, mock_directory]

    def side_effect(arg, *args, **kwargs):
        if arg == "pages":
            return mock_pages_path
        if arg == "result":
            return mock_result_path
        if arg == "result/cleaned_pages":
            return mock_cleaned_pages_path
        new_mock = mocker.MagicMock(spec=Path)
        return new_mock

    mock_path_cls.side_effect = side_effect
    mock_result_path.__truediv__.return_value = mock_cleaned_pages_path

    # Call the function
    rename_and_organize_files("pages", "cleaned_pages")

    # We should see no copy calls for the file
    # and we do see calls for the dir (even though it has no .txt).
    mock_file_item.glob.assert_not_called()
    mock_directory.glob.assert_called_once_with("*.txt")
    mock_shutil_copy2.assert_not_called()  # Because the directory had no .txt


def test_rename_and_organize_files_empty_dir(mocker):
    """
    Ensures we cover the branch where a directory exists but has no *.txt files.
    """
    from pathlib import Path

    from product_school_scraper.services.cleaning_service import (
        rename_and_organize_files,
    )

    mock_path_cls = mocker.patch(
        "product_school_scraper.services.cleaning_service.Path", autospec=True
    )
    mock_shutil_copy2 = mocker.patch(
        "product_school_scraper.services.cleaning_service.shutil.copy2"
    )

    # Mock directory with no txt files
    mock_directory = mocker.MagicMock(spec=Path)
    mock_directory.is_dir.return_value = True
    mock_directory.name = "EmptyDir"
    mock_directory.glob.return_value = []  # no *.txt

    # Mock pages / result / cleaned_pages
    mock_pages_path = mocker.MagicMock(spec=Path)
    mock_pages_path.iterdir.return_value = [mock_directory]
    mock_result_path = mocker.MagicMock(spec=Path)
    mock_cleaned_pages_path = mocker.MagicMock(spec=Path)

    def side_effect(arg, *args, **kwargs):
        if arg == "pages":
            return mock_pages_path
        if arg == "result":
            return mock_result_path
        if arg == "result/cleaned_pages":
            return mock_cleaned_pages_path
        return mocker.MagicMock(spec=Path)

    mock_path_cls.side_effect = side_effect
    mock_result_path.__truediv__.return_value = mock_cleaned_pages_path

    rename_and_organize_files("pages", "cleaned_pages")

    # Assertions
    mock_directory.glob.assert_called_once_with("*.txt")
    mock_shutil_copy2.assert_not_called()  # No text files => no copy


def test_merge_text_files_read_error(mocker):
    """
    Forces an exception while reading a file to cover the 'except Exception as e:' block
    in merge_text_files.
    """
    from pathlib import Path

    from product_school_scraper.services.cleaning_service import merge_text_files

    # Mock Path
    mock_path_cls = mocker.patch(
        "product_school_scraper.services.cleaning_service.Path", autospec=True
    )
    mock_pages_path = mocker.MagicMock(spec=Path)
    mock_result_path = mocker.MagicMock(spec=Path)
    mock_merged_content_path = mocker.MagicMock(spec=Path)

    # Directory with 1 txt file
    mock_page_dir = mocker.MagicMock(spec=Path)
    mock_page_dir.is_dir.return_value = True
    mock_page_dir.name = "ErrorDir"
    mock_page_dir.glob.return_value = [mocker.MagicMock(spec=Path, name="file1.txt")]

    mock_pages_path.iterdir.return_value = [mock_page_dir]

    def side_effect(arg, *args, **kwargs):
        if arg == "pages":
            return mock_pages_path
        if arg == "result":
            return mock_result_path
        if arg == "result/merged_content.txt":
            return mock_merged_content_path
        return mocker.MagicMock(spec=Path)

    mock_path_cls.side_effect = side_effect
    mock_result_path.__truediv__.return_value = mock_merged_content_path

    # Mock open to raise an exception on the first read
    mock_open = mocker.patch("builtins.open", side_effect=OSError("Read error"))

    # Patch the logger's error method to confirm it's called
    mock_logger_error = mocker.patch(
        "product_school_scraper.services.cleaning_service.logger.error"
    )

    merge_text_files(pages_dir="pages", output_filename="merged_content.txt")

    # We expect the read error to be logged
    mock_logger_error.assert_any_call(mocker.ANY)


def test_merge_text_files_write_error(mocker):
    """
    Forces an exception while writing the merged file to cover the 'except Exception as e:' block
    for writing in merge_text_files.
    """
    from pathlib import Path

    from product_school_scraper.services.cleaning_service import merge_text_files

    # Mock Path
    mock_path_cls = mocker.patch(
        "product_school_scraper.services.cleaning_service.Path", autospec=True
    )
    mock_pages_path = mocker.MagicMock(spec=Path)
    mock_result_path = mocker.MagicMock(spec=Path)
    mock_merged_content_path = mocker.MagicMock(spec=Path)

    # Directory with 1 txt file
    mock_page_dir = mocker.MagicMock(spec=Path)
    mock_page_dir.is_dir.return_value = True
    mock_page_dir.name = "WriteErrorDir"
    mock_page_dir.glob.return_value = []

    mock_pages_path.iterdir.return_value = [mock_page_dir]

    def side_effect(arg, *args, **kwargs):
        if arg == "pages":
            return mock_pages_path
        if arg == "result":
            return mock_result_path
        if arg == "result/merged_content.txt":
            return mock_merged_content_path
        return mocker.MagicMock(spec=Path)

    mock_path_cls.side_effect = side_effect
    mock_result_path.__truediv__.return_value = mock_merged_content_path

    # We still need to mock open() for reading (though we have no txt files here).
    # We'll attach a separate side_effect for the "write" usage.
    original_open = mocker.mock_open()

    def open_side_effect(*args, **kwargs):
        # If it's in 'w' mode => raise exception
        if "w" in args or kwargs.get("mode") == "w":
            raise OSError("Write error")
        return original_open.return_value

    mock_open = mocker.patch("builtins.open", side_effect=open_side_effect)

    # Patch the logger's error method to confirm it's called
    mock_logger_error = mocker.patch(
        "product_school_scraper.services.cleaning_service.logger.error"
    )

    # Call the function
    merge_text_files(pages_dir="pages", output_filename="merged_content.txt")

    # Confirm the error was logged
    mock_logger_error.assert_any_call(mocker.ANY)


def test_merge_text_files_skips_non_dir(mocker):
    """Ensure that merge_text_files hits the `if not page_dir.is_dir(): continue` branch."""

    # Mock out Path so it returns a mix of directory and non-directory items
    mock_path_cls = mocker.patch(
        "product_school_scraper.services.cleaning_service.Path", autospec=True
    )

    mock_pages_path = MagicMock(spec=Path)
    mock_result_path = MagicMock(spec=Path)
    mock_merged_content_path = MagicMock(spec=Path)

    # 1) A "file" that is not a directory
    mock_file = MagicMock(spec=Path)
    mock_file.is_dir.return_value = False

    # 2) A "directory" that is_dir() == True
    mock_dir = MagicMock(spec=Path)
    mock_dir.is_dir.return_value = True
    # We'll say it has no .txt files
    mock_dir.glob.return_value = []

    # The pages path will iterate over both the non-dir and the dir
    mock_pages_path.iterdir.return_value = [mock_file, mock_dir]

    # Make sure Path("pages") -> mock_pages_path, etc.
    def side_effect(arg, *args, **kwargs):
        if arg == "pages":
            return mock_pages_path
        if arg == "result":
            return mock_result_path
        if arg == "result/merged_content.txt":
            return mock_merged_content_path
        return MagicMock(spec=Path)

    mock_path_cls.side_effect = side_effect
    mock_result_path.__truediv__.return_value = mock_merged_content_path

    # We don't need to do anything special with open() for this test,
    # but we do patch it to avoid actual file I/O
    mocker.patch("builtins.open", mocker.mock_open())

    # Call merge_text_files
    merge_text_files("pages", "merged_content.txt")

    # The line "if not page_dir.is_dir(): continue" is now exercised
    # and that should give you coverage on line 185.
    mock_file.glob.assert_not_called()  # Because it's not a directory
    mock_dir.glob.assert_called_once_with("*.txt")
