---
title: CodeReviewArena
emoji: 🔍
colorFrom: red
colorTo: blue
sdk: docker
pinned: false
---

# 🔍 CodeReviewArena: Adversarial Multi-Agent Code Review RL Environment

[![OpenEnv](https://img.shields.io/badge/OpenEnv-compatible-brightgreen)](https://openenv.dev)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🔗 Links
- **HF Space:** https://huggingface.co/spaces/mkdavboyzz/code_review_arena
- **GitHub:** https://github.com/mkstudioslearncbse-art/code-review-arena
- **API Docs:** https://mkdavboyzz-code-review-arena.hf.space/docs
- **Training Notebook:** https://colab.research.google.com/drive/1CV_ml50YkwGpUFhvC4sa_HRw67mmXPbD
- **Blog Post:** https://huggingface.co/spaces/mkdavboyzz/code_review_arena/blob/main/Blog.md

---

## 🎯 Problem

Every day, developers push thousands of lines of code to production. Human reviewers miss subtle bugs under time pressure. Security vulnerabilities such as SQL injection, path traversal, and race conditions slip through disguised as normal code. No reinforcement learning training environment existed specifically for adversarial code review. CodeReviewArena fills this gap.

---

## 🏗️ Environment Design

CodeReviewArena is an OpenEnv-compatible RL environment where a CodeReviewer agent learns to detect and fix bugs in Python code through adversarial self-play and adaptive difficulty escalation.

Episode Flow:
1. Agent receives buggy Python code snippet
2. Agent issues RETRIEVE — RAG retrieves relevant bug patterns from knowledge base
3. Agent identifies bug type and location
4. Agent proposes a fix
5. Fix is executed in sandbox and verified programmatically
6. Reward computed from 4 independent signals
7. Difficulty escalates if agent succeeds consistently

### Agent Actions

| Action | Description |
|---|---|
| retrieve | Query knowledge base for relevant bug patterns |
| identify_bug | Identify bug type and line number |
| propose_fix | Submit corrected code |
| escalate | Flag as critical security vulnerability |
| mark_clean | Declare code has no bugs |

---

## 🏆 Reward Function

Four independent verifiable reward signals that are impossible to game without actually solving the task:

reward = 0.35 x detection_accuracy
       + 0.20 x localization_accuracy
       + 0.25 x fix_correctness
       + 0.10 x retrieval_discipline
       + 0.10 x efficiency
       + execution_bonus
       + hallucination_penalty

**Sandbox Execution Verification** — proposed fixes are actually executed in a subprocess. If the fix runs cleanly, +0.2 bonus. If it times out, -0.3 penalty. This makes the reward verifiable and objective.

**Hallucination-Aware Penalty** — two trap snippets contain plausible but fake CVE identifiers. If the agent cites these fake CVEs, it receives a -0.8 penalty. This trains agents to be accurate, not just confident.

**Adaptive Difficulty** — if the agent catches 3 consecutive bugs correctly, the difficulty multiplier increases by 0.15 up to a maximum of 2.0x. If it misses 3 consecutive bugs, difficulty decreases. This creates a measurable self-improvement signal over episodes.

---

## 📋 Tasks

| Task | Snippets | Bug Types | Difficulty | Pass Threshold |
|---|---|---|---|---|
| task1_easy | 4 | Off-by-one, wrong operator | Easy | 0.50 |
| task2_medium | 8 | Logic bugs, mutable defaults | Medium | 0.55 |
| task3_hard | 15 | Security bugs, hallucination traps | Hard | 0.60 |
| task4_longhor | 3 | Multi-function files, 4 connected bugs each | Long-Horizon | 0.55 |
---

## 🧠 Knowledge Base

10 bug patterns indexed with FAISS using paraphrase-multilingual-MiniLM-L12-v2. Retrieval is hybrid — FAISS semantic search combined with keyword boost for deterministic pattern matching on known bug names.

Bug patterns covered: OFF_BY_ONE, WRONG_OPERATOR, NULL_POINTER, INTEGER_OVERFLOW, SQL_INJECTION, PATH_TRAVERSAL, RACE_CONDITION, MUTABLE_DEFAULT, WRONG_COMPARISON, INSECURE_RANDOM.

---

## 📊 Training

Trained using GRPO with Unsloth on Qwen2.5-1.5B-Instruct.

**Wandb Training Run:** https://wandb.ai/mkstudioslearncbse-amrita-vishwa-vidyapeetham/code-review-arena/runs/g2ml5nva
![Reward Curve](https://raw.githubusercontent.com/mkstudioslearncbse-art/code-review-arena/main/assets/reward_curve.png)
![Loss Curve](https://raw.githubusercontent.com/mkstudioslearncbse-art/code-review-arena/main/assets/loss_curve.png)

---

## 📈 Baseline Results (HeuristicAgent, seed=42)

| Task | Score | Pass |
|---|---|---|
| task1_easy | 0.5300 | ✅ |
| task2_medium | 1.0000 | ✅ |
| task3_hard | 1.0000 | ✅ |
| task4_longhor | 0.6821 | ✅ |
| Overall Mean | 0.8030 | ✅ |
---

## 🚀 Quick Start

Reset the environment:

curl -X POST https://mkdavboyzz-code-review-arena.hf.space/reset -H "Content-Type: application/json" -d '{"task_id": "task1_easy"}'

Step with a retrieve action:

curl -X POST https://mkdavboyzz-code-review-arena.hf.space/step -H "Content-Type: application/json" -d '{"action": {"action_type": "retrieve", "snippet_id": "s001"}}'

---

## 🎯 Hackathon Themes

Theme 1 — Multi-Agent Interactions: Adversarial arms race between injector difficulty and reviewer capability.

Theme 2 — Long-Horizon Planning: task4_longhor requires agents to analyze multi-function files with 4 connected bugs across 10-20 steps with sparse delayed rewards.

Theme 3.1 — World Modeling Professional Tasks: Agent interacts with real tools — FAISS knowledge base via RAG, sandbox subprocess for fix execution, and adaptive difficulty system. Cannot exploit shortcuts as reward is verified programmatically through actual code execution.

Theme 4 — Self-Improvement: Adaptive difficulty multiplier escalates as agent improves through self-play.

Theme 5 — Wild Card: Novel adversarial code intelligence domain with no prior OpenEnv environment.

---

## 📁 Project Structure

code_review_arena/
├── models.py              # Pydantic models: Action, Observation, Reward
├── baseline.py            # HeuristicAgent baseline runner
├── inference.py           # Hackathon inference script
├── openenv.yaml           # OpenEnv spec metadata
├── Dockerfile             # Container definition
├── assets/
│   ├── reward_curve.png   # GRPO training reward curve
│   └── loss_curve.png     # GRPO training loss curve
├── corpus/
│   └── snippets.py        # 15 Python bug snippets with ground truth
├── rag/
│   ├── retriever.py       # Hybrid FAISS + keyword retriever
│   ├── bug_patterns.json  # 10 bug pattern documents
│   └── index.faiss        # Pre-built vector index
├── server/
│   ├── app.py             # FastAPI entry point
│   ├── environment.py     # Core environment + adaptive difficulty
│   └── reward.py          # 4 independent reward signals + sandbox
└── tasks/
    └── graders.py         # grade_task1/2/3 + BaseAgent

---

## 📜 License

MIT — see [LICENSE](LICENSE)