from azure.storage.blob import BlobServiceClient
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def upload_to_blob(data: list, folder: str = "jobs"):
    conn_str = os.getenv("AZURE_CONNECTION_STRING")
    client = BlobServiceClient.from_connection_string(conn_str)
    container = client.get_container_client("raw-jobs")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    blob_name = f"{folder}/{timestamp}_jobs.json"

    data_bytes = json.dumps(data).encode("utf-8")
    container.upload_blob(name=blob_name, data=data_bytes, overwrite=True)
    print(f"✅ Uploaded {len(data)} jobs → {blob_name}")
    return blob_name

if __name__ == "__main__":
    with open("validated_jobs.json", "r") as f:
        validated_jobs = json.load(f)
    print(f"📤 Uploading {len(validated_jobs)} jobs to Azure Blob...")
    blob_path = upload_to_blob(validated_jobs)
    print(f"✅ Done! Blob path: {blob_path}")