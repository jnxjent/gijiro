import os
from dotenv import load_dotenv

# .env ファイルを読み込む
load_dotenv()

# 環境変数の取得
print(os.getenv("FFMPEG_PATH"))
print(os.getenv("FFPROBE_PATH"))
