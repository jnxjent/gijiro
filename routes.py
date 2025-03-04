from flask import request, render_template
from storage import upload_to_blob, download_blob
from extraction import extract_meeting_info_and_speakers
from docwriter import process_document
from pathlib import Path
from datetime import datetime
import asyncio
import logging

def setup_routes(app):
    logger = logging.getLogger("routes")
    logging.basicConfig(level=logging.INFO)

    @app.route('/', methods=['GET', 'POST'])
    def upload():
        if request.method == 'POST':
            try:
                audio_file = request.files.get('audio_file')
                word_file = request.files.get('word_file')

                if not audio_file or not word_file:
                    logger.error(f"Files missing. audio_file={audio_file}, word_file={word_file}")
                    return render_template("error.html", message="音声ファイルと Word ファイルを両方アップロードしてください。"), 400

                audio_blob_name = f"audio/{audio_file.filename}"
                word_blob_name  = f"word/{word_file.filename}"

                logger.info(f"Uploading audio: {audio_file.filename}")
                audio_url = upload_to_blob(audio_blob_name, audio_file.stream)

                logger.info(f"Uploading word: {word_file.filename}")
                word_url = upload_to_blob(word_blob_name, word_file.stream)

                if not audio_url or not word_url:
                    logger.error("Blob URL generation failed.")
                    return render_template("error.html", message="Blob URL generation failed"), 500

                downloads_dir = Path("./downloads")
                downloads_dir.mkdir(exist_ok=True)

                audio_local_path = downloads_dir / audio_file.filename
                word_local_path  = downloads_dir / word_file.filename

                logger.info(f"Downloading audio file to {audio_local_path}")
                download_blob(audio_blob_name, str(audio_local_path))

                logger.info(f"Downloading word file to {word_local_path}")
                download_blob(word_blob_name, str(word_local_path))

                uploads_dir = Path("./uploads")
                uploads_dir.mkdir(exist_ok=True)

                timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
                output_filename   = f"updated_meeting_notes - {timestamp}.docx"
                output_file_local = uploads_dir / output_filename

                logger.info(f"Processing files: {audio_local_path}, {word_local_path}")

                extracted_info = asyncio.run(extract_meeting_info_and_speakers(
                    str(audio_local_path), str(word_local_path)
                ))

                if not extracted_info:
                    logger.error("[ERROR] extracted_info が空です")
                    return render_template("error.html", message="議事録の情報抽出に失敗しました"), 500

                try:
                    process_document(str(word_local_path), str(output_file_local), extracted_info)

                    logger.info("[OK] Wordファイルへの転記が完了")
                except Exception as e:
                    logger.error(f"[ERROR] process_document でエラー発生: {e}")
                    return render_template("error.html", message=f"Wordファイルの更新に失敗しました: {e}"), 500

                try:
                    with open(output_file_local, "rb") as f:
                        final_doc_blob_path = f"processed/{output_filename}"
                        updated_word_url = upload_to_blob(final_doc_blob_path, f)

                    if not updated_word_url:
                        logger.error("[ERROR] 処理後の Word ファイルのアップロードに失敗")
                        return render_template("error.html", message="処理後の Word ファイルのアップロードに失敗しました"), 500

                    logger.info(f"[OK] Updated Word file uploaded to Blob: {updated_word_url}")
                except Exception as e:
                    logger.error(f"[ERROR] Word ファイルのアップロード中にエラー発生: {e}")
                    return render_template("error.html", message=f"処理後の Word ファイルのアップロードに失敗: {e}"), 500

                return render_template("result.html",
                    message="処理成功！",
                    output_file_path=str(output_file_local).replace("\\", "/"),
                    uploaded_audio_url=audio_url,
                    uploaded_word_url=word_url,
                    updated_word_url=updated_word_url
                )

            except Exception as e:
                logger.error(f"Error during processing: {e}")
                return render_template("error.html", message=f"Error during processing: {e}"), 500

        return render_template("index.html")
