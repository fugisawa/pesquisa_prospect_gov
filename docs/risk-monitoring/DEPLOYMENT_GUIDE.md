# 🚀 Risk Monitoring System - Production Deployment Guide

## 📋 Prerequisites

### System Requirements
- **OS**: Linux/macOS/Windows (Linux Ubuntu 20.04+ recommended)
- **Python**: 3.9+ (3.12 recommended)
- **CPU**: 4+ cores for production workloads
- **Memory**: 8GB+ RAM (16GB recommended)
- **Storage**: 50GB+ free space for logs and data
- **Network**: Stable internet connection for external monitoring

### Required Dependencies
```bash
# Core Python packages
conda install -c conda-forge plotly dash scipy matplotlib seaborn dash-bootstrap-components
conda install -c conda-forge aiohttp beautifulsoup4 numpy pandas

# Additional packages via pip (if needed)
pip install asyncio logging argparse pathlib datetime json
```

## 🔧 Installation Steps

### 1. Environment Setup
```bash
# Clone or download the risk monitoring system
cd /path/to/your/project
mkdir -p pesquisa_prospect_gov
cd pesquisa_prospect_gov

# Create directory structure
mkdir -p {src/risk-monitoring,config/risk-monitoring,docs/risk-monitoring,tests/risk-monitoring,scripts,logs}

# Set environment variables
export RISK_MONITORING_HOME=$(pwd)
export PYTHONPATH=$RISK_MONITORING_HOME/src/risk-monitoring:$PYTHONPATH
```

### 2. Configuration Files Setup
```bash
# Copy default configuration
cp config/risk-monitoring/default-configs.json config/risk-monitoring/production-configs.json

# Create individual component configs (system will auto-generate if missing)
# - bigtech-config.json
# - regulatory-config.json
# - portfolio-config.json
# - warning-system-config.json
# - dashboard-config.json
```

### 3. Secure Configuration
Edit configuration files to include production settings:

#### Email Configuration (config/risk-monitoring/warning-system-config.json)
```json
{
  "notification_channels": {
    "email": {
      "enabled": true,
      "smtp_server": "your-smtp-server.com",
      "smtp_port": 587,
      "username": "your-email@company.com",
      "password": "your-app-password",
      "from_email": "alerts@company.com"
    }
  }
}
```

#### Slack Integration
```json
{
  "notification_channels": {
    "slack": {
      "enabled": true,
      "webhook_url": "https://hooks.slack.com/services/YOUR/ACTUAL/WEBHOOK"
    }
  }
}
```

### 4. Security Setup
```bash
# Create secure credential storage
mkdir -p ~/.risk-monitoring/credentials
chmod 700 ~/.risk-monitoring/credentials

# Store sensitive information securely
echo "smtp_password=your_actual_password" > ~/.risk-monitoring/credentials/email.env
echo "slack_webhook=https://hooks.slack.com/services/..." > ~/.risk-monitoring/credentials/slack.env
chmod 600 ~/.risk-monitoring/credentials/*.env
```

## 🎯 Production Configuration

### Stakeholder Configuration
Update stakeholder information in `config/risk-monitoring/production-configs.json`:

```json
{
  "stakeholder_config": {
    "roles": {
      "CEO": {
        "name": "John Doe",
        "email": "ceo@yourcompany.com",
        "phone": "+55119999999999",
        "alert_level": "Orange"
      },
      "CTO": {
        "name": "Jane Smith",
        "email": "cto@yourcompany.com",
        "phone": "+55119999999998",
        "alert_level": "Orange"
      }
      // ... add all relevant stakeholders
    }
  }
}
```

### Monitoring Intervals (Production Optimized)
```json
{
  "warning_system_config": {
    "monitoring_intervals": {
      "critical_threats": 60,      // 1 minute
      "high_priority": 300,        // 5 minutes
      "medium_priority": 1800,     // 30 minutes
      "low_priority": 21600        // 6 hours
    }
  }
}
```

### API Rate Limiting
```json
{
  "bigtech_config": {
    "rate_limiting": {
      "requests_per_minute": 30,
      "burst_limit": 100,
      "backoff_strategy": "exponential"
    }
  }
}
```

## 🐳 Docker Deployment (Recommended)

### 1. Create Dockerfile
```dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Set environment variables
ENV PYTHONPATH=/app/src/risk-monitoring
ENV RISK_MONITORING_CONFIG=/app/config/risk-monitoring

# Expose dashboard port
EXPOSE 8050

# Create non-root user
RUN useradd -m -u 1000 riskmon
USER riskmon

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8050', timeout=5)"

# Start the monitoring system
CMD ["python", "scripts/start_monitoring.py", "--config-dir", "/app/config/risk-monitoring"]
```

### 2. Create docker-compose.yml
```yaml
version: '3.8'

services:
  risk-monitoring:
    build: .
    container_name: risk-monitoring-system
    ports:
      - "8050:8050"
    environment:
      - PYTHONPATH=/app/src/risk-monitoring
      - RISK_MONITORING_CONFIG=/app/config/risk-monitoring
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    networks:
      - monitoring-network

  # Optional: Add Redis for caching
  redis:
    image: redis:7-alpine
    container_name: risk-monitoring-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - monitoring-network

networks:
  monitoring-network:
    driver: bridge

volumes:
  redis-data:
```

### 3. Deploy with Docker Compose
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f risk-monitoring

# Stop services
docker-compose down
```

## 🖥️ Traditional Server Deployment

### 1. Systemd Service Setup
Create `/etc/systemd/system/risk-monitoring.service`:

```ini
[Unit]
Description=Risk Monitoring System
After=network.target
Wants=network.target

[Service]
Type=simple
User=riskmon
Group=riskmon
WorkingDirectory=/opt/risk-monitoring
Environment=PYTHONPATH=/opt/risk-monitoring/src/risk-monitoring
ExecStart=/usr/bin/python3 /opt/risk-monitoring/scripts/start_monitoring.py --config-dir /opt/risk-monitoring/config/risk-monitoring
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=risk-monitoring

[Install]
WantedBy=multi-user.target
```

### 2. Service Management
```bash
# Enable and start service
sudo systemctl enable risk-monitoring
sudo systemctl start risk-monitoring

# Check status
sudo systemctl status risk-monitoring

# View logs
sudo journalctl -u risk-monitoring -f

# Restart service
sudo systemctl restart risk-monitoring
```

## 📊 Monitoring and Observability

### 1. Application Logging
```bash
# Log locations
/opt/risk-monitoring/logs/
├── risk_monitoring.log          # Main application log
├── bigtech_monitoring.log       # Big Tech monitoring
├── regulatory_monitoring.log    # Regulatory monitoring
├── portfolio_analysis.log       # Portfolio analysis
├── early_warning.log           # Alert system
└── dashboard.log               # Dashboard operations
```

### 2. Log Rotation Setup
Create `/etc/logrotate.d/risk-monitoring`:

```bash
/opt/risk-monitoring/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 riskmon riskmon
    postrotate
        systemctl reload risk-monitoring
    endscript
}
```

### 3. Health Monitoring Script
```bash
#!/bin/bash
# health_check.sh

DASHBOARD_URL="http://localhost:8050"
LOG_FILE="/opt/risk-monitoring/logs/health_check.log"

# Check dashboard accessibility
if curl -f -s "$DASHBOARD_URL" > /dev/null; then
    echo "$(date): Dashboard healthy" >> "$LOG_FILE"
else
    echo "$(date): Dashboard unhealthy - restarting service" >> "$LOG_FILE"
    systemctl restart risk-monitoring
fi

# Check log files for errors
if tail -n 100 /opt/risk-monitoring/logs/risk_monitoring.log | grep -q "ERROR\|CRITICAL"; then
    echo "$(date): Errors detected in logs" >> "$LOG_FILE"
fi
```

## 🔒 Security Hardening

### 1. Network Security
```bash
# Firewall configuration (UFW)
sudo ufw allow ssh
sudo ufw allow 8050/tcp  # Dashboard port
sudo ufw enable

# Or using iptables
iptables -A INPUT -p tcp --dport 8050 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -j DROP
```

### 2. SSL/TLS Configuration
For production, serve dashboard through NGINX with SSL:

```nginx
# /etc/nginx/sites-available/risk-monitoring
server {
    listen 443 ssl;
    server_name risk-monitoring.yourcompany.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://localhost:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Access Control
```bash
# Create dedicated user
sudo useradd -m -s /bin/bash riskmon
sudo usermod -aG sudo riskmon

# Set proper permissions
sudo chown -R riskmon:riskmon /opt/risk-monitoring
sudo chmod 750 /opt/risk-monitoring
sudo chmod 640 /opt/risk-monitoring/config/risk-monitoring/*.json
```

## 🔄 Backup and Recovery

### 1. Configuration Backup
```bash
#!/bin/bash
# backup_config.sh

BACKUP_DIR="/backup/risk-monitoring/$(date +%Y%m%d)"
SOURCE_DIR="/opt/risk-monitoring"

mkdir -p "$BACKUP_DIR"

# Backup configuration
tar -czf "$BACKUP_DIR/config_backup.tar.gz" "$SOURCE_DIR/config"

# Backup logs (last 30 days)
find "$SOURCE_DIR/logs" -name "*.log" -mtime -30 | \
    tar -czf "$BACKUP_DIR/logs_backup.tar.gz" -T -

# Backup historical data
tar -czf "$BACKUP_DIR/data_backup.tar.gz" "$SOURCE_DIR/data"

echo "Backup completed: $BACKUP_DIR"
```

### 2. Automated Backup (Crontab)
```bash
# Add to crontab (crontab -e)
0 2 * * * /opt/risk-monitoring/scripts/backup_config.sh

# Weekly full backup
0 3 * * 0 /opt/risk-monitoring/scripts/full_backup.sh
```

### 3. Recovery Procedure
```bash
#!/bin/bash
# restore_backup.sh

BACKUP_FILE="$1"
RESTORE_DIR="/opt/risk-monitoring"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

# Stop service
systemctl stop risk-monitoring

# Restore from backup
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"

# Fix permissions
chown -R riskmon:riskmon "$RESTORE_DIR"

# Start service
systemctl start risk-monitoring

echo "Recovery completed from $BACKUP_FILE"
```

## 📈 Performance Tuning

### 1. Memory Optimization
```python
# Add to startup script
import gc
import os

# Set memory limits
os.environ['PYTHONOPTIMIZE'] = '1'

# Configure garbage collection
gc.set_threshold(700, 10, 10)
```

### 2. Database Connection Pooling
```python
# For future database integration
DATABASE_CONFIG = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_timeout': 30,
    'pool_recycle': 3600
}
```

### 3. Caching Configuration
```python
# Redis caching for dashboard data
CACHE_CONFIG = {
    'redis_host': 'localhost',
    'redis_port': 6379,
    'cache_ttl': 300,  # 5 minutes
    'max_memory': '256mb'
}
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Solution: Check Python path
export PYTHONPATH=/opt/risk-monitoring/src/risk-monitoring:$PYTHONPATH
python -c "import big_tech_monitor; print('Import successful')"
```

#### 2. Permission Errors
```bash
# Solution: Fix ownership and permissions
sudo chown -R riskmon:riskmon /opt/risk-monitoring
sudo chmod -R 755 /opt/risk-monitoring
```

#### 3. Dashboard Not Loading
```bash
# Check if service is running
systemctl status risk-monitoring

# Check port availability
netstat -tuln | grep 8050

# Check firewall
sudo ufw status
```

#### 4. Email Alerts Not Working
```bash
# Test SMTP connectivity
python -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email', 'app-password')
print('SMTP connection successful')
server.quit()
"
```

### Performance Issues

#### High Memory Usage
```bash
# Monitor memory usage
htop
ps aux | grep python

# Restart service to clear memory
systemctl restart risk-monitoring
```

#### Slow Dashboard Loading
```bash
# Enable caching
# Add Redis configuration to docker-compose.yml
# Implement dashboard data caching in code
```

## 📞 Support and Maintenance

### Maintenance Schedule
- **Daily**: Check service status and logs
- **Weekly**: Review performance metrics and alerts
- **Monthly**: Update configurations and run full tests
- **Quarterly**: Security audit and dependency updates

### Support Contacts
- **Level 1**: Operations team (system restarts, basic troubleshooting)
- **Level 2**: Development team (configuration changes, bug fixes)
- **Level 3**: Architecture team (major issues, system modifications)

### Escalation Procedures
1. **Service Down**: Immediate restart attempt, escalate to Level 2 if persistent
2. **Data Issues**: Validate configurations, check external APIs
3. **Security Incidents**: Follow security incident response plan
4. **Performance Degradation**: Review system resources, consider scaling

## 📋 Post-Deployment Checklist

- [ ] All services running correctly
- [ ] Dashboard accessible at configured URL
- [ ] Email alerts delivering successfully
- [ ] Slack notifications working
- [ ] Log files being created and rotated
- [ ] Backup system operational
- [ ] Health checks passing
- [ ] Security configurations applied
- [ ] Documentation updated
- [ ] Team training completed

## 🎯 Success Criteria

The deployment is considered successful when:

✅ **System Availability**: 99.5% uptime achieved
✅ **Response Time**: Dashboard loads in <3 seconds
✅ **Alert Delivery**: <30 seconds for critical alerts
✅ **Data Accuracy**: >95% accuracy in threat detection
✅ **Performance**: Handles 1000+ monitoring sources
✅ **Security**: No security vulnerabilities detected
✅ **Scalability**: Can scale to 10+ concurrent users

---

**🛡️ Your risk monitoring system is now ready for production!**

For additional support, refer to the [Risk Monitoring Documentation](README.md) or contact the development team.