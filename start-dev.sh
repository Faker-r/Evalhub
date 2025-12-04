#!/bin/bash

# Evalhub Development Server Startup Script

echo "🚀 Starting Evalhub Development Environment"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Please run 'uv sync' or 'pip install -e .' first."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Node modules not found. Please run 'cd frontend && npm install' first."
    exit 1
fi

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend server
echo "📦 Starting FastAPI backend on port 8000..."
uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend server
echo "⚛️  Starting React frontend on port 5173..."
cd frontend && npm run dev:client &
FRONTEND_PID=$!

echo ""
echo "✅ Development servers started!"
echo ""
echo "🌐 Frontend:  http://localhost:5173"
echo "🔧 API Docs:  http://localhost:8000/docs"
echo "💚 Health:    http://localhost:8000/api/health"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

