"""
Inference Script — CodeReviewArena
===================================
MANDATORY environment variables:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face / API key.
"""
import os
import sys
import json
import subprocess

# Auto-install dependencies
for pkg in ["openai", "requests"]:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

from openai import OpenAI
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "gpt-4o-mini")
HF_TOKEN     = os.getenv("HF_TOKEN")

ENV_URL = "https://mkdavboyzz-code-review-arena.hf.space"  # update after deploy

client = OpenAI(
    api_key=HF_TOKEN or "dummy",
    base_url=API_BASE_URL,
)

SYSTEM_PROMPT = """You are an expert code reviewer.
For each buggy Python code snippet you must:
1. Identify the bug type
2. Identify the bug line number
3. Propose a fix

Available bug types: off_by_one, wrong_operator, null_pointer,
integer_overflow, sql_injection, path_traversal, race_condition,
mutable_default, wrong_comparison, insecure_random

NEVER cite a CVE that you are not 100% sure exists.
If unsure about CVE, leave cve_reference as null.

Respond ONLY with valid JSON:
{
  "action_type": "identify_bug",
  "bug_type": "<bug_type>",
  "bug_line": <line_number>,
  "proposed_fix": "<fixed code>",
  "cve_reference": null
}"""


def call_llm(snippet) -> dict:
    prompt = (
        f"Title: {snippet.get('title')}\n"
        f"Buggy code:\n{snippet.get('buggy_code', '')[:800]}\n\n"
        f"Identify the bug and propose a fix."
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature=0,
            max_tokens=400,
        )
        raw = resp.choices[0].message.content.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        print(f"[WARN] LLM error: {e}")
        return {"action_type": "identify_bug", "bug_type": "wrong_operator", "bug_line": 1}


def run_task(task_id: str) -> dict:
    print(f"[START] task={task_id} model={MODEL_NAME}", flush=True)

    resp = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id}, timeout=30)
    if resp.status_code != 200:
        raise Exception(f"Reset failed: {resp.status_code}")

    data         = resp.json()
    obs          = data.get("observation", data)
    step         = 0
    total_reward = 0.0
    done         = False
    retrieved    = False
    last_id      = None

    while not done and step < 80:
        snippet = obs.get("current_snippet")
        if not snippet:
            break

        sid = snippet.get("id")
        if sid != last_id:
            retrieved = False
            last_id   = sid

        # Always retrieve first
        if not retrieved and not obs.get("retrieved_this_step", False):
            retrieved = True
            action = {"action_type": "retrieve", "snippet_id": sid}
        else:
            llm = call_llm(snippet)
            action = {
                "action_type":  llm.get("action_type", "identify_bug"),
                "snippet_id":   sid,
                "bug_type":     llm.get("bug_type"),
                "bug_line":     llm.get("bug_line"),
                "proposed_fix": llm.get("proposed_fix"),
                "cve_reference": llm.get("cve_reference"),
            }

        step_resp = requests.post(
            f"{ENV_URL}/step",
            json={"action": action},
            timeout=30,
        )
        if step_resp.status_code != 200:
            break

        step_data    = step_resp.json()
        obs          = step_data.get("observation", {})
        reward       = step_data.get("reward", 0.0)
        done         = step_data.get("done", False)
        total_reward += reward
        step         += 1

        print(f"[STEP] step={step} snippet={sid} action={action['action_type']} reward={round(reward,4)} done={done}", flush=True)

    counts     = {"task1_easy": 4, "task2_medium": 8, "task3_hard": 15}
    thresholds = {"task1_easy": 0.50, "task2_medium": 0.55, "task3_hard": 0.60}
    score      = round(max(0.0, min(1.0, total_reward / float(counts.get(task_id, 4)))), 4)
    passed     = score >= thresholds.get(task_id, 0.50)

    print(f"[END] task={task_id} score={score} passed={passed} steps={step}", flush=True)
    return {"score": score, "passed": passed, "steps": step}


if __name__ == "__main__":
    tasks      = ["task1_easy", "task2_medium", "task3_hard"]
    all_scores = []
    results    = {}

    for task_id in tasks:
        try:
            result = run_task(task_id)
            results[task_id] = result
            all_scores.append(result["score"])
        except Exception as e:
            print(f"[END] task={task_id} score=0.0 passed=False steps=0 error={e}", flush=True)
            results[task_id] = {"score": 0.0, "passed": False}
            all_scores.append(0.0)

    overall = round(sum(all_scores) / len(all_scores), 4) if all_scores else 0.0
    print(f"[SUMMARY] overall_mean={overall}", flush=True)

    with open("inference_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("[INFO] Results saved to inference_results.json", flush=True)