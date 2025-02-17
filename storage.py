# storage.py
import os
import logging
from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import load_dotenv

load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

# ロガーの設定
logger = logging.getLogger("storage")
logging.basicConfig(level=logging.INFO)

# Blob Service Client の初期化
try:
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER_NAME)
    logger.info(f"Connected to Azure Blob Storage: {AZURE_STORAGE_ACCOUNT_NAME}, Container: {AZURE_STORAGE_CONTAINER_NAME}")
except Exception as e:
    logger.error(f"Failed to initialize BlobServiceClient: {e}")
    raise

def upload_to_blob(blob_name, file_stream):
    """
    Azure Blob Storage にファイルをアップロードする

    :param blob_name: アップロード先のファイルパス (例: 'audio/sample.wav')
    :param file_stream: アップロードするデータを持つファイルオブジェクト (バイナリモード推奨)
    :return: アップロードしたファイルのURL (成功時) または None (失敗時)
    """
    try:
        # MIME Type をより適切に指定したい場合:
        #   docx なら "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        #   wav  なら "audio/wav"
        # といった形に切り替えてください。
        content_settings = ContentSettings(content_type="application/octet-stream")

        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(file_stream, overwrite=True, content_settings=content_settings)

        logger.info(f"'{blob_name}' をアップロードしました！")

        # URLを生成
        blob_url = generate_blob_url(blob_name)
        if not blob_url:
            logger.error(f"URL生成に失敗しました: {blob_name}")
        return blob_url

    except Exception as e:
        logger.error(f"アップロード中にエラーが発生しました: {e}")
        return None

def generate_blob_url(blob_name):
    """
    Azure Blob Storage のファイル URL を生成
    :param blob_name: 対象の Blob 名
    :return: Blob の URL
    """
    try:
        logger.info(f"Generating URL for blob: {blob_name}")
        # URL の生成
        blob_url = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_STORAGE_CONTAINER_NAME}/{blob_name}"
        logger.info(f"Blob URL を生成しました: {blob_url}")
        return blob_url
    except Exception as e:
        logger.error(f"URL 生成中にエラーが発生しました: {e}")
        return None

def download_blob(blob_name, download_file_path):
    """
    Azure Blob Storage からファイルをダウンロード

    :param blob_name: ダウンロードする Blob 名 (例: 'audio/sample.wav')
    :param download_file_path: ローカルに保存するパス (例: 'downloads/sample.wav')
    """
    try:
        blob_client = container_client.get_blob_client(blob_name)

        # バイナリモードで書き込み
        with open(download_file_path, "wb") as file:
            file.write(blob_client.download_blob().readall())

        logger.info(f"'{blob_name}' を '{download_file_path}' にダウンロードしました！")
    except Exception as e:
        logger.error(f"ダウンロード中にエラーが発生しました: {e}")
        raise
