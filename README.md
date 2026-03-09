# AI Gmail Guardian

An intelligent spam detection system that monitors your Gmail account using machine learning to automatically identify and label spam emails.

## Features

- **Gmail Integration**: OAuth2 authentication with Gmail API
- **AI-Powered Detection**: Machine learning using scikit-learn and Naive Bayes
- **Continuous Monitoring**: Automatic email checking every 5 minutes
- **Automatic Labeling**: Applies "SPAM_AI" label to detected spam
- **Comprehensive Logging**: Detailed activity logs and error tracking
- **Production Ready**: Designed for Raspberry Pi and Linux server deployment

## Project Structure

```
ai-gmail-guardian/
│
├── main.py              # Main application entry point
├── train_model.py       # Model training script
├── gmail_client.py      # Gmail API client
├── spam_detector.py     # ML spam detection
├── preprocessing.py     # Text preprocessing
├── scheduler.py         # Email monitoring scheduler
├── config.yaml          # Configuration file
├── requirements.txt     # Python dependencies
│
├── models/              # Trained models
│   ├── model.pkl
│   └── vectorizer.pkl
│
├── data/                # Dataset storage
│   └── spam_dataset.csv
│
├── utils/               # Utility modules
│   ├── logger.py
│   └── helpers.py
│
└── logs/                # Application logs
    └── gmail_guardian.log
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Gmail account with API access
- Google Cloud Console project

### Setup Steps

1. **Clone the project**
```bash
git clone <repository-url>
cd ai-gmail-guardian
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Enable Gmail API**

   a. Go to [Google Cloud Console](https://console.cloud.google.com/)
   
   b. Create a new project or select existing one
   
   c. Enable Gmail API:
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"
   
   d. Create OAuth2 credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Select "Desktop app"
   - Download the JSON file and rename it to `credentials.json`
   
   e. Configure consent screen:
   - Go to "APIs & Services" → "OAuth consent screen"
   - Fill in required information
   - Add scope: `https://www.googleapis.com/auth/gmail.modify`

4. **Train the spam detection model**
```bash
python train_model.py
```

5. **Run the application**
```bash
python main.py
```

## Configuration

Edit `config.yaml` to customize settings:

```yaml
gmail:
  max_results: 10          # Number of emails to fetch per check
  check_interval: 300      # Seconds between checks (300 = 5 minutes)
  spam_label: "SPAM_AI"    # Label to apply to spam emails

model:
  path: "models/model.pkl"
  vectorizer: "models/vectorizer.pkl"

dataset:
  url: "https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset"
  local_path: "data/spam_dataset.csv"

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/gmail_guardian.log"
```

## Usage

### First Time Setup

1. Place `credentials.json` in the project root
2. Run `python train_model.py` to train the spam detection model
3. Run `python main.py` to start monitoring

### Daily Operation

The system will automatically:
- Check for new emails every 5 minutes
- Analyze each email for spam characteristics
- Label spam emails with "SPAM_AI"
- Mark processed emails as read
- Log all activities

### Monitoring Logs

View real-time logs:
```bash
tail -f logs/gmail_guardian.log
```

## Model Training

The training script automatically:
- Downloads a spam dataset from Kaggle
- Preprocesses the text data
- Trains a Multinomial Naive Bayes classifier
- Evaluates model performance
- Saves the trained model and vectorizer

### Training Metrics

The model is evaluated using:
- **Accuracy**: Overall classification accuracy
- **Precision**: Spam detection precision
- **Recall**: Spam detection recall
- **F1-Score**: Harmonic mean of precision and recall

## Deployment

### Raspberry Pi Deployment

1. **Prepare Raspberry Pi**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip -y

# Install system dependencies
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y
```

2. **Deploy application**
```bash
# Copy project files
scp -r ai-gmail-guardian/ pi@raspberry-pi:~/

# SSH into Raspberry Pi
ssh pi@raspberry-pi

# Navigate to project
cd ai-gmail-guardian

# Install Python dependencies
pip3 install -r requirements.txt
```

3. **Setup systemd service**
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

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable gmail-guardian
sudo systemctl start gmail-guardian
sudo systemctl status gmail-guardian
```

### Linux Server Deployment

1. **Create dedicated user**
```bash
sudo useradd -m -s /bin/bash gmailguardian
sudo usermod -aG sudo gmailguardian
```

2. **Setup application**
```bash
# Switch to user
sudo su - gmailguardian

# Clone and setup
git clone <repository-url>
cd ai-gmail-guardian
pip install -r requirements.txt
```

3. **Setup cron job for auto-start**
```bash
crontab -e
```

Add:
```bash
@reboot cd /home/gmailguardian/ai-gmail-guardian && python main.py
```

## Advanced Features (Placeholder)

The project includes placeholder modules for future enhancements:

- **Phishing Detection** (`phishing_detector.py`): Advanced phishing attempt detection
- **Link Scanning** (`link_scanner.py`): Security analysis of email links
- **Email Summarization** (`email_summarizer.py`): AI-powered email content summarization

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Ensure `credentials.json` is in the project root
   - Check that Gmail API is enabled in Google Cloud Console
   - Verify OAuth consent screen is configured

2. **Model Not Found**
   - Run `python train_model.py` to create the model
   - Check `config.yaml` model paths are correct

3. **Permission Denied**
   - Ensure Gmail account has necessary permissions
   - Check that OAuth scopes include `gmail.modify`

4. **Memory Issues on Raspberry Pi**
   - Reduce `max_results` in `config.yaml`
   - Increase swap space on Raspberry Pi

### Debug Mode

Enable debug logging by editing `config.yaml`:
```yaml
logging:
  level: "DEBUG"
```

## Security Considerations

- Store `credentials.json` securely and never share it
- The system only reads and labels emails, never deletes content
- All API communications use HTTPS
- Local model files are not sensitive

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the logs in `logs/gmail_guardian.log`
- Create an issue on the project repository

---

**AI Gmail Guardian** - Intelligent spam protection for your Gmail account.
