from table_writer import table_writer
from minutes_writer import write_minutes_section

def process_document(word_file_path: str, output_file_path: str, extracted_info: dict):
    """
    統合関数: テーブルの更新と議事録の書き込みを処理する

    :param word_file_path: 読み込むWORDファイルのパス（テンプレート）
    :param output_file_path: 更新後のWORDファイルの保存先
    :param extracted_info: 生成AIが抽出した辞書データ {label: value}
    """
    # ✅ (修正) `table_writer()` で更新後のファイルを `output_file_path` に保存
    table_writer(word_file_path, output_file_path, extracted_info)

    # ✅ `replaced_transcription` を取得
    replaced_transcription = extracted_info.get("replaced_transcription", "")

    # ✅ (修正) 修正後の `output_file_path` を使って議事録を書き込む
    write_minutes_section(output_file_path, output_file_path, replaced_transcription)
