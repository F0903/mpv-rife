# Loosely based on https://raw.githubusercontent.com/hooke007/MPV_lazy/50ebf2c6570aa2db45bb158c3da2cbc8e3fb013e/portable_config/vs/rife_2x.vpy

from fractions import Fraction
from enum import Enum, auto
import vapoursynth as vs
from vsrife import rife
import sys
import os

# Add the portable_config directory to Python path to allow importing from vs_script
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from vs_script.target_fps_mode import TargetFpsMode
except ImportError as e:
    print(f"Failed to import TargetFpsMode: {e}")
    raise


class ExpensiveClipMode(Enum):
    DOWNSCALE = auto()  # Downscale the clip to downscale_res.
    SKIP = auto()  # Don't interpolate the clip.
    NORMAL = auto()  # Interpolate the clip normally.


rife_model = (
    "4.26"  # The RIFE model to use. Recommended ones are 4.26, 4.25 or 4.25.lite
)
scale = 1  # Interpolation scale.


# Target FPS mode. Can be TargetFpsMode.fixed_fps(*target_fps*) or TargetFpsMode.fixed_multiplier(*multiplier*)
target_mode = TargetFpsMode.fixed_multiplier(2)
disable_fps_threshold = 60  # Disable when source media is above threshold.

# You can change these to better match your display or source media.
output_format = vs.YUV420P10
output_colorspace = vs.MATRIX_BT2020_NCL
output_transfer = vs.TRANSFER_BT2020_10
output_primaries = vs.PRIMARIES_BT2020


# Resolution threshold for what determines if a clip is "expensive".
expensive_res_threshold = (1920, 1080)

# How do we handle expensive clips?
expensive_clip_handling = ExpensiveClipMode.DOWNSCALE

# Resolution to downscale to if expensive_clip_handling is "downscale".
downscale_res = (1920, 1080)

# Uses Nvidia TensorRT framework which is faster.
# It also takes a million years to build an RT engine for each resolution and config, but it is much faster than regular.
tensorrt = True
tensorrt_debug = False  # Enable for TensorRT debug logging.
tensorrt_optimization = 3  # 0 is min - 5 is max. This will increase the time it takes to build the RT engine.
ensemble = False  # Produces better results at a decently heavy cost. NOTE: NOT SUPPORTED BY ALL MODELS

# Dynamic shapes allows TensorRT to build a single engine for multiple resolutions.
# Meaning that you only have to compile the engine once, and it will work for all resolutions within the min-max range.
# The downside is worse performance and memory usage than static shapes.
# You should set opt_shape to the resolution you will be using most of the time.
tensorrt_static_shape = False

# Min size of dynamic shape
tensorrt_min_shape = [128, 128]

# Optimized size of dynamic shape.
tensorrt_opt_shape = [1920, 1080]

# Max size of dynamic shape.
tensorrt_max_shape = [
    expensive_res_threshold[0],
    expensive_res_threshold[1],
]


gpu_index = 0  # Which GPU to use.
gpu_format = vs.RGBH  # RGBH is faster, RGBS is more accurate


log =  None #open("./rife_log.txt", mode="w")  # Set to None for no log, or to an output stream to a log file.


core = vs.core
clip = video_in

def print_log(*values: object):
    if not log:
        return
    print(*values, file=log)


# Main interpolation logic
if container_fps < disable_fps_threshold:
    print_log(
        f"Containers FPS '{container_fps}' is below {disable_fps_threshold}. Interpolating..."
    )

    set_width = None
    set_height = None

    if (
        clip.width >= expensive_res_threshold[0]
        and clip.height >= expensive_res_threshold[1]
    ):
        print_log(f"Clip is too expensive. Downscaling to {downscale_res}...")
        set_width = downscale_res[0]
        set_height = downscale_res[1]

    sup = core.mv.Super(clip, pel=1)
    vec = core.mv.Analyse(sup, blksize=8, isb=True)
    clip = core.mv.SCDetection(clip=clip, vectors=vec, thscd1=240, thscd2=130)

    container_fps_frac = Fraction(container_fps).limit_denominator(100)
    print_log(f"Container FPS fraction: {container_fps_frac.numerator}/{container_fps_frac.denominator}={float(container_fps_frac)}")

    target_fps_frac = target_mode.get_fps_fraction(container_fps_frac).limit_denominator(100)
    [target_num, target_den] = target_fps_frac.as_integer_ratio()
    print_log(f"Target FPS fraction: {target_fps_frac.numerator}/{target_fps_frac.denominator}={float(target_fps_frac)}")

    dest_fps_frac = container_fps_frac * target_fps_frac
    dest_fps_frac = dest_fps_frac.limit_denominator(100)
    [dest_num, dest_den] = dest_fps_frac.as_integer_ratio()
    print_log(f"Destination FPS fraction: {dest_fps_frac.numerator}/{dest_fps_frac.denominator}={float(dest_fps_frac)}")

    print_log(
        f"Using settings:\nscale: {scale},ensemble={ensemble},gpu_index={gpu_index},gpu_tensorrt={tensorrt}"
    )

    original_size = (clip.width, clip.height)
    original_format = clip.format
    print_log(f"Original size: {original_size}")
    print_log(f"Original format: {original_format}")

    # Change format for RIFE
    clip = core.resize.Lanczos(
        clip=clip,
        format=gpu_format,
        width=set_width,
        height=set_height,
        matrix_in=output_colorspace,
        transfer_in=output_transfer,
        primaries_in=output_primaries,
    )
    clip = rife(
        clip=clip,
        model=rife_model,
        factor_num=target_num,
        factor_den=target_den,
        device_index=gpu_index,
        scale=scale,
        ensemble=ensemble,
        sc=False,
        trt=tensorrt,
        trt_optimization_level=tensorrt_optimization,
        trt_static_shape=tensorrt_static_shape,
        trt_min_shape=tensorrt_min_shape,
        trt_opt_shape=tensorrt_opt_shape,
        trt_max_shape=tensorrt_max_shape,
        trt_debug=tensorrt_debug,
        auto_download=True,  # Downloads the model on first run.
    )
    clip = core.resize.Lanczos(
        clip,
        format=output_format,
        matrix=output_colorspace,
        transfer=output_transfer,
        primaries=output_primaries,
    )

    clip = core.std.AssumeFPS(
        clip=clip,
        fpsnum=dest_num,
        fpsden=dest_den,
    )
    print_log(f"Final clip: {clip}")

else:
    print_log("Video is above FPS threshold. Ignoring...")

clip.set_output()
