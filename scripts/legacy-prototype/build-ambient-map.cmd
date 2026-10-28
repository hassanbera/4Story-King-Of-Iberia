@echo off
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x86 >nul
if errorlevel 1 exit /b %errorlevel%
set "PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.16.27023\bin\HostX86\x86;C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\Common7\IDE;%PATH%"
set "BASE=%~dp0"
set "ROOT=%BASE%Source 3.3"
set "SRC=%ROOT%\TServer\TMapSvr"
set "OLD=%BASE%build-probe\TMapSvr"
set "OUT=%BASE%build-ambient\TMapSvr"
if not exist "%OUT%" mkdir "%OUT%"
if not exist "%OUT%\objects.rsp" (
  copy /y "%OLD%\*.obj" "%OUT%\" >nul
  copy /y "%OLD%\objects.rsp" "%OUT%\objects.rsp" >nul
  copy /y "%OLD%\TMapSvr.res" "%OUT%\TMapSvr.res" >nul
)
pushd "%OUT%"
if /I "%~1"=="link" goto link
for %%F in (TMonster.cpp TAICmdRoam.cpp AmbientRoutes.cpp) do (
  cl /nologo /c /MT /W0 /EHsc /Zc:forScope- /DWIN32 /D_WINDOWS /DNDEBUG /DWINVER=0x0601 /D_WIN32_WINNT=0x0601 /I "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.16.27023\include" /I "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.16.27023\atlmfc\include" /I "%SRC%" /I "%ROOT%\TServer\TNetLib" /I "%ROOT%\TProtocol" /I "%ROOT%\Apex\Server" /I "%ROOT%\HShield\Include" /I "%ROOT%\NPGame\Server" /Fo"%OUT%\%%~nF.obj" "%SRC%\%%F"
  if errorlevel 1 exit /b 1
)
:link
copy /y "%OLD%\objects.rsp" "%OUT%\objects.rsp" >nul
echo AmbientRoutes.obj>>"%OUT%\objects.rsp"
link /nologo /MACHINE:X86 /SUBSYSTEM:WINDOWS /LIBPATH:"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.16.27023\lib\x86" /LIBPATH:"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.16.27023\atlmfc\lib\x86" /LIBPATH:"C:\Program Files (x86)\Windows Kits\10\Lib\10.0.19041.0\um\x86" /LIBPATH:"C:\Program Files (x86)\Windows Kits\10\Lib\10.0.19041.0\ucrt\x86" /LIBPATH:"%ROOT%\Apex\Server" /LIBPATH:"%ROOT%\HShield\Lib\Win\x86\Multithreaded\AntiCrack" /LIBPATH:"%ROOT%\NPGame\Server\MT" /OUT:"%OUT%\TMapSvr.ambient.exe" @objects.rsp "%OUT%\TMapSvr.res" "%BASE%build-probe\TNetLib\TNetLib.localdb.lib" odbc32.lib ws2_32.lib mswsock.lib
exit /b %errorlevel%
