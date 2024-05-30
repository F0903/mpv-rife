# These will need updating over time
$VapourSynthScriptUrl = "https://github.com/vapoursynth/vapoursynth/releases/download/R68/Install-Portable-VapourSynth-R68.ps1"
$PyTorchTensorRTUrl = "https://github.com/HolyWu/vs-rife/releases/download/v5.0.0/torch_tensorrt-2.4.0.dev20240518+cu121-cp312-cp312-win_amd64.whl"

function Download ($filename, $link) {
    Write-Host "Downloading" $filename -ForegroundColor Green
    Invoke-WebRequest -UserAgent "Mozilla/5.0 (Windows NT; Windows NT 6.1; en-US) Gecko/20100401 Firefox/4.0" -Uri $link -OutFile $filename
}

function Get-VS {
    # This script does the majority of the heavy lifting for us, including downloading 7zip and python.
    $VSScriptDest = "install_vs.ps1"
    Write-Host "Running VapourSynth script..."
    Download $VSScriptDest $VapourSynthScriptUrl
    & "./$VSScriptDest" -Unattended -TargetFolder "./"
    Write-Host "Installing VapourSynth plugins..."
    & "./python" vsrepo.py update
    & "./python" vsrepo.py install mv
    & "./python" vsrepo.py install ffms2
}

# Heavily modified version of the function from shinchiro's MPV bootstrap script. (found on the official sourceforge mirror)
function Get-Mpv {
    $rss_link = "https://sourceforge.net/projects/mpv-player-windows/rss?path=/64bit-v3"

    Write-Host "Fetching RSS feed for mpv" -ForegroundColor Green
    $result = [xml](New-Object System.Net.WebClient).DownloadString($rss_link)
    $latest = $result.rss.channel.item.link[0]
    $tempname = $latest.split("/")[-2]
    $filename = [System.Uri]::UnescapeDataString($tempname)
    $download_link = "https://deac-fra.dl.sourceforge.net/project/mpv-player-windows/64bit-v3/" + $filename + "?viasf=1"

    if ($filename -is [array]) {
        $filename = $filename[0]
        $download_link = $download_link[0]
    }

    $retcode = 1
    $tries = 0
    while ($True) {
        Download $filename $download_link
        ./7z.exe -y x $filename
        $retcode = $LastExitCode
        if ($retcode -eq 0) {
            break
        }
        if ($tries -ge 5) {
            throw "Could not download and extract MPV archive!"
        }
        $tries++
        Start-Sleep -Seconds 15
    }
}

function Get-VSRife {
    Write-Host "Installing PyTorch..."
    & "./python.exe" -m pip install --pre torch torchvision torchaudio --index-url "https://download.pytorch.org/whl/nightly/cu121"

    Write-Host "Installing TensorRT..."
    & "./python.exe" -m pip install tensorrt==10.0.1 tensorrt-cu12_bindings==10.0.1 tensorrt-cu12_libs==10.0.1 --extra-index-url "https://pypi.nvidia.com"

    Write-Host "Installing Torch-TensorRT..."
    $PyTorchFilename = $PyTorchTensorRTUrl.Split("/")[-1]
    Download $PyTorchFilename $PyTorchTensorRTUrl
    & "./python.exe" -m pip install $PyTorchFilename

    Write-Host "Installing vs-rife..."
    & "./python.exe" -m pip install -U vsrife
    & "./python.exe" -m vsrife
}

Get-VS
Get-Mpv
Get-VSRife

Write-Host
Write-Host "All Done!" $filename -ForegroundColor White -BackgroundColor Green