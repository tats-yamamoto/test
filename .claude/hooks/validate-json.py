"""A1: JSON構文検証 (PostToolUse)
.ai-secretary/ 配下の JSON ファイルへの書き込み後、構文を自動検証する。
壊れた JSON を即検出し、修正を促す。
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

def main():
    tool_input_raw = os.environ.get("CLAUDE_TOOL_INPUT", "{}")
    try:
        tool_input = json.loads(tool_input_raw)
    except json.JSONDecodeError:
        return

    file_path = tool_input.get("file_path", "").replace("\\", "/")

    # .ai-secretary 配下の .json ファイルのみ対象
    if ".ai-secretary/" not in file_path or not file_path.endswith(".json"):
        return

    # 実際のファイルパス（OS形式）で読み込み
    actual_path = tool_input.get("file_path", "")
    try:
        with open(actual_path, "r", encoding="utf-8") as f:
            json.load(f)
    except json.JSONDecodeError as e:
        print(f"[JSON構文エラー] {file_path} の構文が壊れています: {e}")
        print("即座に修正してください。")
        sys.exit(1)
    except FileNotFoundError:
        pass
    except Exception:
        pass

if __name__ == "__main__":
    main()
