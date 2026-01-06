# monitor.py - Simple metrics endpoint
from fastapi import APIRouter
import psutil
import datetime

router = APIRouter()

@router.get("/metrics")
async def get_metrics():
    """Simple system metrics"""
    with open("api_requests.log", "r") as f:
        total_requests = len(f.readlines())
    
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "total_requests": total_requests,
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }

@router.get("/logs")
async def get_logs(limit: int = 10):
    """View recent logs"""
    with open("api_requests.log", "r") as f:
        logs = f.readlines()[-limit:]
    return {"recent_logs": logs}