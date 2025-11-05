#!/bin/bash

echo "================================================"
echo " Personal Finance Assistant - Full Stack Startup"
echo "================================================"
echo ""

echo "Starting Backend Server..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

echo "Waiting for backend to initialize..."
sleep 5

echo ""
echo "Starting Frontend Server..."
cd frontend
streamlit run app.py &
FRONTEND_PID=$!
cd ..

echo ""
echo "================================================"
echo " Servers are running!"
echo "================================================"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:8501"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
