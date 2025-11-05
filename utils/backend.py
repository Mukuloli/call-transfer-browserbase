"""FastAPI backend server"""
import logging
from datetime import datetime
from fastapi import FastAPI, WebSocket
from starlette.middleware.cors import CORSMiddleware
from livekit import api
import uvicorn

from .config import LIVEKIT_KEY, LIVEKIT_SECRET, LIVEKIT_URL, BACKEND_HOST, BACKEND_PORT
from .models import AcceptTransfer
from . import storage

logger = logging.getLogger("backend")

# ============================================
# FASTAPI APPLICATION
# ============================================
app = FastAPI(title="AI Call Center Backend")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "running",
        "message": "AI Call Center Backend",
        "agents_online": storage.get_agent_count(),
        "pending_transfers": len(storage.get_pending_transfers())
    }

@app.websocket("/ws/agent")
async def agent_websocket(websocket: WebSocket):
    """WebSocket for real-time agent notifications"""
    await websocket.accept()
    storage.add_agent(websocket)
    logger.info(f"✅ Agent connected. Total: {storage.get_agent_count()}")
    
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to call center"
        })
        
        while True:
            await websocket.receive_text()
            
    except Exception as e:
        logger.info(f"Agent disconnected: {e}")
    finally:
        storage.remove_agent(websocket)

@app.get("/api/transfers")
async def get_transfers():
    """Get all pending transfers"""
    pending = storage.get_pending_transfers()
    return {"transfers": pending, "count": len(pending)}

@app.post("/api/accept-transfer")
async def accept_transfer(request: AcceptTransfer):
    """Accept a transfer and get LiveKit token"""
    transfer = storage.get_transfer_by_id(request.transfer_id)
    if not transfer:
        return {"error": "Transfer not found"}
    
    if transfer["status"] != "pending":
        return {"error": "Transfer already handled"}
    
    transfer["status"] = "accepted"
    transfer["agent_name"] = request.agent_name
    transfer["accepted_at"] = datetime.now().isoformat()
    
    room_name = transfer["room_name"]
    
    # Signal AI to disconnect
    assistant = storage.get_active_session(room_name)
    if assistant:
        assistant.state.should_disconnect = True
        logger.info(f"🚪 Signaling AI to leave room {room_name}")
    
    # Generate LiveKit token
    token = api.AccessToken(LIVEKIT_KEY, LIVEKIT_SECRET)
    token.with_identity(f"agent_{request.agent_name}")
    token.with_name(request.agent_name)
    token.with_grants(api.VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True
    ))
    
    jwt_token = token.to_jwt()
    logger.info(f"✅ Transfer accepted by {request.agent_name} for room {room_name}")
    
    # Notify all connected agents
    for agent_ws in storage.connected_agents:
        try:
            await agent_ws.send_json({
                "type": "transfer_accepted",
                "transfer_id": request.transfer_id
            })
        except:
            pass
    
    return {
        "success": True,
        "token": jwt_token,
        "room_name": room_name,
        "livekit_url": LIVEKIT_URL,
        "caller_info": transfer
    }

@app.post("/api/create-transfer")
async def create_transfer(room_name: str, reason: str = "Customer request"):
    """Create new transfer request"""
    transfer = {
        "id": f"transfer_{len(storage.transfers)}_{datetime.now().strftime('%H%M%S')}",
        "room_name": room_name,
        "reason": reason,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    storage.add_transfer(transfer)
    
    logger.info(f"📞 New transfer created: {transfer['id']}")
    
    # Notify all connected agents
    for agent_ws in storage.connected_agents:
        try:
            await agent_ws.send_json({
                "type": "incoming_call",
                "transfer": transfer
            })
        except:
            pass
    
    return {"success": True, "transfer": transfer}

@app.post("/api/end-transfer/{transfer_id}")
async def end_transfer(transfer_id: str):
    """Mark transfer as completed"""
    transfer = storage.get_transfer_by_id(transfer_id)
    if transfer:
        transfer["status"] = "completed"
        transfer["completed_at"] = datetime.now().isoformat()
        logger.info(f"✅ Transfer completed: {transfer_id}")
    return {"success": True}

def start_server():
    """Start the FastAPI backend server"""
    logger.info("\n🚀 Starting Backend Server...")
    logger.info(f"   URL: http://localhost:{BACKEND_PORT}")
    logger.info(f"   WebSocket: ws://localhost:{BACKEND_PORT}/ws/agent")
    
    uvicorn.run(app, host=BACKEND_HOST, port=BACKEND_PORT, log_level="warning")