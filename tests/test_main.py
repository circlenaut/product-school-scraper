import runpy
import signal
import sys


def test_main_calls_run_cli_and_sets_signal_handler(mocker):
    """
    Test that the main() function sets up the SIGINT handler and calls run_cli().
    """
    # Patch 'run_cli' in 'product_school_scraper.cli'
    mock_run_cli = mocker.patch("product_school_scraper.cli.run_cli")

    # Patch 'signal.signal' to monitor its calls
    mock_signal = mocker.patch("product_school_scraper.main.signal.signal")

    # Import 'main' and 'sigint_handler' after patching
    from product_school_scraper.main import main, sigint_handler

    # Call the main() function
    main()

    # Assert that 'signal.signal' was called with SIGINT and 'sigint_handler'
    mock_signal.assert_called_once_with(signal.SIGINT, sigint_handler)

    # Assert that 'run_cli' was called once
    mock_run_cli.assert_called_once()


def test_sigint_handler_logs_warning_and_exits(mocker):
    """
    Test that the sigint_handler logs a warning and exits gracefully when called.
    """
    # Patch the logger's warning method
    mock_logger_warning = mocker.patch("product_school_scraper.main.logger.warning")

    # Patch 'sys.exit' to prevent the test from exiting
    mock_sys_exit = mocker.patch("product_school_scraper.main.sys.exit")

    # Import 'sigint_handler' after patching
    from product_school_scraper.main import sigint_handler

    # Call the sigint_handler with arbitrary signal number and frame
    sigint_handler(signum=signal.SIGINT, frame=None)

    # Assert that logger.warning was called with the correct message
    mock_logger_warning.assert_called_once_with("Ctrl-C detected! Exiting gracefully.")

    # Assert that sys.exit was called with 0
    mock_sys_exit.assert_called_once_with(0)


def test_main_script_execution(mocker, monkeypatch):
    """
    Test that main.py executes main() when run as a script.
    """
    # Patch 'run_cli' in 'product_school_scraper.cli'
    mock_run_cli = mocker.patch("product_school_scraper.cli.run_cli")

    # Patch 'signal.signal' to monitor its calls
    mock_signal = mocker.patch("product_school_scraper.main.signal.signal")

    # Patch 'logger.warning' to prevent actual logging
    mock_logger_warning = mocker.patch("product_school_scraper.main.logger.warning")

    # Patch 'sys.exit' to prevent exiting the test runner
    mock_sys_exit = mocker.patch("product_school_scraper.main.sys.exit")

    # Mock 'sys.argv' to simulate running the script without extra arguments
    # This prevents 'fire.Fire' from interpreting test-related arguments
    monkeypatch.setattr(sys, "argv", ["product_school_scraper.main"])

    # Remove 'product_school_scraper.main' from sys.modules to force re-import
    if "product_school_scraper.main" in sys.modules:
        del sys.modules["product_school_scraper.main"]

    # Run the main.py module as '__main__'
    runpy.run_module("product_school_scraper.main", run_name="__main__")

    # Assert that 'signal.signal' was called with SIGINT and a callable
    mock_signal.assert_called_once()
    call_args = mock_signal.call_args[0]
    assert call_args[0] == signal.SIGINT
    assert callable(call_args[1])

    # Assert that 'run_cli' was called once
    mock_run_cli.assert_called_once()
