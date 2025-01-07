import requests
import logging
from sqlalchemy.exc import SQLAlchemyError
from db.setup import session  # Use the session from setup.py
from db.models import Source, Download, Document, Chunk  # Ensure models are imported correctly

# Configure logging
logging.basicConfig(level=logging.INFO)

def fetch_wp_posts(base_url):
    """
    Fetch all posts from the WordPress REST API.
    """
    response = requests.get(f"{base_url}/wp-json/wp/v2/posts")
    response.raise_for_status()
    return response.json()

def fetch_wp_post(base_url, post_slug):
    """
    Fetch a single post from WordPress REST API based on the slug.
    """
    response = requests.get(f"{base_url}/wp-json/wp/v2/posts", params={"slug": post_slug})
    response.raise_for_status()
    posts = response.json()
    if len(posts) > 0:
        return posts[0]  # Return the first matching post
    else:
        raise ValueError(f"No post found for slug: {post_slug}")

def import_wp_content(base_url, post_slug=None):
    """
    Import WordPress content into the database. If post_slug is provided,
    only that specific post is imported.
    """
    logging.info(f"Importing content from {base_url}")
    try:
        # Add or get the source
        source = session.query(Source).filter_by(base_url=base_url).first()
        if not source:
            source = Source(name="WordPress Site", base_url=base_url)
            session.add(source)
            session.commit()

        # Fetch the specific post or all posts
        if post_slug:
            post = fetch_wp_post(base_url, post_slug)
            posts = [post]  # Convert single post into a list for consistency
        else:
            posts = fetch_wp_posts(base_url)

        # Process each post
        for post in posts:
            # Check if post is already downloaded
            download = session.query(Download).filter_by(url=post['link']).first()
            if not download:
                download = Download(url=post['link'], source_id=source.id)
                session.add(download)
                session.commit()

                # Create a document
                document = Document(
                    title=post['title']['rendered'],
                    content=post['content']['rendered'],
                    download_id=download.id
                )
                session.add(document)
                session.commit()

                # Optionally split content into chunks
                chunks = post['content']['rendered'].split(". ")
                for idx, chunk_text in enumerate(chunks):
                    chunk = Chunk(
                        content=chunk_text,
                        document_id=document.id,
                        start_position=idx * 100,  # Example: mock start position
                        end_position=(idx + 1) * 100  # Example: mock end position
                    )
                    session.add(chunk)
                session.commit()

        logging.info("Content imported successfully!")

    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        session.rollback()
    except Exception as e:
        logging.error(f"Error importing content: {e}")
