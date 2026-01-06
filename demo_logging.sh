#!/bin/bash
# demo_logging.sh
echo "Demonstrating API logging in 3 steps:"
echo "1. Starting API..."
python app.py &
API_PID=$!
sleep 3

echo "2. Making test requests..."
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"age":52,"sex":1,"cp":0,"trestbps":125,"chol":212,"fbs":0,"restecg":1,"thalach":168,"exang":0,"oldpeak":1.0,"slope":2,"ca":2,"thal":3}' \
  -s | jq .

echo "3. Showing logs..."
curl -s "http://localhost:8000/logs" | jq '.logs[-2:]'

echo "4. Showing metrics..."
curl -s "http://localhost:8000/metrics" | jq .

kill $API_PID 2>/dev/null