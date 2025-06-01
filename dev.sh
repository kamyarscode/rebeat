#! /bin/bash

# run the backend
cd backend
source .rebeat/bin/activate
python3 app.py &

# run the frontend
cd ../frontend
bun run dev &
