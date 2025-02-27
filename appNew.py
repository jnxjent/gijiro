from dotenv import load_dotenv
import os
from flask import Flask
from flask_cors import CORS
from routes import setup_routes
from pydub import AudioSegment

load_dotenv()

# pydub の ffmpeg パスを指定（実際のパスに合わせてください）
AudioSegment.converter = "/opt/homebrew/bin/ffmpeg"

# Flask インスタンスの生成
app = Flask(__name__)

# CORS の設定
CORS(app)

# ルーティングの設定
setup_routes(app)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    # 指定した IP アドレスにバインド（例: 192.168.1.3）
    app.run(host="192.168.1.3", port=port, debug=False)
