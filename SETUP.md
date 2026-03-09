# AI Gmail Guardian - Setup Guide

This guide provides step-by-step instructions for setting up and deploying the AI Gmail Guardian.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Gmail API Setup](#gmail-api-setup)
3. [Installation](#installation)
4. [Model Training](#model-training)
5. [Running the Application](#running-the-application)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.10 or higher
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: Minimum 500MB free space
- **Network**: Internet connection for Gmail API access

### Software Dependencies

- Python 3.10+
- pip (Python package manager)
- Git (for cloning repository)

## Gmail API Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click the project dropdown and select "NEW PROJECT"
4. Enter project name: "AI Gmail Guardian"
5. Click "CREATE"

### Step 2: Enable Gmail API

1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on "Gmail API" from the results
4. Click "ENABLE"

### Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" and click "CREATE"
3. Fill in required information:
   - **App name**: AI Gmail Guardian
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
4. Click "SAVE AND CONTINUE"
5. On "Scopes" page, click "ADD OR REMOVE SCOPES"
6. Search for and add: `https://www.googleapis.com/auth/gmail.modify`
7. Click "UPDATE" → "SAVE AND CONTINUE"
8. Add test users (your email address)
9. Click "SAVE AND CONTINUE" → "BACK TO DASHBOARD"

### Step 4: Create OAuth2 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "+ CREATE CREDENTIALS" → "OAuth client ID"
3. Select "Desktop app" as application type
4. Enter name: "AI Gmail Guardian Client"
5. Click "CREATE"
6. Download the JSON file
7. Rename the downloaded file to `credentials.json`
8. Place `credentials.json` in the ai-gmail-guardian project root directory

## Installation

### Step 1: Clone or Download Project

**Option A: Clone with Git**
```bash
git clone <repository-url>
cd ai-gmail-guardian
```

**Option B: Download ZIP**
1. Download the project ZIP file
2. Extract to a folder named `ai-gmail-guardian`
3. Navigate to the project directory

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python -c "import google.auth; import sklearn; print('Installation successful')"
```

## Model Training

### Step 1: Train the Spam Detection Model

```bash
python train_model.py
```

This script will:
- Download a spam dataset (if not present)
- Preprocess the data
- Train a Naive Bayes classifier
- Evaluate model performance
- Save the model and vectorizer

### Step 2: Verify Model Files

Check that the following files exist:
- `models/model.pkl`
- `models/vectorizer.pkl`

### Expected Training Output

```
=== AI Gmail Guardian - Model Training ===
Loaded 5572 samples from dataset
Spam samples: 747 (13.4%)
Ham samples: 4825 (86.6%)
Training set: 4457 samples
Test set: 1115 samples

Training model...
Training Metrics:
Accuracy: 0.9856
Precision: 0.9821
Recall: 0.9118
F1-Score: 0.9458

Test Metrics:
Accuracy: 0.9821
Precision: 0.9750
Recall: 0.8966
F1-Score: 0.9342
```

## Running the Application

### Step 1: First Run

```bash
python main.py
```

**First Time Authentication:**
1. A browser window will open
2. Sign in with your Google account
3. Grant permissions to the application
4. You'll be redirected to a success page
5. The application will start monitoring emails

### Step 2: Verify Operation

The application should display:
```
=== AI Gmail Guardian ===
Intelligent Spam Detection for Gmail

2024-03-09 10:00:00 - gmail_guardian - INFO - AI Gmail Guardian initialized
2024-03-09 10:00:01 - gmail_guardian - INFO - Authenticating with Gmail API...
2024-03-09 10:00:02 - gmail_guardian - INFO - Successfully authenticated with Gmail API
2024-03-09 10:00:03 - gmail_guardian - INFO - Loading spam detection model...
2024-03-09 10:00:04 - gmail_guardian - INFO - Starting continuous email monitoring (check interval: 300 seconds)
2024-03-09 10:00:05 - gmail_guardian - INFO - Starting email check
2024-03-09 10:00:06 - gmail_guardian - INFO - No new emails to process
```

### Step 3: Check Logs

Monitor the application logs:
```bash
tail -f logs/gmail_guardian.log
```

## Deployment

### Raspberry Pi Deployment

#### Step 1: Prepare Raspberry Pi

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and development tools
sudo apt install python3 python3-pip python3-dev build-essential -y

# Install additional dependencies
sudo apt install libssl-dev libffi-dev -y
```

#### Step 2: Deploy Application

```bash
# Copy project to Raspberry Pi
scp -r ai-gmail-guardian/ pi@raspberry-pi-ip:~/

# SSH into Raspberry Pi
ssh pi@raspberry-pi-ip

# Navigate to project
cd ai-gmail-guardian

# Install Python dependencies
pip3 install -r requirements.txt
```

#### Step 3: Setup Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/gmail-guardian.service
```

Add the following content:
```ini
[Unit]
Description=AI Gmail Guardian
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ai-gmail-guardian
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gmail-guardian
sudo systemctl start gmail-guardian
sudo systemctl status gmail-guardian
```

### Linux Server Deployment

#### Step 1: Create Dedicated User

```bash
sudo useradd -m -s /bin/bash gmailguardian
sudo usermod -aG sudo gmailguardian
sudo su - gmailguardian
```

#### Step 2: Setup Application

```bash
# Clone or copy project
git clone <repository-url>
cd ai-gmail-guardian

# Install dependencies
pip3 install -r requirements.txt
python3 train_model.py
```

#### Step 3: Setup Auto-start with Cron

```bash
crontab -e
```

Add the following line:
```bash
@reboot cd /home/gmailguardian/ai-gmail-guardian && /usr/bin/python3 main.py
```

#### Step 4: Setup Log Rotation

```bash
sudo nano /etc/logrotate.d/gmail-guardian
```

Add:
```
/home/gmailguardian/ai-gmail-guardian/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 gmailguardian gmailguardian
}
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Authentication Error

**Problem**: `Error: credentials.json not found`

**Solution**: 
- Ensure `credentials.json` is in the project root
- Download fresh credentials from Google Cloud Console
- Check file permissions: `chmod 600 credentials.json`

#### 2. Gmail API Not Enabled

**Problem**: `Error: Gmail API not enabled`

**Solution**:
- Go to Google Cloud Console
- Enable Gmail API for your project
- Wait a few minutes for changes to propagate

#### 3. Model Not Found

**Problem**: `Error: Spam detection model not found`

**Solution**:
- Run `python train_model.py` to create the model
- Check that `models/` directory exists
- Verify `config.yaml` paths are correct

#### 4. Permission Denied

**Problem**: `Error: Insufficient permissions`

**Solution**:
- Re-authenticate by deleting `token.pickle`
- Check OAuth consent screen configuration
- Ensure Gmail account has API access

#### 5. Memory Issues (Raspberry Pi)

**Problem**: Application crashes due to low memory

**Solution**:
- Reduce `max_results` in `config.yaml` to 5
- Increase swap space:
```bash
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

#### 6. Network Issues

**Problem**: Connection timeout errors

**Solution**:
- Check internet connectivity
- Verify firewall settings
- Test Gmail API access manually

### Debug Mode

Enable detailed logging by editing `config.yaml`:

```yaml
logging:
  level: "DEBUG"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/gmail_guardian.log"
```

### Log Analysis

Common log messages and their meanings:

- `INFO - Successfully authenticated with Gmail API` ✅
- `INFO - Fetched X unread messages` ✅
- `INFO - SPAM DETECTED: sender - subject` ✅
- `ERROR - Error fetching messages` ❌ Check API access
- `ERROR - Model not loaded` ❌ Run training script

### Performance Optimization

For better performance:

1. **Reduce check interval** in `config.yaml`:
```yaml
gmail:
  check_interval: 600  # 10 minutes instead of 5
```

2. **Limit concurrent processing**:
```yaml
gmail:
  max_results: 5  # Process fewer emails per batch
```

3. **Use SSD storage** for better I/O performance

4. **Monitor system resources**:
```bash
htop  # CPU and memory usage
df -h  # Disk usage
```

## Support

If you encounter issues not covered in this guide:

1. Check the application logs: `logs/gmail_guardian.log`
2. Verify all setup steps were completed correctly
3. Ensure your Gmail account has API access
4. Create an issue on the project repository with:
   - Error messages
   - System information
   - Configuration details

---

For additional help, refer to the main README.md file or create an issue on the project repository.
