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

## 🎯 Problem

Every day developers push buggy code to production. Human reviewers miss subtle bugs under time pressure. Security vulnerabilities slip through disguised as normal code. **No RL training environment existed to train agents for adversarial code review.**

## 🏗️ Environment

CodeReviewArena is an OpenEnv-compatible RL environment where:

- **CodeReviewer agent** reads buggy Python code, retrieves relevant bug patterns via RAG, identifies the bug type and location, and proposes a fix
- **Hallucination-aware reward** penalizes agents that cite fake CVE references (-0.8 penalty)
- **Self-improving difficulty** escalates as agent performance improves
- **3 difficulty tasks** from obvious bugs to critical security vulnerabilities

## 🤖 Agent Actions

| Action | Description |
|---|---|
| `retrieve` | Look up bug patterns in knowledge base |
| `identify_bug` | Point to bug type and line |
| `propose_fix` | Submit corrected code |
| `escalate` | Flag as critical security issue |
| `mark_clean` | Declare code has no bugs |

## 🏆 Reward Function
## 📊 Results

| Task | Difficulty | Heuristic Baseline | Pass Threshold |
|---|---|---|---|
| task1_easy | Easy | 0.4988 | 0.50 |
| task2_medium | Medium | 0.5365 | 0.55 |
| task3_hard | Hard | 0.6289 ✅ | 0.60 |
| **Mean** | — | **0.5547** | — |

## 🚀 Training

Trained using GRPO with Unsloth on Qwen2.5-1.5B-Instruct.
Training script: [Google Colab](#)

## 🔗 Links

- **HF Space:** https://huggingface.co/spaces/mkdavboyzz/code_review_arena
- **GitHub:** https://github.com/mkstudioslearncbse-art/code-review-arena
- **API Docs:** https://mkdavboyzz-code-review-arena.hf.space/docs

## 🎯 Themes

- Theme 1: Multi-Agent Interactions (Adversarial arms race)
- Theme 4: Self-Improvement (Adaptive difficulty escalation)
- Theme 5: Wild Card (Novel adversarial code intelligence)