# Loosely based on https://raw.githubusercontent.com/hooke007/MPV_lazy/50ebf2c6570aa2db45bb158c3da2cbc8e3fb013e/portable_config/vs/rife_2x.vpy

from fractions import Fraction
import vapoursynth as vs
from vsrife import rife

output_format = (
    vs.YUV444P10
)  # YUV444P10 (or YUV420P10) for full 10-bit color YUV420P8 for 8-bit color.
output_colorspace = "2020ncl"
display_peak_brightness = 800  # Your displays peak HDR brightness.

# Disable when above threshold.
# Skip interpolation of >=60 Hz content.
disable_fps_threshold = 60

downscale_res_threshold = (2560, 1440)
downscale_res = (1920, 1080)

rife_model = "4.17"  # The RIFE model to use. Recommended is 4.17 or 4.16-lite
scale = 1  # Interpolation scale.

# Uses Nvidia TensorRT framework which is faster.
# It also takes a million years to build an RT engine for each resolution and config, but it is much faster than regular.
gpu_tensorrt = True
tensorrt_debug = False  # Enable for TensorRT debug logging.
tensorrt_optimization = 0  # 0 is min - 5 is max. This will increase the time it takes to build the RT engine.

gpu_streams = 2  # This settings very quickly explodes your VRAM usage.
gpu_format = vs.RGBH  # RGBH is faster, RGBS is more accurate
ensemble = True  # Produces better results at a decently heavy cost.


core = vs.core
clip = video_in

if container_fps < disable_fps_threshold:
    expensive = (
        clip.width >= downscale_res_threshold[0]
        and clip.height >= downscale_res_threshold[1]
    )

    if expensive:
        print("Clip is too expensive. Downscaling...")
        clip = core.resize.Lanczos(
            clip=clip, width=downscale_res[0], height=downscale_res[1]
        )

    sup = core.mv.Super(clip, pel=1)
    vec = core.mv.Analyse(sup, blksize=8, isb=True)
    clip = core.mv.SCDetection(clip=clip, vectors=vec, thscd1=240, thscd2=130)

    target_fps = 60
    target_frac = Fraction(target_fps / container_fps).limit_denominator(100)

    print(
        f"Target frac={target_frac.numerator}/{target_frac.denominator}={target_frac.numerator/target_frac.denominator}"
    )

    print(
        f"Using settings:\ngpu_streams={gpu_streams},gpu_format={gpu_format},scale={scale},ensemble={ensemble},gpu_tensorrt={gpu_tensorrt}"
    )

    clip = core.resize.Lanczos(clip=clip, format=gpu_format, matrix_in_s="709")
    clip = rife(
        clip=clip,
        model=rife_model,
        factor_num=target_frac.numerator,
        factor_den=target_frac.denominator,
        device_index=0,
        num_streams=gpu_streams,
        scale=scale,
        ensemble=ensemble,
        sc=True,
        trt=gpu_tensorrt,
        trt_optimization_level=tensorrt_optimization,
        trt_debug=tensorrt_debug,
    )
    clip = core.resize.Lanczos(
        clip=clip,
        format=output_format,
        matrix_s=output_colorspace,
        nominal_luminance=display_peak_brightness,
    )

else:
    print("Video is above FPS threshold. Ignoring...")

clip.set_output()
