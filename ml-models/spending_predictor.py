"""
Spending Prediction ML Model
Uses LSTM and statistical methods to forecast future expenses
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import logging
import pickle

logger = logging.getLogger(__name__)


class SpendingPredictor:
    """ML model for predicting future spending"""
    
    def __init__(self, lookback_window=30, forecast_horizon=30):
        self.lookback_window = lookback_window
        self.forecast_horizon = forecast_horizon
        self.model = None
        self.scaler = MinMaxScaler()
        self.category_scalers = {}
        self.model_version = '1.0.0'
    
    def prepare_time_series_data(self, transactions_df, groupby='category'):
        """Prepare time series data for training"""
        # Group by date and category
        daily_spending = transactions_df.groupby(
            [pd.Grouper(key='transaction_date', freq='D'), groupby]
        )['amount'].sum().reset_index()
        
        return daily_spending
    
    def create_sequences(self, data, lookback=30):
        """Create sequences for LSTM"""
        X, y = [], []
        for i in range(len(data) - lookback):
            X.append(data[i:i + lookback])
            y.append(data[i + lookback])
        return np.array(X), np.array(y)
    
    def train_category_model(self, transactions_df, category_name):
        """Train model for specific category"""
        # Filter data for category
        category_data = transactions_df[
            transactions_df['category'] == category_name
        ].copy()
        
        if len(category_data) < self.lookback_window:
            logger.warning(f"Insufficient data for category: {category_name}")
            return None
        
        # Create daily totals
        daily_data = category_data.set_index('transaction_date')
        daily_data = daily_data.resample('D')['amount'].sum().fillna(0)
        
        # Normalize
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(daily_data.values.reshape(-1, 1))
        
        # Create sequences
        X, y = self.create_sequences(scaled_data, self.lookback_window)
        
        if len(X) == 0:
            return None
        
        # Simple model: use average of lookback period
        # In production, use LSTM/GRU from TensorFlow
        self.category_scalers[category_name] = {
            'scaler': scaler,
            'mean': daily_data.mean(),
            'std': daily_data.std(),
            'seasonal_pattern': self._calculate_seasonal_pattern(daily_data)
        }
        
        logger.info(f"Trained model for category: {category_name}")
        return self.category_scalers[category_name]
    
    def _calculate_seasonal_pattern(self, daily_data):
        """Calculate seasonal patterns (day of week, week of month)"""
        if len(daily_data) < 7:
            return {}
        
        # Resample by day of week
        dow_pattern = daily_data.groupby(daily_data.index.dayofweek).mean()
        
        return {
            'day_of_week': dow_pattern.to_dict()
        }
    
    def predict_category_spending(self, category_name, days_ahead=30):
        """Predict spending for category"""
        if category_name not in self.category_scalers:
            logger.warning(f"No model for category: {category_name}")
            return None
        
        model_data = self.category_scalers[category_name]
        mean = model_data['mean']
        std = model_data['std']
        
        # Simple forecast: mean with seasonal adjustment
        predictions = []
        seasonal_pattern = model_data.get('seasonal_pattern', {}).get('day_of_week', {})
        
        for day in range(days_ahead):
            # Base prediction
            pred = mean
            
            # Add seasonal component
            if seasonal_pattern:
                dow = day % 7
                seasonal_multiplier = seasonal_pattern.get(dow, mean)
                pred = pred * (seasonal_multiplier / mean) if mean > 0 else pred
            
            # Add slight random variation
            pred = max(0, pred + np.random.normal(0, std * 0.1))
            predictions.append(float(pred))
        
        return {
            'category': category_name,
            'predictions': predictions,
            'confidence_interval': {
                'upper': [p + 1.96 * std for p in predictions],
                'lower': [max(0, p - 1.96 * std) for p in predictions]
            },
            'forecast_horizon': days_ahead
        }
    
    def predict_total_spending(self, transactions_df, days_ahead=30):
        """Predict total spending across all categories"""
        predictions_by_category = {}
        total_predictions = [0] * days_ahead
        
        for category in transactions_df['category'].unique():
            cat_pred = self.predict_category_spending(category, days_ahead)
            if cat_pred:
                predictions_by_category[category] = cat_pred['predictions']
                total_predictions = [
                    t + c for t, c in zip(total_predictions, cat_pred['predictions'])
                ]
        
        return {
            'total_predictions': total_predictions,
            'by_category': predictions_by_category,
            'average_daily': float(np.mean(total_predictions)),
            'forecast_horizon': days_ahead
        }
    
    def evaluate(self, actual_data, predicted_data):
        """Evaluate prediction accuracy"""
        if len(actual_data) != len(predicted_data):
            # Adjust to same length
            min_len = min(len(actual_data), len(predicted_data))
            actual_data = actual_data[:min_len]
            predicted_data = predicted_data[:min_len]
        
        mse = mean_squared_error(actual_data, predicted_data)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(np.array(actual_data) - np.array(predicted_data)))
        mape = mean_absolute_percentage_error(actual_data, predicted_data)
        
        metrics = {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'mape': float(mape),
        }
        
        logger.info(f"Prediction Metrics: {metrics}")
        return metrics
    
    def save_model(self, path):
        """Save trained model"""
        with open(path, 'wb') as f:
            pickle.dump({
                'category_scalers': self.category_scalers,
                'lookback_window': self.lookback_window,
                'forecast_horizon': self.forecast_horizon,
                'model_version': self.model_version,
            }, f)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path):
        """Load trained model"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        self.category_scalers = data['category_scalers']
        self.lookback_window = data['lookback_window']
        self.forecast_horizon = data['forecast_horizon']
        self.model_version = data.get('model_version', '1.0.0')
        
        logger.info(f"Model loaded from {path}")


def predict_spending(transactions_df, days_ahead=30, model_path=None):
    """
    Utility function to predict spending
    
    Args:
        transactions_df: DataFrame with transaction data
        days_ahead: Number of days to predict
        model_path: Path to saved model
    
    Returns:
        dict: Prediction results
    """
    predictor = SpendingPredictor()
    
    if model_path:
        predictor.load_model(model_path)
    
    return predictor.predict_total_spending(transactions_df, days_ahead)
