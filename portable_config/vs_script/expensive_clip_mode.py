from enum import Enum, auto


class ExpensiveClipMode(Enum):
    DOWNSCALE = auto()  # Downscale the clip to downscale_res.
    SKIP = auto()  # Don't interpolate the clip.
    NORMAL = auto()  # Interpolate the clip normally.