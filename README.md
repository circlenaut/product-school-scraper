# Product School Scraper

This command-line tool is designed to scrape data from [Product School](https://productschool.com/), the global leader in Product Management training. It parses Product School's sitemaps, stores the resulting URLs in a local SQLite database, and fetches page content as both PDF and text. Additionally, it offers verification to ensure that downloaded PDFs are valid and text files are non-empty.

## Features

1. **Sitemap Parsing**  
   - Fetches and parses XML sitemaps (using `requests` and `ElementTree`).
   - Supports optional directory filtering (e.g., only fetch `/blog/`).

2. **Local Database (SQLite)**  
   - Stores the URLs extracted from the sitemap.
   - CRUD operations (create, read, update, delete) via `SQLiteHandler`.

3. **Page Scraping**  
   - Fetches HTML pages (rate-limited to avoid overloading servers).
   - Converts pages to PDF using `pdfkit`.
   - Cleans HTML content to remove navigation/footer and boilerplate.

4. **Verification**  
   - Checks downloaded PDF files for validity (with `PyPDF`).
   - Ensures corresponding text files are non-empty.

5. **CLI with Fire**  
   - Easy-to-use commands: `list_pages`, `fetch_pages`, `estimate_time`, `render_pdf`, `verify`, and database utilities.

6. **Verbose Logging**  
   - Use `--verbose` or `-v` to enable debug-level logs.
   - Colored console output via `colorlog` for log level highlighting.

7. **Comprehensive Unit Tests**  
   - Achieves 100% test coverage across all services.
   - Tests located in the `tests/` directory.
   - Utilize `pytest` and `pytest-mock` for testing and mocking.

---

## Quick Start

### Prerequisites
- Python 3.12+ recommended
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management
- [wkhtmltopdf](https://wkhtmltopdf.org/) installed (needed by `pdfkit`)

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/your-organization/product-school-scraper.git
   cd product-school-scraper
   ```

2. Install dependencies via Poetry:
   ```bash
   poetry install
   ```

3. (Optional) Activate your virtual environment:
   ```bash
   poetry shell
   ```

### Usage

Run the main CLI:
```bash
poetry run product-school-scraper [OPTIONS] <COMMAND> [ARGS...]
```

#### Available Commands

**Scraper Commands** (under `scraper`):

- `list_pages`  
  Parse the sitemap and store results in the DB.  
  Example:
  ```bash
  poetry run product-school-scraper scraper list_pages \
      --sitemap_url https://productschool.com/sitemap.xml \
      --directory /blog/
  ```

- `fetch_pages`  
  Fetch a limited number (or all) of pages from the sitemap, storing each as PDF/TXT.  
  Example:
  ```bash
  poetry run product-school-scraper scraper fetch_pages \
      --sitemap_url https://productschool.com/sitemap.xml \
      --directory /blog/ \
      --number_of_pages 5
  ```

- `fetch_page`  
  Fetch a single page by index.

- `list_directories`  
  List all directories in sitemap.

- `render_pdf`  
  Similar to `fetch_pages`, but renders PDFs directly from URLs (via `pdfkit.from_url`).  

- `estimate_time`  
  Estimate how long the entire scrape might take (10 requests/s + overhead).  

- `verify`  
  Verify that all downloaded PDF/TXT files in the `pages` folder are valid and non-empty:
  ```bash
  poetry run product-school-scraper scraper verify
  ```

**Database Commands** (under `database`):

- `show_urls`  
  List all URLs currently stored in the SQLite DB.

- `update_url <url_id> <new_url>`  
  Update a specific URL.

- `delete_url <url_id>`  
  Remove a URL by ID.

**Cleaning Commands** (under `cleaning`):

- `rename-files`  
  Rename text files based on parent directory.

- `merge-files`  
  Merge text files into a single output

### Verbose Logging

If you want to see debug-level logs, simply add `-v` or `--verbose` anywhere in the command:
```bash
poetry run product-school-scraper -v scraper fetch_pages
```
or
```bash
poetry run product-school-scraper --verbose scraper verify
```

### Project Structure

```
product-school-scraper/
├── main.py
├── cli.py
├── database/
│   └── sqlite_handler.py
├── factories/
│   └── db_factory.py
├── parsing/
│   └── sitemap_parser.py
├── services/
│   ├── cleaning_service.py
│   ├── database_service.py
│   ├── estimate_service.py
│   ├── scraping_service.py
│   └── verification_service.py
├── utils/
│   └── logger.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_cleaning_service.py
│   ├── test_cli.py
│   ├── test_database.py
│   ├── test_database_service.py
│   ├── test_db_factory.py
│   ├── test_estimate_service.py
│   ├── test_main.py
│   ├── test_scraping_service.py
│   ├── test_sitemap_parser.py
│   └── test_verification_service.py
└── ...
```

---

## Testing

The project includes comprehensive unit tests to ensure reliability and maintainability. Tests cover all services with **100% coverage**, ensuring that all code paths are verified.

### Running Unit Tests

To run all unit tests, execute:
```bash
poetry run pytest
```

### Viewing Coverage Report

To generate a coverage report and view which parts of the code are covered by tests:
```bash
poetry run pytest --cov=product_school_scraper --cov-report=term-missing -v
```

### Running Specific Tests

To run a specific test module or function, specify its path:
```bash
poetry run pytest tests/test_verification_service.py -v
```

### Debugging Tests

If you need to debug tests, you can use the `--pdb` flag to enter the debugger on test failure:
```bash
poetry run pytest tests/test_verification_service.py --pdb -v
```
Alternatively, you can use IDE integrations or insert breakpoints within your test code using `import pdb; pdb.set_trace()`.

### Test Structure

- **Location**: All tests are located in the `tests/` directory.
- **Naming Convention**: Test files are prefixed with `test_` and correspond to the module they are testing (e.g., `test_scraping_service.py` for `scraping_service.py`).
- **Fixtures**: Common test fixtures and mocks are defined in `tests/conftest.py` for reusability across multiple test files.
- **Mocking**: External dependencies (like file I/O, network requests, and database interactions) are mocked using `pytest-mock` to ensure tests are fast and reliable.

### Example Test Command

To run all tests with coverage:
```bash
poetry run pytest --cov=product_school_scraper --cov-report=term-missing -v
```

**Expected Output:**
```plaintext
============================================= test session starts ==============================================
platform linux -- Python 3.12.3, pytest-8.3.4, pluggy-1.5.0 -- /path/to/python
cachedir: .pytest_cache
rootdir: /path/to/product-school-scraper
configfile: pyproject.toml
plugins: cov-6.0.0, mock-3.14.0
collected 67 items                                                                                                                                                                                         

... [test results] ...

---------- coverage: platform linux, python 3.12.3-final-0 -----------
Name                                                      Stmts   Miss  Cover   Missing
---------------------------------------------------------------------------------------
product_school_scraper/__init__.py                            0      0   100%
product_school_scraper/cli.py                                49      0   100%
product_school_scraper/database/sqlite_handler.py            44      0   100%
product_school_scraper/factories/db_factory.py                7      0   100%
product_school_scraper/main.py                               12      0   100%
product_school_scraper/parsing/sitemap_parser.py             22      0   100%
product_school_scraper/services/cleaning_service.py          33      0   100%
product_school_scraper/services/database_service.py          16      0   100%
product_school_scraper/services/estimate_service.py          14      0   100%
product_school_scraper/services/scraping_service.py         110      0    100%
product_school_scraper/services/verification_service.py      53      0    100%
product_school_scraper/utils/logger.py                        9      0   100%
---------------------------------------------------------------------------------------
TOTAL                                                       369      0    100%
---------------------------------------------------------------------------------------
============================================== 67 passed in 5.62s ===============================================
```

---

## Linting

The project uses Ruff for linting and code formatting, providing fast and comprehensive Python code quality checks.

### Setup

Ruff is included in the development dependencies. If you haven't installed dev dependencies yet:
```bash
poetry install
```

### Running Linting Checks

Check your code for style issues:
```bash
poetry run ruff check .
```

Auto-fix issues that can be fixed automatically:
```bash
poetry run ruff check --fix .
```

### Code Formatting

Format your code according to the project's style rules:
```bash
poetry run ruff format .
```

### Configuration

The project's Ruff configuration is defined in `pyproject.toml`. Key features include:

- Line length set to 88 characters (same as Black)
- Python 3.12+ compatibility checks
- Comprehensive rule set with pragmatic exceptions
- Special rules for test files
- Integration with common Python coding standards

### Pre-commit Integration

For automatic linting before commits, add this to your `.pre-commit-config.yaml`:
```yaml
repos:
-   repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.4
    hooks:
    -   id: ruff
        args: [--fix, --exit-non-zero-on-fix]
    -   id: ruff-format
```

Then install pre-commit hooks:
```bash
pre-commit install
```

---

## Troubleshooting

1. **wkhtmltopdf Not Found**  
   Ensure `wkhtmltopdf` is installed and on your system's PATH.

2. **Rate Limiting**  
   The default rate limit is 1 request every 10 seconds. Change `RATE_LIMIT_SECONDS` in `scraping_service.py` if needed.

3. **Debug Logs Not Showing**  
   Remember to use `-v/--verbose`, and ensure both the logger and console handler levels are set to `DEBUG`.

4. **Unit Tests Fail**  
   - Ensure all dependencies are installed.
   - Verify that mocks are correctly set up.
   - Check for recent changes that might have affected test coverage.

---

## Contributing

1. Fork the repository or create a new branch.
2. Make your changes.
3. Open a Pull Request. We'll review and merge as soon as possible.

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). Feel free to modify or distribute as needed.