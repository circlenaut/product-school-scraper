import logging

import pytest

from product_school_scraper.cli import CleaningCLI, DatabaseCLI, ScraperCLI


def test_scraper_cli_verify(mocker, caplog):
    """
    Test the ScraperCLI.verify method.
    """
    # Patch 'verify_pages' where it's imported in cli.py
    mock_verify_pages = mocker.patch("product_school_scraper.cli.verify_pages")

    scraper_cli = ScraperCLI()
    scraper_cli.verify(pages_dir="pages_dir")

    # Assert that 'verify_pages' was called once with the correct arguments
    mock_verify_pages.assert_called_once_with("pages_dir")


def test_scraper_cli_list_pages(mocker, caplog):
    """
    Test the ScraperCLI.list_pages method.
    """
    # Patch 'list_pages' where it's imported in cli.py
    mock_list_pages = mocker.patch("product_school_scraper.cli.list_pages")

    scraper_cli = ScraperCLI()
    scraper_cli.list_pages(
        sitemap_url="https://example.com/sitemap.xml", directory="/news/"
    )

    # Assert that 'list_pages' was called once with the correct arguments
    mock_list_pages.assert_called_once_with(
        "https://example.com/sitemap.xml", ["/news/"]
    )


def test_scraper_cli_estimate_time(mocker, caplog, capsys):
    """
    Test the ScraperCLI.estimate_time method and capture printed output.
    """
    # Patch 'estimate_time' where it's imported in cli.py
    mock_estimate_time = mocker.patch("product_school_scraper.cli.estimate_time")

    scraper_cli = ScraperCLI()
    scraper_cli.estimate_time(
        sitemap_url="https://example.com/sitemap.xml", directory="/news/"
    )

    # Assert that 'estimate_time' was called once with the correct arguments
    mock_estimate_time.assert_called_once_with(
        "https://example.com/sitemap.xml", ["/news/"]
    )

    # Capture printed output
    captured = capsys.readouterr()
    assert "dirs: ['/news/']" in captured.out


def test_scraper_cli_fetch_pages(mocker, caplog):
    """
    Test the ScraperCLI.fetch_pages method.
    """
    # Patch 'fetch_pages' where it's imported in cli.py
    mock_fetch_pages = mocker.patch("product_school_scraper.cli.fetch_pages")

    scraper_cli = ScraperCLI()
    scraper_cli.fetch_pages(
        sitemap_url="https://example.com/sitemap.xml",
        directory="/news/",
        number_of_pages=10,
    )

    # Assert that 'fetch_pages' was called once with the correct arguments
    mock_fetch_pages.assert_called_once_with(
        "https://example.com/sitemap.xml", ["/news/"], 10
    )


def test_scraper_cli_render_pdf(mocker, caplog):
    """
    Test the ScraperCLI.render_pdf method.
    """
    # Patch 'render_pdf_pages' where it's imported in cli.py
    mock_render_pdf_pages = mocker.patch("product_school_scraper.cli.render_pdf_pages")

    scraper_cli = ScraperCLI()
    scraper_cli.render_pdf(
        sitemap_url="https://example.com/sitemap.xml",
        directory="/news/",
        number_of_pages=5,
    )

    # Assert that 'render_pdf_pages' was called once with the correct arguments
    mock_render_pdf_pages.assert_called_once_with(
        "https://example.com/sitemap.xml", ["/news/"], 5
    )


def test_database_cli_show_urls(mocker, caplog):
    """
    Test the DatabaseCLI.show_urls method.
    """
    # Patch 'show_all_urls' where it's imported in cli.py
    mock_show_all_urls = mocker.patch("product_school_scraper.cli.show_all_urls")

    db_cli = DatabaseCLI()
    db_cli.show_urls()

    # Assert that 'show_all_urls' was called once with no arguments
    mock_show_all_urls.assert_called_once_with()


def test_database_cli_update_url(mocker, caplog):
    """
    Test the DatabaseCLI.update_url method.
    """
    # Patch 'update_url' where it's imported in cli.py
    mock_update_url = mocker.patch("product_school_scraper.cli.update_url")

    db_cli = DatabaseCLI()
    db_cli.update_url(url_id=1, new_url="https://example.com/new_page")

    # Assert that 'update_url' was called once with the correct arguments
    mock_update_url.assert_called_once_with(1, "https://example.com/new_page")


def test_database_cli_delete_url(mocker, caplog):
    """
    Test the DatabaseCLI.delete_url method.
    """
    # Patch 'delete_url' where it's imported in cli.py
    mock_delete_url = mocker.patch("product_school_scraper.cli.delete_url")

    db_cli = DatabaseCLI()
    db_cli.delete_url(url_id=1)

    # Assert that 'delete_url' was called once with the correct arguments
    mock_delete_url.assert_called_once_with(1)


def test_scraper_cli_list_directories(mocker, caplog):
    """
    Test the ScraperCLI.list_directories method.
    """
    # Patch 'list_directories' where it's imported in cli.py
    mock_list_directories = mocker.patch("product_school_scraper.cli.list_directories")

    scraper_cli = ScraperCLI()
    scraper_cli.list_directories(sitemap_url="https://example.com/sitemap.xml")

    # Assert that 'list_directories' was called once with the correct argument
    mock_list_directories.assert_called_once_with("https://example.com/sitemap.xml")


def test_scraper_cli_fetch_page(mocker, caplog):
    """
    Test the ScraperCLI.fetch_page method.
    """
    # Patch 'fetch_page' where it's imported in cli.py
    mock_fetch_page = mocker.patch("product_school_scraper.cli.fetch_page")

    scraper_cli = ScraperCLI()
    scraper_cli.fetch_page(
        page_index=5,
        sitemap_url="https://example.com/sitemap.xml",
        directory="/news/",
    )

    # Assert that 'fetch_page' was called once with the correct arguments
    mock_fetch_page.assert_called_once_with(
        "https://example.com/sitemap.xml", ["/news/"], 5
    )


def test_cleaning_cli_rename_files(mocker, caplog):
    """
    Test the CleaningCLI.rename_files method.
    """
    # Patch 'rename_and_organize_files' where it's imported in cli.py
    mock_rename_and_organize_files = mocker.patch(
        "product_school_scraper.cli.rename_and_organize_files"
    )

    cleaning_cli = CleaningCLI()
    cleaning_cli.rename_files(pages_dir="source_pages", output_dir="organized_pages")

    # Assert that 'rename_and_organize_files' was called once with the correct arguments
    mock_rename_and_organize_files.assert_called_once_with(
        "source_pages", "organized_pages"
    )


def test_cleaning_cli_merge_files(mocker, caplog):
    """
    Test the CleaningCLI.merge_files method.
    """
    # Patch 'merge_text_files' where it's imported in cli.py
    mock_merge_text_files = mocker.patch("product_school_scraper.cli.merge_text_files")

    cleaning_cli = CleaningCLI()
    cleaning_cli.merge_files(pages_dir="source_pages", output_filename="combined.txt")

    # Assert that 'merge_text_files' was called once with the correct arguments
    mock_merge_text_files.assert_called_once_with("source_pages", "combined.txt")


def test_scraper_cli_fetch_page_invalid_page_number(mocker, caplog):
    """
    Test the ScraperCLI.fetch_page method with an invalid page number.
    """
    # Patch 'fetch_page' to raise a ValueError
    mock_fetch_page = mocker.patch(
        "product_school_scraper.cli.fetch_page",
        side_effect=ValueError("Invalid page number"),
    )

    scraper_cli = ScraperCLI()

    with pytest.raises(ValueError, match="Invalid page number"):
        scraper_cli.fetch_page(
            page_index=999,  # Assuming this is out of range
            sitemap_url="https://example.com/sitemap.xml",
            directory="/news/",
        )

    # Assert that 'fetch_page' was called once with the correct arguments
    mock_fetch_page.assert_called_once_with(
        "https://example.com/sitemap.xml", ["/news/"], 999
    )


def test_cleaning_cli_merge_files_exception(mocker, caplog):
    """
    Test the CleaningCLI.merge_files method when an exception occurs.
    """
    # Patch 'merge_text_files' to raise an exception
    mock_merge_text_files = mocker.patch(
        "product_school_scraper.cli.merge_text_files",
        side_effect=Exception("Merge failed"),
    )

    cleaning_cli = CleaningCLI()

    with pytest.raises(Exception, match="Merge failed"):
        cleaning_cli.merge_files(
            pages_dir="source_pages", output_filename="combined.txt"
        )

    # Assert that 'merge_text_files' was called once with the correct arguments
    mock_merge_text_files.assert_called_once_with("source_pages", "combined.txt")


def test_root_cli_initialization(mocker, caplog):
    """
    Test the RootCLI initialization.
    """
    # Patch the logger's setLevel method
    mock_logger_set_level = mocker.patch("product_school_scraper.cli.logger.setLevel")
    mock_handler_set_level = mocker.patch.object(
        logging.Handler, "setLevel", return_value=None
    )

    # Import RootCLI
    from product_school_scraper.cli import RootCLI

    # Initialize RootCLI without verbose
    root_cli = RootCLI()

    # Assert that logger was set to INFO
    mock_logger_set_level.assert_called_with(logging.INFO)

    # Assert that each handler's setLevel was called with INFO
    assert mock_handler_set_level.call_count == len(
        logging.getLogger("product_school_scraper").handlers
    )
    mock_handler_set_level.assert_called_with(logging.INFO)

    # Check that scraper and database attributes are instances of ScraperCLI and DatabaseCLI
    from product_school_scraper.cli import DatabaseCLI, ScraperCLI

    assert isinstance(root_cli.scraper, ScraperCLI)
    assert isinstance(root_cli.database, DatabaseCLI)

    # Initialize RootCLI with verbose=True
    root_cli_verbose = RootCLI(verbose=True)

    # Assert that logger was set to DEBUG
    mock_logger_set_level.assert_called_with(logging.DEBUG)

    # Assert that each handler's setLevel was called with DEBUG
    mock_handler_set_level.assert_called_with(logging.DEBUG)


def test_run_cli(mocker, caplog):
    """
    Test the run_cli function.
    """
    # Patch 'fire.Fire' where it's imported in cli.py
    mock_fire = mocker.patch("product_school_scraper.cli.fire.Fire")

    from product_school_scraper.cli import RootCLI, run_cli

    # Call the run_cli function
    run_cli()

    # Assert that 'fire.Fire' was called once with 'RootCLI'
    mock_fire.assert_called_once_with(RootCLI)
