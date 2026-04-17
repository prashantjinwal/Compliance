from dotenv import load_dotenv
load_dotenv()
from vectorstore.qdrant import setup_collection

if __name__ == "__main__":
    setup_collection()
    print("Setup complete. Ready to ingest documents.")