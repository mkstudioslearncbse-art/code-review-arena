\# CodeReviewArena: Training LLMs to Catch Security Bugs Through Adversarial Self-Play



\## The Problem



Every day, engineers at large technology companies like Meta push thousands of lines of code to production. Despite sophisticated code review processes, subtle bugs and security vulnerabilities slip through — SQL injection, path traversal, race conditions — often disguised as perfectly normal-looking code. Human reviewers miss these under time pressure. No reinforcement learning training environment existed specifically for adversarial code review.



CodeReviewArena fills this gap.



\## What We Built



CodeReviewArena is an OpenEnv-compatible RL environment where a CodeReviewer agent learns to detect and fix bugs in Python code through adversarial self-play and adaptive difficulty escalation.



The agent follows this workflow every episode:

1\. Receives buggy Python code

2\. Issues RETRIEVE action — RAG retrieves relevant bug patterns from FAISS knowledge base

3\. Identifies bug type and exact line number

4\. Proposes a fix

5\. Fix is executed in a sandbox subprocess — verified programmatically

6\. Reward computed from 4 independent signals

7\. Difficulty escalates automatically if agent succeeds



\## The Reward Function



Four independent verifiable reward signals:



\- \*\*Detection accuracy (35%)\*\* — did the agent correctly identify the bug type?

\- \*\*Localization accuracy (20%)\*\* — did the agent find the right line number?

\- \*\*Fix correctness (25%)\*\* — is the proposed fix actually correct?

\- \*\*Retrieval discipline (10%)\*\* — did the agent retrieve before identifying?

\- \*\*Efficiency (10%)\*\* — did the agent complete without wasting steps?

\- \*\*Sandbox execution bonus (+0.2)\*\* — does the fix actually run in subprocess?

\- \*\*Hallucination penalty (-0.8)\*\* — did the agent cite a fake CVE?



The sandbox execution verification is the key research contribution. Proposed fixes are actually executed as Python code in a subprocess. If the fix runs cleanly, the agent gets a +0.2 bonus. If it times out or crashes, -0.3 penalty. This makes the reward impossible to game without actually solving the task.



\## Hallucination-Aware Training



Two trap snippets in the corpus contain plausible-sounding but completely fake CVE identifiers (CVE-2024-99999, CVE-2025-00001). If the agent cites these fake CVEs, it receives a -0.8 penalty. This trains agents to be accurate and grounded rather than confidently wrong — a critical property for any AI system deployed in a real engineering organization.



\## Self-Improving Arms Race



If the agent catches 3 consecutive bugs correctly, the difficulty multiplier increases by 0.15 (up to 2.0x). If it misses 3 consecutive bugs, difficulty decreases. This creates a measurable self-improvement signal that drives capability growth without manual curriculum design.



\## Long-Horizon Planning Task



Task 4 (task4\_longhor) presents the agent with multi-function Python files containing 4 connected bugs each. The agent must perform sequential analysis across the entire file, tracking state across 10-20 steps before receiving reward. This directly tests the kind of deep, multi-step reasoning that production code review requires.



\## Tasks



| Task | Snippets | Difficulty | Baseline Score |

|---|---|---|---|

| task1\_easy | 4 | Easy | 0.5300 |

| task2\_medium | 8 | Medium | 0.5795 |

| task3\_hard | 15 | Hard | 0.7617 |

| task4\_longhor | 3 | Long-Horizon | 0.6821 |

| \*\*Overall Mean\*\* | — | — | \*\*0.6383\*\* |



\## Training



We trained Qwen2.5-1.5B-Instruct using GRPO with Unsloth on this environment.



Training Notebook: https://colab.research.google.com/drive/1CV\_ml50YkwGpUFhvC4sa\_HRw67mmXPbD



\## Hackathon Themes Covered



\- \*\*Theme 1\*\* — Multi-Agent Interactions: Adversarial arms race between injector difficulty and reviewer capability

\- \*\*Theme 2\*\* — Long-Horizon Planning: Multi-bug files requiring 10-20 step sequential analysis with sparse rewards

\- \*\*Theme 3.1\*\* — World Modeling: Agent interacts with real tools — FAISS knowledge base, sandbox subprocess

\- \*\*Theme 4\*\* — Self-Improvement: Adaptive difficulty multiplier escalates as agent improves

\- \*\*Theme 5\*\* — Wild Card: Novel adversarial code intelligence domain



\## R\&D Applications



For a company like Meta maintaining billions of lines of code, CodeReviewArena directly addresses several research challenges. The verifiable reward function is suitable for large-scale RL post-training. The hallucination penalty trains agents to avoid confidently wrong answers. The long-horizon planning task tests deep multi-step reasoning across entire codebases.



\## Links



\- HF Space: https://huggingface.co/spaces/mkdavboyzz/code\_review\_arena

\- GitHub: https://github.com/mkstudioslearncbse-art/code-review-arena

\- API Docs: https://mkdavboyzz-code-review-arena.hf.space/docs

\- Training Notebook: # CodeReviewArena: Training LLMs to Catch Security Bugs Through Adversarial Self-Play



\## The Problem



Every day, engineers at large technology companies like Meta push thousands of lines of code to production. Despite sophisticated code review processes, subtle bugs and security vulnerabilities slip through — SQL injection, path traversal, race conditions — often disguised as perfectly normal-looking code. Human reviewers miss these under time pressure. No reinforcement learning training environment existed specifically for adversarial code review.



CodeReviewArena fills this gap.



\## What We Built



CodeReviewArena is an OpenEnv-compatible RL environment where a CodeReviewer agent learns to detect and fix bugs in Python code through adversarial self-play and adaptive difficulty escalation.



The agent follows this workflow every episode:

1\. Receives buggy Python code

2\. Issues RETRIEVE action — RAG retrieves relevant bug patterns from FAISS knowledge base

3\. Identifies bug type and exact line number

4\. Proposes a fix

5\. Fix is executed in a sandbox subprocess — verified programmatically

6\. Reward computed from 4 independent signals

7\. Difficulty escalates automatically if agent succeeds



\## The Reward Function



Four independent verifiable reward signals:



\- \*\*Detection accuracy (35%)\*\* — did the agent correctly identify the bug type?

\- \*\*Localization accuracy (20%)\*\* — did the agent find the right line number?

\- \*\*Fix correctness (25%)\*\* — is the proposed fix actually correct?

\- \*\*Retrieval discipline (10%)\*\* — did the agent retrieve before identifying?

\- \*\*Efficiency (10%)\*\* — did the agent complete without wasting steps?

\- \*\*Sandbox execution bonus (+0.2)\*\* — does the fix actually run in subprocess?

\- \*\*Hallucination penalty (-0.8)\*\* — did the agent cite a fake CVE?



The sandbox execution verification is the key research contribution. Proposed fixes are actually executed as Python code in a subprocess. If the fix runs cleanly, the agent gets a +0.2 bonus. If it times out or crashes, -0.3 penalty. This makes the reward impossible to game without actually solving the task.



\## Hallucination-Aware Training



Two trap snippets in the corpus contain plausible-sounding but completely fake CVE identifiers (CVE-2024-99999, CVE-2025-00001). If the agent cites these fake CVEs, it receives a -0.8 penalty. This trains agents to be accurate and grounded rather than confidently wrong — a critical property for any AI system deployed in a real engineering organization.



\## Self-Improving Arms Race



If the agent catches 3 consecutive bugs correctly, the difficulty multiplier increases by 0.15 (up to 2.0x). If it misses 3 consecutive bugs, difficulty decreases. This creates a measurable self-improvement signal that drives capability growth without manual curriculum design.



\## Long-Horizon Planning Task



Task 4 (task4\_longhor) presents the agent with multi-function Python files containing 4 connected bugs each. The agent must perform sequential analysis across the entire file, tracking state across 10-20 steps before receiving reward. This directly tests the kind of deep, multi-step reasoning that production code review requires.



\## Tasks



| Task | Snippets | Difficulty | Baseline Score |

|---|---|---|---|

| task1\_easy | 4 | Easy | 0.5300 |

| task2\_medium | 8 | Medium | 0.5795 |

| task3\_hard | 15 | Hard | 0.7617 |

| task4\_longhor | 3 | Long-Horizon | 0.6821 |

| \*\*Overall Mean\*\* | — | — | \*\*0.6383\*\* |



\## Training



We trained Qwen2.5-1.5B-Instruct using GRPO with Unsloth on this environment.



Training Notebook: https://colab.research.google.com/drive/1CV\_ml50YkwGpUFhvC4sa\_HRw67mmXPbD



\## Hackathon Themes Covered



\- \*\*Theme 1\*\* — Multi-Agent Interactions: Adversarial arms race between injector difficulty and reviewer capability

\- \*\*Theme 2\*\* — Long-Horizon Planning: Multi-bug files requiring 10-20 step sequential analysis with sparse rewards

\- \*\*Theme 3.1\*\* — World Modeling: Agent interacts with real tools — FAISS knowledge base, sandbox subprocess

\- \*\*Theme 4\*\* — Self-Improvement: Adaptive difficulty multiplier escalates as agent improves

\- \*\*Theme 5\*\* — Wild Card: Novel adversarial code intelligence domain



\## R\&D Applications



For a company like Meta maintaining billions of lines of code, CodeReviewArena directly addresses several research challenges. The verifiable reward function is suitable for large-scale RL post-training. The hallucination penalty trains agents to avoid confidently wrong answers. The long-horizon planning task tests deep multi-step reasoning across entire codebases.



\## Links



\- HF Space: https://huggingface.co/spaces/mkdavboyzz/code\_review\_arena

\- GitHub: https://github.com/mkstudioslearncbse-art/code-review-arena

\- API Docs: https://mkdavboyzz-code-review-arena.hf.space/docs

\- Training Notebook: https://colab.research.google.com/drive/1CV\_ml50YkwGpUFhvC4sa\_HRw67mmXPbD

