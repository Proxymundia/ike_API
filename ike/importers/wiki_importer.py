import requests
import logging
from urllib.parse import urlparse, parse_qs, unquote
from sqlalchemy.exc import SQLAlchemyError
from db.setup import session
from db.models import Source, Download, Document, Chunk

logging.basicConfig(level=logging.INFO)

def extract_page_title(wikipedia_url):
    """
    Extract the Wikipedia page title from the provided URL.
    """
    parsed_url = urlparse(wikipedia_url)
    if '/wiki/' in parsed_url.path:
        return unquote(parsed_url.path.split('/wiki/')[1])
    elif 'title=' in wikipedia_url:
        query_params = parse_qs(parsed_url.query)
        return query_params.get('title', [None])[0]
    else:
        raise ValueError("Invalid Wikipedia URL format.")

def fetch_wikipedia_page(base_url, page_title):
    """
    Fetch the content of a Wikipedia page using the MediaWiki API.
    """
    params = {
        'action': 'parse',
        'page': page_title,
        'format': 'json'
    }
    api_url = f"{base_url}/w/api.php"
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    data = response.json()
    if 'parse' in data:
        return data['parse']
    else:
        raise ValueError(f"Error fetching Wikipedia page for {page_title}")

def import_wikipedia_content(wikipedia_url):
    """
    Import Wikipedia content into the database using a Wikipedia page URL.
    """
    logging.info(f"Importing content from: {wikipedia_url}")
    try:
        # Extract base URL and page title
        parsed_url = urlparse(wikipedia_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        page_title = extract_page_title(wikipedia_url)

        # Add or get the source
        source = session.query(Source).filter_by(base_url=base_url).first()
        if not source:
            source = Source(name="Wikipedia", base_url=base_url)
            session.add(source)
            session.commit()

        # Fetch the Wikipedia page
        page = fetch_wikipedia_page(base_url, page_title)
        page_url = f"{base_url}/wiki/{page_title}"

        # Check if the page is already downloaded
        download = session.query(Download).filter_by(url=page_url).first()
        if not download:
            download = Download(url=page_url, source_id=source.id)
            session.add(download)
            session.commit()

            # Create a document for the Wikipedia page
            document = Document(
                title=page['title'],
                content=page['text']['*'],
                download_id=download.id
            )
            session.add(document)
            session.commit()

            # Optionally split content into chunks
            chunks = page['text']['*'].split(". ")
            for idx, chunk_text in enumerate(chunks):
                chunk = Chunk(
                    content=chunk_text,
                    document_id=document.id,
                    start_position=idx * 100,  # Example: mock start position
                    end_position=(idx + 1) * 100  # Example: mock end position
                )
                session.add(chunk)
            session.commit()

        logging.info("Wikipedia content imported successfully!")

    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        session.rollback()
    except Exception as e:
        logging.error(f"Error importing content: {e}")
