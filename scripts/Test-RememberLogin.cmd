@echo off
setlocal EnableExtensions

set "REPO=%~dp0.."
set "ROOT=%REPO%\source"
set "SRC=%ROOT%\TServer\TMapSvr"
set "OUT=%REPO%\build\remember-login-test"
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
cl /nologo /EHsc /MT /I "%ROOT%\TClient\TClient" /Fe"%OUT%\RememberLoginStoreTest.exe" /Fo"%OUT%\RememberLoginStoreTest.obj" "%REPO%\tests\client\RememberLoginStoreTest.cpp"
if errorlevel 1 exit /b 1
"%OUT%\RememberLoginStoreTest.exe"
exit /b %errorlevel%
