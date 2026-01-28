class PartMartColors:
    """PartMart × Steam Fusion color palette"""

    # Primary (PartMart Dragon Red)
    PRIMARY = "#E63946"          # Red accent
    PRIMARY_HOVER = "#D62828"    # Hover state
    PRIMARY_DARK = "#C11F28"     # Pressed state

    # Background (Steam Dark Theme)
    BG_DARK = "#1B2838"          # Main background (Steam-like)
    BG_MEDIUM = "#2A475E"        # Cards / panels
    BG_LIGHT = "#66C0F4"        # Highlights

    # Text
    TEXT_PRIMARY = "#FFFFFF"     # Primary text
    TEXT_SECONDARY = "#B8B6B4"   # Secondary text
    TEXT_MUTED = "#8B8B8B"       # Muted text

    # Status
    SUCCESS = "#5DA130"          # Success
    WARNING = "#F79F1A"          # Warning
    ERROR = "#D32F2F"            # Error
    INFO = "#66C0F4"             # Info

    # Gradients (for QSS usage via string concatenation)
    GRADIENT_HEADER = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        "stop:0 #E63946, stop:1 #C11F28)"
    )
    GRADIENT_BUTTON = (
        "qlineargradient(x1:0, y1:0, x2:0, y2:1, "
        "stop:0 #E63946, stop:1 #C11F28)"
    )
