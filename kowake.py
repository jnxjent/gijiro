import os
import openai
from dotenv import load_dotenv

from pydub import AudioSegment   # 音声分割に使用（pip install pydub）
from deepgram import Deepgram

# .env ファイルの読み込み
load_dotenv()
# .env から FFMPEG_PATH, FFPROBE_PATH を取得（デフォルト値として空文字を指定）
ffmpeg_path = os.getenv("FFMPEG_PATH", "")
ffprobe_path = os.getenv("FFPROBE_PATH", "")

# 環境変数にセット
os.environ["FFMPEG_BINARY"] = ffmpeg_path
os.environ["FFPROBE_BINARY"] = ffprobe_path
# ここで、システム PATH に ffmpeg-bin のディレクトリを追加する
# これにより、pydub の subprocess 呼び出し時に ffprobe が確実に見つかります
os.environ["PATH"] = "/home/site/wwwroot/ffmpeg-bin:" + os.environ.get("PATH", "")
# `pydub` をインポートする前にパスを設定
from pydub import AudioSegment
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# デバッグ用に出力
print(f"FFMPEG_BINARY: {AudioSegment.converter}")
print(f"FFPROBE_BINARY: {AudioSegment.ffprobe}")

OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE  = os.getenv("OPENAI_API_BASE")
DEPLOYMENT_ID    = os.getenv("DEPLOYMENT_ID")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

openai.api_key  = OPENAI_API_KEY
openai.api_base = OPENAI_API_BASE
openai.api_type = "azure"
openai.api_version = "2024-08-01-preview"

# Deepgram クライアントの初期化
deepgram_client = Deepgram(DEEPGRAM_API_KEY)

async def transcribe_and_correct(audio_file_path: str) -> str:
    """
    音声ファイルを10分ずつチャンク分割し、DeepGramで文字起こし、
    その後OpenAIで日本語テキストを補正して全チャンクを結合した
    最終的な全文文字起こしを返す。
    
    - DeepGram API 呼び出し
    - OpenAI (ChatCompletion) で日本語補正
    - 全チャンクのテキストを結合
    """
    # -------------------------
    # 1) 音声をチャンク分割する (10分 = 600秒ごと)
    # -------------------------
    audio = AudioSegment.from_file(audio_file_path)
    chunk_length_ms = 10 * 60 * 1000  # 10分(600秒)をミリ秒に変換

    chunks = []
    start = 0
    while start < len(audio):
        end = min(start + chunk_length_ms, len(audio))
        audio_chunk = audio[start:end]
        chunks.append(audio_chunk)
        start = end

    # -------------------------
    # 2) 各チャンクを DeepGram にかけて文字起こし
    # -------------------------
    partial_transcriptions = []

    for idx, chunk_data in enumerate(chunks):
        # チャンクを一時ファイルに保存して DeepGram API を呼び出す
        chunk_temp_path = f"temp_chunk_{idx}.wav"
        chunk_data.export(chunk_temp_path, format="wav")

        with open(chunk_temp_path, "rb") as f:
            audio_buffer = f.read()

        # Deepgram API オプション
        options = {
            "model": "nova-2-general",
            "detect_language": True,
            "diarize": True,
            "utterances": True,
        }

        response = await deepgram_client.transcription.prerecorded(
            {"buffer": audio_buffer, "mimetype": "audio/wav"},
            options
        )

        # 発話ごとにまとめ、1チャンク分のトランスクリプション文字列を作る
        chunk_transcript = "\n".join(
            f"[Speaker {u['speaker']}] {u['transcript']}"
            for u in response["results"]["utterances"]
        )

        # 一時ファイル削除（必要に応じて）
        os.remove(chunk_temp_path)

        partial_transcriptions.append(chunk_transcript)

    # -------------------------
    # 3) 各チャンクの文字起こしを OpenAI で文面補正
    #    （トークン制限: 入力4k, 出力28kを想定）
    # -------------------------
    corrected_chunks = []
    for idx, partial_text in enumerate(partial_transcriptions):
        prompt = (
            "以下の音声書き起こしを正しい自然な日本語にしてください。"
            "話者表記 ([Speaker X]) は残しつつ、連続する発話は一つにまとめ、"
            "読みやすく整形してください。\n\n"
            f"{partial_text}\n\n"
            "【出力形式】\n"
            "[Speaker X] 発話内容\n"
            "[Speaker X] 発話内容\n"
        )

        # OpenAI へチャンク単位で問い合わせ
        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_ID,
            messages=[
                {"role": "system", "content": "あなたは優秀な日本語整形アシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,  # 出力28kトークンを想定
            temperature=0,
        )
        corrected_text = response["choices"][0]["message"]["content"]
        corrected_chunks.append(corrected_text)

    # -------------------------
    # 4) 全チャンクの補正後テキストを結合し、最終文字起こしとする
    # -------------------------
    full_transcription = "\n".join(corrected_chunks)

    return full_transcription

