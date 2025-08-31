#!/bin/bash

# Start the web interface from coding-crew directory with UV environment
echo "Starting AgentAI Web Interface..."
cd coding-crew
PYTHONPATH="/Users/royashish/AI/AgentAI:$PYTHONPATH" uv run python -m uvicorn web.app:app --host 0.0.0.0 --port 8000 --reload &
WEB_PID=$!
echo "Web interface started on port 8000 (PID: $WEB_PID)"

# Start the API backend
echo "Starting AgentAI API Backend..."
python main.py &
API_PID=$!
echo "API backend started (PID: $API_PID)"

# Save PIDs for cleanup
echo $WEB_PID > ../web.pid
echo $API_PID > ../api.pid

echo "AgentAI is running!"
echo "Web Interface: http://localhost:8000"
echo "API Backend: Check coding-crew logs"
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo "Stopping services..."; kill $WEB_PID $API_PID 2>/dev/null; exit' INT
wait