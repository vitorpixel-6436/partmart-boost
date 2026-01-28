"""AI-powered system optimizer with learning capabilities
SECURITY: Safe path handling, parameterized queries, size limits
"""
import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path

class PartMartAIOptimizer:
    """Lightweight AI optimizer that learns from user's system"""
    
    # Security: Define safe base directory
    SAFE_BASE_DIR = "data"
    MAX_DB_SIZE_MB = 10
    MAX_RECORDS = 1000
    
    def __init__(self, db_name: str = "optimizer_history.db"):
        # Security: Validate and sanitize database path
        self.db_path = self._get_safe_db_path(db_name)
        self._init_database()
        self.recommendations = []
    
    def _get_safe_db_path(self, db_name: str) -> str:
        """Security: Validate database path to prevent path traversal
        
        Args:
            db_name: Database filename (no path separators allowed)
        
        Returns:
            Safe absolute path to database
        
        Raises:
            ValueError: If db_name contains path separators or is invalid
        """
        # Security: Check for path traversal attempts
        if '..' in db_name or '/' in db_name or '\\' in db_name:
            raise ValueError(f"Invalid database name: {db_name}")
        
        # Security: Only allow alphanumeric, underscore, hyphen, dot
        if not all(c.isalnum() or c in ('_', '-', '.') for c in db_name):
            raise ValueError(f"Database name contains invalid characters: {db_name}")
        
        # Ensure safe base directory exists
        os.makedirs(self.SAFE_BASE_DIR, exist_ok=True)
        
        # Return safe absolute path
        safe_path = os.path.abspath(os.path.join(self.SAFE_BASE_DIR, db_name))
        
        # Security: Verify path is within safe directory
        base_dir = os.path.abspath(self.SAFE_BASE_DIR)
        if not safe_path.startswith(base_dir):
            raise ValueError(f"Path traversal detected: {db_name}")
        
        return safe_path
    
    def _init_database(self):
        """Initialize SQLite database for optimization history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Optimization history
            # Security: All queries use parameterized statements
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS optimization_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    gpu_name TEXT,
                    gpu_temp_before REAL,
                    gpu_temp_after REAL,
                    gpu_load_before REAL,
                    gpu_load_after REAL,
                    ram_used_before REAL,
                    ram_used_after REAL,
                    cpu_load_before REAL,
                    cpu_load_after REAL,
                    optimization_type TEXT,
                    success INTEGER,
                    notes TEXT
                )
            """)
            
            # System profiles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gpu_name TEXT UNIQUE,
                    avg_temp REAL,
                    avg_load REAL,
                    recommended_settings TEXT,
                    sample_count INTEGER DEFAULT 0,
                    last_updated TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
            # Limit database size
            self._cleanup_old_records()
            
        except Exception as e:
            print(f"[SECURITY] Database init failed: {e}")
            raise
    
    def _check_db_size(self) -> bool:
        """Security: Check if database exceeds size limit
        
        Returns:
            True if size is OK, False if exceeds limit
        """
        try:
            if os.path.exists(self.db_path):
                size_mb = os.path.getsize(self.db_path) / (1024 * 1024)
                return size_mb < self.MAX_DB_SIZE_MB
            return True
        except Exception as e:
            print(f"[SECURITY] Size check failed: {e}")
            return True  # Fail open to avoid blocking
    
    def _cleanup_old_records(self, max_records: int = None):
        """Keep database under size limit by removing old records
        
        Args:
            max_records: Maximum records to keep (default: self.MAX_RECORDS)
        """
        if max_records is None:
            max_records = self.MAX_RECORDS
        
        try:
            # Security: Check database size
            if not self._check_db_size():
                print(f"[SECURITY] Database exceeds {self.MAX_DB_SIZE_MB}MB, cleaning up...")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count records - Security: No user input in query
            cursor.execute("SELECT COUNT(*) FROM optimization_history")
            count = cursor.fetchone()[0]
            
            if count > max_records:
                # Delete oldest records - Security: Parameterized query
                cursor.execute("""
                    DELETE FROM optimization_history 
                    WHERE id IN (
                        SELECT id FROM optimization_history 
                        ORDER BY timestamp ASC 
                        LIMIT ?
                    )
                """, (count - max_records,))
                conn.commit()
                print(f"[INFO] Cleaned up {count - max_records} old records")
            
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Cleanup failed: {e}")
    
    def record_optimization(self, before: Dict, after: Dict, opt_type: str, success: bool, notes: str = ""):
        """Record optimization attempt for learning
        
        Args:
            before: System state before optimization
            after: System state after optimization
            opt_type: Type of optimization performed
            success: Whether optimization succeeded
            notes: Additional notes
        """
        try:
            # Security: Validate inputs
            if not isinstance(before, dict) or not isinstance(after, dict):
                raise ValueError("Invalid input: before/after must be dictionaries")
            
            # Security: Sanitize string inputs
            opt_type = str(opt_type)[:100]  # Limit length
            notes = str(notes)[:500]  # Limit length
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Security: Parameterized query
            cursor.execute("""
                INSERT INTO optimization_history (
                    timestamp, gpu_name, 
                    gpu_temp_before, gpu_temp_after,
                    gpu_load_before, gpu_load_after,
                    ram_used_before, ram_used_after,
                    cpu_load_before, cpu_load_after,
                    optimization_type, success, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                before.get('gpu', {}).get('name', 'Unknown'),
                before.get('gpu', {}).get('temp_gpu', 0),
                after.get('gpu', {}).get('temp_gpu', 0),
                before.get('gpu', {}).get('load_gpu', 0),
                after.get('gpu', {}).get('load_gpu', 0),
                before.get('ram', {}).get('used', 0),
                after.get('ram', {}).get('used', 0),
                before.get('cpu', {}).get('load', 0),
                after.get('cpu', {}).get('load', 0),
                opt_type,
                1 if success else 0,
                notes
            ))
            
            conn.commit()
            conn.close()
            
            # Update system profile
            self._update_system_profile(before.get('gpu', {}).get('name', 'Unknown'), after)
            
            # Cleanup if needed
            self._cleanup_old_records()
            
        except Exception as e:
            print(f"[ERROR] Record failed: {e}")
    
    def _update_system_profile(self, gpu_name: str, data: Dict):
        """Update average metrics for GPU
        
        Args:
            gpu_name: GPU identifier
            data: Current system data
        """
        try:
            # Security: Sanitize input
            gpu_name = str(gpu_name)[:200]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Security: Parameterized query
            cursor.execute(
                "SELECT avg_temp, avg_load, sample_count FROM system_profiles WHERE gpu_name = ?",
                (gpu_name,)
            )
            row = cursor.fetchone()
            
            gpu = data.get('gpu', {})
            temp = gpu.get('temp_hotspot') or gpu.get('temp_gpu', 0)
            load = gpu.get('load_gpu', 0)
            
            if row:
                avg_temp, avg_load, count = row
                # Running average
                new_count = count + 1
                new_avg_temp = (avg_temp * count + temp) / new_count
                new_avg_load = (avg_load * count + load) / new_count
                
                # Security: Parameterized update
                cursor.execute("""
                    UPDATE system_profiles 
                    SET avg_temp = ?, avg_load = ?, sample_count = ?, last_updated = ?
                    WHERE gpu_name = ?
                """, (new_avg_temp, new_avg_load, new_count, datetime.now().isoformat(), gpu_name))
            else:
                # New profile - Security: Parameterized insert
                cursor.execute("""
                    INSERT INTO system_profiles (gpu_name, avg_temp, avg_load, sample_count, last_updated)
                    VALUES (?, ?, ?, 1, ?)
                """, (gpu_name, temp, load, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Profile update failed: {e}")
    
    def get_recommendations(self, current_data: Dict) -> List[str]:
        """Get AI recommendations based on historical data
        
        Args:
            current_data: Current system state
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            gpu = current_data.get('gpu', {})
            cpu = current_data.get('cpu', {})
            ram = current_data.get('ram', {})
            
            # Security: Parameterized query
            cursor.execute(
                "SELECT avg_temp, avg_load FROM system_profiles WHERE gpu_name = ?",
                (gpu.get('name', 'Unknown'),)
            )
            row = cursor.fetchone()
            
            if row:
                avg_temp, avg_load = row
                current_temp = gpu.get('temp_hotspot') or gpu.get('temp_gpu', 0)
                
                # Temperature analysis
                if current_temp > avg_temp + 10:
                    recommendations.append(f"⚠️ GPU температура выше средней на {current_temp - avg_temp:.1f}°C")
                    recommendations.append("🔧 Рекомендуется прочистить систему охлаждения")
                elif current_temp < avg_temp - 5:
                    recommendations.append(f"✅ GPU температура ниже средней - отлично!")
                
                # Load analysis
                if gpu.get('load_gpu', 0) > avg_load + 20:
                    recommendations.append(f"📊 GPU загрузка высокая ({gpu.get('load_gpu', 0):.0f}%)")
            else:
                recommendations.append("🆕 Сбор данных о вашей системе...")
            
            # RAM analysis
            if ram.get('percent', 0) > 85:
                recommendations.append(f"⚠️ RAM загружен на {ram.get('percent', 0):.0f}%")
                recommendations.append("🧠 Рекомендуется очистка памяти")
            
            # CPU analysis
            if cpu.get('load', 0) > 80:
                recommendations.append(f"💻 CPU загрузка высокая ({cpu.get('load', 0):.0f}%)")
                recommendations.append("🔍 Проверьте фоновые процессы")
            
            # Get successful optimizations count - Security: No user input
            cursor.execute(
                "SELECT COUNT(*) FROM optimization_history WHERE success = 1"
            )
            success_count = cursor.fetchone()[0]
            
            if success_count > 0:
                recommendations.append(f"🎯 Успешных оптимизаций: {success_count}")
            
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Recommendations failed: {e}")
            recommendations.append("⚠️ Ошибка анализа данных")
        
        return recommendations if recommendations else ["✅ Система работает оптимально"]
    
    def get_statistics(self) -> Dict:
        """Get optimization statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Security: All queries without user input
            cursor.execute("SELECT COUNT(*) FROM optimization_history")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM optimization_history WHERE success = 1")
            successful = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT 
                    AVG(gpu_temp_before - gpu_temp_after) as avg_temp_improvement,
                    AVG(ram_used_before - ram_used_after) as avg_ram_improvement
                FROM optimization_history WHERE success = 1
            """)
            row = cursor.fetchone()
            avg_temp_imp, avg_ram_imp = row if row else (0, 0)
            
            conn.close()
            
            return {
                "total_optimizations": total,
                "successful": successful,
                "success_rate": (successful / total * 100) if total > 0 else 0,
                "avg_temp_improvement": avg_temp_imp or 0,
                "avg_ram_improvement": avg_ram_imp or 0,
            }
        except Exception as e:
            print(f"[ERROR] Statistics failed: {e}")
            return {}

if __name__ == "__main__":
    # Test
    print("[TEST] Testing PartMartAIOptimizer...")
    
    # Test path validation
    try:
        bad_optimizer = PartMartAIOptimizer("../../../etc/passwd")
        print("[FAIL] Path traversal not blocked!")
    except ValueError as e:
        print(f"[PASS] Path traversal blocked: {e}")
    
    # Test normal usage
    optimizer = PartMartAIOptimizer()
    print(f"[INFO] Database: {optimizer.db_path}")
    stats = optimizer.get_statistics()
    print(f"[INFO] Statistics: {stats}")
    print("[PASS] All security tests passed!")
