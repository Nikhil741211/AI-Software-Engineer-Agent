# AI Software Engineer Agent

An AI-powered software engineering agent that reads GitHub issues, analyzes the codebase, generates code fixes, runs tests inside a Docker sandbox, stores reasoning logs, supports human approval, and creates GitHub pull requests.

## Features

- GitHub Webhook Integration
- FastAPI Backend
- Redis Queue and RQ Worker
- Groq LLM Integration
- RAG with Sentence Transformers
- FAISS Vector Search
- AST Parsing
- Dependency Graph Analysis
- Docker Sandbox Testing
- SQLite Database Storage
- Frontend Dashboard
- Human Approval Workflow
- GitHub Pull Request Automation
- LangGraph Workflow

## Tech Stack

Python, FastAPI, Redis, RQ, Groq LLM, Docker, SQLite, GitHub API, FAISS, Sentence Transformers, LangGraph, HTML, CSS, JavaScript.

## Workflow

GitHub Issue → FastAPI Webhook → Redis Queue → Worker → AI Agent → RAG Search → Code Fix → Docker Test → Database → Dashboard → Human Approval → GitHub Pull Request

## Project Status

Completed:
- GitHub Webhooks
- AI Agent
- RAG + Embeddings
- LangGraph Workflow
- Docker Sandbox
- Human Approval
- GitHub PR Automation
- Frontend Dashboard

Project ready for internship demonstration and technical interviews.

## How to Run

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# AI Agent Test
