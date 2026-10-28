@echo off
setlocal
set "NAME=%~1"
if "%NAME%"=="" exit /b 2
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x86 >nul
if errorlevel 1 exit /b %errorlevel%
set "PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.16.27023\bin\HostX86\x86;C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\Common7\IDE;%PATH%"
set "ROOT=C:\Users\Bera-T\Documents\Codex\2026-10-17\4story-living-world-ana-geli-tirme\work\philipmorris-oldschool\Source 3.3"
set "BASE=C:\Users\Bera-T\Documents\Codex\2026-10-17\4story-living-world-ana-geli-tirme\work\philipmorris-oldschool\build-probe"
set "SRC=%ROOT%\TServer\%NAME%"
set "OUT=%BASE%\%NAME%"
set "PATCH=%BASE%\RuntimePatched\%NAME%.cpp"
if not exist "%PATCH%" exit /b 2
if not exist "%OUT%\%NAME%.res" exit /b 2
if not exist "%BASE%\TNetLib\TNetLib.localdb.lib" exit /b 2
set "EXTRA="
if /I "%NAME%"=="TLoginSvr" set "EXTRA=/DPACKET_CRYPT"
pushd "%OUT%"
cl /nologo /c /MT /W0 /EHsc /Zc:forScope- /DWIN32 /D_WINDOWS /DNDEBUG %EXTRA% /DWINVER=0x0601 /D_WIN32_WINNT=0x0601 /I "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.16.27023\include" /I "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.16.27023\atlmfc\include" /I "%SRC%" /I "%ROOT%\TServer\TNetLib" /I "%ROOT%\TProtocol" /I "%ROOT%\Apex\Server" /I "%ROOT%\HShield\Include" /I "%ROOT%\NPGame\Server" /Fo"%OUT%\%NAME%.obj" "%PATCH%"
if errorlevel 1 exit /b %errorlevel%
type nul > "%OUT%\objects.rsp"
for %%F in (*.obj) do @echo %%F>>"%OUT%\objects.rsp"
link /nologo /MACHINE:X86 /SUBSYSTEM:WINDOWS /LIBPATH:"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.16.27023\lib\x86" /LIBPATH:"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.16.27023\atlmfc\lib\x86" /LIBPATH:"C:\Program Files (x86)\Windows Kits\10\Lib\10.0.19041.0\um\x86" /LIBPATH:"C:\Program Files (x86)\Windows Kits\10\Lib\10.0.19041.0\ucrt\x86" /LIBPATH:"%ROOT%\Apex\Server" /LIBPATH:"%ROOT%\HShield\Lib\Win\x86\Multithreaded\AntiCrack" /LIBPATH:"%ROOT%\NPGame\Server\MT" /OUT:"%OUT%\%NAME%.localdb.exe" @objects.rsp "%OUT%\%NAME%.res" "%BASE%\TNetLib\TNetLib.localdb.lib" odbc32.lib ws2_32.lib mswsock.lib
exit /b %errorlevel%
