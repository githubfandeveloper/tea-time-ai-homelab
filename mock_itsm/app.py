from fastapi import FastAPI
import datetime

app = FastAPI(title="Tea Time Mock ITSM")

incidents = []

runbooks = {
    "high_error_rate": {
        "title": "High Error Rate Runbook",
        "priority": "P2",
        "steps": [
            "1. Check application logs for error patterns",
            "2. Verify recent deployments in Gitea",
            "3. Check resource utilization (CPU/Memory)",
            "4. If caused by recent deploy then rollback",
            "5. If resource issue then scale up or restart",
            "6. Monitor for 15 minutes after remediation"
        ],
        "escalation": "SRE Team",
        "sla_response": "15 minutes"
    },
    "service_down": {
        "title": "Service Down Runbook",
        "priority": "P1",
        "steps": [
            "1. Confirm service is unreachable",
            "2. Check if container is running",
            "3. Check for OOMKilled or crash",
            "4. Review recent changes in Gitea",
            "5. Restart the service",
            "6. If restart fails then rollback",
            "7. Escalate if unresolved in 10 minutes"
        ],
        "escalation": "SRE Team Lead",
        "sla_response": "5 minutes"
    },
    "high_latency": {
        "title": "High Latency Runbook",
        "priority": "P3",
        "steps": [
            "1. Check P95/P99 latency in Prometheus",
            "2. Identify slow endpoints",
            "3. Check database performance",
            "4. Look for resource contention",
            "5. Consider scaling or caching"
        ],
        "escalation": "Application Team",
        "sla_response": "30 minutes"
    }
}

change_records = [
    {
        "id": "CHG001",
        "title": "Deploy sample-app v1.2.0",
        "status": "completed",
        "timestamp": "2025-01-15T09:00:00Z",
        "risk": "medium"
    },
    {
        "id": "CHG002",
        "title": "Update database connection pool",
        "status": "completed",
        "timestamp": "2025-01-15T10:30:00Z",
        "risk": "low"
    }
]


@app.get("/")
def root():
    return {"service": "Tea Time Mock ITSM", "status": "running"}


@app.get("/api/runbook/{symptom}")
def get_runbook(symptom: str):
    runbook = runbooks.get(symptom)
    if runbook:
        return {"found": True, "runbook": runbook}
    return {
        "found": False,
        "message": "No runbook for " + symptom + ". Escalate to L2.",
        "available": list(runbooks.keys())
    }


@app.get("/api/runbooks")
def list_runbooks():
    return {"runbooks": runbooks}


@app.post("/api/incident")
def create_incident(data: dict):
    incident = {
        "id": "INC" + str(len(incidents) + 1).zfill(5),
        "created": str(datetime.datetime.now()),
        "status": "open",
    }
    incident.update(data)
    incidents.append(incident)
    return incident


@app.get("/api/incidents")
def list_incidents():
    return {"incidents": incidents}


@app.get("/api/changes/recent")
def recent_changes():
    return {"changes": change_records}