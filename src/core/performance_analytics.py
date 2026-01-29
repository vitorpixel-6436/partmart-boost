#!/usr/bin/env python3
"""Performance Analytics Engine

Version: 0.3.5g (package 3.9a, stage 7.5/7.7)

Package 3.9a Stage 7.5: Advanced analytics and insights.

Features:
- Bottleneck detection
- Performance scoring
- Trend analysis
- Recommendations
- Anomaly detection
"""
import statistics
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from performance_history import PerformanceHistory, PerformanceSnapshot
    HISTORY_AVAILABLE = True
except ImportError:
    HISTORY_AVAILABLE = False
    print("[PerformanceAnalytics] History module not available")


class BottleneckType(Enum):
    """Bottleneck types"""
    CPU = 'cpu'
    GPU = 'gpu'
    RAM = 'ram'
    THERMAL = 'thermal'
    NONE = 'none'


class BottleneckSeverity(Enum):
    """Bottleneck severity levels"""
    NONE = 'none'
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


@dataclass
class Bottleneck:
    """Bottleneck information
    
    Attributes:
        type: Bottleneck type
        severity: Severity level
        value: Current value
        threshold: Threshold value
        description: Human-readable description
    """
    type: BottleneckType
    severity: BottleneckSeverity
    value: float
    threshold: float
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type.value,
            'severity': self.severity.value,
            'value': self.value,
            'threshold': self.threshold,
            'description': self.description,
        }


@dataclass
class Recommendation:
    """Performance recommendation
    
    Attributes:
        category: Category ('optimization', 'hardware', 'settings')
        priority: Priority (1-10)
        title: Short title
        description: Detailed description
        expected_improvement: Expected improvement description
    """
    category: str
    priority: int
    title: str
    description: str
    expected_improvement: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'category': self.category,
            'priority': self.priority,
            'title': self.title,
            'description': self.description,
            'expected_improvement': self.expected_improvement,
        }


@dataclass
class AnalyticsReport:
    """Complete analytics report
    
    Attributes:
        score: Overall performance score (0-100)
        bottleneck: Primary bottleneck
        recommendations: List of recommendations
        trends: Trend information
        efficiency: Efficiency rating (0-100)
    """
    score: float
    bottleneck: Bottleneck
    recommendations: List[Recommendation]
    trends: Dict[str, str]
    efficiency: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'score': self.score,
            'bottleneck': self.bottleneck.to_dict(),
            'recommendations': [r.to_dict() for r in self.recommendations],
            'trends': self.trends,
            'efficiency': self.efficiency,
        }


class PerformanceAnalytics:
    """Performance analytics engine
    
    v0.3.5g (package 3.9a, stage 7.5/7.7)
    
    Features:
    - Bottleneck detection
    - Performance scoring
    - Recommendations
    - Trend analysis
    
    Usage:
        >>> analytics = PerformanceAnalytics(history)
        >>> report = analytics.analyze()
        >>> print(f"Score: {report.score}")
        >>> print(f"Bottleneck: {report.bottleneck.type.value}")
    """
    
    def __init__(self, history: Optional['PerformanceHistory'] = None):
        """Initialize analytics
        
        Args:
            history: PerformanceHistory instance (optional)
        """
        self._history = history
        
        # Thresholds
        self._cpu_threshold = 85.0
        self._gpu_threshold = 90.0
        self._ram_threshold = 90.0
        self._temp_threshold = 85.0
        
        print("[PerformanceAnalytics] Initialized")
    
    def analyze(self, current_metrics: Optional[Dict[str, float]] = None) -> AnalyticsReport:
        """Perform complete analysis
        
        Args:
            current_metrics: Current metrics (optional, uses history if None)
        
        Returns:
            AnalyticsReport
        """
        # Get metrics
        if current_metrics is None and self._history:
            recent = self._history.get_recent(seconds=30)
            if recent:
                last = recent[-1]
                current_metrics = {
                    'cpu': last.cpu,
                    'gpu': last.gpu,
                    'ram': last.ram,
                    'fps': last.fps,
                    'gpu_temp': last.gpu_temp,
                }
            else:
                current_metrics = {}
        elif current_metrics is None:
            current_metrics = {}
        
        # Detect bottleneck
        bottleneck = self._detect_bottleneck(current_metrics)
        
        # Calculate score
        score = self._calculate_score(current_metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(current_metrics, bottleneck)
        
        # Analyze trends
        trends = self._analyze_trends()
        
        # Calculate efficiency
        efficiency = self._calculate_efficiency(current_metrics)
        
        return AnalyticsReport(
            score=score,
            bottleneck=bottleneck,
            recommendations=recommendations,
            trends=trends,
            efficiency=efficiency
        )
    
    def _detect_bottleneck(self, metrics: Dict[str, float]) -> Bottleneck:
        """Detect primary bottleneck
        
        Args:
            metrics: Current metrics
        
        Returns:
            Bottleneck information
        """
        cpu = metrics.get('cpu', 0)
        gpu = metrics.get('gpu', 0)
        ram = metrics.get('ram', 0)
        temp = metrics.get('gpu_temp', 0)
        
        # Check each component
        bottlenecks = []
        
        # CPU bottleneck
        if cpu > self._cpu_threshold:
            severity = self._calculate_severity(cpu, self._cpu_threshold)
            bottlenecks.append((BottleneckType.CPU, severity, cpu, self._cpu_threshold))
        
        # GPU bottleneck
        if gpu > self._gpu_threshold:
            severity = self._calculate_severity(gpu, self._gpu_threshold)
            bottlenecks.append((BottleneckType.GPU, severity, gpu, self._gpu_threshold))
        
        # RAM bottleneck
        if ram > self._ram_threshold:
            severity = self._calculate_severity(ram, self._ram_threshold)
            bottlenecks.append((BottleneckType.RAM, severity, ram, self._ram_threshold))
        
        # Thermal bottleneck
        if temp > self._temp_threshold:
            severity = self._calculate_severity(temp, self._temp_threshold)
            bottlenecks.append((BottleneckType.THERMAL, severity, temp, self._temp_threshold))
        
        # Return most severe
        if bottlenecks:
            # Sort by severity
            severity_order = {
                BottleneckSeverity.CRITICAL: 4,
                BottleneckSeverity.HIGH: 3,
                BottleneckSeverity.MEDIUM: 2,
                BottleneckSeverity.LOW: 1,
                BottleneckSeverity.NONE: 0,
            }
            bottlenecks.sort(key=lambda b: severity_order[b[1]], reverse=True)
            
            b_type, severity, value, threshold = bottlenecks[0]
            description = self._get_bottleneck_description(b_type, severity, value)
            
            return Bottleneck(
                type=b_type,
                severity=severity,
                value=value,
                threshold=threshold,
                description=description
            )
        
        # No bottleneck
        return Bottleneck(
            type=BottleneckType.NONE,
            severity=BottleneckSeverity.NONE,
            value=0.0,
            threshold=0.0,
            description="System performing optimally"
        )
    
    def _calculate_severity(self, value: float, threshold: float) -> BottleneckSeverity:
        """Calculate bottleneck severity
        
        Args:
            value: Current value
            threshold: Threshold value
        
        Returns:
            Severity level
        """
        if value < threshold:
            return BottleneckSeverity.NONE
        
        excess = value - threshold
        
        if excess >= 10:
            return BottleneckSeverity.CRITICAL
        elif excess >= 7:
            return BottleneckSeverity.HIGH
        elif excess >= 4:
            return BottleneckSeverity.MEDIUM
        else:
            return BottleneckSeverity.LOW
    
    def _get_bottleneck_description(self, b_type: BottleneckType,
                                    severity: BottleneckSeverity,
                                    value: float) -> str:
        """Get human-readable bottleneck description"""
        descriptions = {
            BottleneckType.CPU: f"CPU usage at {value:.0f}% - consider closing background apps",
            BottleneckType.GPU: f"GPU usage at {value:.0f}% - reduce graphics settings",
            BottleneckType.RAM: f"RAM usage at {value:.0f}% - close memory-intensive apps",
            BottleneckType.THERMAL: f"GPU temperature at {value:.0f}°C - improve cooling",
        }
        
        return descriptions.get(b_type, "No bottleneck detected")
    
    def _calculate_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall performance score
        
        Args:
            metrics: Current metrics
        
        Returns:
            Score (0-100)
        """
        cpu = metrics.get('cpu', 0)
        gpu = metrics.get('gpu', 0)
        ram = metrics.get('ram', 0)
        fps = metrics.get('fps', 0)
        
        # Component scores (inverse of usage)
        cpu_score = max(0, 100 - cpu)
        gpu_score = max(0, 100 - gpu)
        ram_score = max(0, 100 - ram)
        
        # FPS score (normalize to 0-100, assume 60fps = 100 score)
        fps_score = min(100, (fps / 60) * 100) if fps > 0 else 50
        
        # Weighted average
        score = (
            cpu_score * 0.25 +
            gpu_score * 0.30 +
            ram_score * 0.20 +
            fps_score * 0.25
        )
        
        return max(0, min(100, score))
    
    def _calculate_efficiency(self, metrics: Dict[str, float]) -> float:
        """Calculate system efficiency
        
        Args:
            metrics: Current metrics
        
        Returns:
            Efficiency (0-100)
        """
        cpu = metrics.get('cpu', 0)
        gpu = metrics.get('gpu', 0)
        fps = metrics.get('fps', 0)
        
        # Efficiency = FPS per unit of resource usage
        if cpu + gpu == 0:
            return 0.0
        
        resource_usage = (cpu + gpu) / 2
        efficiency = (fps / resource_usage) * 10 if resource_usage > 0 else 0
        
        return max(0, min(100, efficiency))
    
    def _generate_recommendations(self, metrics: Dict[str, float],
                                 bottleneck: Bottleneck) -> List[Recommendation]:
        """Generate performance recommendations
        
        Args:
            metrics: Current metrics
            bottleneck: Detected bottleneck
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Bottleneck-specific recommendations
        if bottleneck.type == BottleneckType.CPU:
            recommendations.append(Recommendation(
                category='optimization',
                priority=9,
                title='Close background applications',
                description='CPU usage is high. Close unnecessary browser tabs and background apps.',
                expected_improvement='5-15% CPU reduction'
            ))
            
            recommendations.append(Recommendation(
                category='settings',
                priority=7,
                title='Reduce CPU-intensive settings',
                description='Lower physics quality, view distance, or NPC count in games.',
                expected_improvement='10-20% CPU reduction'
            ))
        
        elif bottleneck.type == BottleneckType.GPU:
            recommendations.append(Recommendation(
                category='settings',
                priority=9,
                title='Lower graphics settings',
                description='Reduce resolution, texture quality, or anti-aliasing.',
                expected_improvement='15-30% FPS increase'
            ))
            
            recommendations.append(Recommendation(
                category='optimization',
                priority=6,
                title='Update graphics drivers',
                description='Ensure GPU drivers are up to date for optimal performance.',
                expected_improvement='5-10% FPS increase'
            ))
        
        elif bottleneck.type == BottleneckType.RAM:
            recommendations.append(Recommendation(
                category='optimization',
                priority=10,
                title='Free up memory',
                description='Close memory-intensive applications like browsers or development tools.',
                expected_improvement='Prevent stuttering'
            ))
            
            recommendations.append(Recommendation(
                category='hardware',
                priority=8,
                title='Consider RAM upgrade',
                description='Your system would benefit from additional RAM.',
                expected_improvement='Eliminate memory bottleneck'
            ))
        
        elif bottleneck.type == BottleneckType.THERMAL:
            recommendations.append(Recommendation(
                category='optimization',
                priority=10,
                title='Improve cooling',
                description='Clean dust from fans, improve case airflow, or lower ambient temperature.',
                expected_improvement='10-15°C reduction'
            ))
        
        # General recommendations
        fps = metrics.get('fps', 0)
        if fps > 0 and fps < 60:
            recommendations.append(Recommendation(
                category='settings',
                priority=8,
                title='Enable performance mode',
                description='Use performance-focused graphics presets instead of quality presets.',
                expected_improvement='20-40% FPS increase'
            ))
        
        # Sort by priority
        recommendations.sort(key=lambda r: r.priority, reverse=True)
        
        return recommendations[:5]  # Return top 5
    
    def _analyze_trends(self) -> Dict[str, str]:
        """Analyze performance trends
        
        Returns:
            Dictionary of metric trends
        """
        if not self._history:
            return {}
        
        trends = {}
        
        for metric in ['cpu', 'gpu', 'ram', 'fps']:
            stats = self._history.get_stats(metric)
            if stats:
                trends[metric] = stats.trend
        
        return trends


# Testing
if __name__ == '__main__' and HISTORY_AVAILABLE:
    print("="*60)
    print("PerformanceAnalytics Test")
    print("="*60)
    print()
    
    # Create history with test data
    history = PerformanceHistory(max_samples=100)
    
    # Simulate high CPU usage
    for i in range(20):
        history.add_snapshot(
            cpu=90,  # High CPU
            gpu=60,
            ram=70,
            fps=45,  # Low FPS
            gpu_temp=75,
            score=60
        )
    
    # Create analytics
    analytics = PerformanceAnalytics(history)
    
    # Analyze
    report = analytics.analyze()
    
    print(f"Performance Score: {report.score:.1f}/100")
    print(f"Efficiency: {report.efficiency:.1f}/100")
    print()
    
    print(f"Bottleneck: {report.bottleneck.type.value} ({report.bottleneck.severity.value})")
    print(f"  {report.bottleneck.description}")
    print()
    
    print("Recommendations:")
    for i, rec in enumerate(report.recommendations, 1):
        print(f"  {i}. [{rec.priority}/10] {rec.title}")
        print(f"     {rec.description}")
        print(f"     Expected: {rec.expected_improvement}")
    
    print()
    print("✅ Test completed!")
