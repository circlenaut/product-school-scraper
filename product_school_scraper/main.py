import signal
import sys

from product_school_scraper.cli import run_cli
from product_school_scraper.utils.logger import logger

def sigint_handler(signum, frame):
    logger.warning("Ctrl-C detected! Exiting gracefully.")
    sys.exit(0)

def main():
    # Install our signal handler
    signal.signal(signal.SIGINT, sigint_handler)

    run_cli()

if __name__ == "__main__":
    main()