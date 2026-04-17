from vectorstore.qdrant import setup_collection, get_client

setup_collection()
client = get_client()
cols = [c.name for c in client.get_collections().collections]
print(f"Collections: {cols}")