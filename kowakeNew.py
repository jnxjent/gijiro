import os
import openai
from dotenv import load_dotenv

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

# pydub をインポートして、明示的に ffmpeg, ffprobe のパスを設定
from pydub import AudioSegment
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# デバッグ用に出力
print(f"FFMPEG_BINARY: {AudioSegment.converter}")
print(f"FFPROBE_BINARY: {AudioSegment.ffprobe}")

# 以下、OpenAI や Deepgram の初期化処理など
from deepgram import Deepgram

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

# 以下、transcribe_and_correct 関数等の処理…
