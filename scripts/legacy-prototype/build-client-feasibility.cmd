@echo off
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x86 >nul
set "PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.16.27023\bin\HostX86\x86;%PATH%"
set "ROOT=%~dp0Source 3.3"
set "SRC=%ROOT%\TClient\TClient"
set "OUT=%~dp0build-client-feasibility"
set "DX9=%~dp0..\4ever-build-2026-10-26\4Ever\Includes\External\sdk-directx9\Include"
if not exist "%OUT%" mkdir "%OUT%"
cl /nologo /c /MT /W0 /EHsc /Zc:forScope- /DWIN32 /DNDEBUG /DKOREA /DWINVER=0x0601 /D_WIN32_WINNT=0x0601 ^
 /FI "%OUT%\ClientCompat.h" ^
 /I "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.16.27023\include" ^
 /I "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.16.27023\atlmfc\include" ^
 /I "%DX9%" ^
 /I "C:\Program Files (x86)\Microsoft DirectX SDK (June 2010)\Include" ^
 /I "%SRC%" /I "%ROOT%\NPGame" /I "%ROOT%\TProtocol" ^
 /I "%ROOT%\TClient\TEngine\TachyonControl" ^
 /I "%ROOT%\TClient\TEngine\Engine Lib" ^
 /I "%ROOT%\TClient\TEngine\TComp" ^
 /I "%ROOT%\TClient\TEngine\TCML" ^
 /I "%ROOT%\XTrap\client" ^
 /I "%ROOT%\TClient\History Files" /I "%ROOT%\TClient\TChart" ^
 /I "%ROOT%\Apex\client" /I "%ROOT%\HShield\Include" ^
 /Fo"%OUT%\TClient.obj" "%SRC%\TClient.cpp"
exit /b %errorlevel%
