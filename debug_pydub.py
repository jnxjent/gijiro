import os
import logging
from pydub import AudioSegment

# デバッグ用のログ設定
logging.basicConfig(level=logging.DEBUG)

# FFMPEG のパスを明示的に設定
AudioSegment.converter = os.getenv("FFMPEG_PATH")
AudioSegment.ffprobe = os.getenv("FFPROBE_PATH")

# 環境変数が適用されているか確認
print(f"FFMPEG_PATH: {AudioSegment.converter}")
print(f"FFPROBE_PATH: {AudioSegment.ffprobe}")

# テストする音声ファイル
file_path = "C:/Users/021213/gijiro/downloads/英語取材サンプル.m4a"

# ファイルの存在確認
if not os.path.exists(file_path):
    print(f"ファイルが見つかりません: {file_path}")
else:
    print(f"ファイルが存在します: {file_path}")

# pydub で音声ファイルを開く
try:
    audio = AudioSegment.from_file(file_path)
    print("pydub で音声ファイルの読み込み成功！")
except Exception as e:
    print(f"エラー発生: {e}")
