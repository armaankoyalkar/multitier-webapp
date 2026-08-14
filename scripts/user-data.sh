#!/bin/bash
# EC2 user-data script -- bootstraps the Python/Flask task manager app.
#
# This file is a Terraform template (see infra/asg.tf). db_host, db_user, db_pass,
# db_name, and app_code are injected automatically by `templatefile()` at apply
# time -- db_host comes live from the RDS resource, app_code is the current
# contents of app/app.py. No manual editing of this file is required.

set -e

DB_HOST="${db_host}"
DB_USER="${db_user}"
DB_PASS="${db_pass}"
DB_NAME="${db_name}"

# 1. Install Python (Ubuntu 22.04/24.04 LTS)
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3 python3-pip python3-venv

# 2. App directory + virtual environment
mkdir -p /opt/app
cd /opt/app
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install flask mysql-connector-python gunicorn

# 3. Deploy the Flask application (this is the live content of app/app.py)
cat > /opt/app/app.py <<'PYEOF'
${app_code}
PYEOF

# 4. systemd service -- passes DB config via environment variables, restarts on
#    crash, and starts automatically on boot
cat > /etc/systemd/system/flaskapp.service <<EOF
[Unit]
Description=Flask Task Manager App
After=network.target

[Service]
User=root
WorkingDirectory=/opt/app
Environment=PATH=/opt/app/venv/bin
Environment=DB_HOST=$DB_HOST
Environment=DB_USER=$DB_USER
Environment=DB_PASS=$DB_PASS
Environment=DB_NAME=$DB_NAME
ExecStart=/opt/app/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable flaskapp
systemctl start flaskapp
