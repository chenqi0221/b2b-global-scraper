$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $DesktopPath 'WhatsApp Bot.lnk'
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = 'E:\办公小程序\WhatsApp自动化库\whatsapp-web.js\start-whatsapp-bot.bat'
$Shortcut.WorkingDirectory = 'E:\办公小程序\WhatsApp自动化库\whatsapp-web.js'
$Shortcut.IconLocation = '%SystemRoot%\System32\SHELL32.dll,15'
$Shortcut.Description = 'Start WhatsApp Bot'
$Shortcut.Save()
Write-Output "Shortcut created: $ShortcutPath"
