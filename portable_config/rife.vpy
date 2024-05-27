# Loosely based on https://raw.githubusercontent.com/hooke007/MPV_lazy/50ebf2c6570aa2db45bb158c3da2cbc8e3fb013e/portable_config/vs/rife_2x.vpy

import sys
import vapoursynth as vs
from vsrife import rife

output_format = vs.YUV444P10 # YUV444P10 for full 10-bit color YUV420P8 for 8-bit color.
display_peak_brightness=800

# Disable RIFE when above threshold.
# Skip interpolation for >4K or >=60 Hz content due to performance (using this with 4K@60 requires a very beefy gpu to begin with)
disable_fps_threshold = 59
disable_width_threshold = 3840
disable_height_threshold = 2160

# Switch to half scale when above threshold.
half_scale_width_threshold = disable_width_threshold * 0.85
half_scale_height_threshold = disable_height_threshold * 0.85

# Uses nvidia RT cores. Will require an RTX GPU (not tested on anything other than RTX 4080)
# It also takes a million years to build an RT engine for each resolution and config, but it is much faster than regular.
gpu_tensorrt=True

gpu_streams=12 # This most likely wont work for everyone. 1 or 2 is probably a safe choice.
gpu_format=vs.RGBH #RGBH for best performance, RGBS for best quality (you likely wont notice a difference)
ensemble=True # Produces better results at a decently heavy cost.


core = vs.core
clip = video_in

def aprox(num, target, margin = 0.05):
    return target - margin <= num <= target + margin

if not (clip.width > disable_width_threshold or clip.height > disable_height_threshold or container_fps > disable_fps_threshold):
    w = clip.width
    h = clip.height

    sup  = core.mv.Super(clip, pel=1)
    vec = core.mv.Analyse(sup, blksize=16, isb=True)
    clip = core.mv.SCDetection(clip=clip, vectors=vec, thscd1=240, thscd2=130)

    uhd = clip.width >= half_scale_width_threshold and clip.height >= half_scale_height_threshold # Just turn on uhd mode for content that is aprox 4K

    # This could be replaced
    print(f"Determining optimal interpolation factors... [FPS: {container_fps}]")
    match container_fps:
        case container_fps if aprox(container_fps, 30):
            print(f"Using num=2 and den=1")
            target_num=2
            target_den=1
        case _: # Assuming most media played will be ~24 fps
            print(f"Using num=5 and den=2")
            target_num=5
            target_den=2

    # Required to round the clip fps or it will throw invalid fps.
    #clip = core.std.AssumeFPS(clip=clip, fpsnum=round(container_fps), fpsden=1)

    uhd = clip.width >= half_scale_width_threshold and clip.height >= half_scale_height_threshold
    scale = 0.5 if uhd else 1

    clip = core.resize.Lanczos(clip=clip, format=gpu_format, matrix_in_s='709')
    clip = rife(clip=clip, model="4.16.lite", factor_num=target_num, factor_den=target_den, device_index=0, num_streams=gpu_streams, ensemble=ensemble, sc=True, trt=gpu_tensorrt, trt_debug=False)
    clip = core.resize.Lanczos(clip=clip, format=output_format, matrix_s="2020ncl", nominal_luminance=display_peak_brightness)

clip.set_output()
