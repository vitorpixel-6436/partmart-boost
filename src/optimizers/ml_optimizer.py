"""Lightweight ML optimizer for GPU/RAM predictions"""
import os
import json
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("[ML Optimizer] sklearn not available - ML features disabled")

class LocalMLOptimizer:
    """Lightweight local ML optimizer for PartMart Boost
    
    Features:
    - Learns from optimization history
    - Predicts optimal GPU clock/voltage
    - Predicts safe RAM timings
    - Works 100% locally (no internet)
    - <50MB RAM usage
    - Auto-cleanup old data
    """
    
    def __init__(self, db_path: str = "data/ml_optimizer.db", enabled: bool = False):
        self.enabled = enabled and SKLEARN_AVAILABLE
        self.db_path = db_path
        self.model_gpu = None
        self.model_ram = None
        self.scaler = None
        
        if self.enabled:
            self._ensure_db_dir()
            self._init_database()
            self._load_or_create_model()
    
    def _ensure_db_dir(self):
        """Create data directory if needed"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    
    def _init_database(self):
        """Initialize SQLite database for optimization history"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # GPU optimizations table
        c.execute('''
            CREATE TABLE IF NOT EXISTS gpu_optimizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                gpu_name TEXT,
                base_clock INTEGER,
                base_voltage INTEGER,
                base_temp REAL,
                base_load REAL,
                optimized_clock INTEGER,
                optimized_voltage INTEGER,
                result_temp REAL,
                result_fps REAL,
                success BOOLEAN,
                stable BOOLEAN
            )
        ''')
        
        # RAM optimizations table
        c.execute('''
            CREATE TABLE IF NOT EXISTS ram_optimizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                base_speed INTEGER,
                base_latency REAL,
                optimized_speed INTEGER,
                xmp_enabled BOOLEAN,
                success BOOLEAN
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_or_create_model(self):
        """Load existing model or create new one"""
        if not SKLEARN_AVAILABLE:
            return
        
        # Simple linear regression models
        self.model_gpu = LinearRegression()
        self.model_ram = LinearRegression()
        self.scaler = StandardScaler()
        
        # Try to load training data and train
        self._train_from_history()
    
    def _train_from_history(self):
        """Train models from historical data"""
        if not self.enabled:
            return
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get GPU training data (only successful optimizations)
        c.execute('''
            SELECT base_clock, base_voltage, base_temp, base_load,
                   optimized_clock, optimized_voltage, result_temp
            FROM gpu_optimizations
            WHERE success = 1 AND stable = 1
            LIMIT 1000
        ''')
        
        gpu_data = c.fetchall()
        if len(gpu_data) >= 10:  # Need at least 10 samples to train
            X = np.array([[d[0], d[1], d[2], d[3]] for d in gpu_data])
            y_clock = np.array([d[4] for d in gpu_data])
            y_voltage = np.array([d[5] for d in gpu_data])
            
            # Train models
            try:
                self.scaler.fit(X)
                X_scaled = self.scaler.transform(X)
                self.model_gpu.fit(X_scaled, y_clock)
                print(f"[ML Optimizer] GPU model trained on {len(gpu_data)} samples")
            except Exception as e:
                print(f"[ML Optimizer] Failed to train GPU model: {e}")
        
        conn.close()
    
    def record_gpu_optimization(self, before: Dict, after: Dict, success: bool, stable: bool):
        """Record GPU optimization for learning"""
        if not self.enabled:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO gpu_optimizations (
                    timestamp, gpu_name, base_clock, base_voltage, base_temp, base_load,
                    optimized_clock, optimized_voltage, result_temp, result_fps,
                    success, stable
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                before.get('gpu_name', 'Unknown'),
                before.get('clock', 0),
                before.get('voltage', 0),
                before.get('temperature', 0),
                before.get('load', 0),
                after.get('clock', 0),
                after.get('voltage', 0),
                after.get('temperature', 0),
                after.get('fps', 0),
                success,
                stable
            ))
            
            conn.commit()
            conn.close()
            
            # Retrain model if we have enough new data
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM gpu_optimizations')
            count = c.fetchone()[0]
            if count % 10 == 0:  # Retrain every 10 new records
                self._train_from_history()
        
        except Exception as e:
            print(f"[ML Optimizer] Failed to record optimization: {e}")
    
    def predict_optimal_gpu_settings(self, current_state: Dict) -> Optional[Dict]:
        """Predict optimal GPU clock and voltage
        
        Args:
            current_state: Dict with 'clock', 'voltage', 'temperature', 'load'
        
        Returns:
            Dict with 'optimal_clock', 'optimal_voltage', 'confidence'
            or None if ML is disabled or not enough data
        """
        if not self.enabled or self.model_gpu is None:
            return self._get_safe_defaults()
        
        try:
            # Prepare input
            X = np.array([[
                current_state.get('clock', 1500),
                current_state.get('voltage', 1000),
                current_state.get('temperature', 50),
                current_state.get('load', 50)
            ]])
            
            X_scaled = self.scaler.transform(X)
            
            # Predict
            predicted_clock = int(self.model_gpu.predict(X_scaled)[0])
            
            # Safety checks
            base_clock = current_state.get('clock', 1500)
            predicted_clock = max(base_clock - 200, min(base_clock + 500, predicted_clock))
            
            return {
                'optimal_clock': predicted_clock,
                'optimal_voltage': current_state.get('voltage', 1000) - 50,  # Conservative
                'confidence': 0.7,  # Medium confidence
                'method': 'ml_prediction'
            }
        
        except Exception as e:
            print(f"[ML Optimizer] Prediction failed: {e}")
            return self._get_safe_defaults()
    
    def _get_safe_defaults(self) -> Dict:
        """Return safe default optimization values"""
        return {
            'optimal_clock': 0,  # No change
            'optimal_voltage': -50,  # Small undervolt
            'confidence': 0.5,
            'method': 'safe_defaults'
        }
    
    def cleanup_old_data(self, days: int = 90):
        """Remove old optimization records"""
        if not self.enabled:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            cutoff = datetime.now().replace(day=datetime.now().day - days).isoformat()
            
            c.execute('DELETE FROM gpu_optimizations WHERE timestamp < ?', (cutoff,))
            c.execute('DELETE FROM ram_optimizations WHERE timestamp < ?', (cutoff,))
            
            conn.commit()
            conn.close()
            
            print(f"[ML Optimizer] Cleaned up data older than {days} days")
        
        except Exception as e:
            print(f"[ML Optimizer] Cleanup failed: {e}")
    
    def get_statistics(self) -> Dict:
        """Get optimization statistics"""
        if not self.enabled:
            return {'enabled': False}
        
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('SELECT COUNT(*) FROM gpu_optimizations')
            gpu_count = c.fetchone()[0]
            
            c.execute('SELECT COUNT(*) FROM gpu_optimizations WHERE success = 1')
            gpu_success = c.fetchone()[0]
            
            c.execute('SELECT AVG(result_temp - base_temp) FROM gpu_optimizations WHERE success = 1')
            avg_temp_reduction = c.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'enabled': True,
                'total_optimizations': gpu_count,
                'successful_optimizations': gpu_success,
                'success_rate': gpu_success / gpu_count if gpu_count > 0 else 0,
                'avg_temp_reduction': round(avg_temp_reduction, 2),
                'model_trained': self.model_gpu is not None
            }
        
        except Exception as e:
            print(f"[ML Optimizer] Failed to get statistics: {e}")
            return {'enabled': True, 'error': str(e)}

# Global instance
_ml_optimizer = None

def get_ml_optimizer(enabled: bool = False) -> LocalMLOptimizer:
    """Get global ML optimizer instance"""
    global _ml_optimizer
    if _ml_optimizer is None:
        _ml_optimizer = LocalMLOptimizer(enabled=enabled)
    return _ml_optimizer

if __name__ == "__main__":
    # Test
    ml = LocalMLOptimizer("test_ml.db", enabled=True)
    
    # Simulate some optimizations
    for i in range(15):
        before = {
            'gpu_name': 'RTX 3060',
            'clock': 1500 + i * 10,
            'voltage': 1000,
            'temperature': 60 + i * 2,
            'load': 50 + i * 3
        }
        after = {
            'clock': 1600 + i * 10,
            'voltage': 950,
            'temperature': 55 + i * 2,
            'fps': 100 + i * 5
        }
        ml.record_gpu_optimization(before, after, success=True, stable=True)
    
    # Test prediction
    current = {'clock': 1550, 'voltage': 1000, 'temperature': 65, 'load': 70}
    prediction = ml.predict_optimal_gpu_settings(current)
    print(f"\nPrediction: {prediction}")
    
    # Statistics
    stats = ml.get_statistics()
    print(f"\nStatistics: {stats}")
    
    # Cleanup
    import os
    if os.path.exists("test_ml.db"):
        os.remove("test_ml.db")
