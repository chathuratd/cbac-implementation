import json
import os
from pymongo import MongoClient

# -------------------------------
# 1️⃣ MongoDB Connection
# -------------------------------
# Replace username/password if you set them in Docker
client = MongoClient("mongodb://admin:admin123@localhost:27017/?authSource=admin")

# Choose database and collection
db = client["cbac_system"]
collection = db["prompts"]

# -------------------------------
# 2️⃣ Load prompt data from JSON file
# -------------------------------
# Update path to point to test_data directory
script_dir = os.path.dirname(os.path.abspath(__file__))
test_data_dir = os.path.join(script_dir, "..", "..", "test_data")
file_path = os.path.join(test_data_dir, "prompts_user_4_1765826173.json")

print(f"Loading prompts from: {file_path}")

with open(file_path, "r") as f:
    prompts = json.load(f)

# -------------------------------
# 3️⃣ Clear existing data for this user (for clean testing)
# -------------------------------
user_id = "user_4_1765826173"
deleted = collection.delete_many({"user_id": user_id})
print(f"Deleted {deleted.deleted_count} existing prompts for {user_id}")

# -------------------------------
# 4️⃣ Insert into MongoDB
# -------------------------------
if prompts:
    result = collection.insert_many(prompts)
    print(f"✅ Inserted {len(result.inserted_ids)} prompts into MongoDB!")
else:
    print("❌ No prompts found in JSON file.")

# -------------------------------
# 5️⃣ Verify insertion
# -------------------------------
count = collection.count_documents({"user_id": user_id})
print(f"\n📊 Total prompts for {user_id}: {count}")

# Show first few prompts
print("\n📝 Sample prompts:")
for i, doc in enumerate(collection.find({"user_id": user_id}).limit(3)):
    print(f"  {i+1}. {doc['prompt_text'][:60]}...")
