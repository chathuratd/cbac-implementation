import json
import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "user_behaviors"

def main():
    # Update path to point to test_data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_data_dir = os.path.join(script_dir, "..", "..", "test_data")
    file_path = os.path.join(test_data_dir, "behaviors_user_4_1765826173.json")
    
    print(f"Loading behaviors from: {file_path}")
    
    # Load behaviors
    with open(file_path, "r") as f:
        behaviors = json.load(f)
    
    print(f"Loaded {len(behaviors)} behaviors")

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
    else:
        # Clear existing data for this user (for clean testing)
        user_id = "user_4_1765826173"
        print(f"Clearing existing behaviors for {user_id}...")
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        try:
            client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=Filter(
                    must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
                )
            )
            print(f"Cleared existing data for {user_id}")
        except Exception as e:
            print(f"Note: Could not clear existing data (may be empty): {e}")

    print("Processing behaviors...")
    texts = [b["behavior_text"] for b in behaviors]
    vectors = model.encode(texts, show_progress_bar=True).tolist()

    # Get current max ID to avoid conflicts
    try:
        scroll_result = client.scroll(collection_name=COLLECTION_NAME, limit=1, with_payload=False)
        start_id = len(scroll_result[0]) if scroll_result[0] else 0
    except:
        start_id = 0

    points = []
    for i, (vec, b) in enumerate(zip(vectors, behaviors)):
        points.append(
            PointStruct(
                id=start_id + i,   # Use sequential integer IDs
                vector=vec,
                payload=b   # save all metadata including string behavior_id
            )
        )

    print(f"Inserting {len(points)} behaviors...")
    client.upsert(collection_name=COLLECTION_NAME, points=points)

    print(f"✅ Done! {len(behaviors)} behaviors saved to Qdrant.")
    
    # Verify
    user_id = "user_4_1765826173"
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    result = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=Filter(
            must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        ),
        limit=1
    )
    print(f"\n📊 Verified: Found {len(result[0])} behaviors for {user_id} in Qdrant")

if __name__ == "__main__":
    main()
