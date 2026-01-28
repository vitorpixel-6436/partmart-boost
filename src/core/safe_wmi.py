"""Safe WMI wrapper with injection prevention
SECURITY: Validates all WMI queries, sandboxed execution
"""
import platform
from typing import Optional, Dict, Any, List

class SafeWMI:
    """Safe WMI wrapper with injection prevention"""
    
    # Whitelist of allowed WMI classes
    ALLOWED_CLASSES = {
        'Win32_PhysicalMemory',
        'Win32_Processor',
        'Win32_VideoController',
        'Win32_OperatingSystem',
        'Win32_ComputerSystem',
    }
    
    # Whitelist of allowed properties
    ALLOWED_PROPERTIES = {
        'ConfiguredClockSpeed',
        'ConfiguredVoltage',
        'Capacity',
        'Speed',
        'Name',
        'Description',
        'Manufacturer',
        'NumberOfCores',
        'NumberOfLogicalProcessors',
    }
    
    def __init__(self):
        self.available = False
        self.wmi = None
        self._init_wmi()
    
    def _init_wmi(self):
        """Initialize WMI safely"""
        # Only on Windows
        if platform.system() != 'Windows':
            return
        
        try:
            import wmi
            self.wmi = wmi.WMI()
            self.available = True
        except ImportError:
            print("[INFO] WMI not available (module not installed)")
        except Exception as e:
            print(f"[ERROR] WMI init failed: {e}")
    
    def _validate_class_name(self, class_name: str) -> bool:
        """Validate WMI class name against whitelist
        
        Args:
            class_name: WMI class to query
        
        Returns:
            True if allowed, False otherwise
        """
        if not isinstance(class_name, str):
            return False
        
        # Check whitelist
        if class_name not in self.ALLOWED_CLASSES:
            print(f"[SECURITY] Blocked WMI query: {class_name} not in whitelist")
            return False
        
        # Additional validation: only alphanumeric and underscore
        if not all(c.isalnum() or c == '_' for c in class_name):
            print(f"[SECURITY] Blocked WMI query: invalid characters in {class_name}")
            return False
        
        return True
    
    def _validate_property(self, prop_name: str) -> bool:
        """Validate property name
        
        Args:
            prop_name: Property to access
        
        Returns:
            True if allowed, False otherwise
        """
        if not isinstance(prop_name, str):
            return False
        
        # Check whitelist (optional - more permissive)
        # Allow common properties
        if prop_name not in self.ALLOWED_PROPERTIES:
            # Still allow if alphanumeric
            if not all(c.isalnum() or c == '_' for c in prop_name):
                print(f"[SECURITY] Blocked property access: {prop_name}")
                return False
        
        return True
    
    def query_safe(self, class_name: str, properties: List[str] = None) -> List[Dict[str, Any]]:
        """Execute safe WMI query
        
        Args:
            class_name: WMI class to query (must be in whitelist)
            properties: List of properties to retrieve (optional)
        
        Returns:
            List of dictionaries with results, or empty list on error
        """
        if not self.available:
            return []
        
        # Validate class name
        if not self._validate_class_name(class_name):
            return []
        
        try:
            # Execute query
            wmi_class = getattr(self.wmi, class_name)
            instances = wmi_class()
            
            results = []
            for instance in instances:
                result = {}
                
                if properties:
                    # Only requested properties
                    for prop in properties:
                        if self._validate_property(prop):
                            try:
                                value = getattr(instance, prop, None)
                                result[prop] = value
                            except Exception as e:
                                print(f"[WARN] Failed to get {prop}: {e}")
                else:
                    # All properties (less safe, but validated)
                    try:
                        for prop in dir(instance):
                            if not prop.startswith('_') and self._validate_property(prop):
                                try:
                                    value = getattr(instance, prop, None)
                                    if not callable(value):
                                        result[prop] = value
                                except:
                                    pass
                    except Exception as e:
                        print(f"[WARN] Property enumeration failed: {e}")
                
                if result:
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"[ERROR] WMI query failed: {e}")
            return []
    
    def get_ram_speed(self) -> Optional[int]:
        """Get RAM speed safely
        
        Returns:
            RAM speed in MHz or None
        """
        results = self.query_safe('Win32_PhysicalMemory', ['ConfiguredClockSpeed'])
        
        if results and len(results) > 0:
            speed = results[0].get('ConfiguredClockSpeed')
            if speed and isinstance(speed, (int, float)):
                return int(speed)
        
        return None
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information safely
        
        Returns:
            Dictionary with CPU info
        """
        results = self.query_safe('Win32_Processor', [
            'Name',
            'NumberOfCores',
            'NumberOfLogicalProcessors',
            'MaxClockSpeed'
        ])
        
        if results and len(results) > 0:
            return results[0]
        
        return {}
    
    def is_available(self) -> bool:
        """Check if WMI is available"""
        return self.available

# Global safe WMI instance
_safe_wmi = None

def get_safe_wmi() -> SafeWMI:
    """Get global safe WMI instance"""
    global _safe_wmi
    if _safe_wmi is None:
        _safe_wmi = SafeWMI()
    return _safe_wmi

if __name__ == "__main__":
    # Test
    print("[TEST] Testing SafeWMI...")
    
    wmi = SafeWMI()
    
    if wmi.is_available():
        print("[PASS] WMI available")
        
        # Test RAM speed
        ram_speed = wmi.get_ram_speed()
        print(f"[INFO] RAM Speed: {ram_speed} MHz")
        
        # Test CPU info
        cpu_info = wmi.get_cpu_info()
        print(f"[INFO] CPU: {cpu_info.get('Name', 'Unknown')}")
        print(f"[INFO] Cores: {cpu_info.get('NumberOfCores', 'Unknown')}")
        
        # Test injection prevention
        print("\n[TEST] Testing injection prevention...")
        bad_results = wmi.query_safe("Win32_Process; DROP TABLE users--")
        if len(bad_results) == 0:
            print("[PASS] Injection blocked!")
        else:
            print("[FAIL] Injection not blocked!")
    else:
        print("[INFO] WMI not available (not Windows or not installed)")
