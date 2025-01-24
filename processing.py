import openai
from deepgram import Deepgram
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import os
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# 環境変数の設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
DEPLOYMENT_ID = os.getenv("DEPLOYMENT_ID")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

openai.api_key = OPENAI_API_KEY
openai.api_base = OPENAI_API_BASE
openai.api_type = "azure"
openai.api_version = "2024-08-01-preview"

async def process_files(audio_blob_url, word_blob_url, output_blob_name):
    """
    音声ファイルとWordファイルを処理し、結果を保存
    """
    try:
        # Deepgramクライアントの初期化
        deepgram_client = Deepgram(DEEPGRAM_API_KEY)

        # Blobストレージから音声ファイルを取得（ダミーデータを代用可能）
        audio_data = download_blob(audio_blob_url)

        # Deepgram APIでトランスクリプション取得
        options = {
            "model": "nova-2-general",
            "detect_language": True,
            "diarize": True,
            "utterances": True,
        }
        mimetype = "audio/mpeg"  # 必要に応じて変更
        response = await deepgram_client.transcription.prerecorded(
            {"buffer": audio_data, "mimetype": mimetype}, options
        )
        transcription = "\n".join(
            f"[Speaker {u['speaker']}] {u['transcript']}" for u in response["results"]["utterances"]
        )

        # OpenAIで情報抽出
        extracted_info = await extract_meeting_info(transcription)

        # Wordファイルをダウンロードし、更新
        word_file_path = "temp_word.docx"
        download_blob(word_blob_url, word_file_path)

        output_file_path = "updated_meeting_notes.docx"
        update_word_file(word_file_path, output_file_path, extracted_info, transcription)

        # Azure Blob Storageにアップロード
        with open(output_file_path, "rb") as updated_file:
            upload_to_blob(output_blob_name, updated_file)
    except Exception as e:
        raise Exception(f"処理中にエラーが発生しました: {e}")

async def extract_meeting_info(transcription):
    """
    トランスクリプションから議事録情報を抽出
    """
    prompt = (
        "以下のトランスクリプションから、会議の議事録を抽出してください...\n\n"
        f"{transcription}\n\n"
    )
    response = openai.ChatCompletion.create(
        engine=DEPLOYMENT_ID,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response["choices"][0]["message"]["content"]

def update_word_file(word_file, output_path, extracted_info, transcription):
    """
    Wordファイルを更新
    """
    doc = Document(word_file)
    # 任意の更新処理
    doc.save(output_path)
