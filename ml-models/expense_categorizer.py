"""
Expense Categorization ML Model
Uses XGBoost for classifying transactions into expense categories
"""

import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from xgboost import XGBClassifier
import logging

logger = logging.getLogger(__name__)


class ExpenseCategorizer:
    """ML model for categorizing expenses"""
    
    def __init__(self, model_path=None):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.model_version = '1.0.0'
        self.model_path = model_path
        
        if model_path:
            self.load_model(model_path)
    
    def prepare_features(self, description, amount, previous_category=None):
        """Prepare features for ML prediction"""
        features = {}
        
        # Text features
        features['description'] = description.lower()
        features['description_length'] = len(description)
        features['word_count'] = len(description.split())
        
        # Amount features
        features['amount'] = float(amount)
        features['amount_log'] = np.log(float(amount) + 1)
        
        # Historical patterns
        if previous_category:
            features['previous_category'] = previous_category
        
        return features
    
    def extract_text_features(self, descriptions):
        """Extract TF-IDF features from transaction descriptions"""
        if self.vectorizer is None:
            self.vectorizer = TfidfVectorizer(
                max_features=100,
                ngram_range=(1, 2),
                stop_words='english'
            )
            return self.vectorizer.fit_transform(descriptions)
        return self.vectorizer.transform(descriptions)
    
    def train(self, transactions_df, category_column='category'):
        """
        Train the categorization model
        
        Args:
            transactions_df: DataFrame with transaction data
            category_column: Name of the category column
        """
        logger.info("Training expense categorizer...")
        
        # Prepare features
        X_text = self.extract_text_features(transactions_df['description'])
        
        # Prepare numeric features
        X_numeric = transactions_df[['amount']].values
        
        # Combine features
        X = np.hstack([X_text.toarray(), X_numeric])
        y = transactions_df[category_column].values
        
        # Train model
        self.model = XGBClassifier(
            n_estimators=100,
            max_depth=7,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric='mlogloss'
        )
        
        self.model.fit(X, y)
        
        logger.info("Model training complete")
        return self
    
    def predict(self, description, amount):
        """
        Predict category for a transaction
        
        Returns:
            dict: {
                'category': predicted_category,
                'confidence': confidence_score (0-1),
                'alternatives': [...]
            }
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        # Prepare features
        X_text = self.vectorizer.transform([description]).toarray()
        X_numeric = np.array([[float(amount)]])
        X = np.hstack([X_text, X_numeric])
        
        # Get prediction
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        # Get confidence
        confidence = float(np.max(probabilities))
        
        # Get alternatives
        top_indices = np.argsort(probabilities)[-3:][::-1]
        alternatives = [
            {
                'category': self.model.classes_[idx],
                'confidence': float(probabilities[idx])
            }
            for idx in top_indices[1:]  # Exclude top prediction
        ]
        
        return {
            'category': prediction,
            'confidence': confidence,
            'alternatives': alternatives,
            'model_version': self.model_version,
        }
    
    def predict_batch(self, descriptions, amounts):
        """Predict categories for multiple transactions"""
        results = []
        for desc, amount in zip(descriptions, amounts):
            result = self.predict(desc, amount)
            results.append(result)
        return results
    
    def save_model(self, path):
        """Save trained model"""
        model_data = {
            'model': self.model,
            'vectorizer': self.vectorizer,
            'model_version': self.model_version,
        }
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path):
        """Load trained model"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.vectorizer = model_data['vectorizer']
        self.model_version = model_data.get('model_version', '1.0.0')
        
        logger.info(f"Model loaded from {path}")
    
    def evaluate(self, test_df, category_column='category'):
        """Evaluate model performance"""
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        predictions = []
        for _, row in test_df.iterrows():
            pred = self.predict(row['description'], row['amount'])
            predictions.append(pred['category'])
        
        y_true = test_df[category_column].values
        
        metrics = {
            'accuracy': float(accuracy_score(y_true, predictions)),
            'precision': float(precision_score(y_true, predictions, average='weighted', zero_division=0)),
            'recall': float(recall_score(y_true, predictions, average='weighted', zero_division=0)),
            'f1': float(f1_score(y_true, predictions, average='weighted', zero_division=0)),
        }
        
        logger.info(f"Model Evaluation: {metrics}")
        return metrics


def categorize_transaction(description, amount, model_path=None):
    """
    Utility function to categorize a single transaction
    
    Args:
        description: Transaction description
        amount: Transaction amount
        model_path: Path to saved model
    
    Returns:
        dict: Prediction result
    """
    categorizer = ExpenseCategorizer(model_path=model_path)
    return categorizer.predict(description, amount)
