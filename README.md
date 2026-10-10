# 🍵 Tea Time AI Home Lab

An AI-driven incident investigation workflow that replicates
enterprise-grade autonomous incident response using open-source
tools and **Podman** (no Docker required).

## 🧠 Concept

When monitoring tells AI **what's broken**, logs tell it
**what happened**, Git tells it **what changed**, ITSM tells it
**how to respond**, and a knowledge base tells it **what the org
already knows** — then AI can perform automated root cause analysis.

## 🏗️ Architecture

| Enterprise Tool | Home Substitute                     | Signal             |
| --------------- | ----------------------------------- | ------------------ |
| Dynatrace       | Prometheus + Alertmanager + Grafana | What's broken      |
| Splunk          | Grafana Loki                        | What happened      |
| GitLab          | Gitea                               | What changed       |
| ServiceNow      | Mock ITSM (FastAPI)                 | How to respond     |
| Confluence      | Wiki.js                             | What the org knows |
| Resolve.ai      | Ollama + Python Agent               | AI Brain           |

## 🚀 Quick Start (Podman)

```bash
git clone https://github.com/YOUR_USERNAME/tea-time-ai-homelab.git
cd tea-time-ai-homelab
podman-compose up -d --build
```
