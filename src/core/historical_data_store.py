#!/usr/bin/env python3
"""Historical Data Store - Time-series monitoring data storage

Version: 0.3.5e (package 3.9a, stage 7.7b.8.1/7.7b.8)

Package 3.9a Stage 7.7b.8.1: Historical data system.

Features:
- SQLite-based time-series storage
- Health metrics history
- Error history
- Recovery history
- Configurable retention policies
- Fast time-range queries
- Automatic cleanup
"""
import sqlite3
import json
import time
import threading
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum


class DataRetentionPolicy(Enum):
    """Data retention policies"""
    DAYS_7 = 7
    DAYS_30 = 30
    DAYS_90 = 90
    DAYS_365 = 365
    UNLIMITED = 0


@dataclass
class HealthSnapshot:
    """Health snapshot data"""
    timestamp: float
    component: str
    status: str
    message: str
    metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ErrorRecord:
    """Error record data"""
    timestamp: float
    severity: str
    component: str
    message: str
    details: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RecoveryRecord:
    """Recovery record data"""
    timestamp: float
    component: str
    strategy: str
    status: str
    duration: float
    message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HistoricalDataStore:
    """Store and retrieve historical monitoring data
    
    v0.3.5e (package 3.9a, stage 7.7b.8.1/7.7b.8)
    
    Features:
    - Time-series storage using SQLite
    - Separate tables for health, errors, recoveries
    - Configurable retention policies
    - Indexed queries for fast retrieval
    - Automatic old data cleanup
    - Thread-safe operations
    """
    
    def __init__(
        self,
        db_path: str = "data/monitoring_history.db",
        retention_policy: DataRetentionPolicy = DataRetentionPolicy.DAYS_30
    ):
        """Initialize historical data store
        
        Args:
            db_path: Path to SQLite database file
            retention_policy: Data retention policy
        """
        self._db_path = db_path
        self._retention_policy = retention_policy
        self._lock = threading.Lock()
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            # Health history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    component TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    metrics TEXT
                )
            """)
            
            # Error history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    severity TEXT NOT NULL,
                    component TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT
                )
            """)
            
            # Recovery history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recovery_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    component TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    status TEXT NOT NULL,
                    duration REAL NOT NULL,
                    message TEXT
                )
            """)
            
            # Aggregated statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statistics_hourly (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    hour_start REAL NOT NULL,
                    total_checks INTEGER DEFAULT 0,
                    successful_checks INTEGER DEFAULT 0,
                    total_errors INTEGER DEFAULT 0,
                    total_recoveries INTEGER DEFAULT 0,
                    metrics TEXT
                )
            """)
            
            # Create indexes for faster queries
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_health_timestamp ON health_history(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_health_component ON health_history(component)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_error_timestamp ON error_history(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_error_severity ON error_history(severity)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_recovery_timestamp ON recovery_history(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_statistics_timestamp ON statistics_hourly(timestamp)"
            )
            
            conn.commit()
            conn.close()
    
    def store_health_snapshot(
        self,
        component: str,
        status: str,
        message: str = "",
        metrics: Optional[Dict[str, Any]] = None,
        timestamp: Optional[float] = None
    ) -> int:
        """Store health snapshot
        
        Args:
            component: Component name
            status: Health status
            message: Status message
            metrics: Additional metrics dict
            timestamp: Timestamp (defaults to current time)
        
        Returns:
            Record ID
        """
        if timestamp is None:
            timestamp = time.time()
        
        metrics_json = json.dumps(metrics or {})
        
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO health_history (timestamp, component, status, message, metrics)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, component, status, message, metrics_json))
            
            record_id = cursor.lastrowid
            conn.commit()
            conn.close()
        
        return record_id
    
    def store_error(
        self,
        severity: str,
        component: str,
        message: str,
        details: Optional[str] = None,
        timestamp: Optional[float] = None
    ) -> int:
        """Store error record
        
        Args:
            severity: Error severity
            component: Component name
            message: Error message
            details: Additional details
            timestamp: Timestamp (defaults to current time)
        
        Returns:
            Record ID
        """
        if timestamp is None:
            timestamp = time.time()
        
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO error_history (timestamp, severity, component, message, details)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, severity, component, message, details))
            
            record_id = cursor.lastrowid
            conn.commit()
            conn.close()
        
        return record_id
    
    def store_recovery(
        self,
        component: str,
        strategy: str,
        status: str,
        duration: float,
        message: Optional[str] = None,
        timestamp: Optional[float] = None
    ) -> int:
        """Store recovery record
        
        Args:
            component: Component name
            strategy: Recovery strategy
            status: Recovery status
            duration: Duration in seconds
            message: Additional message
            timestamp: Timestamp (defaults to current time)
        
        Returns:
            Record ID
        """
        if timestamp is None:
            timestamp = time.time()
        
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO recovery_history (timestamp, component, strategy, status, duration, message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp, component, strategy, status, duration, message))
            
            record_id = cursor.lastrowid
            conn.commit()
            conn.close()
        
        return record_id
    
    def query_health_history(
        self,
        start_time: float,
        end_time: float,
        component: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Query health history
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            component: Filter by component (optional)
            status: Filter by status (optional)
            limit: Maximum records to return
        
        Returns:
            List of health records
        """
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM health_history WHERE timestamp BETWEEN ? AND ?"
            params = [start_time, end_time]
            
            if component:
                query += " AND component = ?"
                params.append(component)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            records = []
            for row in rows:
                record = dict(row)
                if record.get('metrics'):
                    record['metrics'] = json.loads(record['metrics'])
                records.append(record)
            
            conn.close()
        
        return records
    
    def query_errors(
        self,
        start_time: float,
        end_time: float,
        severity: Optional[str] = None,
        component: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Query error history
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            severity: Filter by severity (optional)
            component: Filter by component (optional)
            limit: Maximum records to return
        
        Returns:
            List of error records
        """
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM error_history WHERE timestamp BETWEEN ? AND ?"
            params = [start_time, end_time]
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            if component:
                query += " AND component = ?"
                params.append(component)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            records = [dict(row) for row in rows]
            conn.close()
        
        return records
    
    def query_recoveries(
        self,
        start_time: float,
        end_time: float,
        component: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Query recovery history
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            component: Filter by component (optional)
            status: Filter by status (optional)
            limit: Maximum records to return
        
        Returns:
            List of recovery records
        """
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM recovery_history WHERE timestamp BETWEEN ? AND ?"
            params = [start_time, end_time]
            
            if component:
                query += " AND component = ?"
                params.append(component)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            records = [dict(row) for row in rows]
            conn.close()
        
        return records
    
    def get_statistics(
        self,
        start_time: float,
        end_time: float
    ) -> Dict[str, Any]:
        """Get aggregated statistics for time range
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            # Count health checks
            cursor.execute("""
                SELECT COUNT(*) FROM health_history
                WHERE timestamp BETWEEN ? AND ?
            """, (start_time, end_time))
            total_checks = cursor.fetchone()[0]
            
            # Count successful checks
            cursor.execute("""
                SELECT COUNT(*) FROM health_history
                WHERE timestamp BETWEEN ? AND ?
                AND status = 'healthy'
            """, (start_time, end_time))
            successful_checks = cursor.fetchone()[0]
            
            # Count errors by severity
            cursor.execute("""
                SELECT severity, COUNT(*) as count
                FROM error_history
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY severity
            """, (start_time, end_time))
            errors_by_severity = dict(cursor.fetchall())
            
            # Count recoveries by status
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM recovery_history
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY status
            """, (start_time, end_time))
            recoveries_by_status = dict(cursor.fetchall())
            
            # Average recovery duration
            cursor.execute("""
                SELECT AVG(duration) FROM recovery_history
                WHERE timestamp BETWEEN ? AND ?
            """, (start_time, end_time))
            avg_recovery_duration = cursor.fetchone()[0] or 0
            
            conn.close()
        
        return {
            'total_checks': total_checks,
            'successful_checks': successful_checks,
            'success_rate': (successful_checks / total_checks * 100) if total_checks > 0 else 0,
            'errors_by_severity': errors_by_severity,
            'total_errors': sum(errors_by_severity.values()),
            'recoveries_by_status': recoveries_by_status,
            'total_recoveries': sum(recoveries_by_status.values()),
            'avg_recovery_duration': avg_recovery_duration
        }
    
    def cleanup_old_data(self, retention_days: Optional[int] = None) -> int:
        """Clean up old data based on retention policy
        
        Args:
            retention_days: Retention period in days (uses policy if not specified)
        
        Returns:
            Number of records deleted
        """
        if retention_days is None:
            retention_days = self._retention_policy.value
        
        if retention_days == 0:  # UNLIMITED
            return 0
        
        cutoff_time = time.time() - (retention_days * 86400)  # days to seconds
        
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            # Delete old health records
            cursor.execute("""
                DELETE FROM health_history WHERE timestamp < ?
            """, (cutoff_time,))
            health_deleted = cursor.rowcount
            
            # Delete old error records
            cursor.execute("""
                DELETE FROM error_history WHERE timestamp < ?
            """, (cutoff_time,))
            errors_deleted = cursor.rowcount
            
            # Delete old recovery records
            cursor.execute("""
                DELETE FROM recovery_history WHERE timestamp < ?
            """, (cutoff_time,))
            recoveries_deleted = cursor.rowcount
            
            # Delete old statistics
            cursor.execute("""
                DELETE FROM statistics_hourly WHERE timestamp < ?
            """, (cutoff_time,))
            stats_deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
        
        total_deleted = health_deleted + errors_deleted + recoveries_deleted + stats_deleted
        return total_deleted
    
    def get_database_size(self) -> int:
        """Get database file size in bytes
        
        Returns:
            Database size in bytes
        """
        return Path(self._db_path).stat().st_size
    
    def vacuum(self):
        """Optimize database (reclaim space after deletions)"""
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            conn.execute("VACUUM")
            conn.close()
    
    def get_record_counts(self) -> Dict[str, int]:
        """Get record counts for all tables
        
        Returns:
            Dictionary with table names and record counts
        """
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM health_history")
            health_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM error_history")
            error_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM recovery_history")
            recovery_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM statistics_hourly")
            stats_count = cursor.fetchone()[0]
            
            conn.close()
        
        return {
            'health_records': health_count,
            'error_records': error_count,
            'recovery_records': recovery_count,
            'statistics_records': stats_count,
            'total_records': health_count + error_count + recovery_count + stats_count
        }


# Testing
if __name__ == '__main__':
    import tempfile
    import os
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        print("Testing HistoricalDataStore...\n")
        
        store = HistoricalDataStore(db_path, DataRetentionPolicy.DAYS_7)
        
        # Store test data
        print("Storing test data...")
        store.store_health_snapshot('TestComponent', 'healthy', 'Operating normally', {'cpu': 50})
        store.store_error('error', 'TestComponent', 'Test error', 'Error details')
        store.store_recovery('TestComponent', 'restart', 'success', 1.5, 'Recovered successfully')
        
        # Query data
        print("\nQuerying data...")
        end_time = time.time()
        start_time = end_time - 3600  # Last hour
        
        health = store.query_health_history(start_time, end_time)
        errors = store.query_errors(start_time, end_time)
        recoveries = store.query_recoveries(start_time, end_time)
        
        print(f"Health records: {len(health)}")
        print(f"Error records: {len(errors)}")
        print(f"Recovery records: {len(recoveries)}")
        
        # Get statistics
        print("\nStatistics:")
        stats = store.get_statistics(start_time, end_time)
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Record counts
        print("\nRecord counts:")
        counts = store.get_record_counts()
        for key, value in counts.items():
            print(f"  {key}: {value}")
        
        print(f"\nDatabase size: {store.get_database_size()} bytes")
        
        print("\n✅ Test completed successfully!")
    
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
