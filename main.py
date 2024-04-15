import argparse
import os
import sys
from core.utils import Utils
from scrapper.paginationScrapper import KijijiPaginationFSM
from scrapper.completionScrapper import KijijiCompletionFSM
def parse_arguments():
    parser = argparse.ArgumentParser(description='Run the scrapping tool with optional configuration.')
    parser.add_argument('-c', '--config', default='config.yaml', type=str,
                        help='Specify the configuration file. Default is "config.yaml".')
    parser.add_argument('-hl', '--headless', nargs='?', const=True, type=bool, default=None,
                        help='Run browsers in headless mode. No value needed, presence enables it.')
    parser.add_argument('-p', '--pagination', nargs='?', const=True, type=bool, default=None,
                        help='Run the pagination scrapper. No value needed, presence enables it.')
    parser.add_argument('-comp', '--completion', nargs='?', const=True, type=bool, default=None,
                        help='Run the completion scrapper. No value needed, presence enables it.')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    config = Utils.read_yaml(args.config)
    if not config:
        print("Failed to load or parse the configuration file.")
        sys.exit(1)
    # Initialize the logger
    log_path = config.get('log_path', 'data/log/scrapper.log')
    logger = Utils.setup_logging(log_path)
    logger.info("===== Kijiji  Scrapper =====")
    logger.info(f"Using configuration file: {args.config}")
    # Read configuration
    # Merge command-line arguments with config file settings
    run_pagination = args.pagination if args.pagination is not None else config.get('pagination', True)
    run_completion = args.completion if args.completion is not None else config.get('completion', True)
    db_path = config.get('db_path', None)
    if not db_path:
        logger.warning("Database path not provided. Using default path: 'sqlite:///default.db'")
        db_path = 'sqlite:///default.db'
        sys.exit(1)
    if not run_pagination and not run_completion:
        logger.error("Neither pagination nor completion scrappers are specified to run. Exiting.")
        sys.exit(1)
    # Execute pagination scrapper if enabled
    if run_pagination:
        pagination_scraper_config = config.get('pagination_scrapper', {})
        headers = config.get('headers', None)
        if pagination_scraper_config:
            logger.info("Starting the pagination scrapper.")
            paginationScrapper = KijijiPaginationFSM(headers=headers, db_path=db_path,**pagination_scraper_config, )
            paginationScrapper.run()
            logger.info("Pagination scrapper completed.")
        else:
            logger.error("No configuration found for pagination scrapper.")
    if run_completion:
        completion_scrapper_config = config.get('completion_scrapper', {})
        logger.info("Starting the completion scrapper.")
        completionScrapper = KijijiCompletionFSM(headers=headers, db_path=db_path, **completion_scrapper_config)
        completionScrapper.run()
        logger.info("Completion scrapper completed.")
