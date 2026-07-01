import logfire
from atlassian import Confluence
from bs4 import BeautifulSoup
from app.config import settings
from atlassian import Confluence
from app.ingestion.chunking.chunktext import chunk_text
from app.ingestion.services.qadarntservice import push_to_qdrant


CONFLUENCE_URL = settings.CONFLUENCE_URL
CONFLUENCE_EMAIL = settings.CONFLUENCE_EMAIL
CONFLUENCE_TOKEN = settings.CONFLUENCE_TOKEN
SPACE_KEY = settings.SPACE_KEY

logfire.configure()

with logfire.span("loading of pages from confluence started"):

  confluence = Confluence(url=CONFLUENCE_URL, username=CONFLUENCE_EMAIL, password=CONFLUENCE_TOKEN)

  cql_query = f'space = "{SPACE_KEY}" AND type = "page"'

  results = confluence.cql(cql_query)["results"]


for item in results:
   
    page_data = item.get("content", item)
    title = page_data.get("title", item.get("title", "Untitled Page"))
    page_id = page_data.get("id")
    
    # If the search result item doesn't have an ID, skip it
    if not page_id:
        logfire.error("Skipping an item because no Page ID was found.")      
        continue
        
    try:        
        full_page = confluence.get_page_by_id(page_id, expand="body.storage")
        
        raw_html_content = full_page.get("body", {}).get("storage", {}).get("value", "")
        
        if raw_html_content:
           
            soup = BeautifulSoup(raw_html_content, "html.parser")           
           
            for element in soup(["style", "script"]):
                element.decompose()
            
           
            body_content = soup.get_text(separator="\n", strip=True)           
            if "<!DOCTYPE html" in body_content or "<html" in body_content:              
                inner_soup = BeautifulSoup(body_content, "html.parser")                
               
                for element in inner_soup(["style", "script"]):
                    element.decompose()                
              
                body_content = inner_soup.get_text(separator="\n", strip=True)

           
            page_chunks = chunk_text(body_content, max_chars=2000, overlap=200)
            logfire.info(f"Processing '{title}': Split into {len(page_chunks)} chunks.")
            
            # 2. Push chunks to Qdrant
            push_to_qdrant(text_chunks=page_chunks, page_id=page_id, title=title)
            logfire.info(f"Successfully pushed '{title}' chunks to Qdrant.")  
            logfire.info("\nPipeline execution complete! All entries processed.")

        else:
            logfire.error(f"Skipping '{title}' (ID: {page_id}) because it has no content.")
              
    except Exception as e:
         logfire.error(f"Skipping page {title} (ID: {page_id}) due to error: {e}")
       


