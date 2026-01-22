#!/bin/bash
set -xe

# Variables passed from CDK
REPO_URL=${REPO_URL:-"https://github.com/Siyabongahenry/SteinalyticsReportAPI.git"}
BRANCH=${BRANCH:-"main"}
APP_DIR=${APP_DIR:-"SteinalyticsReportAPI"}

yum update -y
yum install -y python3 git

cd /home/ec2-user

# Clone repo with branch
git clone --depth 1 -b $BRANCH $REPO_URL $APP_DIR
cd $APP_DIR

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
cat <<EOF > /etc/systemd/system/fastapi.service
[Unit]
Description=FastAPI Uvicorn service

[Service]
WorkingDirectory=/home/ec2-user/$APP_DIR
ExecStart=/home/ec2-user/$APP_DIR/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable fastapi.service
systemctl start fastapi.service
