# MPV RIFE

Simple PowerShell installer and configuration files for MPV Player with [vs-RIFE](https://github.com/HolyWu/vs-rife) interpolation and [uosc interface](https://github.com/tomasklaen/uosc).

## Requirements

- Powershell 7 or newer.

## Installation

To install for Windows, it's as simple as the steps below.

For Linux, you would first need to install PowerShell to run the installer. Afterwards you will have to modify the paths in the config to match your installation.

>**NOTE:** The only tested installation path is ``C:\Program Files\mpv``, other paths will require you to modify the config.

1. Clone the repo
2. Run the script.
3. Enjoy!

The provided .gitignore file will ignore all other files by default, so you can pull new changes easily if needed.

> **NOTE:**
> With TensorRT enabled, the first launch of a media file with specific resolution and specific RIFE config will take a million years, but it will launch eventually!

## Configuration (recommended)

It's recommended that you edit the **mpv.conf** and **rife.vpy** files in **portable_config/** to match your preferences, especially the settings related to display colorspaces and HDR.

## Features

- RIFE interpolation enabled by default with TensorRT.
- UOSC interface.
- Autocrop video to fill your whole display with Shift+C.
- If you stumble across media that for some reason refuses to be played with RIFE, you can disable it with CTRL+\_ (this is CTRL+SHIFT+- on my nordic keyboard)
