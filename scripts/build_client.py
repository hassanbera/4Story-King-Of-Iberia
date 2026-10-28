"""Build a loopback-only client candidate; never deploy or launch it automatically."""
from pathlib import Path
import argparse
import re
import sys

import build_server

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "source"
CLIENT = SOURCE / "TClient" / "TClient"
ENGINE = SOURCE / "TClient" / "TEngine"
OUTPUT = REPO / "build" / "client-local"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dx-sdk", required=True, type=Path)
    parser.add_argument("--allow-cursor-fallback", action="store_true", help="Use the valid source Sword.cur for invalid cursor resources in the build copy only")
    parser.add_argument("--link-only", action="store_true", help="Relink already compiled objects after library builds finish")
    args = parser.parse_args()
    dx = args.dx_sdk.resolve()
    if not (dx / "Include" / "dmusici.h").is_file():
        parser.error("Legacy DirectX SDK root required")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    env = build_server.toolchain()
    shared = Path(env["WindowsSdkDir"]) / "Include" / env["WindowsSDKVersion"].rstrip("\\/") / "shared"
    compat = OUTPUT / "ClientCompat.h"
    compat.write_text("#include <afxwin.h>\n#include <dxgitype.h>\n", encoding="ascii")
    includes = [shared, dx / "Include", CLIENT, SOURCE / "NPGame", SOURCE / "TProtocol",
                ENGINE / "TachyonControl", ENGINE / "Engine Lib", ENGINE / "TComp", ENGINE / "TCML",
                SOURCE / "TClient" / "History Files", SOURCE / "TClient" / "TChart",
                SOURCE / "XTrap" / "client", SOURCE / "Apex" / "client", SOURCE / "HShield" / "Include"]
    flags = ["cl", "/nologo", "/c", "/MT", "/EHsc", "/W0", "/Zc:forScope-", "/DWIN32", "/DNDEBUG",
             "/DKOREA", "/DKOI_LOCAL_CLIENT", "/DWINVER=0x0601", "/D_WIN32_WINNT=0x0601",
             "/FI" + str(compat), *["/I" + str(p) for p in includes]]
    pch = OUTPUT / "client.pch"
    if not args.link_only:
        build_server.run("pch-client", [*flags, '/Ycstdafx.h', "/Fp" + str(pch), str(CLIENT / "stdafx.cpp")], OUTPUT, env)
    project = (CLIENT / "TClient.vcproj").read_bytes().decode("cp949", errors="replace")
    units = [(CLIENT / path).resolve() for path in re.findall(r'RelativePath="([^"]+\.(?:cpp|c))"', project, re.I)]
    units = [p for p in units if p.name.lower() != "stdafx.cpp"]
    response = OUTPUT / "sources.rsp"
    response.write_text("\n".join('"' + str(p) + '"' for p in units), encoding="utf-8")
    if not args.link_only:
        build_server.run("compile-client", [*flags, "/MP2", "/Yustdafx.h", "/Fp" + str(pch), "@" + str(response)], OUTPUT, env)
    resource = (CLIENT / "TClient.rc").read_bytes()
    invalid = []
    def cursor(match):
        relative = match.group(1).decode("ascii").replace("\\\\", "\\")
        path = CLIENT / relative
        data = path.read_bytes()
        if data.startswith(b"\x00\x00\x02\x00"):
            return match.group(0)
        invalid.append(relative)
        return b'"res\\\\Sword.cur"'
    resource = re.sub(rb'"(res\\\\[^"\r\n]+\.cur)"', cursor, resource, flags=re.I)
    if invalid and not args.allow_cursor_fallback:
        raise RuntimeError(f"Invalid source cursors: {invalid}; explicit --allow-cursor-fallback required for a candidate build")
    if invalid:
        print(f"Candidate-only cursor fallback: {invalid}", flush=True)
    rc = OUTPUT / "TClient.build.rc"
    rc.write_bytes(resource)
    res = OUTPUT / "TClient.res"
    build_server.run("resource-client", ["rc", "/nologo", "/DKOREA", "/I" + str(CLIENT), "/fo" + str(res), str(rc)], OUTPUT, env)
    local_libs = REPO / "build" / "client-libraries-local" / "lib"
    library_paths = [local_libs, dx / "Lib", dx / "Lib" / "x86"]
    library_names = "EngineLib.lib TCML.lib TUIs.lib TComp.lib TChatFilter.lib TChart.lib zlib.lib d3d9.lib d3dx9.lib winmm.lib advapi32.lib imm32.lib dsound.lib dxguid.lib strmiids.lib version.lib dbghelp.lib psapi.lib".split()
    objects = [OUTPUT / "stdafx.obj", *[OUTPUT / (p.stem + ".obj") for p in units]]
    binary = OUTPUT / "TClient.exe"
    build_server.run("link-client", ["link", "/nologo", "/MACHINE:X86", "/SUBSYSTEM:WINDOWS", "/OUT:" + str(binary),
        "/MAP:" + str(OUTPUT / "TClient.map"),
        *["/LIBPATH:" + str(p) for p in library_paths], *map(str, objects), str(res), *library_names], OUTPUT, env)
    print(f"Built candidate {binary}; not installed into the running game.", flush=True)


if __name__ == "__main__":
    sys.exit(main())
