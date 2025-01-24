from flask import request, render_template
from storage import upload_to_blob, generate_blob_url
from processing import process_files
import asyncio

def setup_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    def upload():
        if request.method == 'POST':
            audio_file = request.files.get('audio_file')
            word_file = request.files.get('word_file')

            if not audio_file or not word_file:
                return "音声ファイルと Word ファイルを両方アップロードしてください。", 400

            try:
                # ファイルをAzure Blob Storageにアップロード
                audio_blob_name = f"audio/{audio_file.filename}"
                word_blob_name = f"word/{word_file.filename}"

                upload_to_blob(audio_blob_name, audio_file.stream)
                upload_to_blob(word_blob_name, word_file.stream)

                # Blob URLを生成
                audio_blob_url = generate_blob_url(audio_blob_name)
                word_blob_url = generate_blob_url(word_blob_name)

                # 処理実行
                output_blob_name = "output/updated_meeting_notes.docx"
                asyncio.run(process_files(audio_blob_url, word_blob_url, output_blob_name))

                # 処理後ファイルのURLを生成
                output_url = generate_blob_url(output_blob_name)
                return f"<a href='{output_url}' download>処理済みファイルをダウンロード</a>"
            except Exception as e:
                return f"処理中にエラーが発生しました: {e}", 500

        return render_template("index.html")
