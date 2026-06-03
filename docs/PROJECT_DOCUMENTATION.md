# AI Software Engineer Agent - Project Documentation

## Abstract

This project is an AI-powered software engineering agent that reads GitHub issues, analyzes the codebase, generates code fixes, runs tests in a Docker sandbox, stores reasoning logs, supports human approval, and creates GitHub pull requests.

## Problem Statement

Manual bug fixing is time-consuming. Developers need to read issues, inspect code, identify the root cause, write fixes, test the code, and create pull requests. This project automates that workflow using an AI agent with human approval before merging.

## Objectives

- Automatically receive GitHub issues using webhooks
- Analyze source code using RAG, AST parsing, and dependency graph
- Generate code fixes using Groq LLM
- Run tests safely inside Docker
- Store reasoning logs in PostgreSQL
- Add cost guard and loop detection
- Provide human approval/rejection dashboard
- Create GitHub pull requests after approval

## System Architecture

GitHub
│
▼
GitHub Webhook
│
▼
FastAPI Backend
│
▼
Redis Queue
│
▼
RQ Worker
│
▼
AI Agent
├── RAG Search
├── AST Analysis
├── Dependency Graph
├── Loop Detector
└── Cost Guard
│
▼
Docker Sandbox
│
▼
Pytest Execution
│
▼
PostgreSQL Database
│
▼
Approval Dashboard
│
▼
Human Approval
│
▼
GitHub Pull Request

## Technology Stack

### Backend

* Python
* FastAPI

### Queue

* Redis
* RQ Worker

### AI

* Groq API
* Llama Model

### Database

* PostgreSQL

### DevOps

* Docker
* Docker Compose

### Version Control

* Git
* GitHub

### Frontend

* HTML
* CSS
* JavaScript

## Project Workflow

1. GitHub issue is created.
2. GitHub webhook sends issue data to FastAPI backend.
3. Backend stores the job in Redis Queue.
4. RQ Worker picks the job asynchronously.
5. AI Agent analyzes the codebase.
6. RAG identifies relevant files.
7. AST parser extracts functions and imports.
8. Dependency graph analyzes file relationships.
9. Groq LLM generates a code fix.
10. Fixed code is written to the project.
11. Tests are executed inside Docker sandbox.
12. Reasoning logs are stored in PostgreSQL.
13. Human reviews the generated fix.
14. Approval dashboard provides Approve/Reject options.
15. Approved fixes create GitHub Pull Requests.

## Major Modules

### Webhook Module

Receives GitHub issue events and forwards them to the processing pipeline.

### Queue Module

Uses Redis and RQ Worker for asynchronous processing.

### AI Agent Module

Responsible for reasoning, code analysis, fix generation, and test execution.

### RAG Module

Performs semantic search to identify the most relevant files.

### AST Analysis Module

Extracts functions, classes, and imports from source code.

### Dependency Graph Module

Analyzes relationships between project files.

### Guardrails Module

Implements cost limits and loop detection.

### Database Module

Stores issues, reasoning logs, approval status, and pull request information.

### Dashboard Module

Provides a human approval interface before PR creation.

## API Endpoints

### GET /

Returns backend health status.

### POST /webhook

Receives GitHub issue webhook payloads.

### GET /issues

Returns all stored issues from PostgreSQL.

### POST /approve

Approves generated fixes and creates GitHub Pull Requests.

### POST /reject

Rejects generated fixes.

## Results

* Successfully receives GitHub issues.
* Automatically analyzes codebases.
* Generates code fixes using AI.
* Executes tests inside Docker containers.
* Stores reasoning logs in PostgreSQL.
* Supports human approval workflow.
* Creates GitHub pull requests automatically after approval.

## Future Enhancements

* Support multi-repository analysis.
* Integrate advanced code review agents.
* Add automatic vulnerability scanning.
* Support multiple LLM providers.
* Add CI/CD integration.
* Generate pull request descriptions automatically.
* Add role-based access control.
* Implement distributed worker architecture.

## Conclusion

The AI Software Engineer Agent successfully automates the software maintenance workflow by integrating GitHub webhooks, AI-driven code analysis, Docker-based sandbox testing, PostgreSQL logging, and a human approval mechanism. The system reduces manual effort while maintaining safety through approval gates, cost limits, and loop detection. This project demonstrates the practical application of AI agents in modern software engineering workflows.

