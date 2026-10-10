import requests
import json
import os
import logging

logger = logging.getLogger("teatime-investigator")

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
LOKI_URL = os.getenv("LOKI_URL", "http://loki:3100")
GITEA_URL = os.getenv("GITEA_URL", "http://gitea:3000")
ITSM_URL = os.getenv("ITSM_URL", "http://mock-itsm:8000")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")


def query_prometheus_alerts():
    try:
        r = requests.get(PROMETHEUS_URL + "/api/v1/alerts", timeout=5)
        return {"source": "Prometheus", "alerts": r.json().get("data", {}).get("alerts", [])}
    except Exception as e:
        return {"source": "Prometheus", "error": str(e)}


def query_prometheus_metrics(query):
    try:
        r = requests.get(PROMETHEUS_URL + "/api/v1/query", params={"query": query}, timeout=5)
        return {"source": "Prometheus", "query": query, "result": r.json()}
    except Exception as e:
        return {"source": "Prometheus", "error": str(e)}


def query_loki_logs(service="sample-app"):
    try:
        query = '{job="' + service + '"}'
        r = requests.get(LOKI_URL + "/loki/api/v1/query", params={"query": query, "limit": 20}, timeout=5)
        return {"source": "Loki", "logs": r.json()}
    except Exception as e:
        return {"source": "Loki", "error": str(e)}


def query_git_changes():
    try:
        r = requests.get(GITEA_URL + "/api/v1/repos/search", params={"limit": 5}, timeout=5)
        return {"source": "Gitea", "repos": r.json()}
    except Exception as e:
        return {"source": "Gitea", "error": str(e)}


def query_runbook(symptom):
    try:
        r = requests.get(ITSM_URL + "/api/runbook/" + symptom, timeout=5)
        return {"source": "Mock ITSM", "runbook": r.json()}
    except Exception as e:
        return {"source": "Mock ITSM", "error": str(e)}


def query_recent_changes():
    try:
        r = requests.get(ITSM_URL + "/api/changes/recent", timeout=5)
        return {"source": "Mock ITSM", "changes": r.json()}
    except Exception as e:
        return {"source": "Mock ITSM", "error": str(e)}


def ask_llm(prompt):
    try:
        r = requests.post(
            OLLAMA_HOST + "/api/generate",
            json={"model": "llama3.2:latest", "prompt": prompt, "stream": False},
            timeout=120
        )
        return r.json().get("response", "No response from LLM")
    except Exception as e:
        return "LLM unavailable: " + str(e) + " - using rule-based analysis"


def investigate_incident(alert):
    alert_name = alert.get("labels", {}).get("alertname", "Unknown")
    severity = alert.get("labels", {}).get("severity", "unknown")
    description = alert.get("annotations", {}).get("description", "")

    logger.info("Investigating: %s", alert_name)

    signals = {}

    logger.info("  Signal 1: Prometheus (Whats broken?)")
    signals["whats_broken"] = query_prometheus_alerts()
    signals["error_rate"] = query_prometheus_metrics(
        'rate(http_requests_total{job="sample-app",status="500"}[1m])'
    )

    logger.info("  Signal 2: Loki (What happened?)")
    signals["what_happened"] = query_loki_logs()

    logger.info("  Signal 3: Gitea (What changed?)")
    signals["what_changed"] = query_git_changes()

    symptom_map = {
        "HighErrorRate": "high_error_rate",
        "ServiceDown": "service_down",
        "HighLatency": "high_latency"
    }
    logger.info("  Signal 4: Mock ITSM (How to respond?)")
    signals["runbook"] = query_runbook(symptom_map.get(alert_name, "unknown"))
    signals["recent_changes"] = query_recent_changes()

    logger.info("  Signal 5: Wiki.js (What org knows?)")
    signals["org_knowledge"] = {
        "source": "Wiki.js",
        "note": "Knowledge search - to be implemented in Week 3"
    }

    logger.info("  Asking LLM to correlate findings...")
    llm_prompt = (
        "You are an SRE investigating an incident. Analyze:\n\n"
        "ALERT: " + alert_name + " (Severity: " + severity + ")\n"
        "DESCRIPTION: " + description + "\n"
        "RUNBOOK: " + json.dumps(signals.get("runbook", {}), default=str)[:500] + "\n"
        "RECENT CHANGES: " + json.dumps(signals.get("recent_changes", {}), default=str)[:500] + "\n\n"
        "Provide:\n"
        "1. ROOT CAUSE - What is most likely causing this?\n"
        "2. BLAST RADIUS - What is affected?\n"
        "3. RECOMMENDED ACTION - What to do now?\n"
        "4. CONFIDENCE - Low/Medium/High\n"
    )
    llm_analysis = ask_llm(llm_prompt)

    logger.info("Investigation complete for %s", alert_name)

    return {
        "alert": alert_name,
        "severity": severity,
        "signals": signals,
        "llm_analysis": llm_analysis
    }