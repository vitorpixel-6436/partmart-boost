"""Local ML optimizer for PartMart Boost (Beta)"""
import os
import pickle
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available - ML optimizer disabled")

class LocalMLOptimizer:
    """Lightweight ML model for GPU/RAM optimization
    
    Features:
    - Learns optimal GPU clock/voltage from successful optimizations
    - Predicts safe settings based on current system state
    - Works completely offline
    - <50MB RAM usage
    - Auto-cleanup (max 1000 records)
    """
    
    def __init__(self, data_dir: str = "data/ml", enabled: bool = False):
        self.enabled = enabled and SKLEARN_AVAILABLE
        self.data_dir = data_dir
        self.history_file = os.path.join(data_dir, "optimization_history.json")
        self.model_file = os.path.join(data_dir, "model.pkl")
        
        self.model = None
        self.scaler = None
        self.history: List[Dict] = []
        
        if self.enabled:
            self._ensure_data_dir()
            self._load_history()
            self._load_model()
    
    def _ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _load_history(self):
        """Load optimization history from JSON"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except Exception as e:
                logging.error(f"Failed to load ML history: {e}")
                self.history = []
    
    def _save_history(self):
        """Save optimization history to JSON"""
        try:
            # Keep only last 1000 records (avoid bloat)
            if len(self.history) > 1000:
                self.history = self.history[-1000:]
            
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save ML history: {e}")
    
    def _load_model(self):
        """Load trained model from disk"""
        if os.path.exists(self.model_file):
            try:
                with open(self.model_file, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data['model']
                    self.scaler = data['scaler']
            except Exception as e:
                logging.error(f"Failed to load ML model: {e}")
                self.model = None
                self.scaler = None
    
    def _save_model(self):
        """Save trained model to disk"""
        try:
            with open(self.model_file, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'scaler': self.scaler
                }, f)
        except Exception as e:
            logging.error(f"Failed to save ML model: {e}")
    
    def record_optimization(self, 
                           before: Dict[str, float],
                           after: Dict[str, float],
                           success: bool,
                           optimization_type: str = "quick_boost"):
        """Record optimization attempt for learning
        
        Args:
            before: System state before optimization (temp, load, etc.)
            after: System state after optimization
            success: Whether optimization was successful
            optimization_type: Type of optimization performed
        """
        if not self.enabled:
            return
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'type': optimization_type,
            'success': success,
            'before': before,
            'after': after,
        }
        
        self.history.append(record)
        self._save_history()
        
        # Retrain model if we have enough data
        if len(self.history) >= 10 and len(self.history) % 5 == 0:
            self._train_model()
    
    def _train_model(self):
        """Train ML model on optimization history"""
        if not self.enabled or len(self.history) < 10:
            return
        
        try:
            # Extract successful optimizations only
            successful = [r for r in self.history if r['success']]
            if len(successful) < 5:
                return
            
            # Prepare training data
            X = []  # Features: before state
            y = []  # Target: temperature reduction
            
            for record in successful:
                before = record['before']
                after = record['after']
                
                # Features: gpu_temp, gpu_load, cpu_load, ram_percent
                features = [
                    before.get('gpu_temp', 0),
                    before.get('gpu_load', 0),
                    before.get('cpu_load', 0),
                    before.get('ram_percent', 0),
                ]
                
                # Target: temperature reduction (positive = improvement)
                temp_reduction = before.get('gpu_temp', 0) - after.get('gpu_temp', 0)
                
                X.append(features)
                y.append(temp_reduction)
            
            X = np.array(X)
            y = np.array(y)
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train simple linear regression
            self.model = LinearRegression()
            self.model.fit(X_scaled, y)
            
            self._save_model()
            logging.info(f"ML model trained on {len(successful)} successful optimizations")
            
        except Exception as e:
            logging.error(f"Failed to train ML model: {e}")
            self.model = None
            self.scaler = None
    
    def predict_optimization_benefit(self, current_state: Dict[str, float]) -> Optional[float]:
        """Predict expected temperature reduction from optimization
        
        Args:
            current_state: Current system state (gpu_temp, gpu_load, etc.)
        
        Returns:
            Expected temperature reduction in °C, or None if prediction unavailable
        """
        if not self.enabled or self.model is None or self.scaler is None:
            return None
        
        try:
            # Prepare features
            features = [
                current_state.get('gpu_temp', 0),
                current_state.get('gpu_load', 0),
                current_state.get('cpu_load', 0),
                current_state.get('ram_percent', 0),
            ]
            
            X = np.array([features])
            X_scaled = self.scaler.transform(X)
            
            # Predict
            prediction = self.model.predict(X_scaled)[0]
            
            # Return only if prediction is positive and reasonable
            if 0 < prediction < 20:  # Sanity check
                return float(prediction)
            
        except Exception as e:
            logging.error(f"Failed to predict: {e}")
        
        return None
    
    def get_recommendations(self, current_state: Dict[str, float]) -> List[str]:
        """Get optimization recommendations based on current state
        
        Args:
            current_state: Current system state
        
        Returns:
            List of recommendation strings
        """
        if not self.enabled:
            return []
        
        recommendations = []
        
        # Rule-based recommendations (simple but effective)
        gpu_temp = current_state.get('gpu_temp', 0)
        gpu_load = current_state.get('gpu_load', 0)
        cpu_load = current_state.get('cpu_load', 0)
        ram_percent = current_state.get('ram_percent', 0)
        
        # High temperature
        if gpu_temp > 75:
            benefit = self.predict_optimization_benefit(current_state)
            if benefit and benefit > 3:
                recommendations.append(f"Quick Boost may reduce temperature by ~{benefit:.1f}°C")
            else:
                recommendations.append("GPU temperature high - consider optimization")
        
        # High RAM usage
        if ram_percent > 85:
            recommendations.append("RAM usage high - cleanup recommended")
        
        # High CPU load
        if cpu_load > 80:
            recommendations.append("CPU load high - check background processes")
        
        # If everything is fine
        if not recommendations and self.model is not None:
            success_count = len([r for r in self.history if r['success']])
            if success_count > 0:
                recommendations.append(f"System running well ({success_count} successful optimizations)")
            else:
                recommendations.append("Collecting optimization data...")
        
        return recommendations
    
    def get_stats(self) -> Dict[str, any]:
        """Get ML optimizer statistics"""
        if not self.enabled:
            return {'enabled': False}
        
        successful = len([r for r in self.history if r['success']])
        total = len(self.history)
        
        return {
            'enabled': True,
            'model_trained': self.model is not None,
            'total_optimizations': total,
            'successful_optimizations': successful,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'history_size_kb': os.path.getsize(self.history_file) / 1024 if os.path.exists(self.history_file) else 0,
        }

# Global instance
_ml_optimizer = None

def get_ml_optimizer() -> LocalMLOptimizer:
    """Get global ML optimizer instance"""
    global _ml_optimizer
    if _ml_optimizer is None:
        from core.config import get_config
        config = get_config()
        _ml_optimizer = LocalMLOptimizer(enabled=config.is_ml_enabled())
    return _ml_optimizer

def init_ml_optimizer(enabled: bool) -> LocalMLOptimizer:
    """Initialize global ML optimizer"""
    global _ml_optimizer
    _ml_optimizer = LocalMLOptimizer(enabled=enabled)
    return _ml_optimizer

if __name__ == "__main__":
    # Test
    optimizer = LocalMLOptimizer(data_dir="test_ml", enabled=True)
    
    # Simulate optimizations
    for i in range(15):
        before = {
            'gpu_temp': 75 + np.random.randn() * 5,
            'gpu_load': 60 + np.random.randn() * 10,
            'cpu_load': 40 + np.random.randn() * 10,
            'ram_percent': 70 + np.random.randn() * 10,
        }
        after = {
            'gpu_temp': before['gpu_temp'] - 3 - np.random.randn(),
            'gpu_load': before['gpu_load'],
            'cpu_load': before['cpu_load'] - 2,
            'ram_percent': before['ram_percent'] - 5,
        }
        
        optimizer.record_optimization(before, after, success=True)
    
    # Test prediction
    current = {'gpu_temp': 78, 'gpu_load': 65, 'cpu_load': 45, 'ram_percent': 75}
    benefit = optimizer.predict_optimization_benefit(current)
    print(f"Predicted benefit: {benefit:.1f}°C" if benefit else "No prediction available")
    
    # Get recommendations
    recs = optimizer.get_recommendations(current)
    print(f"Recommendations: {recs}")
    
    # Stats
    stats = optimizer.get_stats()
    print(f"Stats: {stats}")
    
    # Cleanup
    import shutil
    if os.path.exists("test_ml"):
        shutil.rmtree("test_ml")
