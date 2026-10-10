from fastapi import FastAPI, Request
from investigator import investigate_incident
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("teatime-ai-agent")

app = FastAPI(title="Tea Time AI Agent")


@app.get("/")
def root():
    return {"service": "Tea Time AI Agent", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/alert")
async def receive_alert(request: Request):
    payload = await request.json()
    alerts = payload.get("alerts", [])

    logger.info("Received %d alert(s) from Alertmanager", len(alerts))

    results = []
    for alert in alerts:
        alert_name = alert.get("labels", {}).get("alertname", "Unknown")
        status = alert.get("status", "unknown")
        severity = alert.get("labels", {}).get("severity", "unknown")

        logger.info("  Alert: %s | %s | %s", alert_name, severity, status)

        if status == "firing":
            result = investigate_incident(alert)
            results.append(result)
        else:
            results.append({"alert": alert_name, "status": "resolved"})

    return {"received": len(alerts), "investigations": results}


if __name__ == '__main__':
    import uvicorn
    logger.info("Tea Time AI Agent starting on port 8080...")
    uvicorn.run(app, host='0.0.0.0', port=8080)