import os

file_path = os.path.abspath("downloads/英語取材サンプル.m4a")  # フルパスを取得
print(f"Checking file existence: {file_path}")
print(f"Exists: {os.path.exists(file_path)}")
