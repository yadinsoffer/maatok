#!/bin/bash
cd /home/ubuntu/maatiktok

# Add timestamp to log
echo "Starting MaaTikTok run at $(date)" >> /home/ubuntu/maatiktok/cron.log 2>&1

# Stop any existing containers and clean up
docker-compose down >> /home/ubuntu/maatiktok/cron.log 2>&1
docker system prune -f >> /home/ubuntu/maatiktok/cron.log 2>&1

# Run in detached mode
docker-compose up -d --build >> /home/ubuntu/maatiktok/cron.log 2>&1 