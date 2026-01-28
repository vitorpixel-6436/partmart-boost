#!/usr/bin/env python3
"""Advanced Frame Generation

Version: 0.3.5d_package3.4d

Advanced frame generation features for PartMart Boost.

Components:
- generator: Advanced frame generator
- optical_flow: Optical flow computation
- depth: Depth map estimation
- blending: Advanced blending

Example:
    >>> from framegen.advanced import AdvancedFrameGenerator
    >>> 
    >>> generator = AdvancedFrameGenerator()
    >>> generator.set_interpolation_factor(4)
    >>> 
    >>> # Generate multiple frames
    >>> frames = generator.generate_multi_frame(frame1, frame2)
"""

from .generator import AdvancedFrameGenerator
from .optical_flow import OpticalFlowEngine, FlowMethod
from .depth import DepthEstimator

__version__ = "0.3.5d_package3.4d"
__all__ = [
    'AdvancedFrameGenerator',
    'OpticalFlowEngine',
    'FlowMethod',
    'DepthEstimator',
]
