import os
import openai
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE  = os.getenv("OPENAI_API_BASE")
DEPLOYMENT_ID    = os.getenv("DEPLOYMENT_ID")

openai.api_key  = OPENAI_API_KEY
openai.api_base = OPENAI_API_BASE
openai.api_type = "azure"
openai.api_version = "2024-08-01-preview"

async def extract_meeting_info_and_speakers(transcription: str) -> dict:
    """
    (A) 会議情報(出席者,次回予定,次回開催場所,決定事項,宿題事項)を抽出
    (B) [Speaker X] 形式から推定話者名を推定（敬称「さん」は付けない）
    """

    # ----------------------------------------------------
    # A) まずは「会議情報」を抽出
    # ----------------------------------------------------
    prompt_info = (
        "以下の議事録から、次の情報を抽出してください:\n\n"
        "1. 出席者\n"
        "2. 次回予定\n"
        "3. 次回開催場所\n"
        "4. 決定事項\n"
        "5. 宿題事項\n\n"
        f"議事録:\n{transcription}\n\n"
        "【出力形式】:\n"
        "出席者: <内容>\n"
        "次回予定: <内容>\n"
        "次回開催場所: <内容>\n"
        "決定事項:\n- <内容>\n"
        "宿題事項:\n- <内容>\n"
    )

    try:
        response_info = openai.ChatCompletion.create(
            engine=DEPLOYMENT_ID,
            messages=[
                {
                    "role": "system",
                    "content": "あなたは議事録を解析するアシスタントです。"
                },
                {
                    "role": "user",
                    "content": prompt_info
                },
            ],
            max_tokens=4000,  # GPT-4の出力上限
            temperature=0,
        )
        content_info = response_info["choices"][0]["message"]["content"]

        # 情報を格納する辞書
        extracted_info = {
            "出席者": "",
            "次回予定": "",
            "次回開催場所": "",
            "決定事項": "",
            "宿題事項": "",
        }

        current_section = None
        for line in content_info.splitlines():
            line = line.strip()
            if line.startswith("出席者:"):
                current_section = "出席者"
                extracted_info[current_section] = line.replace("出席者:", "").strip()
            elif line.startswith("次回予定:"):
                current_section = "次回予定"
                extracted_info[current_section] = line.replace("次回予定:", "").strip()
            elif line.startswith("次回開催場所:"):
                current_section = "次回開催場所"
                extracted_info[current_section] = line.replace("次回開催場所:", "").strip()
            elif line.startswith("決定事項:"):
                current_section = "決定事項"
            elif line.startswith("宿題事項:"):
                current_section = "宿題事項"
            elif line.startswith("-") and current_section:
                extracted_info[current_section] += line + "\n"

        # 空欄なら「なし」に置き換え
        for key in extracted_info:
            extracted_info[key] = extracted_info[key].strip() or "なし"

    except Exception as e:
        raise Exception(f"情報抽出中にエラーが発生しました: {e}")

    # ----------------------------------------------------
    # B) 次に「話者推定」を行う（Speaker0 → 「鈴木」 など）
    #    ※ 敬称「さん」は付けない
    # ----------------------------------------------------
    try:
        prompt_speakers = (
            "以下のテキストで '[Speaker 0]' '[Speaker 1]' のような表記を、"
            "実際の話者名や役職などに推定変換してください。\n"
            "必ず敬称『さん』は付けず、名前だけにしてください。\n"
            "不明な場合は '[Speaker 0]→不明0' のようにしてください。\n\n"
            f"=== 議事録全文 ===\n{transcription}\n\n"
            "【出力形式】:\n"
            "- Speaker0 -> 田中\n"
            "- Speaker1 -> 山田\n"
            "のように箇条書きで全スピーカーを列挙してください。"
        )

        response_speakers = openai.ChatCompletion.create(
            engine=DEPLOYMENT_ID,
            messages=[
                {
                    "role": "system",
                    "content": "あなたは文字起こしを整理し話者名を推定するアシスタントです。"
                },
                {
                    "role": "user",
                    "content": prompt_speakers
                }
            ],
            max_tokens=4000,
            temperature=0,
        )
        content_speakers = response_speakers["choices"][0]["message"]["content"].strip()

        # ここでは例として extracted_info["推定話者"] に入れる
        extracted_info["推定話者"] = content_speakers

    except Exception as e:
        # 話者推定に失敗しても他の情報は返す
        extracted_info["推定話者"] = "推定不可"
        print(f"話者推定に失敗しました: {e}")

    # 最後にまとめて返す
    return extracted_info
