# Loosely based on https://raw.githubusercontent.com/hooke007/MPV_lazy/50ebf2c6570aa2db45bb158c3da2cbc8e3fb013e/portable_config/vs/rife_2x.vpy

from fractions import Fraction
from enum import Enum, auto
import vapoursynth as vs
from vsrife import rife

class ExpensiveClipMode(Enum):
    DOWNSCALE = auto()  # Downscale the clip to downscale_res.
    SKIP = auto()       # Don't interpolate the clip.
    NORMAL = auto()     # Interpolate the clip normally.


rife_model = "4.26"  # The RIFE model to use. Recommended ones are 4.26 or 4.25.lite
scale = 1  # Interpolation scale.
disable_fps_threshold = 60 # Disable when above threshold.
target_fps = 60
target_fps_frac = Fraction(target_fps).limit_denominator(1000)

# You can change these to better match your display or source media.
output_format = vs.YUV420P10
output_colorspace = vs.MATRIX_BT2020_NCL
output_transfer = vs.TRANSFER_BT2020_10
output_primaries = vs.PRIMARIES_BT2020

expensive_res_threshold = (
    2560,
    1440,
)  # Resolution threshold for what determines if a clip is "expensive".
expensive_clip_handling = ExpensiveClipMode.DOWNSCALE # How do we handle expensive clips?
downscale_res = (1920, 1080)  # Resolution to downscale to if expensive_clip_handling is "downscale".

# Uses Nvidia TensorRT framework which is faster.
# It also takes a million years to build an RT engine for each resolution and config, but it is much faster than regular.
tensorrt = True
tensorrt_debug = False  # Enable for TensorRT debug logging.
tensorrt_optimization = 3  # 0 is min - 5 is max. This will increase the time it takes to build the RT engine.
ensemble = False  # Produces better results at a decently heavy cost. NOTE: NOT SUPPORTED BY ALL MODELS

gpu_index = 0  # Which GPU to use.
gpu_format = vs.RGBS  # RGBH is faster, RGBS is more accurate

log = open(
    "./rife_log.txt", mode="w"
)  # Set to None for no log, or to an output stream to a log file.


core = vs.core
clip = video_in

def print_log(*values: object):
    if not log:
        return
    print(*values, file=log)

if container_fps < disable_fps_threshold:
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

    target_ratio_frac = target_fps_frac / Fraction(container_fps).limit_denominator(1000)

    print_log(
        f"Target frac={target_ratio_frac.numerator}/{target_ratio_frac.denominator}={target_ratio_frac.numerator/target_ratio_frac.denominator}"
    )

    print_log(
        f"Using settings:\nscale={scale},ensemble={ensemble},gpu_index={gpu_index},gpu_tensorrt={tensorrt}"
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
        factor_num=target_ratio_frac.numerator,
        factor_den=target_ratio_frac.denominator,
        device_index=gpu_index,
        scale=scale,
        ensemble=ensemble,
        sc=False,
        trt=tensorrt,
        trt_optimization_level=tensorrt_optimization,
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

    clip = core.std.AssumeFPS(clip=clip, fpsnum=target_fps_frac.numerator, fpsden=target_fps_frac.denominator)
    print_log(f"Final clip: {clip}")

else:
    print_log("Video is above FPS threshold. Ignoring...")

clip.set_output()
