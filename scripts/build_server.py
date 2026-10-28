"""Build isolated x86 LocalDB server binaries from this repository's source."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys


REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "source"
OUTPUT = REPO / "build" / "server"
SERVICES = ("TControlSvr", "TWorldSvr", "TLoginSvr", "TMapSvr")
SERVICE_NAMES = {
    "TControlSvr": "TCTRL_PM33_PROBE",
    "TWorldSvr": "TWORLD_PM33_PROBE",
    "TLoginSvr": "TLOGIN_PM33_PROBE",
    "TMapSvr": "TMAP_PM33_PROBE",
}


def replace_exact(data: bytes, old: bytes, new: bytes, count: int = 1) -> bytes:
    actual = data.count(old)
    if actual != count:
        raise RuntimeError(f"Expected {count} source site(s), found {actual}: {old[:70]!r}")
    return data.replace(old, new)


def toolchain() -> dict[str, str]:
    program_files = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
    vc_root = program_files / "Microsoft Visual Studio" / "2019" / "BuildTools" / "VC" / "Tools" / "MSVC" / "14.16.27023"
    vcvars = program_files / "Microsoft Visual Studio" / "2019" / "BuildTools" / "VC" / "Auxiliary" / "Build" / "vcvarsall.bat"
    if not vcvars.is_file() or not (vc_root / "bin" / "HostX86" / "x86" / "cl.exe").is_file():
        raise RuntimeError("Required VS 2019 Build Tools v141 (14.16.27023) not found")
    bootstrap = OUTPUT / "vc-env.cmd"
    bootstrap.parent.mkdir(parents=True, exist_ok=True)
    bootstrap.write_text(f'@echo off\ncall "{vcvars}" x86 >nul\nif errorlevel 1 exit /b 1\nset\n', encoding="ascii")
    process = subprocess.run(["cmd", "/c", str(bootstrap)], capture_output=True, text=True, errors="replace")
    if process.returncode:
        raise RuntimeError(process.stderr or "vcvarsall failed")
    env = os.environ.copy()
    env.update(dict(line.split("=", 1) for line in process.stdout.splitlines() if "=" in line and not line.startswith("=")))
    for key in list(env):
        if key.lower() in {"path", "include", "lib"} and key not in {"PATH", "INCLUDE", "LIB"}:
            env[key.upper()] = env[key]
            del env[key]
    env["PATH"] = str(vc_root / "bin" / "HostX86" / "x86") + os.pathsep + env.get("PATH", "")
    env["INCLUDE"] = os.pathsep.join([str(vc_root / "include"), str(vc_root / "atlmfc" / "include"), env.get("INCLUDE", "")])
    env["LIB"] = os.pathsep.join([str(vc_root / "lib" / "x86"), str(vc_root / "atlmfc" / "lib" / "x86"), env.get("LIB", "")])
    return env


def run(name: str, args: list[str], cwd: Path, env: dict[str, str]) -> None:
    print(name, flush=True)
    executable = shutil.which(args[0], path=env["PATH"])
    if not executable:
        raise RuntimeError(f"Tool not found: {args[0]}")
    process = subprocess.run([executable, *args[1:]], cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (cwd / f"{name}.log").write_bytes(process.stdout)
    if process.returncode:
        output = process.stdout.decode("utf-8", errors="replace")
        print("\n".join(output.splitlines()[-35:]), file=sys.stderr)
        raise RuntimeError(f"{name} failed with code {process.returncode}; see {cwd / (name + '.log')}")


def local_session() -> Path:
    src = SOURCE / "TServer" / "TNetLib" / "Session.cpp"
    data = src.read_bytes()
    start = data.index(b"BOOL CSession::Listen( WORD wPort)")
    end = data.index(b"BOOL CSession::Connect", start)
    target = b"addr.sin_addr.s_addr = INADDR_ANY;"
    if data[start:end].count(target) != 1:
        raise RuntimeError("Unexpected listener source")
    data = data[:start] + replace_exact(data[start:end], target, b'addr.sin_addr.s_addr = inet_addr("127.0.0.1");') + data[end:]
    dest = OUTPUT / "TNetLib" / "Session.localdb.cpp"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return dest


def local_service_main(name: str) -> Path:
    src = SOURCE / "TServer" / name / f"{name}.cpp"
    data = src.read_bytes()
    data = replace_exact(data, b"return _AtlModule.WinMain(nShowCmd);", b"return _AtlModule.Run(nShowCmd);")
    constructor = f"C{name}Module::C{name}Module()\r\n{{\r\n".encode("ascii")
    insert = constructor + b"\tm_bService = FALSE;\r\n" + f'\tstrcpy(m_szServiceName, "{SERVICE_NAMES[name]}");\r\n'.encode("ascii")
    data = replace_exact(data, constructor, insert)
    data = replace_exact(data, b"#ifdef _DEBUG\r\n\tHKEY hOpenKey = HKEY_CURRENT_USER;", b"#if 1\r\n\tHKEY hOpenKey = HKEY_CURRENT_USER;")
    dest = OUTPUT / name / f"{name}.localdb.cpp"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return dest


def local_map_handler() -> Path:
    src = SOURCE / "TServer" / "TMapSvr" / "SSHandler.cpp"
    data = src.read_bytes()
    data = replace_exact(data, b"static bCurStatus = BS_NORMAL;", b"static BYTE bCurStatus = BS_NORMAL;", 3)
    data = replace_exact(data, b"static dwCurStart = 0;", b"static DWORD dwCurStart = 0;")
    data = replace_exact(
        data,
        b"CTime next = CTime(now.GetYear(), now.GetMonth(), now.GetDay(), 0, 0, dwAdd);",
        b"CTime midnight(now.GetYear(), now.GetMonth(), now.GetDay(), 0, 0, 0);\r\n\t\t\tCTime next(midnight.GetTime() + dwAdd);",
    )
    dest = OUTPUT / "TMapSvr" / "SSHandler.localdb.cpp"
    dest.write_bytes(data)
    return dest


def common_compiler_args(name: str) -> list[str]:
    project = SOURCE / "TServer" / name
    includes = [project, SOURCE / "TServer" / "TNetLib", SOURCE / "TProtocol", SOURCE / "Apex" / "Server", SOURCE / "HShield" / "Include", SOURCE / "NPGame" / "Server"]
    args = ["cl", "/nologo", "/c", "/MT", "/W0", "/EHsc", "/Zc:forScope-", "/DWIN32", "/D_WINDOWS", "/DNDEBUG", "/DWINVER=0x0601", "/D_WIN32_WINNT=0x0601"]
    if name == "TLoginSvr":
        args.append("/DPACKET_CRYPT")
    args.extend("/I" + str(path) for path in includes)
    return args


def build_netlib(env: dict[str, str]) -> Path:
    name = "TNetLib"
    src = SOURCE / "TServer" / name
    out = OUTPUT / name
    out.mkdir(parents=True, exist_ok=True)
    staged = local_session()
    units = [staged if path.name == "Session.cpp" else path for path in sorted(src.glob("*.cpp"))]
    objects = []
    for unit in units:
        obj = out / ("Session.obj" if unit == staged else unit.stem + ".obj")
        args = ["cl", "/nologo", "/c", "/MT", "/EHsc", "/Zc:forScope-", "/DWINVER=0x0601", "/D_WIN32_WINNT=0x0601", "/I" + str(src), "/Fo" + str(obj), str(unit)]
        run(f"compile-{unit.stem}", args, out, env)
        objects.append(obj)
    library = out / "TNetLib.localdb.lib"
    run("archive-TNetLib", ["lib", "/nologo", "/OUT:" + str(library), *map(str, objects)], out, env)
    return library


def build_service(name: str, network_lib: Path, env: dict[str, str]) -> Path:
    src = SOURCE / "TServer" / name
    out = OUTPUT / name
    out.mkdir(parents=True, exist_ok=True)
    main = local_service_main(name)
    handler = local_map_handler() if name == "TMapSvr" else None
    units = [main if path.name == f"{name}.cpp" else handler if handler and path.name == "SSHandler.cpp" else path for path in sorted(src.glob("*.cpp"))]
    units += sorted(src.glob("*_i.c"))
    objects = []
    for unit in units:
        stem = name if unit == main else "SSHandler" if unit == handler else unit.stem
        obj = out / (stem + ".obj")
        run(f"compile-{stem}", common_compiler_args(name) + ["/Fo" + str(obj), str(unit)], out, env)
        objects.append(obj)
    midl = shutil.which("midl", path=env["PATH"])
    rc = shutil.which("rc", path=env["PATH"])
    if not midl or not rc:
        raise RuntimeError("Windows SDK MIDL/RC tools not found")
    run("midl", [midl, "/nologo", "/env", "win32", "/out", str(out), "/tlb", str(out / f"{name}.tlb"), str(src / f"{name}.idl")], out, env)
    resource = out / f"{name}.res"
    run("resource", [rc, "/nologo", "/I", str(src), "/fo", str(resource), str(src / f"{name}.rc")], out, env)
    binary = out / f"{name}.localdb.exe"
    libs = [SOURCE / "Apex" / "Server", SOURCE / "HShield" / "Lib" / "Win" / "x86" / "Multithreaded" / "AntiCrack", SOURCE / "NPGame" / "Server" / "MT"]
    link_args = ["link", "/nologo", "/MACHINE:X86", "/SUBSYSTEM:WINDOWS", "/OUT:" + str(binary)]
    link_args.extend("/LIBPATH:" + str(path) for path in libs)
    link_args.extend(map(str, objects))
    link_args.extend([str(resource), str(network_lib), "odbc32.lib", "ws2_32.lib", "mswsock.lib"])
    run("link", link_args, out, env)
    return binary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", choices=SERVICES, action="append", help="Build selected service(s); default all four")
    args = parser.parse_args()
    env = toolchain()
    network_lib = build_netlib(env)
    for name in args.service or SERVICES:
        binary = build_service(name, network_lib, env)
        print(f"Built {binary}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
