#!/bin/bash

echo "Stopping AgentAI services..."

# Kill processes by PID files
if [ -f "web.pid" ]; then
    WEB_PID=$(cat web.pid)
    if kill -0 $WEB_PID 2>/dev/null; then
        echo "Stopping web interface (PID: $WEB_PID)..."
        kill $WEB_PID
    fi
    rm -f web.pid
fi

if [ -f "api.pid" ]; then
    API_PID=$(cat api.pid)
    if kill -0 $API_PID 2>/dev/null; then
        echo "Stopping API backend (PID: $API_PID)..."
        kill $API_PID
    fi
    rm -f api.pid
fi

# Fallback: kill by port
echo "Cleaning up any remaining processes on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

echo "All services stopped."