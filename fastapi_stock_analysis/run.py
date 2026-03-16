"""
Stock Analysis API - Run Script

Simple script to start the FastAPI application
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration
host = os.getenv("API_HOST", "0.0.0.0")
port = int(os.getenv("API_PORT", 8000))
log_level = os.getenv("LOG_LEVEL", "info")

# Check for API key
api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key:
    print("✅ Anthropic API Key found - Advanced LLM analysis enabled")
else:
    print("⚠️  Anthropic API Key not found - Basic analysis only")
    print("   Set ANTHROPIC_API_KEY in .env file for full features")

# Start the server
print(f"\n🚀 Starting Stock Analysis API...")
print(f"📍 Server will be available at: http://localhost:{port}")
print(f"📚 API Documentation: http://localhost:{port}/docs")
print(f"🏥 Health Check: http://localhost:{port}/health")
print("\n" + "="*50)
print("Press Ctrl+C to stop the server")
print("="*50 + "\n")

if __name__ == "__main__":
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=True,
            log_level=log_level
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down server...")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
