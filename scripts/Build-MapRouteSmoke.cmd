@echo off
setlocal EnableExtensions

set "REPO=%~dp0.."
set "ROOT=%REPO%\source"
set "SRC=%ROOT%\TServer\TMapSvr"
set "OUT=%REPO%\build\route-smoke"
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
)
where cl >nul 2>&1
if errorlevel 1 (
  echo x86 C++ compiler not found after vcvarsall.
  exit /b 2
)

if not exist "%OUT%" mkdir "%OUT%"
if errorlevel 1 exit /b 2
for %%F in (AmbientRoutes.cpp TAICmdRoam.cpp TMonster.cpp) do (
  echo Compiling %%F
  cl /nologo /c /MT /W0 /EHsc /Zc:forScope- /DWIN32 /D_WINDOWS /DNDEBUG /DWINVER=0x0601 /D_WIN32_WINNT=0x0601 /I "%SRC%" /I "%ROOT%\TServer\TNetLib" /I "%ROOT%\TProtocol" /I "%ROOT%\Apex\Server" /I "%ROOT%\HShield\Include" /I "%ROOT%\NPGame\Server" /Fo"%OUT%\%%~nF.obj" "%SRC%\%%F"
  if errorlevel 1 exit /b 1
)
echo Route source compilation passed. Object files: %OUT%
exit /b 0

