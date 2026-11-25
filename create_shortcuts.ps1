$wsh = New-Object -ComObject WScript.Shell

$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (-not (Test-Path $chrome)) {
    $chrome = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
}
$icon = "C:\ReVahan_Project\static\images\favicon.ico"

# 1. Start Menu Shortcut
$startMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$s1 = $wsh.CreateShortcut((Join-Path $startMenuDir "ReVahan.lnk"))
$s1.TargetPath = $chrome
$s1.Arguments = "--app=http://127.0.0.1:5000"
$s1.WorkingDirectory = "C:\ReVahan_Project"
$s1.IconLocation = $icon
$s1.Description = "ReVahan Used Vehicle Price Prediction"
$s1.Save()
Write-Host "Created Start Menu Shortcut: $startMenuDir\ReVahan.lnk"

# 2. Desktop Shortcut
$desktopDir = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$s2 = $wsh.CreateShortcut((Join-Path $desktopDir "ReVahan.lnk"))
$s2.TargetPath = $chrome
$s2.Arguments = "--app=http://127.0.0.1:5000"
$s2.WorkingDirectory = "C:\ReVahan_Project"
$s2.IconLocation = $icon
$s2.Description = "ReVahan Used Vehicle Price Prediction"
$s2.Save()
Write-Host "Created Desktop Shortcut: $desktopDir\ReVahan.lnk"
