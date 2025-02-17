# docwriter.py

import re
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn

def write_information_to_existing_table(
    word_file_path: str,
    output_file_path: str,
    extracted_info: dict,
    full_transcription: str
):
    """
    1) テンプレートWordファイルを開く
    2) テーブル各セルへ抽出情報を書き込み。
       - '出席者' セルには "推定話者" の名前一覧を「、」区切りで1行にまとめる
    3) 「■議事」段落に全文文字起こしを追記 → "Speaker0→○○" の置換
    4) フォントをMeiryoに統一して保存
    """

    doc = Document(word_file_path)

    # 推定話者情報 (例: "- Speaker0 -> 本田\n- Speaker1 -> 橋本")
    speaker_info_text = extracted_info.get("推定話者", "")
    # => 辞書 {"Speaker0":"本田","Speaker1":"橋本"} を作成
    speaker_map = create_speaker_map(speaker_info_text)

    # ★ 出席者欄に書くため、「名前リスト」をパースする (敬称は外す)
    speaker_name_list = parse_speaker_names_only(speaker_info_text)
    # 例: ["本田", "橋本"]

    # ------------------------------------------------------
    # STEP A: テーブルの各セルを更新
    # ------------------------------------------------------
    for table in doc.tables:
        for row in table.rows:
            first_cell_text = row.cells[0].text.strip()

            if "出席者" in first_cell_text:
                # 出席者は「推定話者一覧」を「、」区切りで1行にまとめる
                if speaker_name_list:
                    row.cells[1].text = "、".join(speaker_name_list)
                else:
                    row.cells[1].text = "なし"

            elif "次回予定" in first_cell_text:
                row.cells[1].text = extracted_info.get("次回予定", "なし")

            elif "次回開催場所" in first_cell_text:
                row.cells[1].text = extracted_info.get("次回開催場所", "なし")

            elif "決定事項" in first_cell_text:
                row.cells[1].text = extracted_info.get("決定事項", "なし")

            elif "宿題事項" in first_cell_text:
                row.cells[1].text = extracted_info.get("宿題事項", "なし")

            elif "推定話者" in first_cell_text:
                # 別途「推定話者」という欄があるなら原文を記載
                row.cells[1].text = speaker_info_text or "不明"

    # ------------------------------------------------------
    # STEP B: 「■議事」段落を探して、全文文字起こしを追記
    #         → Speaker置換
    # ------------------------------------------------------
    paragraph_index = None
    for i, paragraph in enumerate(doc.paragraphs):
        if "■ 議事" in paragraph.text:
            paragraph_index = i
            # (1) そのまま追記（AIに再度かけない）
            paragraph.text += "\n" + full_transcription

            # (2) 次の段落に「以上」を右寄せで追加
            if i + 1 < len(doc.paragraphs):
                new_paragraph = doc.paragraphs[i + 1]
                new_paragraph.text = "以上"
                new_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
            break

    # 追記後、置換を実施
    if paragraph_index is not None:
        paragraph = doc.paragraphs[paragraph_index]
        replaced_paragraph_text = apply_speaker_map(paragraph.text, speaker_map)
        paragraph.text = replaced_paragraph_text

    # ------------------------------------------------------
    # STEP C: 文書全体のフォントを 'Meiryo' に統一
    # ------------------------------------------------------
    def set_meiryo_font(run):
        run.font.name = 'Meiryo'
        run.font.element.rPr.rFonts.set(qn('w:eastAsia'), 'Meiryo')

    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            set_meiryo_font(run)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        set_meiryo_font(run)

    # ------------------------------------------------------
    # STEP D: 保存
    # ------------------------------------------------------
    doc.save(output_file_path)


def create_speaker_map(speaker_info_text: str) -> dict:
    """
    '推定話者' 文字列 (例: '- Speaker0 -> 本田\n- Speaker1 -> 橋本')
    を解析して、{"Speaker0":"本田","Speaker1":"橋本"} のような辞書を返す。
    """
    mapping = {}
    for line in speaker_info_text.splitlines():
        line = line.strip()
        if line.startswith("-"):
            line = line.lstrip("-").strip()  # "Speaker0 -> 本田"
            if "->" in line:
                left, right = line.split("->", 1)
                speaker_key = left.strip()
                name_val = right.strip()
                # 敬称「さん」は除去
                name_val = name_val.replace("さん", "").strip()
                mapping[speaker_key] = name_val
    return mapping


def parse_speaker_names_only(speaker_info_text: str) -> list:
    """
    '推定話者' 文字列を解析し、「名前」だけのリストを返す。
    例:
      - Speaker0 -> 本田
      - Speaker1 -> 橋本 さん
    => ["本田", "橋本"]
    """
    names = []
    for line in speaker_info_text.splitlines():
        line = line.strip()
        if line.startswith("-") and "->" in line:
            # 例: "- Speaker0 -> 本田"
            _, right = line.split("->", 1)
            name_val = right.strip()
            name_val = name_val.replace("さん", "").strip()
            names.append(name_val)
    return names


def apply_speaker_map(text: str, speaker_map: dict) -> str:
    """
    本文中の "Speaker0" や "[Speaker 0]" を [本田] のように置換する。
    """
    replaced_text = text
    for speaker_key, name_val in speaker_map.items():
        digits = re.sub(r"[^0-9]", "", speaker_key)  # "0","1" 等
        pattern = rf"\[?[sS][pP][eE][aA][kK][eE][rR]\s*{digits}\]?"
        replaced_text = re.sub(pattern, f"[{name_val}]", replaced_text, flags=re.IGNORECASE)
    return replaced_text
