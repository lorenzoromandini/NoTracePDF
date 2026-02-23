# NoTracePDF Production Deployment Guide

## Overview
This guide covers deploying NoTracePDF to a production server with SSL, reverse proxy, and proper security hardening.

## Prerequisites
- A VPS with at least 2GB RAM and 1 vCPU
- A domain name (pointed to your server IP)
- Ubuntu 22.04 LTS (recommended)
- Docker and Docker Compose installed

---

## Step 1: Server Setup

### 1.1 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Install Required Packages
```bash
sudo apt install -y curl git nginx certbot python3-certbot-nginx ufw fail2ban
```

### 1.3 Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install -y docker-compose-plugin
```

---

## Step 2: Clone and Configure

### 2.1 Clone Repository
```bash
cd /opt
sudo git clone https://github.com/lorenzoromandini/NoTracePDF.git
sudo chown -R $USER:$USER NoTracePDF
cd NoTracePDF
```

### 2.2 Create Environment File
```bash
cat > .env << 'EOF'
# Production settings
ENVIRONMENT=production
DEBUG=false

# Server settings
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Rate limiting (requests per minute)
RATE_LIMIT=60

# File upload limits (in MB)
MAX_FILE_SIZE_MB=100
MAX_UPLOAD_SIZE_MB=500

# Cleanup settings
CLEANUP_INTERVAL_MINUTES=30
MAX_FILE_AGE_MINUTES=60
EOF
```

### 2.3 Create Docker Compose Override
```bash
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  notracepdf:
    build: .
    container_name: notracepdf
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - PYTHONDONTWRITEBYTECODE=1
      - PYTHONUNBUFFERED=1
    volumes:
      - /tmp:/tmp
    networks:
      - notracepdf-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

networks:
  notracepdf-network:
    driver: bridge
EOF
```

---

## Step 3: Configure Nginx Reverse Proxy

### 3.1 Create Nginx Configuration
```bash
sudo tee /etc/nginx/sites-available/notracepdf << 'EOF'
# Rate limiting zone
limit_req_zone $binary_remote_addr zone=pdf_limit:10m rate=10r/m;
limit_conn_zone $binary_remote_addr zone=pdf_conn:10m;

upstream notracepdf {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Logging
    access_log /var/log/nginx/notracepdf-access.log;
    error_log /var/log/nginx/notracepdf-error.log;
    
    # Client body size (for large PDFs)
    client_max_body_size 100M;
    client_body_timeout 300s;
    client_header_timeout 300s;
    
    # Proxy settings
    location / {
        # Rate limiting
        limit_req zone=pdf_limit burst=20 nodelay;
        limit_conn pdf_conn 10;
        
        proxy_pass http://notracepdf;
        proxy_http_version 1.1;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        
        # Timeouts for long operations
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Disable buffering for streaming responses
        proxy_buffering off;
        proxy_request_buffering off;
    }
    
    # Static files caching
    location /static {
        alias /opt/NoTracePDF/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
}
EOF
```

**Replace `your-domain.com` with your actual domain**

### 3.2 Enable Site
```bash
# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Enable notracepdf site
sudo ln -s /etc/nginx/sites-available/notracepdf /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl restart nginx
```

---

## Step 4: SSL Certificate (Let's Encrypt)

### 4.1 Obtain Certificate
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow prompts:
# - Enter email
# - Accept terms
# - Choose whether to redirect HTTP to HTTPS (recommended: Yes)
```

### 4.2 Auto-Renewal
```bash
# Test auto-renewal
sudo certbot renew --dry-run

# Certbot auto-renewal is already set up via systemd timer
```

---

## Step 5: Configure Firewall

### 5.1 Setup UFW
```bash
# Reset UFW (be careful if connected via SSH!)
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (don't lock yourself out!)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## Step 6: Fail2Ban Configuration

### 6.1 Configure Fail2Ban
```bash
sudo tee /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/notracepdf-error.log
maxretry = 10

[nginx-noscript]
enabled = true
filter = nginx-noscript
action = iptables-multiport[name=NoScript, port="http,https", protocol=tcp]
logpath = /var/log/nginx/notracepdf-access.log
maxretry = 6
EOF

# Restart fail2ban
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban
```

---

## Step 7: Start Application

### 7.1 Build and Start
```bash
cd /opt/NoTracePDF

# Build production image
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check logs
docker logs -f notracepdf
```

### 7.2 Verify Deployment
```bash
# Check containers are running
docker ps

# Check application health
curl http://localhost:8000/health

# Test via domain
curl https://your-domain.com/health
```

---

## Step 8: Monitoring & Logging

### 8.1 Install Logrotate
```bash
sudo tee /etc/logrotate.d/notracepdf << 'EOF'
/var/log/nginx/notracepdf-*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
EOF
```

### 8.2 Setup Basic Monitoring Script
```bash
sudo tee /usr/local/bin/check-notracepdf.sh << 'EOF'
#!/bin/bash
# Health check script

HEALTH_URL="https://your-domain.com/health"
LOG_FILE="/var/log/notracepdf-health.log"

if ! curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
    echo "$(date): NoTracePDF is DOWN" >> "$LOG_FILE"
    # Restart container
    docker restart notracepdf
else
    echo "$(date): NoTracePDF is UP" >> "$LOG_FILE"
fi
EOF

sudo chmod +x /usr/local/bin/check-notracepdf.sh

# Add to cron (check every 5 minutes)
(sudo crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/check-notracepdf.sh") | sudo crontab -
```

---

## Step 9: Backup Strategy

### 9.1 Create Backup Script
```bash
sudo tee /usr/local/bin/backup-notracepdf.sh << 'EOF'
#!/bin/bash
# Backup script for NoTracePDF

BACKUP_DIR="/opt/backups/notracepdf"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup application code
tar -czf "$BACKUP_DIR/notracepdf_code_$DATE.tar.gz" -C /opt NoTracePDF

# Backup environment file
cp /opt/NoTracePDF/.env "$BACKUP_DIR/env_$DATE.backup"

# Clean old backups (older than 7 days)
find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $DATE"
EOF

sudo chmod +x /usr/local/bin/backup-notracepdf.sh

# Run backup daily at 2 AM
(sudo crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-notracepdf.sh") | sudo crontab -
```

---

## Step 10: Cloudflare Setup (Optional but Recommended)

### 10.1 Benefits
- Free SSL/TLS (flexible mode)
- DDoS protection
- CDN caching for static assets
- DNS management

### 10.2 Configuration
1. Sign up at cloudflare.com
2. Add your domain
3. Change nameservers at your registrar
4. In Cloudflare dashboard:
   - **SSL/TLS**: Set to "Full (strict)" or "Flexible"
   - **Caching**: Enable static asset caching
   - **Security**: Set security level to "Medium"
   - **Speed**: Enable auto-minify for CSS/JS

---

## Maintenance Commands

### Restart Application
```bash
cd /opt/NoTracePDF
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart
```

### View Logs
```bash
# Application logs
docker logs -f notracepdf

# Nginx logs
sudo tail -f /var/log/nginx/notracepdf-*.log
```

### Update Application
```bash
cd /opt/NoTracePDF
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Check Resource Usage
```bash
docker stats notracepdf
```

---

## Troubleshooting

### Issue: 502 Bad Gateway
**Solution:**
```bash
# Check if container is running
docker ps | grep notracepdf

# Check logs
docker logs notracepdf

# Restart
docker restart notracepdf
```

### Issue: SSL Certificate Expired
**Solution:**
```bash
sudo certbot renew --force-renewal
sudo systemctl restart nginx
```

### Issue: Large File Uploads Failing
**Solution:**
```bash
# Check nginx client_max_body_size
sudo nano /etc/nginx/sites-available/notracepdf

# Reload nginx
sudo nginx -t && sudo systemctl reload nginx
```

---

## Security Checklist

- [ ] Firewall enabled (UFW) with only necessary ports open
- [ ] Fail2Ban configured for SSH and Nginx
- [ ] SSL certificate installed and auto-renewal working
- [ ] Rate limiting enabled on Nginx
- [ ] Security headers configured
- [ ] Application running as non-root user (in container)
- [ ] Regular backups configured
- [ ] Log rotation enabled
- [ ] Health monitoring in place
- [ ] Container resource limits set
- [ ] .env file with secure SECRET_KEY

---

## Next Steps

1. **Test all features** after deployment
2. **Set up monitoring** (Prometheus/Grafana optional)
3. **Configure alerts** for downtime
4. **Document custom configurations**
5. **Plan for scaling** if needed (Docker Swarm/Kubernetes)

---

## Support

- GitHub Issues: https://github.com/lorenzoromandini/NoTracePDF/issues
- Application Health: https://your-domain.com/health
- Logs: `/var/log/nginx/notracepdf-*.log` and `docker logs notracepdf`