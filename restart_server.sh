#!/bin/bash
# Ku socodsii script-kan DIBADDA sandbox-ka (VPS SSH terminal-ka)
# Run this script on the actual server via SSH as root

echo "=== Restarting Petroleum System ==="

# Kill existing gunicorn
pkill -9 gunicorn 2>/dev/null
sleep 2

# Remove stale socket
rm -f /opt/Petroleum-System/app.sock

# Start gunicorn as daemon
cd /opt/Petroleum-System
source venv/bin/activate
env HOME=/opt/Petroleum-System gunicorn \
    --workers 3 \
    --bind unix:/opt/Petroleum-System/app.sock \
    -m 007 \
    --pid /opt/Petroleum-System/gunicorn.pid \
    --daemon \
    wsgi:app

sleep 3

# Check socket created
if [ -S /opt/Petroleum-System/app.sock ]; then
    echo "✓ Gunicorn running, socket created"
    chmod 777 /opt/Petroleum-System/app.sock
else
    echo "✗ Gunicorn failed to start"
    exit 1
fi

# Restart nginx
systemctl restart nginx || service nginx restart

echo "✓ Done - checking status..."
sleep 1
systemctl status nginx --no-pager | tail -5
ps aux | grep [g]unicorn | head -3
