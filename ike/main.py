import argparse
from db.setup import setup_database, session  # Ensure the setup_database function is imported
from importers.wp_importer import import_wp_content
from importers.wiki_importer import import_wikipedia_content  # Renamed import (optional)
from importers.reddit_importer import import_reddit_content  # Import Reddit importer
from updaters.source_updater import check_for_new_content
import requests
import logging
from db.exporter import export_data
"""from importers.dynamic_wp_importer import import_dynamic_wp_content"""


def main():
    parser = argparse.ArgumentParser(description='Content Importer and Processor')
    parser.add_argument('--import_wp', help='Import WordPress content', action='store_true')
    parser.add_argument('--check_for_updates', help='Check for new content updates', action='store_true')
    parser.add_argument('--setup_db', help='Set up the database', action='store_true')  # New argument
    parser.add_argument('--import_wikipedia', help='Import content from a Wikipedia page URL', type=str)
    parser.add_argument('--export_data', help='Export data to CSV and JSON', action='store_true')  # New export argument
    parser.add_argument('--dynamic_wp_importer', help='Import WordPress content from a URL', type=str)
    parser.add_argument('--import_reddit', help='Import content from a Reddit post URL', type=str)
    args = parser.parse_args()
    
    # Set up the database if the argument is passed
    if args.setup_db:
        setup_database()
        print("Database setup completed!")
        return  # Exit after setup to avoid running other actions

    if args.import_wp:
        base_url = "https://uofsdmedia.wordpress.com"
        post_slug = "trump-triumphs-in-presidential-election"
        import_wp_content(base_url, post_slug)
        print("WordPress content imported successfully!")

    if args.import_wikipedia:
        wikipedia_url = args.import_wikipedia.strip()  # Use the Wikipedia URL passed as an argument
        import_wikipedia_content(wikipedia_url)
        print("Wikipedia content imported successfully!")

    if args.dynamic_wp_importer:
        import_dynamic_wp_content(args.dynamic_wp_importer)  # Use URL from command-line argument
        print("WordPress content imported successfully!")

    if args.import_reddit:
        reddit_url = args.import_reddit.strip()  # Use the Reddit URL passed as an argument
        import_reddit_content(reddit_url)
        print("Reddit content imported successfully!")
    
    if args.check_for_updates:
        check_for_new_content()
        print("Started checking for new content updates.")

    if args.export_data:
        export_data(session, export_to_csv=True, export_to_json=True)

if __name__ == '__main__':
    main()
