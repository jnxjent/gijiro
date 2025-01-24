from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

# Blob Service Clientの初期化
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER_NAME)

def upload_to_blob(blob_name, file_stream):
    """
    Azure Blob Storageにファイルをアップロード
    """
    container_client.upload_blob(blob_name, file_stream, overwrite=True)

def generate_blob_url(blob_name):
    """
    Azure Blob StorageのファイルURLを生成
    """
    return f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_STORAGE_CONTAINER_NAME}/{blob_name}"
