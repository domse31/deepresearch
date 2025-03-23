#!/bin/bash
# Start both the LinkedIn service and ngrok in separate terminals

# Create logs directory
mkdir -p logs

# Check if ngrok is available
if ! command -v ngrok &> /dev/null; then
    echo "Error: ngrok is not installed or not in PATH"
    echo "Please install ngrok from https://ngrok.com/download"
    exit 1
fi

# Start the LinkedIn service
echo "Starting LinkedIn service..."
python -m deepresearch.run --linkedin-service > logs/linkedin_service.log 2>&1 &
LINKEDIN_PID=$!
echo "LinkedIn service started with PID $LINKEDIN_PID"

# Wait for the service to start
sleep 2

# Start ngrok
echo "Starting ngrok..."
ngrok http 8080 > logs/ngrok.log 2>&1 &
NGROK_PID=$!
echo "ngrok started with PID $NGROK_PID"

# Wait for ngrok to start
sleep 3

# Get the ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*')

if [ -z "$NGROK_URL" ]; then
    echo "Error: Could not get ngrok URL. Check logs/ngrok.log for details."
    exit 1
fi

echo ""
echo "==================================================="
echo "LinkedIn service is running!"
echo "ngrok URL: $NGROK_URL"
echo "==================================================="
echo ""
echo "To use this URL in your research, add this to your .env file:"
echo "CALLBACK_URL=$NGROK_URL/webhook/clay-callback"
echo ""
echo "Press Ctrl+C to stop the services"

# Handle cleanup on exit
trap "echo 'Stopping services...'; kill $LINKEDIN_PID $NGROK_PID; echo 'Services stopped.'" EXIT

# Keep script running
wait $LINKEDIN_PID