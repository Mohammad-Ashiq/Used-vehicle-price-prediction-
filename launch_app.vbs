Set WshShell = CreateObject("WScript.Shell")

' 1. Check if server is already running by trying to connect
Dim http
On Error Resume Next
Set http = CreateObject("MSXML2.XMLHTTP")
http.Open "GET", "http://127.0.0.1:5000/", False
http.Send

If Err.Number <> 0 Or http.Status <> 200 Then
    ' Start Flask server silently in background using pythonw
    WshShell.CurrentDirectory = "C:\ReVahan_Project"
    WshShell.Run "cmd /c python app.py", 0, False
    WScript.Sleep 2000
End If
On Error GoTo 0

' 2. Launch Chrome or Edge in standalone Desktop App Mode
Dim chromePath, edgePath
chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")

If fso.FileExists(chromePath) Then
    WshShell.Run """" & chromePath & """ --app=http://127.0.0.1:5000", 1, False
ElseIf fso.FileExists(edgePath) Then
    WshShell.Run """" & edgePath & """ --app=http://127.0.0.1:5000", 1, False
Else
    WshShell.Run "http://127.0.0.1:5000", 1, False
End If
