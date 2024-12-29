import logging

import colorlog

logger = logging.getLogger("product_school_scraper")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Switching to '{' style to use center alignment ^ in format specifiers.
formatter = colorlog.ColoredFormatter(
    fmt=(
        "{blue}[{asctime}]{reset} "
        "{log_color}[{levelname:^8}]{reset} "  # Centered in an 8-char field
        "{message_log_color}{message}"
    ),
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red'
    },
    secondary_log_colors={
        'message': {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red'
        }
    },
    style='{'
)

console_handler.setFormatter(formatter)
logger.addHandler(console_handler)