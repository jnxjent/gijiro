import os

# 環境変数の設定
FFMPEG_PATH = "/home/site/wwwroot/ffmpeg-bin/ffmpeg"
FFPROBE_PATH = "/home/site/wwwroot/ffmpeg-bin/ffprobe"

# Python の環境変数に登録
os.environ["FFMPEG_PATH"] = FFMPEG_PATH
os.environ["FFPROBE_PATH"] = FFPROBE_PATH
