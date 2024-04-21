import argparse
import os
import sys
from core.utils import Utils
from scrapper.paginationScrapper import KijijiPaginationFSM
from scrapper.completionScrapper import KijijiCompletionFSM

def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: The parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description='Run the scrapping tool with optional configuration.')
    parser.add_argument('-c', '--config', default='config.yaml', type=str,
                        help='Specify the configuration file. Default is "config.yaml".')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments() # Parse command line arguments
    config = Utils.read_yaml(args.config) # Read configuration file
    if not config: # Check if the configuration file was loaded successfully
        print("Failed to load or parse the configuration file.")
        sys.exit(1)
    # Initialize the logger
    log_path = config.get('log_path', 'data/log/scrapper.log')
    log_debug = config.get('log_debug', False)  
    logger = Utils.setup_logging(log_path,log_debug)
    logger.info("===== Kijiji  Scrapper =====")
    logger.info(f"Using configuration file: {args.config}")
    # Read configuration
    run_pagination = config.get('pagination', True)
    run_completion = config.get('completion', True)
    db_path = config.get('db_path', None)
    # Check if database path is provided
    if not db_path:
        logger.warning("Database path not provided. Using default path: 'sqlite:///default.db'")
        db_path = 'sqlite:///default.db'
        sys.exit(1)
    # Check if pagination or completion scrapper is enabled
    if not run_pagination and not run_completion:
        logger.error("Neither pagination nor completion scrappers are specified to run. Exiting.")
        sys.exit(1)
    # Execute pagination scrapper if enabled
    headers = config.get('headers', None)
    if run_pagination:
        # Read pagination scrapper configuration
        pagination_scraper_config = config.get('pagination_scrapper', {})
        if pagination_scraper_config:
            logger.info("== Starting the pagination scrapper.")
            paginationScrapper = KijijiPaginationFSM(headers=headers, db_path=db_path,**pagination_scraper_config, )
            paginationScrapper.run()
            logger.info("== Pagination scrapper completed.")
        else:
            logger.error(" == No configuration found for pagination scrapper.")
    if run_completion:
        # Read completion scrapper configuration
        completion_scrapper_config = config.get('completion_scrapper', {})
        logger.info("Starting the completion scrapper.")
        completionScrapper = KijijiCompletionFSM(headers=headers, db_path=db_path, **completion_scrapper_config)
        completionScrapper.run()
        logger.info("== Completion scrapper completed.")
    
