# processing.py

import asyncio
from kowake import transcribe_and_correct
from extraction import extract_meeting_info_and_speakers
from docwriter import write_information_to_existing_table

async def process_files(audio_file_path, word_file_path, output_file_path):
    """
    1) 音声ファイルをチャンク処理し、DeepGram→OpenAI(1回目)で全文文字起こし
    2) その文字起こしから抽出情報＆話者推定(2回目AI)
    3) Wordファイルに情報転記 + 議事として全文を貼り付け
    """
    try:
        # 1) 全文文字起こし（1回目のAI）
        full_transcription = await transcribe_and_correct(audio_file_path)
        print("[OK] 全文文字起こしが完了")

        # 2) 抽出情報＋話者推定（2回目のAI）
        extracted_info = await extract_meeting_info_and_speakers(full_transcription)
        print("[OK] 議事録情報＆話者推定が完了")

        # 3) Wordファイル更新
        write_information_to_existing_table(
            word_file_path,
            output_file_path,
            extracted_info,
            full_transcription  # ← AIを通さずにそのまま使う
        )
        print("[OK] Wordへの転記が完了")

    except Exception as e:
        raise Exception(f"処理中にエラーが発生しました: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python processing.py <audio_file_path> <word_template_path> <output_docx_path>")
        sys.exit(1)

    audio_file_path   = sys.argv[1]
    word_file_path    = sys.argv[2]
    output_file_path  = sys.argv[3]

    asyncio.run(process_files(audio_file_path, word_file_path, output_file_path))
    print("完了")
