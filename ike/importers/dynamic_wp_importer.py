import logging
import requests
from urllib.parse import urlparse, unquote
from sqlalchemy import create_engine, sessionmaker
from sqlalchemy.orm import Session
from models import Source, Download, Document, Chunk
from sqlalchemy.exc import SQLAlchemyError
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database setup (adjust based on your database)
DATABASE_URL = "sqlite:///your_database.db"  # Use your actual DB URL
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

def fetch_wp_post(base_url, post_slug):
    """
    Fetch a WordPress post using the REST API.
    """
    wp_api_url = f"{base_url}/wp-json/wp/v2/posts?slug={post_slug}"
    try:
        response = requests.get(wp_api_url)
        response.raise_for_status()
        return response.json()[0]  # Return the first post result
    except RequestException as e:
        logging.error(f"Error fetching post from {wp_api_url}: {e}")
        raise

def scrape_reader_post(wp_url):
    """
    Scrape content from WordPress Reader URLs.
    """
    # Placeholder for your scraping logic
    logging.info(f"Scraping WordPress Reader post: {wp_url}")
    # Simulate scraping with dummy content
    return "Untitled", "No content found"

def extract_wp_details(wp_url):
    """
    Extract the base URL and post slug from a WordPress URL.
    Handles both direct URLs and WordPress Reader URLs.
    Returns None for unsupported URLs or homepages.
    """
    parsed_url = urlparse(wp_url)

    # Handle WordPress Reader URLs
    if "wordpress.com/read" in parsed_url.path:
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) >= 4 and path_parts[0] == "read" and path_parts[2] == "posts":
            feed_id = path_parts[1]
            post_id = path_parts[3]
            return f"https://wordpress.com/read/feeds/{feed_id}", post_id
        else:
            raise ValueError("Invalid WordPress Reader URL format.")

    # Handle Direct Blog Post URLs
    slug = unquote(parsed_url.path.strip('/'))
    if slug and "/posts/" in slug:
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return base_url, slug.split("/")[-1]

    # Unsupported or homepage URLs
    return None, None

def import_dynamic_wp_content(wp_url):
    """
    Import WordPress content into the database.
    Handles both direct blog URLs and WordPress Reader URLs.
    """
    logging.info(f"Importing content from: {wp_url}")
    try:
        # Extract base URL and slug
        base_url, post_slug = extract_wp_details(wp_url)

        if not base_url or not post_slug:
            logging.error("Unsupported URL or homepage: Cannot process the given URL.")
            return

        if "wordpress.com/read" in wp_url:
            # Handle Reader URLs by scraping
            title, content = scrape_reader_post(wp_url)
        else:
            # Fetch content via REST API for direct blog URLs
            post = fetch_wp_post(base_url, post_slug)
            title = post.get('title', {}).get('rendered', 'Untitled')
            content = post.get('content', {}).get('rendered', '')

        # Database operations
        source = session.query(Source).filter_by(base_url=base_url).first()
        if not source:
            source = Source(name="WordPress", base_url=base_url)
            session.add(source)
            session.commit()

        download = session.query(Download).filter_by(url=wp_url).first()
        if not download:
            download = Download(url=wp_url, source_id=source.id)
            session.add(download)
            session.commit()

            document = Document(
                title=title,
                content=content,
                download_id=download.id
            )
            session.add(document)
            session.commit()

            chunks = content.split(". ")
            for idx, chunk_text in enumerate(chunks):
                chunk = Chunk(
                    content=chunk_text,
                    document_id=document.id,
                    start_position=idx * 100,
                    end_position=(idx + 1) * 100
                )
                session.add(chunk)
            session.commit()

        logging.info("WordPress content imported successfully!")

    except ValueError as ve:
        logging.error(f"Invalid URL: {ve}")
    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        session.rollback()
    except RequestException as re:
        logging.error(f"Request error: {re}")
    except Exception as e:
        logging.error(f"Error importing content: {e}")
