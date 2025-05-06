#!/bin/bash

set -e

# 1. Create virtual environment if it does not exist
echo "==== [1/5] Creating virtual environment if it does not exist ===="
if [ ! -d "env" ]; then
  python3 -m venv env
fi

# 2. Activate virtual environment
echo "==== [2/5] Activating virtual environment ===="
source env/bin/activate

# 3. Install dependencies
echo "==== [3/5] Installing dependencies ===="
pip install --upgrade pip
pip install -r requirements.txt

# 4. Create MongoDB data directory if it does not exist
echo "==== [4/5] Creating MongoDB data directory if it does not exist ===="
if [ ! -d "$HOME/data/db" ]; then
  mkdir -p $HOME/data/db
fi

# 5. Check if mongod is running
echo "==== [5/5] Checking if mongod is running ===="
if ! pgrep mongod > /dev/null; then
  echo "Starting mongod in the background..."
  mongod --dbpath $HOME/data/db --bind_ip 127.0.0.1 --fork --logpath $HOME/data/db/mongod.log
else
  echo "mongod is already running."
fi

# Start the FastAPI app
python app.py
