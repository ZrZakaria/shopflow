# Screenshot specific window by title
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$windowTitle = $args[0]
$outputPath = $args[1]

# Find window
$windows = [System.Windows.Forms.Form]::FindFormByHandle | ForEach-Object { $_ }

# Use Win32 API to find window
$code = @'
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string className, string windowTitle);
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool IsIconic(IntPtr hWnd);
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
'@
Add-Type -TypeDefinition $code -Language CSharpVersion4

$hwnd = [Win32]::FindWindow($null, $windowTitle)
if ($hwnd -eq [IntPtr]::Zero) {
    Write-Host "Window not found: $windowTitle"
    exit 1
}

# Restore if minimized
if ([Win32]::IsIconic($hwnd)) {
    [Win32]::ShowWindow($hwnd, 9) # SW_RESTORE
}
[System.Threading.Thread]::Sleep(500)
[Win32]::SetForegroundWindow($hwnd)
[System.Threading.Thread]::Sleep(1000)

# Get window rect
$rect = New-Object Win32+RECT
[Win32]::GetWindowRect($hwnd, [ref]$rect)
$width = $rect.Right - $rect.Left
$height = $rect.Bottom - $rect.Top

Write-Host "Window: $windowTitle ($width x $height)"

$bmp = New-Object System.Drawing.Bitmap($width, $height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($rect.Left, $rect.Top, 0, 0, [System.Drawing.Size]::new($width, $height))
$bmp.Save($outputPath)
$bmp.Dispose()
$g.Dispose()
Write-Host "Screenshot saved to: $outputPath"
