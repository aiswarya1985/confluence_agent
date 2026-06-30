import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    CONFLUENCE_URL=os.getenv("CONFLUENCE_URL")
    CONFLUENCE_EMAIL=os.getenv("CONFLUENCE_EMAIL")
    CONFLUENCE_TOKEN=os.getenv("CONFLUENCE_TOKEN")   
    SPACE_KEY = "Confluence"  # e.g., "TEAM" or "PROJ"

    QADRANT_API_URL=os.getenv("QADRANT_API_URL")
    QDRANT_API_KEY=os.getenv("QADRANT_API_KEY")
    COLLECTION_NAME="confluence_knowledge_base"

 
settings = Settings()   