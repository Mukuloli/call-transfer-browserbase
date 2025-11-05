"""
AI Call Center - Main Entry Point
Run this file to start the complete system
"""
import threading
import time
from utils import config, backend, agent

def main():
    """Start the AI Call Center system"""
    
    print("\n" + "="*60)
    print("🎧 AI CALL CENTER - GEMINI REALTIME")
    print("="*60)
    
    # Validate configuration
    errors = config.validate_config()
    if errors:
        print("\n❌ CONFIGURATION ERRORS:")
        for error in errors:
            print(f"   - {error}")
        print("\n💡 Please set the required environment variables in .env file")
        return
    
    print("\n✅ Configuration loaded")
    print(f"   LiveKit: {config.LIVEKIT_URL}")
    print(f"   AI Model: {config.AI_MODEL}")
    print(f"   Voice: {config.AI_VOICE}")
    
    # Start backend server in separate thread
    print("\n🚀 Starting backend server...")
    backend_thread = threading.Thread(target=backend.start_server, daemon=True)
    backend_thread.start()
    
    # Wait for backend to start
    time.sleep(3)
    
    print("\n" + "="*60)
    print("✅ SYSTEM READY")
    print("="*60)
    print("\n📋 Next Steps:")
    print("   1. Open index.html in your browser")
    print("   2. Enter your name and click 'Go Online'")
    print("   3. Make a test call to your LiveKit room")
    print("   4. Say 'I want to speak to a human'")
    print("   5. Accept the call in the dashboard")
    print("   6. AI will automatically disconnect - humans talk directly!")
    print("\n💡 Test phrases:")
    print("   - 'Can I speak to a real person?'")
    print("   - 'Transfer me to an agent'")
    print("   - 'I need human help'")
    print("\n🔗 URLs:")
    print(f"   Backend API: http://localhost:{config.BACKEND_PORT}")
    print(f"   WebSocket: ws://localhost:{config.BACKEND_PORT}/ws/agent")
    print(f"   API Docs: http://localhost:{config.BACKEND_PORT}/docs")
    print("\n🛑 Press Ctrl+C to stop\n")
    
    # Start AI agent (blocks until stopped)
    try:
        agent.start_agent()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        print("✅ Goodbye!\n")

if __name__ == "__main__":
    main()