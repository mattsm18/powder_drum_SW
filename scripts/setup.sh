#!/bin/bash
sudo apt update
sudo apt install -y python3-picamera2
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt