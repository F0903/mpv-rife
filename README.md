# MPV RIFE

Simple installer for MPV Player with [vs-RIFE](https://github.com/HolyWu/vs-rife) TensorRT interpolation, MVTools and [UOSC interface](https://github.com/tomasklaen/uosc).

## Requirements

- Powershell 7 or newer.

## Installation

1. Clone the repo (recommended to do this in non-admin directory).
2. Run the script.
3. Enjoy!

**NOTE:**
With TensorRT enabled, the first launch of a media file with specific resolution and specific RIFE config will take a million years, but it will launch eventually!

## Configuration

It's recommended that you edit the mpv.conf file in portable_config to match your display.  
If your GPU struggles to run RIFE, you can try to edit to global variables provided in /portable_config/rife.vpy

## Features

- RIFE interpolation enabled by default with TensorRT.
- UOSC interface.
- Autocrop video to fill your whole display with Shift+C.
- If you stumble across media that for some reason refuses to be played with RIFE, you can disable it with CTRL+\_ (this is CTRL+SHIFT+- on my nordic keyboard)
