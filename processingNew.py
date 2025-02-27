import asyncio
import sys
from kowake import transcribe_and_correct
from extraction import extract_meeting_info_and_speakers
from docwriter import process_document  # ✅ 修正: ここを変更

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python processing.py <audio_file_path> <template_path> <output_file_path>")
        sys.exit(1)

    audio_file_path = sys.argv[1]
    template_path = sys.argv[2]
    output_file_path = sys.argv[3]

    try:
        # 1️⃣ 音声認識 & 情報抽出
        extracted_info = asyncio.run(extract_meeting_info_and_speakers(audio_file_path, template_path))
        if not isinstance(extracted_info, dict):
            raise ValueError("extracted_info が辞書型ではありません")

        print("[OK] 議事録情報＆話者推定が完了")

        # ✅ (修正) Wordファイルの更新（テーブルと議事録）
        process_document(output_file_path, output_file_path, extracted_info)

        print("[OK] Wordファイルの更新が完了")
        print("完了")

    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}")
        sys.exit(1)
