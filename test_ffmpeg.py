import os
from dotenv import load_dotenv
from pydub import AudioSegment

# .env を読み込む
load_dotenv()

# FFMPEG, FFPROBE のパスを取得
FFMPEG_PATH = os.getenv("FFMPEG_PATH")
FFPROBE_PATH = os.getenv("FFPROBE_PATH")

# pydub に適用
AudioSegment.converter = FFMPEG_PATH
AudioSegment.ffprobe = FFPROBE_PATH

# 設定の確認
print(f"FFMPEG_PATH: {AudioSegment.converter}")
print(f"FFPROBE_PATH: {AudioSegment.ffprobe}")

# 簡単な音声処理テスト（ファイルがあれば実行）
try:
    audio = AudioSegment.from_file("test_audio.mp3")  # 何か適当な音声ファイル
    print("音声ファイルの読み込みに成功しました！")
except Exception as e:
    print(f"エラー発生: {e}")
