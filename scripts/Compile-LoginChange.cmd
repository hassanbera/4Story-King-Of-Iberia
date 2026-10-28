@echo off
setlocal EnableExtensions

set "REPO=%~dp0.."
set "ROOT=%REPO%\source"
set "SRC=%ROOT%\TServer\TMapSvr"
set "OUT=%REPO%\build\login-change"
set "VCVARS=%ProgramFiles(x86)%\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvarsall.bat"
if not exist "%VCVARS%" set "VCVARS=%ProgramFiles%\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"
if not exist "%VCVARS%" (
  echo Visual Studio 2019 Build Tools or 2022 Community C++ tools not found.
  exit /b 2
)
call "%VCVARS%" x86 >nul
if errorlevel 1 exit /b 2
set "LEGACY_CL=%ProgramFiles(x86)%\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.16.27023\bin\HostX86\x86"
set "LEGACY_VC=%ProgramFiles(x86)%\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.16.27023"
if exist "%LEGACY_CL%\cl.exe" (
  set "PATH=%LEGACY_CL%;%PATH%"
  set "INCLUDE=%LEGACY_VC%\include;%LEGACY_VC%\atlmfc\include;%INCLUDE%"
  set "LIB=%LEGACY_VC%\lib\x86;%LEGACY_VC%\atlmfc\lib\x86;%LIB%"
)
where cl >nul 2>&1
if errorlevel 1 (
  echo x86 C++ compiler not found after vcvarsall.
  exit /b 2
)

if not exist "%OUT%" mkdir "%OUT%"
if errorlevel 1 exit /b 2
if "%~1"=="" (
  echo Usage: Compile-LoginChange.cmd "path-to-legacy-DirectX9-Include"
  exit /b 2
)
set "DX9=%~1"
if not exist "%DX9%\dmusici.h" exit /b 2
>"%OUT%\ClientCompat.h" echo #include ^<afxwin.h^>
>>"%OUT%\ClientCompat.h" echo #include ^<dxgitype.h^>
set "SRC=%ROOT%\TClient\TClient"
for %%F in (TClientWnd TNetGM) do (
  cl /nologo /c /MT /W0 /EHsc /Zc:forScope- /DWIN32 /DNDEBUG /DKOREA /DWINVER=0x0601 /D_WIN32_WINNT=0x0601 /FI "%OUT%\ClientCompat.h" /I "%WindowsSdkDir%Include\%WindowsSDKVersion%shared" /I "%DX9%" /I "%SRC%" /I "%ROOT%\NPGame" /I "%ROOT%\TProtocol" /I "%ROOT%\TClient\TEngine\TachyonControl" /I "%ROOT%\TClient\TEngine\Engine Lib" /I "%ROOT%\TClient\TEngine\TComp" /I "%ROOT%\TClient\TEngine\TCML" /I "%ROOT%\XTrap\client" /I "%ROOT%\TClient\History Files" /I "%ROOT%\TClient\TChart" /I "%ROOT%\Apex\client" /I "%ROOT%\HShield\Include" /Fo"%OUT%\%%F.obj" "%SRC%\%%F.cpp"
  if errorlevel 1 exit /b 1
)
exit /b 0
