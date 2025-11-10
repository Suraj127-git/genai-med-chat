# backend/scripts/export_training_data.py
"""
Export training data from MySQL conversation/messages to a jsonl file suitable for supervised fine-tuning.
Each line: {"prompt": "<prompt text>", "completion": "<completion text>"}

Strategy (simple):
 - For each conversation, pair each user message with the next bot message (if present).
 - You may filter by length, sanitize PHI, or add system prompts.
"""
import json
from app.repos.mysql_repo import engine
from sqlalchemy import text
from pathlib import Path

OUT_FILE = Path("backend/data/training_data.jsonl")

def export_jsonl(limit=None):
    """
    Exports pairs to OUT_FILE.
    """
    sql = """
    SELECT m1.conv_id, m1.content as user_text, m2.content as bot_text
    FROM messages m1
    JOIN messages m2 ON m1.conv_id = m2.conv_id AND m2.id > m1.id
    WHERE m1.sender='user' AND m2.sender='bot'
    ORDER BY m1.conv_id, m1.created_at
    """
    if limit:
        sql = sql + " LIMIT :limit"

    with engine.begin() as conn:
        rows = conn.execute(text(sql), {"limit": limit} if limit else {}).fetchall()
        OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUT_FILE, "w", encoding="utf-8") as fh:
            for r in rows:
                prompt = r["user_text"].strip()
                completion = r["bot_text"].strip()
                # Basic sanitization: ensure not empty
                if prompt and completion:
                    obj = {"prompt": prompt, "completion": completion}
                    fh.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print("Exported training pairs to", OUT_FILE)

if __name__ == "__main__":
    export_jsonl(limit=10000)
