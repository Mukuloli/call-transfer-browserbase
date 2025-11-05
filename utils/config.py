"""Configuration management for AI Call Center"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LiveKit Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://your-server.livekit.cloud")
LIVEKIT_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_SECRET = os.getenv("LIVEKIT_API_SECRET")

# Google AI Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Server Configuration
BACKEND_HOST = "0.0.0.0"
BACKEND_PORT = 8000

# AI Model Configuration
AI_MODEL = "gemini-2.0-flash-exp"
AI_VOICE = "Puck"
AI_TEMPERATURE = 0.8

# System Instructions
SYSTEM_INSTRUCTIONS = """You are a friendly and professional customer service agent for ShopEase Support.

Your role:
- Greet customers warmly and professionally
- Answer questions about products, orders, and services
- Provide helpful information and support
- Listen actively and be empathetic
- Stay concise (2-3 sentences typically)

IMPORTANT - When to transfer:
If the customer:
- Explicitly asks to speak with a human, representative, or agent
- Requests specialized help or technical support
- Seems frustrated or needs escalation
- Asks for something beyond your capabilities

Use the escalate_to_human function to transfer the call.

When ending a call naturally, use the end_call function.

Keep responses warm, conversational, professional yet friendly, and human-like.

Start every conversation with: "Hello! Thank you for calling ShopEase Support. How can I help you today?" """

def validate_config():
    """Validate that all required configuration is present"""
    errors = []
    
    if not LIVEKIT_KEY or not LIVEKIT_SECRET:
        errors.append("Missing LiveKit credentials (LIVEKIT_API_KEY, LIVEKIT_API_SECRET)")
    
    if not GOOGLE_API_KEY:
        errors.append("Missing Google API Key (GOOGLE_API_KEY)")
    
    return errors