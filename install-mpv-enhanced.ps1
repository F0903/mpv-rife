# These will need updating over time
$VapourSynthScriptUrl = "https://github.com/vapoursynth/vapoursynth/releases/download/R70/Install-Portable-VapourSynth-R70.ps1"
$PytorchUrl = "https://download.pytorch.org/whl/cu126"

$MpvRssUrl = "https://sourceforge.net/projects/mpv-player-windows/rss?path=/64bit-v3"
$MpvDownloadBaseUrl = "https://deac-fra.dl.sourceforge.net/project/mpv-player-windows/64bit-v3/"

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
    & "./python" vsrepo.py install com.vapoursynth.misc
}

# Heavily modified version of the function from shinchiro's MPV bootstrap script. (found on the official sourceforge mirror)
function Get-Mpv {
    Write-Host "Fetching RSS feed for mpv" -ForegroundColor Green
    $result = [xml](New-Object System.Net.WebClient).DownloadString($MpvRssUrl)
    $latest = $result.rss.channel.item.link[0]
    $tempname = $latest.split("/")[-2]
    $filename = [System.Uri]::UnescapeDataString($tempname)
    $download_link = $MpvDownloadBaseUrl + $filename + "?viasf=1"

    if ($filename -is [array]) {
        $filename = $filename[0]
        $download_link = $download_link[0]
    }

    $tries = 0
    while ($True) {
        Download $filename $download_link
        ./7z.exe -y x $filename
        $retcode = $LastExitCode
        if ($retcode -eq 0) {
            Remove-Item $filename
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
    Write-Host "Installing PyTorch and Torch-TensorRT..."
    & "./python" -m pip install -U packaging setuptools wheel
    & "./python" -m pip install -U torch torchvision torch_tensorrt --index-url $PytorchUrl --extra-index-url "https://pypi.nvidia.com"

    Write-Host "Installing vs-rife..."
    & "./python" -m pip install -U vsrife

    # vs-rife auto-download is not working as of now, so we just download all manually.
    Write-Host "Downloading vs-rife models..."
    & "./python" -m vsrife
}

try {
    Get-VS
    Get-Mpv
    Get-VSRife

    Write-Host
    Write-Host "All done! Closing in 5 seconds..." $filename -ForegroundColor White -BackgroundColor Green
    Start-Sleep -Seconds 5
}
catch {
    Write-Host "Installation failed!" -ForegroundColor Red
    Write-Output $_
    Write-Host "Press any key to exit..." -NoNewline
    [System.Console]::ReadKey()
}