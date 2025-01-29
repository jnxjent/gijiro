from flask import Flask
from flask_cors import CORS
from routes import setup_routes

# Flaskアプリの初期化
app = Flask(__name__)

# CORSを有効化（全てのオリジンを許可）
CORS(app)

# ルートをセットアップ
setup_routes(app)

if __name__ == '__main__':
    # Flaskアプリを起動（ホスト: 全アドレス、ポート: 8000）
    app.run(host='0.0.0.0', port=8000)
