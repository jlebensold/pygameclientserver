#!/bin/bash

# Kill any existing Python processes running the game
pkill -f "python.*(server.py|client.py)"

# Start the server
python server.py &
SERVER_PID=$!

# Wait for server to start
sleep 1

# Start multiple clients
for i in {1..2}; do
    python client.py &
    CLIENT_PIDS[$i]=$!
    sleep 0.5
done

# Wait for user input to stop
echo "Press Enter to stop all game instances..."
read

# Kill all processes
kill $SERVER_PID
for pid in "${CLIENT_PIDS[@]}"; do
    kill $pid
done

echo "All game instances stopped." 