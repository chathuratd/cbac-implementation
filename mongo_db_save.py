import json
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
with open("prompts_db.json", "r") as f:
    prompts = json.load(f)

# -------------------------------
# 3️⃣ Insert into MongoDB
# -------------------------------
if prompts:
    result = collection.insert_many(prompts)
    print(f"Inserted {len(result.inserted_ids)} prompts into MongoDB!")
else:
    print("No prompts found in JSON file.")

# -------------------------------
# 4️⃣ Optional: Verify
# -------------------------------
for doc in collection.find():
    print(doc)
