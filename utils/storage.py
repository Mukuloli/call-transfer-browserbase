"""In-memory storage for transfers, agents, and sessions"""

# Global storage
transfers = []
connected_agents = []
active_sessions = {}

def get_pending_transfers():
    """Get all pending transfers"""
    return [t for t in transfers if t["status"] == "pending"]

def get_transfer_by_id(transfer_id: str):
    """Find a transfer by ID"""
    return next((t for t in transfers if t["id"] == transfer_id), None)

def add_transfer(transfer: dict):
    """Add a new transfer to storage"""
    transfers.append(transfer)

def add_agent(websocket):
    """Add a connected agent"""
    connected_agents.append(websocket)

def remove_agent(websocket):
    """Remove a disconnected agent"""
    if websocket in connected_agents:
        connected_agents.remove(websocket)

def get_agent_count():
    """Get number of connected agents"""
    return len(connected_agents)

def get_active_session(room_name: str):
    """Get active session for a room"""
    return active_sessions.get(room_name)

def set_active_session(room_name: str, assistant):
    """Store active session"""
    active_sessions[room_name] = assistant

def remove_active_session(room_name: str):
    """Remove active session"""
    if room_name in active_sessions:
        del active_sessions[room_name]