# 1. Run pygbag build
Write-Host "Running Pygbag build..."
python -m pygbag --build .

# 2. Check if build succeeded
if (-not (Test-Path "build\web\version.web.tar.gz")) {
    Write-Error "Pygbag build failed! version.web.tar.gz not found."
    exit 1
}

# 3. Split version.web.tar.gz into chunks ending in .data
Write-Host "Splitting version.web.tar.gz into smaller chunks..."
$inputFile = "build\web\version.web.tar.gz"
$chunkSize = 8MB
$buffer = New-Object System.Byte[] $chunkSize
$fileStream = [System.IO.File]::OpenRead($inputFile)
$partNumber = 1
while (($bytesRead = $fileStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
    $outputFile = "build\web\version.web.00{0}.data" -f $partNumber
    $outputStream = [System.IO.File]::OpenWrite($outputFile)
    $outputStream.Write($buffer, 0, $bytesRead)
    $outputStream.Close()
    Write-Host "Created $outputFile with $bytesRead bytes"
    $partNumber++
}
$fileStream.Close()

# 4. Remove unsplit files to avoid confusion and host limits
Remove-Item -Path "build\web\version.web.tar.gz" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "build\web\version.web.apk" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "build\web\version.web.data" -Force -ErrorAction SilentlyContinue

# 5. Modify index.html to load the split files and add circular loading UI
Write-Host "Modifying build\web\index.html to load split data files and add circular loading UI..."
$indexPath = "build\web\index.html"
$indexContent = Get-Content -Raw -Path $indexPath

# Normalize all line endings to `n (Unix format) to avoid mismatch issues
$indexContent = $indexContent -replace "`r`n", "`n"

# A. Python loading logic replacement (using single-quoted here-strings to prevent interpolation)
$target = @'
    else:
        import tarfile
        async with platform.fopen("version.web.tar.gz", "rb") as archive:
            tar = tarfile.open(fileobj=archive, mode="r:gz")
            tar.extractall(path=appdir.as_posix(), filter='tar')
            tar.close()
'@ -replace "`r`n", "`n"

$targetAlt = @'
    else:
        import tarfile
        async with platform.fopen("version.web.data", "rb") as archive:
            tar = tarfile.open(fileobj=archive, mode="r:gz")
            tar.extractall(path=appdir.as_posix(), filter='tar')
            tar.close()
'@ -replace "`r`n", "`n"

$replacement = @'
    else:
        import tarfile
        import io
        chunks = []
        for i in range(1, 5):
            platform.window.currentLoadingPart = i
            async with platform.fopen(f"version.web.00{i}.data", "rb") as part:
                chunks.append(part.read())
        platform.window.currentLoadingPart = 5
        fileobj = io.BytesIO(b"".join(chunks))
        tar = tarfile.open(fileobj=fileobj, mode="r:gz")
        tar.extractall(path=appdir.as_posix(), filter='tar')
        tar.close()
'@ -replace "`r`n", "`n"

if ($indexContent.Contains($target)) {
    $indexContent = $indexContent.Replace($target, $replacement)
} elseif ($indexContent.Contains($targetAlt)) {
    $indexContent = $indexContent.Replace($targetAlt, $replacement)
} else {
    Write-Error "Could not find Python loading section in index.html to modify!"
    exit 1
}

# B. CSS styles replacement for Circular Progress (using single-quoted here-strings)
$cssTarget = @'
        .framed{
           position: relative;
           top: 150px;
           right: 10px;
           border: 1px solid black;
        }
    </style>
'@ -replace "`r`n", "`n"

$cssReplacement = @'
        .framed{
           position: relative;
           top: 150px;
           right: 10px;
           border: 1px solid black;
        }

        /* Circular Progress styling */
        .circular-progress-container {
            position: relative;
            width: 120px;
            height: 120px;
            margin: 40px auto 20px auto;
        }
        .circular-progress {
            transform: rotate(-90deg);
        }
        .circular-progress circle {
            fill: none;
            stroke-width: 8px;
        }
        .circular-progress circle.bg {
            stroke: rgba(255, 255, 255, 0.15);
        }
        .circular-progress circle.fg {
            stroke: #00f0ff; /* Glowing cyan */
            stroke-linecap: round;
            stroke-dasharray: 339.292; /* 2 * PI * r = 2 * 3.14159 * 54 */
            stroke-dashoffset: 339.292;
            transition: stroke-dashoffset 0.1s ease;
            filter: drop-shadow(0 0 6px rgba(0, 240, 255, 0.8));
        }
        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 22px;
            font-weight: bold;
            color: #ffffff;
            font-family: sans-serif;
            text-shadow: 0 0 4px rgba(0, 0, 0, 0.5);
        }
    </style>
'@ -replace "`r`n", "`n"

if ($indexContent.Contains($cssTarget)) {
    $indexContent = $indexContent.Replace($cssTarget, $cssReplacement)
} else {
    Write-Warning "Could not find CSS section to add circular loading styles."
}

# C. HTML transfer div replacement (using single-quoted here-strings)
$htmlTarget = @'
    <div id="transfer" align=center>
<!--        <div class="spinner" id='spinner'></div> -->
        <div class="emscripten" id="status">Downloading...</div>
        <div class="emscripten">
            <progress value="0" max="100" id="progress"></progress>
        </div>
    </div>
'@ -replace "`r`n", "`n"

$htmlReplacement = @'
    <div id="transfer" align=center>
        <div class="circular-progress-container">
            <svg class="circular-progress" width="120" height="120" viewBox="0 0 120 120">
                <circle class="bg" cx="60" cy="60" r="54" />
                <circle class="fg" cx="60" cy="60" r="54" />
            </svg>
            <div class="progress-text" id="progress-percent">0%</div>
        </div>
        <div class="emscripten" id="status" style="font-family: sans-serif; color: #fff; margin-top: 10px; font-weight: 500;">Downloading...</div>
        <div class="emscripten" style="display: none;">
            <progress value="0" max="100" id="progress"></progress>
        </div>
    </div>
'@ -replace "`r`n", "`n"

if ($indexContent.Contains($htmlTarget)) {
    $indexContent = $indexContent.Replace($htmlTarget, $htmlReplacement)
} else {
    Write-Warning "Could not find HTML transfer section in index.html to modify."
}

# D. JS progress updater replacement (using single-quoted here-strings)
$jsTarget = @'
    function frame_online(url) {
        window.frames["iframe"].location = url;
    }

    </script>
'@ -replace "`r`n", "`n"

$jsReplacement = @'
    function frame_online(url) {
        window.frames["iframe"].location = url;
    }

    // Circular progress updater loop
    setInterval(() => {
        const progressEl = document.getElementById('progress');
        const percentText = document.getElementById('progress-percent');
        const fgCircle = document.querySelector('.circular-progress circle.fg');
        const statusEl = document.getElementById('status');
        
        if (progressEl && percentText && fgCircle) {
            let value = parseFloat(progressEl.value);
            let max = parseFloat(progressEl.max) || 100;
            if (isNaN(value) || value < 0) value = 0;
            
            // Calculate part percentage (0 to 100)
            let partPercentage = (value / max) * 100;
            if (partPercentage > 100) partPercentage = 100;
            
            // Calculate cumulative global percentage across 4 parts
            let currentPart = window.currentLoadingPart || 1;
            let globalPercentage = 0;
            
            if (currentPart >= 1 && currentPart <= 4) {
                // Each part counts for 25% of the total download
                globalPercentage = Math.round(((currentPart - 1) * 25) + (partPercentage * 0.25));
            } else {
                // If loading completed or in another state
                globalPercentage = 100;
            }
            
            if (globalPercentage > 100) globalPercentage = 100;
            
            // Update percentage text
            percentText.innerText = globalPercentage + '%';
            
            // Update circle dashoffset (Circumference = 339.292)
            const circumference = 339.292;
            const offset = circumference - (globalPercentage / 100) * circumference;
            fgCircle.style.strokeDashoffset = offset;
            
            // Add loading feedback to status text
            if (statusEl && currentPart <= 4) {
                statusEl.innerText = `Descargando recursos (Parte ${currentPart} de 4)...`;
            }
        }
    }, 50);

    </script>
'@ -replace "`r`n", "`n"

if ($indexContent.Contains($jsTarget)) {
    $indexContent = $indexContent.Replace($jsTarget, $jsReplacement)
} else {
    Write-Warning "Could not find JS section to add circular progress updater script."
}

# Also ensure browserfs.min.js is referenced locally instead of from the double-slash CDN
$cdnSrc = 'src="https://pygame-web.github.io/cdn/0.9.3//browserfs.min.js"'
$localSrc = 'src="browserfs.min.js"'
if ($indexContent.Contains($cdnSrc)) {
    $indexContent = $indexContent.Replace($cdnSrc, $localSrc)
}

Set-Content -Path $indexPath -Value $indexContent -NoNewline

# 6. Copy browserfs.min.js if not already there
if (-not (Test-Path "build\web\browserfs.min.js")) {
    Write-Host "Copying browserfs.min.js from cdnjs..."
    Invoke-WebRequest -Uri "https://cdnjs.cloudflare.com/ajax/libs/BrowserFS/2.0.0/browserfs.min.js" -OutFile "build\web\browserfs.min.js"
}

Write-Host "Done! Build files ready in build\web\"
