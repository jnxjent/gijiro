import re

def create_speaker_map(speaker_info_text: str) -> dict:
    """
    例:
      - Speaker0 -> 本田
      - Speaker1 -> 橋本 さん
    のような文字列から、{"Speaker0": "本田", "Speaker1": "橋本"} を返す。
    
    改善点:
      - 行頭のハイフンや空白を柔軟に許容
      - "->" の前後の空白をトリム
      - 名前の末尾に付く「さん」や余計な空白を除去
    """
    mapping = {}
    # speaker_key と名前部分を抽出。名前部分は「さん」など余計な語尾を除去できるようにする
    pattern = re.compile(
        r"^-?\s*(?P<speaker>Speaker\s*\d+)\s*->\s*(?P<name>.+)$", re.IGNORECASE)
    
    for line in speaker_info_text.splitlines():
        line = line.strip()
        match = pattern.match(line)
        if match:
            speaker_key = match.group("speaker").strip()
            name_val = match.group("name").strip()
            # 名前の末尾の「さん」や不要な記号・空白を除去（必要に応じて他の敬称も追加可能）
            name_val = re.sub(r"[さん\s]+$", "", name_val)
            mapping[speaker_key] = name_val
    return mapping


def parse_speaker_names_only(speaker_info_text: str) -> list:
    """
    例:
      - Speaker0 -> 本田
      - Speaker1 -> 橋本 さん
    から ["本田", "橋本"] のリストを返す。
    """
    names = []
    # 同じ正規表現で抽出
    pattern = re.compile(
        r"^-?\s*Speaker\s*\d+\s*->\s*(?P<name>.+)$", re.IGNORECASE)
    for line in speaker_info_text.splitlines():
        line = line.strip()
        match = pattern.match(line)
        if match:
            name_val = match.group("name").strip()
            name_val = re.sub(r"[さん\s]+$", "", name_val)
            names.append(name_val)
    return names


def apply_speaker_map(text: str, speaker_map: dict) -> str:
    """
    本文中の "Speaker0" や "[Speaker 0]" などを、対応する名前に置換する。
    例:
      "Hello Speaker0 and [Speaker 0]!"  -> "Hello [本田] and [本田]!"
    
    改善点:
      - 正規表現で余分な空白や角括弧の有無を許容
    """
    replaced_text = text
    for speaker_key, name_val in speaker_map.items():
        # speaker_key から数字のみを抽出（例: "Speaker 0" -> "0"）
        digits = re.sub(r"\D", "", speaker_key)
        # 例: パターンは "[?]speaker\s*digits[?]" を許容する
        pattern = re.compile(rf"\[?\s*speaker\s*{digits}\s*\]?", re.IGNORECASE)
        replaced_text = pattern.sub(f"[{name_val}]", replaced_text)
    return replaced_text
