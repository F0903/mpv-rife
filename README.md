# MPV Enhanced

A simple set of configuration files and scripts that greatly enhances the default MPV experience. Installation is dead simple with a PowerShell installer script that sets everything up for you with minimal configuration needed.

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
> With TensorRT enabled, the first initialization of RIFE with a specific resolution and RIFE config will take a while, but it will play eventually!

## Configuration (recommended)

It's recommended that you edit the **mpv.conf** and **rife.vpy** files in **portable_config/** to match your preferences, especially the settings related to display colorspaces and HDR.

## Features

- [vs-RIFE](https://github.com/HolyWu/vs-rife) interpolation that can be activated with ``CTRL+SHIFT+R``.
- [uosc](https://github.com/tomasklaen/uosc) interface.
- Autocrop video to fill your whole display with ``Shift+C``.
