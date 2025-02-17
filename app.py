from dotenv import load_dotenv
import os
from flask import Flask
from flask_cors import CORS
from routes import setup_routes
load_dotenv()

# Flaskアプリの初期化
app = Flask(__name__)

# CORSを有効化（全てのオリジンを許可）
CORS(app)

# ルートをセットアップ
setup_routes(app)

if __name__ == "__main__":
    from os import getenv
    port = int(getenv("PORT", 8000))  # 8000 をデフォルトに設定
    app.run(host="0.0.0.0", port=port, debug=False)
