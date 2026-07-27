import json
from pathlib import Path

import pandas as pd

from llm.ollama_client import generate


# -------------------------------
# Paths
# -------------------------------

ROOT = Path(__file__).resolve().parent.parent

JOBS_CSV = ROOT / "jobs copy 2.csv"
RESUME_FILE = ROOT / "resume" / "master_resume.md"
PROMPT_FILE = ROOT / "prompts" / "score_prompt.txt"
OUTPUT_CSV = ROOT / "outputs" / "jobs_scored.csv"

OUTPUT_CSV.parent.mkdir(exist_ok=True)


# -------------------------------
# Helpers
# -------------------------------

def load_text(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def clean_json(response: str) -> str:
    """
    Removes markdown code fences if the model returns:

    ```json
    {...}
    ```
    """

    response = response.strip()

    if response.startswith("```json"):
        response = response[7:]

    if response.startswith("```"):
        response = response[3:]

    if response.endswith("```"):
        response = response[:-3]

    return response.strip()


# -------------------------------
# Load static files
# -------------------------------

resume = load_text(RESUME_FILE)
prompt_template = load_text(PROMPT_FILE)

jobs = pd.read_csv(JOBS_CSV)

jobs = jobs.head(10)

results = []

# -------------------------------
# Score every job
# -------------------------------

for idx, row in jobs.iterrows():

    print("=" * 80)
    print(f"{idx + 1}/{len(jobs)}")
    print(row["Company"])
    print(row["Title"])
    print("=" * 80)

    prompt = f"""
{prompt_template}

==============================
CANDIDATE RESUME
==============================

{resume}

==============================
JOB DESCRIPTION
==============================

Title:
{row["Title"]}

Company:
{row["Company"]}

Location:
{row["Location"]}

Description:
{row["Description"]}
"""

    try:

        response = generate(prompt)

        cleaned = clean_json(response)

        parsed = json.loads(cleaned)

        results.append({

            **row.to_dict(),

            "ATS Score":
                parsed.get("score"),

            "Recommendation":
                parsed.get("recommendation"),

            "Strengths":
                ", ".join(parsed.get("strengths", [])),

            "Missing Keywords":
                ", ".join(parsed.get("missing_keywords", [])),

            "Resume Sections":
                ", ".join(
                    parsed.get(
                        "resume_sections_to_emphasize",
                        [],
                    )
                ),

            "Reason":
                parsed.get("reason"),

            "Raw Response":
                response,

        })

        print(
            f"Score: {parsed.get('score')}"
        )

    except Exception as e:

        print(e)

        results.append({

            **row.to_dict(),

            "ATS Score": None,
            "Recommendation": "ERROR",
            "Strengths": "",
            "Missing Keywords": "",
            "Resume Sections": "",
            "Reason": "",
            "Raw Response": response if "response" in locals() else "",

        })


# -------------------------------
# Save
# -------------------------------

df = pd.DataFrame(results)

df.sort_values(
    by="ATS Score",
    ascending=False,
    na_position="last",
    inplace=True,
)

df.to_csv(
    OUTPUT_CSV,
    index=False,
)

print()
print("=" * 80)
print(f"Saved {len(df)} scored jobs")
print(OUTPUT_CSV)
print("=" * 80)