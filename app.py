from flask import Flask
from routes import setup_routes

# Flaskアプリの初期化
app = Flask(__name__)

# ルートをセットアップ
setup_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
