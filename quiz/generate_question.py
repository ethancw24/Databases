import sys
import os
import json
import django
from dotenv import load_dotenv
from openai import OpenAI
from django.db import connection

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("OPENAI_API_KEY not found!")
client = OpenAI(api_key=api_key)

MAX_PER_RUN = 10
MAX_TOTAL_GENS = 30
GEN_TRACK_FILE = os.path.join(os.path.dirname(__file__), "total_gens.txt")

def get_total_generated():
    try:
        with open(GEN_TRACK_FILE, "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0

def update_total_generated(n_new):
    total = get_total_generated() + n_new
    with open(GEN_TRACK_FILE, "w") as f:
        f.write(str(total))

def generate_code_question():
    prompt = (
        "Generate a unique Python multiple-choice quiz question involving a short code snippet. "
        "Keep the code beginner-friendly (e.g., print statements, loops, functions, string formatting, lists). "
        "Choose a random concept and do not reuse previous questions. "
        "Return only JSON with the keys: 'question', 'correct_answer', and 'wrong_answers' (3 of them). "
        "Do not include markdown or triple backticks. Format it like:\n"
        "{"
        "\"question\": \"...Python code here...\", "
        "\"correct_answer\": \"...\", "
        "\"wrong_answers\": [\"...\", \"...\", \"...\"]"
        "}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            timeout=10
        )
        content = response.choices[0].message.content

        cleaned = content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.removeprefix("```json").strip()
        if cleaned.endswith("```"):
            cleaned = cleaned.removesuffix("```").strip()

        data = json.loads(cleaned)

        #Clean up the responses
        data["question"] = clean_answers(data["question"])
        data["correct_answer"] = clean_answers(data["correct_answer"])
        data["wrong_answers"] = clean_answers(clean_answers(ans) for ans in data["wrong_answers"][:3]) # Since there are only 4 options one is right 3 are wrong
        
        print("✅ Parsed & Cleaned JSON:", data)
        return data

    except Exception as e:
        print("❌ Error parsing OpenAI response:", e)
        print("Cleaned content was:\n", cleaned if 'cleaned' in locals() else content)
        return None

def save_to_db():
    data = generate_code_question()
    if data:
        print("Saving question:", data["question"])
        print("✅ Correct answer:", data["correct_answer"])
        print("❌ Wrong answers:", data["wrong_answers"])

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO quiz_question (text, wrong_answers, trust_rating) VALUES (%s, %s, 1.0) RETURNING qnum",
                [data["question"], json.dumps(data["wrong_answers"])]
            )
            qnum = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO quiz_rightanswer (qnum_id, text) VALUES (%s, %s)",
                [qnum, data["correct_answer"]]
            )

        print(f"✅ Saved question {qnum}")
        return True
    else:
        print("Failed to generate question.")
        return False
    
def clean_answers(text):
    return str(text).strip().strip("[]\"'")

def clean_answers(text):
    return str(text).strip().strip("[]\"'")

if __name__ == "__main__":
    print("Starting question generation")
    total_now = get_total_generated()
    room_left = MAX_TOTAL_GENS - total_now

    if room_left <= 0:
        print("Max total generations reached. Aborting.")
    else:
        count = min(MAX_PER_RUN, room_left)
        successes = 0

        for i in range(count):
            print(f"Generating {i + 1} of {count}")
            if save_to_db():
                successes += 1

        update_total_generated(successes)
        print(f"✅ {successes} new questions added. Total is now {get_total_generated()}.")

