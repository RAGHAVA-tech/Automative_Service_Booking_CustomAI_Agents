"""
Automotive Service AI Agent — FastAPI REST API Server
=====================================================
Run: uvicorn api_server:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from main import AutomotiveServiceOrchestrator, ServiceType

app = FastAPI(
    title="AutoCare Pro AI Agent API",
    description="Multi-framework AI agent: CrewAI + AutoGen + Semantic Kernel + Voice",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

orchestrator = AutomotiveServiceOrchestrator()


class ChatRequest(BaseModel):
    message: str
    phone: Optional[str] = None

class BookingRequest(BaseModel):
    customer_id: str
    service_type: str
    preferred_date: str
    preferred_time: Optional[str] = None

class PhoneCallRequest(BaseModel):
    caller_phone: str
    conversation: list[str]

class NewCustomerRequest(BaseModel):
    name: str
    phone: str
    email: str
    vehicle_make: str
    vehicle_model: str
    vehicle_year: int


@app.get("/")
def root():
    return {
        "service": "AutoCare Pro AI Agent",
        "agents": ["ARIA (CrewAI)", "APEX (AutoGen)", "NEXUS (Semantic Kernel)", "VOICE"],
        "status": "operational"
    }

@app.post("/chat")
async def chat(req: ChatRequest):
    """Chat via CrewAI receptionist — auto-triggers booking & CRM."""
    return orchestrator.handle_chat_interaction(req.message, req.phone)

@app.post("/book")
async def book(req: BookingRequest):
    """Direct booking via AutoGen agent."""
    try:
        service = ServiceType(req.service_type)
    except ValueError:
        raise HTTPException(400, f"Valid services: {[s.value for s in ServiceType]}")
    result = orchestrator.booking_agent.orchestrate_booking(
        req.customer_id, service, req.preferred_date, req.preferred_time
    )
    if not result["success"]:
        raise HTTPException(404, result.get("error"))
    return result

@app.post("/call")
async def call(req: PhoneCallRequest):
    """Simulate phone call via VOICE Handler."""
    return orchestrator.handle_phone_call(req.caller_phone, req.conversation)

@app.get("/crm/{customer_id}")
async def crm_profile(customer_id: str):
    """Semantic Kernel CRM intelligence pipeline."""
    result = orchestrator.crm_agent.run_customer_pipeline(customer_id)
    if not result["success"]:
        raise HTTPException(404, result.get("error"))
    return result

@app.post("/customers")
async def create_customer(req: NewCustomerRequest):
    c = orchestrator.crm.create_customer(
        req.name, req.phone, req.email,
        req.vehicle_make, req.vehicle_model, req.vehicle_year
    )
    return {"success": True, "customer_id": c.id}

@app.get("/customers")
async def list_customers():
    return orchestrator.get_crm_dashboard()["customers"]

@app.get("/appointments")
async def list_appointments():
    return orchestrator.get_crm_dashboard()["appointments"]

@app.get("/dashboard")
async def dashboard():
    return orchestrator.get_crm_dashboard()

@app.get("/slots/{date}")
async def slots(date: str):
    available = orchestrator.crm.get_available_slots(date)
    return {"date": date, "available_slots": available}
