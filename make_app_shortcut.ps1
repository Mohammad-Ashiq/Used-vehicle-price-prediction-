$wsh = New-Object -ComObject WScript.Shell
$desktop = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)

$shortcutPath = Join-Path $desktop "ReVahan App.lnk"
$sc = $wsh.CreateShortcut($shortcutPath)
$sc.TargetPath = "wscript.exe"
$sc.Arguments = "`"C:\ReVahan_Project\launch_app.vbs`""
$sc.WorkingDirectory = "C:\ReVahan_Project"
$sc.IconLocation = "C:\ReVahan_Project\static\images\favicon.ico"
$sc.Description = "Launch ReVahan Standalone Application"
$sc.Save()

Write-Host "Created $shortcutPath successfully!"
