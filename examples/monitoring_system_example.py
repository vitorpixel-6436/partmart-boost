#!/usr/bin/env python3
"""Complete Monitoring System Example

Version: 0.3.5u (package 3.9a, stage 7.7b.8/7.7)

Demonstrates complete integration of:
- ErrorReporter
- SystemHealthMonitor
- RecoveryCoordinator
- MonitoringPanel (GUI)
"""
import sys
import os
import time
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.error_reporter import ErrorReporter, ErrorSeverity
from core.system_health_monitor import SystemHealthMonitor, HealthStatus
from core.recovery_coordinator import RecoveryCoordinator, RecoveryStrategy


class ExampleApplication:
    """Example application with monitoring"""
    
    def __init__(self):
        print("\n" + "="*60)
        print("Complete Monitoring System Example")
        print("Version 0.3.5u (Package 3.9a, Stage 7.7 COMPLETE)")
        print("="*60 + "\n")
        
        # Create monitoring systems
        print("[1/4] Creating ErrorReporter...")
        self.error_reporter = ErrorReporter(max_errors=1000)
        
        print("[2/4] Creating SystemHealthMonitor...")
        self.health_monitor = SystemHealthMonitor(
            check_interval=2.0,  # Check every 2 seconds
            error_reporter=self.error_reporter
        )
        
        print("[3/4] Creating RecoveryCoordinator...")
        self.recovery_coordinator = RecoveryCoordinator(
            health_monitor=self.health_monitor,
            error_reporter=self.error_reporter
        )
        
        print("[4/4] Setup complete!\n")
        
        # Setup alert callback
        self.health_monitor.add_alert_callback(self._on_health_alert)
        
        # Component states
        self.components = {
            'ConfigManager': {'running': True, 'fail_count': 0},
            'PerformanceMonitor': {'running': True, 'fail_count': 0},
            'GameDetector': {'running': True, 'fail_count': 0}
        }
    
    def _on_health_alert(self, alert):
        """Handle health alert"""
        print(f"\n⚠️  ALERT: [{alert.level.value.upper()}] {alert.component}")
        print(f"   Message: {alert.message}")
        if alert.details:
            print(f"   Details: {alert.details}")
        print()
    
    def setup_components(self):
        """Setup monitoring for components"""
        print("Setting up components...\n")
        
        for component in self.components:
            print(f"  - Registering {component}")
            
            # Register health check
            self.health_monitor.register_component(
                component,
                health_check=lambda c=component: self._check_component_health(c),
                get_metrics=lambda c=component: self._get_component_metrics(c)
            )
            
            # Register recovery action
            self.recovery_coordinator.register_recovery(
                component,
                RecoveryStrategy.RESTART,
                action=lambda c=component: self._restart_component(c),
                rollback_action=lambda c=component: self._rollback_component(c),
                max_attempts=3,
                cooldown=10.0
            )
        
        print("\n✅ All components registered!\n")
    
    def _check_component_health(self, component: str) -> bool:
        """Check component health"""
        return self.components[component]['running']
    
    def _get_component_metrics(self, component: str) -> Dict[str, Any]:
        """Get component metrics"""
        return {
            'running': self.components[component]['running'],
            'fail_count': self.components[component]['fail_count'],
            'status': 'healthy' if self.components[component]['running'] else 'unhealthy'
        }
    
    def _restart_component(self, component: str) -> bool:
        """Restart component"""
        print(f"  🔄 Restarting {component}...")
        time.sleep(0.5)  # Simulate restart
        
        # Reset component
        self.components[component]['running'] = True
        self.components[component]['fail_count'] = 0
        
        print(f"  ✅ {component} restarted successfully")
        return True
    
    def _rollback_component(self, component: str) -> bool:
        """Rollback component"""
        print(f"  ↩️  Rolling back {component}...")
        time.sleep(0.3)
        print(f"  ✅ {component} rolled back")
        return True
    
    def simulate_error(self, component: str, severity: ErrorSeverity = ErrorSeverity.WARNING):
        """Simulate error in component"""
        print(f"\n💥 Simulating {severity.value} error in {component}...")
        
        self.error_reporter.report_error(
            component,
            f"Simulated {severity.value} error",
            severity=severity
        )
        
        if severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
            self.components[component]['running'] = False
            self.components[component]['fail_count'] += 1
    
    def start(self):
        """Start monitoring"""
        print("Starting monitoring system...\n")
        
        # Start health monitor
        self.health_monitor.start()
        
        # Enable auto-recovery
        self.recovery_coordinator.enable_auto_recovery()
        
        print("✅ Monitoring active")
        print("✅ Auto-recovery enabled\n")
    
    def stop(self):
        """Stop monitoring"""
        print("\nStopping monitoring system...")
        self.health_monitor.stop()
        print("✅ Monitoring stopped\n")
    
    def print_status(self):
        """Print system status"""
        print("\n" + "="*60)
        print("SYSTEM STATUS")
        print("="*60)
        
        # Health status
        health = self.health_monitor.get_system_health()
        print(f"\n🏥 Health Status: {health['status'].upper()}")
        print(f"   Components: {health['total_components']}")
        print(f"   Healthy: {health['healthy_count']} | Degraded: {health['degraded_count']}")
        print(f"   Unhealthy: {health['unhealthy_count']} | Critical: {health['critical_count']}")
        
        # Error statistics
        error_stats = self.error_reporter.get_statistics()
        print(f"\n📊 Error Statistics:")
        print(f"   Total errors: {error_stats['total_errors']}")
        print(f"   Current records: {error_stats['current_errors']}")
        
        # Recovery statistics
        recovery_stats = self.recovery_coordinator.get_statistics()
        print(f"\n🔧 Recovery Statistics:")
        print(f"   Total recoveries: {recovery_stats['total_recoveries']}")
        print(f"   Successful: {recovery_stats['successful_recoveries']}")
        print(f"   Failed: {recovery_stats['failed_recoveries']}")
        print(f"   Success rate: {recovery_stats['success_rate']:.1f}%")
        
        print("\n" + "="*60 + "\n")
    
    def run_demo(self):
        """Run demonstration"""
        try:
            # Setup
            self.setup_components()
            self.start()
            
            print("\n" + "="*60)
            print("RUNNING DEMONSTRATION")
            print("="*60)
            
            # Phase 1: Normal operation
            print("\n[Phase 1] Normal operation (5 seconds)...")
            time.sleep(5)
            self.print_status()
            
            # Phase 2: Warning errors
            print("\n[Phase 2] Generating warning errors...")
            self.simulate_error('ConfigManager', ErrorSeverity.WARNING)
            time.sleep(2)
            self.simulate_error('PerformanceMonitor', ErrorSeverity.WARNING)
            time.sleep(3)
            self.print_status()
            
            # Phase 3: Critical error and recovery
            print("\n[Phase 3] Simulating critical error and recovery...")
            self.simulate_error('GameDetector', ErrorSeverity.CRITICAL)
            
            print("\nWaiting for auto-recovery (10 seconds)...")
            time.sleep(10)
            
            self.print_status()
            
            # Phase 4: Recovery history
            print("\n[Phase 4] Recovery History:")
            history = self.recovery_coordinator.get_recovery_history(limit=10)
            
            if history:
                print(f"\n  Recent recoveries ({len(history)}):")
                for record in history[:5]:
                    timestamp = time.strftime('%H:%M:%S', time.localtime(record['timestamp']))
                    print(f"  - [{timestamp}] {record['component']}: "
                          f"{record['strategy']} → {record['status']} "
                          f"({record['duration']:.2f}s)")
            else:
                print("  No recovery history yet")
            
            print("\n" + "="*60)
            print("DEMONSTRATION COMPLETE")
            print("="*60 + "\n")
            
        finally:
            self.stop()


def main():
    """Main function"""
    app = ExampleApplication()
    app.run_demo()
    
    print("\n✅ Example completed successfully!")
    print("\nTo use with GUI, run:")
    print("  python examples/monitoring_gui_example.py\n")


if __name__ == '__main__':
    main()
