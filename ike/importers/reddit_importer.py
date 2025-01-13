import requests
import logging
from sqlalchemy.exc import SQLAlchemyError
from db.setup import session
from db.models import Source, Download, Document, Chunk

# Configure logging
logging.basicConfig(level=logging.INFO)

def fetch_reddit_post(url):
    """
    Fetch a Reddit post as JSON using the public Reddit API endpoint.
    """
    try:
        # Ensure the URL ends with `.json`
        if not url.endswith('.json'):
            url = f"{url}.json"

        response = requests.get(url, headers={'User-Agent': 'RedditImporter/0.1'})
        response.raise_for_status()
        post_data = response.json()

        # Parse relevant post details
        post = post_data[0]['data']['children'][0]['data']
        return {
            "title": post['title'],
            "content": post.get('selftext', ''),  # Reddit posts can have empty content
            "url": post['url']
        }
    except Exception as e:
        logging.error(f"Error fetching Reddit post: {e}")
        raise

def import_reddit_content(url):
    """
    Import Reddit post content into the database.
    """
    logging.info(f"Importing content from Reddit post: {url}")
    try:
        # Fetch post details
        post = fetch_reddit_post(url)

        # Add or get the source
        source_name = "Reddit"
        source = session.query(Source).filter_by(name=source_name).first()
        if not source:
            source = Source(name=source_name, base_url="https://www.reddit.com")
            session.add(source)
            session.commit()

        # Check if post is already downloaded
        download = session.query(Download).filter_by(url=post['url']).first()
        if not download:
            download = Download(url=post['url'], source_id=source.id)
            session.add(download)
            session.commit()

            # Create a document
            document = Document(
                title=post['title'],
                content=post['content'],
                download_id=download.id
            )
            session.add(document)
            session.commit()

            # Optionally split content into chunks
            chunks = post['content'].split(". ")
            for idx, chunk_text in enumerate(chunks):
                chunk = Chunk(
                    content=chunk_text,
                    document_id=document.id,
                    start_position=idx * 100,  # Example: mock start position
                    end_position=(idx + 1) * 100  # Example: mock end position
                )
                session.add(chunk)
            session.commit()

        logging.info("Reddit content imported successfully!")

    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        session.rollback()
    except Exception as e:
        logging.error(f"Error importing Reddit content: {e}")

