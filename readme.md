🎧 AI Call Center - Complete System Flow
📋 System Overview
This is an intelligent call center where:

AI answers calls first (using Google Gemini)
Transfers to humans when needed
AI automatically leaves when human joins
Everything happens in real-time


🏗️ Architecture Components
1. FastAPI Backend Server (Port 8000)

Manages transfer requests
WebSocket for real-time notifications
Generates LiveKit room tokens
Tracks all active sessions

2. LiveKit AI Agent (Voice AI)

Joins LiveKit rooms automatically
Talks to customers using Gemini 2.0
Can transfer calls to humans
Disconnects gracefully when needed

3. Web Dashboard (index.html)

Human agents monitor incoming calls
Accept transfer requests
Join LiveKit rooms directly


🔄 Complete Flow (Step-by-Step)
PHASE 1: Customer Calls In 📞
1. Customer joins LiveKit room (via phone/web)
   ↓
2. LiveKit triggers the AI agent
   ↓
3. AI agent's entrypoint() function is called
   ↓
4. CallCenterAssistant is created
   ↓
5. Gemini Realtime model connects
   ↓
6. AI greets: "Hello! Thank you for calling ShopEase Support..."
What happens:

entrypoint(ctx: JobContext) is the entry point
Creates CallCenterAssistant instance
Sets up AgentSession with Gemini Realtime
Starts listening with noise cancellation
Generates initial greeting


PHASE 2: Conversation 💬
Customer: "I need help with my order"
   ↓
AI (Gemini): "I'd be happy to help! What's your order number?"
   ↓
Customer: "Actually, can I speak to a human?"
   ↓
AI detects transfer request
What happens:

Gemini processes speech in real-time
AI responds naturally and professionally
Conversation is logged in CallState
AI listens for transfer keywords


PHASE 3: Transfer Request 🔄
1. AI detects customer wants human
   ↓
2. escalate_to_human() function is called
   ↓
3. POST to /api/create-transfer
   ↓
4. Transfer object created:
   {
     "id": "transfer_1_143022",
     "room_name": "customer-room-123",
     "reason": "Customer request",
     "status": "pending"
   }
   ↓
5. All connected agents notified via WebSocket
   ↓
6. AI tells customer: "Transferring you now..."
Key Code:
python@function_tool
async def escalate_to_human(self, ctx: RunContext, reason: str):
    # Mark transfer as initiated
    self.state.transfer_initiated = True
    
    # Create transfer via API
    async with session.post(f"http://localhost:8000/api/create-transfer") as response:
        data = await response.json()
    
    return "I'm transferring you to our support specialist..."

PHASE 4: Human Agent Accepts 👤
1. Human agent sees notification in dashboard
   ↓
2. Clicks "Accept Call"
   ↓
3. POST to /api/accept-transfer with agent name
   ↓
4. Backend generates LiveKit token for human
   ↓
5. Backend signals AI to disconnect:
   active_sessions[room_name].state.should_disconnect = True
   ↓
6. Human receives:
   - Room token
   - Room name
   - LiveKit URL
   - Customer info
Key Code:
python@app.post("/api/accept-transfer")
async def accept_transfer(request: AcceptTransfer):
    # Mark transfer as accepted
    transfer["status"] = "accepted"
    
    # Signal AI to leave
    if room_name in active_sessions:
        active_sessions[room_name].state.should_disconnect = True
    
    # Generate token for human agent
    token = api.AccessToken(LIVEKIT_KEY, LIVEKIT_SECRET)
    token.with_identity(f"agent_{request.agent_name}")
    
    return {"token": jwt_token, "room_name": room_name}

PHASE 5: AI Disconnects 🚪
1. Human agent joins LiveKit room
   ↓
2. "participant_connected" event fires
   ↓
3. AI detects identity starts with "agent_"
   ↓
4. Sets should_disconnect = True
   ↓
5. Main loop breaks
   ↓
6. disconnect_ai_agent() called:
   - Saves conversation log
   - Closes AI session
   - Disconnects from room
   ↓
7. Human and customer now talk directly!