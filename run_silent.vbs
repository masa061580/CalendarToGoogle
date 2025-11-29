Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
AppDir = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = AppDir

' Use uv run for proper dependency management (with hidden window via pythonw workaround)
' First try pythonw in .venv, fallback to uv run
PythonW = AppDir & "\.venv\Scripts\pythonw.exe"
Launcher = AppDir & "\calendar_to_google\launcher.pyw"

If FSO.FileExists(PythonW) Then
    WshShell.Run """" & PythonW & """ """ & Launcher & """", 0, False
Else
    ' Fallback: use uv run (will show brief console flash)
    WshShell.Run "cmd /c uv run calendar-to-google", 0, False
End If
