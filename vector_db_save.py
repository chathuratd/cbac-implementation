import json
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "user_behaviors"

def main():
    # Load behaviors
    with open("behaviors_db.json", "r") as f:
        behaviors = json.load(f)

    # Load embedding model
    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Connect Qdrant
    client = QdrantClient(url="http://localhost:6333")

    # Create collection if not exists
    if not client.collection_exists(COLLECTION_NAME):
        print("Creating collection...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )

    print("Processing behaviors...")
    texts = [b["behavior_text"] for b in behaviors]
    vectors = model.encode(texts, show_progress_bar=True).tolist()

    points = []
    for i, (vec, b) in enumerate(zip(vectors, behaviors)):
        points.append(
            PointStruct(
                id=i,   # 🔥 FIX: use integer ID
                vector=vec,
                payload=b   # save all metadata including string behavior_id
            )
        )

    print(f"Inserting {len(points)} behaviors...")
    client.upsert(collection_name=COLLECTION_NAME, points=points)

    print("Done! All behaviors saved.")

if __name__ == "__main__":
    main()
