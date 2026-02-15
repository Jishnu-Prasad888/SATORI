#!/bin/bash
# SATORI Node Agent Installer

set -e

echo "SATORI Node Agent Installation"
echo "=============================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# Install dependencies
apt-get update
apt-get install -y python3 python3-pip python3-venv

# Create directories
mkdir -p /opt/satori-agent
mkdir -p /etc/satori-agent
mkdir -p /var/log/satori-agent

# Copy agent files
cp agent.py /opt/satori-agent/
cp collector.py /opt/satori-agent/
cp encryptor.py /opt/satori-agent/
cp requirements.txt /opt/satori-agent/

# Create virtual environment
cd /opt/satori-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/satori-agent.service << EOF
[Unit]
Description=SATORI Node Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/satori-agent
ExecStart=/opt/satori-agent/venv/bin/python /opt/satori-agent/agent.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/satori-agent/agent.log
StandardError=append:/var/log/satori-agent/agent.error.log

[Install]
WantedBy=multi-user.target
EOF

# Run configuration
echo "Running initial configuration..."
/opt/satori-agent/venv/bin/python /opt/satori-agent/agent.py --configure

# Enable and start service
systemctl daemon-reload
systemctl enable satori-agent
systemctl start satori-agent

echo "Installation complete!"
echo "Check status with: systemctl status satori-agent"
echo "View logs with: journalctl -u satori-agent -f"