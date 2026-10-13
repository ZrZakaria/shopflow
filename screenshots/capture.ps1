Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Full desktop screenshot
$bmp = New-Object System.Drawing.Bitmap(1280, 800)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0)
$bmp.Save("C:/Users/HP/Studies/Studies/S9/GL/shopflow/screenshots/desktop.png")
$bmp.Dispose()
$g.Dispose()
Write-Host "Desktop screenshot saved"
