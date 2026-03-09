"""
Spam detection module using machine learning.
"""

import os
import pickle
from typing import Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, fbeta_score

from utils.logger import get_logger
from preprocessing import preprocess_email


class SpamDetector:
    """
    Machine learning based spam detector.
    """
    
    def __init__(self, model_path: str = None, vectorizer_path: str = None):
        """
        Initialize spam detector.
        
        Args:
            model_path: Path to saved model file
            vectorizer_path: Path to saved vectorizer file
        """
        self.logger = get_logger()
        self.model: Optional[MultinomialNB] = None
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        
    def load_model(self, model_path: str = None, vectorizer_path: str = None) -> bool:
        """
        Load trained model and vectorizer from files.
        
        Args:
            model_path: Path to model file
            vectorizer_path: Path to vectorizer file
            
        Returns:
            True if loading successful
        """
        model_path = model_path or self.model_path
        vectorizer_path = vectorizer_path or self.vectorizer_path
        
        if not model_path or not vectorizer_path:
            self.logger.error("Model and vectorizer paths must be specified")
            return False
        
        try:
            # Load model
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            # Load vectorizer
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            self.logger.info(f"Successfully loaded model from {model_path}")
            self.logger.info(f"Successfully loaded vectorizer from {vectorizer_path}")
            return True
            
        except FileNotFoundError as e:
            self.logger.error(f"Model file not found: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            return False
    
    def save_model(self, model_path: str = None, vectorizer_path: str = None) -> bool:
        """
        Save trained model and vectorizer to files.
        
        Args:
            model_path: Path to save model
            vectorizer_path: Path to save vectorizer
            
        Returns:
            True if saving successful
        """
        if not self.model or not self.vectorizer:
            self.logger.error("No trained model or vectorizer to save")
            return False
        
        model_path = model_path or self.model_path
        vectorizer_path = vectorizer_path or self.vectorizer_path
        
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            os.makedirs(os.path.dirname(vectorizer_path), exist_ok=True)
            
            # Save model
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            
            # Save vectorizer
            with open(vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            self.logger.info(f"Successfully saved model to {model_path}")
            self.logger.info(f"Successfully saved vectorizer to {vectorizer_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
            return False
    
    def train(self, texts: list, labels: list) -> dict:
        """
        Train the spam detection model.
        
        Args:
            texts: List of email texts
            labels: List of corresponding labels (0=not spam, 1=spam)
            
        Returns:
            Dictionary with training metrics
        """
        if len(texts) != len(labels):
            raise ValueError("Number of texts and labels must match")
        
        self.logger.info(f"Training model on {len(texts)} samples")
        
        # Preprocess texts
        processed_texts = [preprocess_email("", text) for text in texts]
        
        # Create and fit vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95
        )
        
        X = self.vectorizer.fit_transform(processed_texts)
        y = np.array(labels)
        
        # Train model
        self.model = MultinomialNB(alpha=0.1)
        self.model.fit(X, y)
        
        # Calculate training metrics
        y_pred = self.model.predict(X)
        
        metrics = {
            'accuracy': accuracy_score(y, y_pred),
            'precision': precision_score(y, y_pred, average='binary'),
            'recall': recall_score(y, y_pred, average='binary'),
            'f2_score': fbeta_score(y, y_pred, beta=2, average='binary')
        }
        
        self.logger.info(f"Training completed. Accuracy: {metrics['accuracy']:.4f}")
        return metrics
    
    def predict(self, text: str) -> Tuple[int, float]:
        """
        Predict if text is spam.
        
        Args:
            text: Text to classify
            
        Returns:
            Tuple of (prediction, probability)
            prediction: 0 (not spam) or 1 (spam)
            probability: Confidence score
        """
        if not self.model or not self.vectorizer:
            self.logger.error("Model not loaded")
            return 0, 0.0
        
        try:
            # Preprocess text
            processed_text = preprocess_email("", text)
            
            # Vectorize text
            X = self.vectorizer.transform([processed_text])
            
            # Make prediction
            prediction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            probability = max(probabilities)
            
            return int(prediction), float(probability)
            
        except Exception as e:
            self.logger.error(f"Error during prediction: {e}")
            return 0, 0.0
    
    def is_spam(self, text: str, threshold: float = 0.5) -> bool:
        """
        Check if text is spam.
        
        Args:
            text: Text to classify
            threshold: Confidence threshold for spam classification
            
        Returns:
            True if text is classified as spam
        """
        prediction, probability = self.predict(text)
        return prediction == 1 and probability >= threshold
    
    def get_feature_importance(self, top_n: int = 20) -> list:
        """
        Get most important features for spam detection.
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            List of (feature, importance) tuples
        """
        if not self.model or not self.vectorizer:
            self.logger.error("Model not loaded")
            return []
        
        try:
            # Get feature names
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Get feature log probabilities for spam class
            spam_log_prob = self.model.feature_log_prob_[1]
            
            # Calculate importance (difference between spam and ham log probabilities)
            ham_log_prob = self.model.feature_log_prob_[0]
            importance = spam_log_prob - ham_log_prob
            
            # Create list of (feature, importance) tuples
            feature_importance = list(zip(feature_names, importance))
            
            # Sort by importance and return top N
            feature_importance.sort(key=lambda x: x[1], reverse=True)
            
            return feature_importance[:top_n]
            
        except Exception as e:
            self.logger.error(f"Error getting feature importance: {e}")
            return []
