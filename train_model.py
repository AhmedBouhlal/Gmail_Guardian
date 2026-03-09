"""
Training script for spam detection model.
Downloads dataset and trains the classifier.
"""

import os
import pandas as pd
import requests
from tqdm import tqdm
import yaml
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, fbeta_score

from spam_detector import SpamDetector
from utils.logger import setup_logger


def download_dataset(url: str, save_path: str) -> bool:
    """
    Download dataset from URL.
    
    Args:
        url: Dataset URL
        save_path: Path to save dataset
        
    Returns:
        True if download successful
    """
    try:
        print(f"Downloading dataset from {url}")
        
        # For the SMS spam dataset, we'll use a direct download link
        # Note: In production, you might want to use Kaggle API
        dataset_url = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"
        
        response = requests.get(dataset_url, stream=True)
        response.raise_for_status()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Download with progress bar
        total_size = int(response.headers.get('content-length', 0))
        with open(save_path, 'wb') as f, tqdm(
            desc="Downloading",
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                bar.update(size)
        
        print(f"Dataset downloaded to {save_path}")
        return True
        
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return False


def load_dataset(file_path: str) -> tuple:
    """
    Load and prepare dataset for training.
    
    Args:
        file_path: Path to dataset file
        
    Returns:
        Tuple of (texts, labels)
    """
    try:
        # Load TSV file (tab-separated values)
        df = pd.read_csv(file_path, sep='\t', header=None, names=['label', 'message'])
        
        # Convert labels to binary (spam=1, ham=0)
        df['label'] = df['label'].map({'spam': 1, 'ham': 0})
        
        # Remove any rows with missing values
        df = df.dropna()
        
        texts = df['message'].tolist()
        labels = df['label'].tolist()
        
        print(f"Loaded {len(texts)} samples from dataset")
        print(f"Spam samples: {sum(labels)} ({sum(labels)/len(labels)*100:.1f}%)")
        print(f"Ham samples: {len(labels)-sum(labels)} ({(len(labels)-sum(labels))/len(labels)*100:.1f}%)")
        
        return texts, labels
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return [], []


def create_sample_dataset(file_path: str) -> bool:
    """
    Create a sample dataset for testing if download fails.
    
    Args:
        file_path: Path to save sample dataset
        
    Returns:
        True if creation successful
    """
    try:
        # Sample spam and ham messages
        sample_data = [
            ("ham", "Hey, are we still on for tonight?"),
            ("ham", "Can you send me the meeting notes?"),
            ("ham", "Thanks for your help yesterday!"),
            ("ham", "See you at the office tomorrow"),
            ("ham", "The project deadline is next Friday"),
            ("spam", "Congratulations! You've won $1,000,000!!!"),
            ("spam", "URGENT: Your account will be suspended! Click here NOW!"),
            ("spam", "FREE VIAGRA! Limited time offer!!!"),
            ("spam", "Make $5000/week working from home!"),
            ("spam", "Claim your free prize now! Limited time!"),
            ("ham", "Let's catch up over coffee next week"),
            ("ham", "The presentation went really well"),
            ("ham", "Can you review this document when you get a chance?"),
            ("spam", "WINNER! You have been selected for a cash prize!"),
            ("spam", "Last chance to buy at 90% OFF!!!"),
            ("ham", "Happy birthday! Hope you have a great day"),
            ("ham", "The team meeting is moved to 3 PM"),
            ("spam", "Your loan has been approved instantly!"),
            ("spam", "Buy now and get 50% discount! Today only!"),
            ("ham", "Looking forward to our collaboration")
        ]
        
        # Create DataFrame
        df = pd.DataFrame(sample_data, columns=['label', 'message'])
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save to CSV
        df.to_csv(file_path, index=False)
        
        print(f"Created sample dataset with {len(sample_data)} samples")
        return True
        
    except Exception as e:
        print(f"Error creating sample dataset: {e}")
        return False


def main():
    """Main training function."""
    # Setup logging
    logger = setup_logger()
    
    # Load configuration
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("config.yaml not found")
        return
    
    dataset_path = config['dataset']['local_path']
    model_path = config['model']['path']
    vectorizer_path = config['model']['vectorizer']
    
    print("=== AI Gmail Guardian - Model Training ===")
    
    # Download dataset if it doesn't exist
    if not os.path.exists(dataset_path):
        print("Dataset not found, attempting to download...")
        if not download_dataset(config['dataset']['url'], dataset_path):
            print("Download failed, creating sample dataset...")
            if not create_sample_dataset(dataset_path):
                print("Failed to create sample dataset")
                return
    
    # Load dataset
    texts, labels = load_dataset(dataset_path)
    if not texts:
        print("No data loaded, exiting...")
        return
    
    # Split data for evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Initialize and train detector
    detector = SpamDetector()
    
    print("\nTraining model...")
    train_metrics = detector.train(X_train, y_train)
    
    print(f"\nTraining Metrics:")
    print(f"Accuracy: {train_metrics['accuracy']:.4f}")
    print(f"Precision: {train_metrics['precision']:.4f}")
    print(f"Recall: {train_metrics['recall']:.4f}")
    print(f"F2-Score: {train_metrics['f2_score']:.4f}")
    
    # Evaluate on test set
    print("\nEvaluating on test set...")
    test_predictions = []
    test_probabilities = []
    
    for text in tqdm(X_test, desc="Testing"):
        pred, prob = detector.predict(text)
        test_predictions.append(pred)
        test_probabilities.append(prob)
    
    # Calculate test metrics
    test_accuracy = accuracy_score(y_test, test_predictions)
    test_precision = precision_score(y_test, test_predictions)
    test_recall = recall_score(y_test, test_predictions)
    test_f2 = fbeta_score(y_test, test_predictions, beta=2)
    
    print(f"\nTest Metrics:")
    print(f"Accuracy: {test_accuracy:.4f}")
    print(f"Precision: {test_precision:.4f}")
    print(f"Recall: {test_recall:.4f}")
    print(f"F2-Score: {test_f2:.4f}")
    
    # Detailed classification report
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, test_predictions, target_names=['Ham', 'Spam']))
    
    # Confusion matrix
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, test_predictions)
    print(f"True Negative: {cm[0][0]}")
    print(f"False Positive: {cm[0][1]}")
    print(f"False Negative: {cm[1][0]}")
    print(f"True Positive: {cm[1][1]}")
    
    # Show top spam indicators
    print("\nTop Spam Indicators:")
    top_features = detector.get_feature_importance(10)
    for feature, importance in top_features:
        print(f"{feature}: {importance:.4f}")
    
    # Save model
    print(f"\nSaving model to {model_path}")
    if detector.save_model(model_path, vectorizer_path):
        print("Model saved successfully!")
    else:
        print("Failed to save model")
    
    print("\n=== Training Complete ===")


if __name__ == "__main__":
    main()
