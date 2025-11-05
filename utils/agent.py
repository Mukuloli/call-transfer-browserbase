"""AI Agent implementation using LiveKit and Google Gemini"""
import asyncio
import os
import json
import logging
from datetime import datetime
from livekit import rtc
from livekit.agents import (
    JobContext, WorkerOptions, cli, AgentSession, 
    Agent, RoomInputOptions, function_tool, RunContext
)
from livekit.plugins import google as google_livekit
from livekit.plugins import noise_cancellation

from .config import AI_MODEL, AI_VOICE, AI_TEMPERATURE, SYSTEM_INSTRUCTIONS
from .models import CallState
from . import storage

logger = logging.getLogger("agent")

# ============================================
# AI ASSISTANT
# ============================================
class CallCenterAssistant(Agent):
    """AI Assistant with transfer and call management capabilities"""
    
    def __init__(self, room_name: str):
        super().__init__(instructions=SYSTEM_INSTRUCTIONS)
        self.room_name = room_name
        self.state = CallState()
    
    @function_tool
    async def escalate_to_human(self, ctx: RunContext, reason: str = "Customer request") -> str:
        """Transfer call to human agent"""
        if self.state.transfer_initiated:
            return "Transfer already in progress."
        
        self.state.transfer_initiated = True
        logger.info(f"🔄 Escalating call | Reason: {reason}")
        
        try:
            # Create transfer request via API
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://localhost:8000/api/create-transfer",
                    params={"room_name": self.room_name, "reason": reason}
                ) as response:
                    data = await response.json()
                    logger.info(f"✅ Transfer ID: {data['transfer']['id']}")
            
            return "I'm transferring you to our support specialist now. Please hold for just a moment..."
            
        except Exception as e:
            logger.error(f"Transfer failed: {e}")
            self.state.transfer_initiated = False
            return "I apologize, I'm having trouble with the transfer. Let me try to help you directly instead."
    
    @function_tool
    async def end_call(self, ctx: RunContext) -> str:
        """End call gracefully"""
        if self.state.negative_sentiment_count > 0:
            goodbye = "Thank you for your patience. We sincerely apologize for any inconvenience. Your concern will be resolved soon. Goodbye!"
        else:
            goodbye = "Thank you for contacting us. Have a great day!"
        
        logger.info(f"📞 Call ended | Room: {self.room_name}")
        
        # Save conversation log
        await self.save_conversation_log()
        
        return goodbye
    
   

# ============================================
# AGENT ENTRYPOINT
# ============================================
async def entrypoint(ctx: JobContext):
    """AI Agent entry point - called when someone joins"""
    logger.info(f"\n{'='*60}")
    logger.info(f"🎯 NEW CALL")
    logger.info(f"   Room: {ctx.room.name}")
    logger.info(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
    logger.info(f"{'='*60}\n")
    
    # Create assistant instance
    assistant = CallCenterAssistant(ctx.room.name)
    storage.set_active_session(ctx.room.name, assistant)
    
    # Create agent session with Gemini Realtime
    session = AgentSession(
        llm=google_livekit.realtime.RealtimeModel(
            model=AI_MODEL,
            voice=AI_VOICE,
            temperature=AI_TEMPERATURE,
            instructions=SYSTEM_INSTRUCTIONS,
        )
    )
    
    # Start the session with noise cancellation
    await session.start(
        room=ctx.room,
        agent=assistant,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    # Generate initial greeting
    await session.generate_reply(
        instructions="Greet the user and offer your assistance. You should start by speaking in English."
    )
    
    logger.info("✅ AI Agent active and listening with Gemini Realtime...\n")
    
    # Monitor for participant changes - disconnect AI when human joins
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        # Check if this is a human agent (not the original caller)
        if participant.identity.startswith("agent_"):
            logger.info(f"👤 Human agent joined: {participant.identity}")
            logger.info(f"🚪 AI Agent disconnecting to allow human-to-human conversation...")
            
            # Set flag to disconnect
            assistant.state.should_disconnect = True
            
            # Disconnect the AI agent from the room
            asyncio.create_task(disconnect_ai_agent(ctx, session, assistant))
    
    # Keep session alive until disconnection is requested
    try:
        while not assistant.state.should_disconnect:
            await asyncio.sleep(1)
        
        logger.info(f"✅ AI Agent successfully disconnected from {ctx.room.name}")
        
    except Exception as e:
        logger.error(f"Error in AI agent loop: {e}")
    finally:
        # Cleanup
        storage.remove_active_session(ctx.room.name)

async def disconnect_ai_agent(ctx: JobContext, session: AgentSession, assistant: CallCenterAssistant):
    """Gracefully disconnect AI agent from the room"""
    try:
        
        # Stop the agent session
        await session.aclose()
        
        # Disconnect from the room
        await ctx.room.disconnect()
        
        logger.info("🔌 AI Agent disconnected from room")
        
    except Exception as e:
        logger.error(f"Error disconnecting AI: {e}")

def start_agent():
    """Start LiveKit AI agent worker"""
    logger.info("\n🤖 Starting AI Agent with Gemini Realtime...")
    logger.info(f"   Model: {AI_MODEL}")
    logger.info(f"   Voice: {AI_VOICE}")
    
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))