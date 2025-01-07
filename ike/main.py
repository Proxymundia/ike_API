import argparse
from db.setup import setup_database, session  # Ensure the setup_database function is imported
from importers.wp_importer import import_wp_content
from importers.wiki_importer import import_wikipedia_content  # Renamed import (optional)
from updaters.source_updater import check_for_new_content
import requests
import logging
from db.exporter import export_data


def main():
    parser = argparse.ArgumentParser(description='Content Importer and Processor')
    parser.add_argument('--import_wp', help='Import WordPress content', action='store_true')
    parser.add_argument('--check_for_updates', help='Check for new content updates', action='store_true')
    parser.add_argument('--setup_db', help='Set up the database', action='store_true')  # New argument
    parser.add_argument('--import_wikipedia', help='Import Wikipedia content', action='store_true')  # Added argument
    parser.add_argument('--export_data', help='Export data to CSV and JSON', action='store_true')  # New export argument
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
        base_url = "https://en.wikipedia.org"
        page_title = "Kenya_Finance_Bill_protests"  # Wikipedia page title
        import_wikipedia_content(base_url, page_title)
        print("Wikipedia content imported successfully!")
    
    if args.check_for_updates:
        check_for_new_content()
        print("Started checking for new content updates.")

    if args.export_data:
        export_data(session, export_to_csv=True, export_to_json=True)

if __name__ == '__main__':
    main()
