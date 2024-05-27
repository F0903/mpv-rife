# Loosely based on https://raw.githubusercontent.com/hooke007/MPV_lazy/50ebf2c6570aa2db45bb158c3da2cbc8e3fb013e/portable_config/vs/rife_2x.vpy

from fractions import Fraction
import vapoursynth as vs
from vsrife import rife

output_format = vs.YUV444P10 # YUV444P10 (or YUV420P10) for full 10-bit color YUV420P8 for 8-bit color.
display_peak_brightness=800

# Disable RIFE when above threshold.
# Skip interpolation for >4K or >=60 Hz content due to performance (using this with 4K@60 requires a very beefy gpu to begin with)
disable_fps_threshold = 59
disable_width_threshold = 3840
disable_height_threshold = 2160

# Switch to half scale when above threshold.
reduced_scale_width_threshold = disable_width_threshold * 0.85
reduced_scale_height_threshold = disable_height_threshold * 0.85
reduced_scale = 0.5

# Uses nvidia RT cores. Will require an RTX GPU (not tested on anything other than RTX 4080)
# It also takes a million years to build an RT engine for each resolution and config, but it is much faster than regular.
gpu_tensorrt=True
tensorrt_debug=True # Enable for TensorRT debug logging.

gpu_streams=4 # This settings very quickly explodes your VRAM usage.
gpu_format=vs.RGBH #RGBH for best performance, RGBS for best quality (you likely wont notice a difference)
ensemble=True # Produces better results at a decently heavy cost.


core = vs.core
clip = video_in

def aprox(num, target, margin = 0.05):
    return target - margin <= num <= target + margin

if not (clip.width > disable_width_threshold or clip.height > disable_height_threshold or container_fps > disable_fps_threshold):
    sup  = core.mv.Super(clip, pel=1)
    vec = core.mv.Analyse(sup, blksize=8, isb=True)
    clip = core.mv.SCDetection(clip=clip, vectors=vec, thscd1=240, thscd2=130)

    target_fps = 60
    target_frac = Fraction(target_fps / container_fps).limit_denominator(100)

    print(f"Target frac={target_frac.numerator}/{target_frac.denominator}={target_frac.numerator/target_frac.denominator}")

    uhd = clip.width >= reduced_scale_width_threshold and clip.height >= reduced_scale_height_threshold

    if uhd:
        print("Clip is UHD. Adjusting settings...")

    scale = reduced_scale if uhd else 1
    ensemble = False if uhd else ensemble
    print(f"Expensive settings:\ngpu_streams={gpu_streams},scale={scale},ensemble={ensemble},gpu_tensorrt={gpu_tensorrt}")

    clip = core.resize.Lanczos(clip=clip, format=gpu_format, matrix_in_s='709')
    clip = rife(clip=clip, model="4.16.lite", factor_num=target_frac.numerator, factor_den=target_frac.denominator, device_index=0, num_streams=gpu_streams, scale=scale, ensemble=ensemble, sc=True, trt=gpu_tensorrt, trt_debug=tensorrt_debug)
    clip = core.resize.Lanczos(clip=clip, format=output_format, matrix_s="2020ncl", nominal_luminance=display_peak_brightness)

    new_fps = Fraction(container_fps * target_frac).limit_denominator(100)
    print(f"New fps_frac={new_fps.numerator}/{new_fps.denominator}={new_fps.numerator/new_fps.denominator}")
    clip = core.std.AssumeFPS(clip=clip, fpsnum=new_fps.numerator, fpsden=new_fps.denominator)

else:
    print("Video is too expensive to interpolate. Ignoring...")

clip.set_output()
