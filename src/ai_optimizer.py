"""AI-powered system optimizer with learning capabilities"""
import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple

class PartMartAIOptimizer:
    """Lightweight AI optimizer that learns from user's system"""
    
    def __init__(self):
        self.db_path = "data/optimizer_history.db"
        self._init_database()
        self.recommendations = []
    
    def _init_database(self):
        """Initialize SQLite database for optimization history"""
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Optimization history
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
    
    def _cleanup_old_records(self, max_records: int = 1000):
        """Keep database under 10MB by removing old records"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count records
            cursor.execute("SELECT COUNT(*) FROM optimization_history")
            count = cursor.fetchone()[0]
            
            if count > max_records:
                # Delete oldest records
                cursor.execute("""
                    DELETE FROM optimization_history 
                    WHERE id IN (
                        SELECT id FROM optimization_history 
                        ORDER BY timestamp ASC 
                        LIMIT ?
                    )
                """, (count - max_records,))
                conn.commit()
            
            conn.close()
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def record_optimization(self, before: Dict, after: Dict, opt_type: str, success: bool, notes: str = ""):
        """Record optimization attempt for learning"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
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
                before['gpu']['name'],
                before['gpu']['temp_gpu'],
                after['gpu']['temp_gpu'],
                before['gpu']['load_gpu'],
                after['gpu']['load_gpu'],
                before['ram']['used'],
                after['ram']['used'],
                before['cpu']['load'],
                after['cpu']['load'],
                opt_type,
                1 if success else 0,
                notes
            ))
            
            conn.commit()
            conn.close()
            
            # Update system profile
            self._update_system_profile(before['gpu']['name'], after)
            
        except Exception as e:
            print(f"Record error: {e}")
    
    def _update_system_profile(self, gpu_name: str, data: Dict):
        """Update average metrics for GPU"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get existing profile
            cursor.execute(
                "SELECT avg_temp, avg_load, sample_count FROM system_profiles WHERE gpu_name = ?",
                (gpu_name,)
            )
            row = cursor.fetchone()
            
            gpu = data['gpu']
            temp = gpu['temp_hotspot'] if gpu['temp_hotspot'] else gpu['temp_gpu']
            load = gpu['load_gpu']
            
            if row:
                avg_temp, avg_load, count = row
                # Running average
                new_count = count + 1
                new_avg_temp = (avg_temp * count + temp) / new_count
                new_avg_load = (avg_load * count + load) / new_count
                
                cursor.execute("""
                    UPDATE system_profiles 
                    SET avg_temp = ?, avg_load = ?, sample_count = ?, last_updated = ?
                    WHERE gpu_name = ?
                """, (new_avg_temp, new_avg_load, new_count, datetime.now().isoformat(), gpu_name))
            else:
                # New profile
                cursor.execute("""
                    INSERT INTO system_profiles (gpu_name, avg_temp, avg_load, sample_count, last_updated)
                    VALUES (?, ?, ?, 1, ?)
                """, (gpu_name, temp, load, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Profile update error: {e}")
    
    def get_recommendations(self, current_data: Dict) -> List[str]:
        """Get AI recommendations based on historical data"""
        recommendations = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            gpu = current_data['gpu']
            cpu = current_data['cpu']
            ram = current_data['ram']
            
            # Get system profile
            cursor.execute(
                "SELECT avg_temp, avg_load FROM system_profiles WHERE gpu_name = ?",
                (gpu['name'],)
            )
            row = cursor.fetchone()
            
            if row:
                avg_temp, avg_load = row
                current_temp = gpu['temp_hotspot'] if gpu['temp_hotspot'] else gpu['temp_gpu']
                
                # Temperature analysis
                if current_temp > avg_temp + 10:
                    recommendations.append(f"⚠️ GPU температура выше средней на {current_temp - avg_temp:.1f}°C")
                    recommendations.append("🔧 Рекомендуется прочистить систему охлаждения")
                elif current_temp < avg_temp - 5:
                    recommendations.append(f"✅ GPU температура ниже средней - отлично!")
                
                # Load analysis
                if gpu['load_gpu'] > avg_load + 20:
                    recommendations.append(f"📊 GPU загрузка высокая ({gpu['load_gpu']:.0f}%)")
            else:
                # No historical data yet
                recommendations.append("🆕 Сбор данных о вашей системе...")
            
            # RAM analysis
            if ram['percent'] > 85:
                recommendations.append(f"⚠️ RAM загружен на {ram['percent']:.0f}%")
                recommendations.append("🧠 Рекомендуется очистка памяти")
            
            # CPU analysis
            if cpu['load'] > 80:
                recommendations.append(f"💻 CPU загрузка высокая ({cpu['load']:.0f}%)")
                recommendations.append("🔍 Проверьте фоновые процессы")
            
            # Get successful optimizations count
            cursor.execute(
                "SELECT COUNT(*) FROM optimization_history WHERE success = 1"
            )
            success_count = cursor.fetchone()[0]
            
            if success_count > 0:
                recommendations.append(f"🎯 Успешных оптимизаций: {success_count}")
            
            conn.close()
            
        except Exception as e:
            print(f"Recommendations error: {e}")
            recommendations.append("⚠️ Ошибка анализа данных")
        
        return recommendations if recommendations else ["✅ Система работает оптимально"]
    
    def get_statistics(self) -> Dict:
        """Get optimization statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total optimizations
            cursor.execute("SELECT COUNT(*) FROM optimization_history")
            total = cursor.fetchone()[0]
            
            # Successful optimizations
            cursor.execute("SELECT COUNT(*) FROM optimization_history WHERE success = 1")
            successful = cursor.fetchone()[0]
            
            # Average improvements
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
            print(f"Statistics error: {e}")
            return {}

if __name__ == "__main__":
    # Test
    optimizer = PartMartAIOptimizer()
    print("AI Optimizer initialized")
    print(f"Database: {optimizer.db_path}")
    stats = optimizer.get_statistics()
    print(f"Statistics: {stats}")
