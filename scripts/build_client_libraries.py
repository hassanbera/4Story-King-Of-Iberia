"""Build legacy client libraries into build/, without installing them into the game."""
from pathlib import Path
import argparse
import re
import sys

import build_server

REPO = Path(__file__).resolve().parents[1]
ENGINE = REPO / "source" / "TClient" / "TEngine"
OUT = REPO / "build" / "client-libraries"
PROJECTS = {
    "TCML": ENGINE / "TCML" / "TCML.vcproj",
    "EngineLib": ENGINE / "Engine Lib" / "Engine Lib.vcproj",
    "TUIs": ENGINE / "TachyonControl" / "TachyonControl.vcproj",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dx-include", required=True, type=Path)
    parser.add_argument("--library", choices=PROJECTS, action="append")
    parser.add_argument("--zlib-source", type=Path, help="Optional zlib 1.3.1 source tree to build the compression dependency")
    args = parser.parse_args()
    if not (args.dx_include / "dmusici.h").is_file():
        parser.error("Legacy DirectX include directory with dmusici.h required")
    env = build_server.toolchain()
    shared = Path(env["WindowsSdkDir"]) / "Include" / env["WindowsSDKVersion"].rstrip("\\/") / "shared"
    includes = [shared, args.dx_include.resolve(), ENGINE / "TachyonControl", ENGINE / "Engine Lib",
                ENGINE / "TComp", ENGINE / "TCML", ENGINE / "Engine Lib" / "zlib"]
    libraries = OUT / "lib"
    libraries.mkdir(parents=True, exist_ok=True)
    if args.zlib_source:
        zlib = args.zlib_source.resolve()
        if '#define ZLIB_VERSION "1.3.1"' not in (zlib / "zlib.h").read_text():
            raise RuntimeError("Expected zlib 1.3.1 headers")
        out = OUT / "zlib"
        out.mkdir(parents=True, exist_ok=True)
        names = "adler32 compress crc32 deflate gzclose gzlib gzread gzwrite inflate infback inftrees inffast trees uncompr zutil".split()
        units = [str(zlib / (name + ".c")) for name in names]
        build_server.run("compile-zlib", ["cl", "/nologo", "/c", "/MP2", "/MT", "/O2", "/D_CRT_SECURE_NO_WARNINGS", "/I" + str(zlib), *units], out, env)
        objects = [str(out / (name + ".obj")) for name in names]
        build_server.run("archive-zlib", ["lib", "/nologo", "/OUT:" + str(libraries / "zlib.lib"), *objects], out, env)
        smoke = out / "LegacyZlibSmoke.exe"
        build_server.run("compile-zlib-smoke", ["cl", "/nologo", "/MT", "/EHsc",
            "/I" + str(ENGINE / "Engine Lib" / "zlib"),
            "/Fe" + str(smoke), "/Fo" + str(out / "LegacyZlibSmoke.obj"),
            str(REPO / "tests" / "client" / "LegacyZlibSmoke.cpp"), str(libraries / "zlib.lib")], out, env)
        build_server.run("test-zlib-smoke", [str(smoke)], out, env)
    for name in args.library or PROJECTS:
        project = PROJECTS[name]
        out = OUT / name
        out.mkdir(parents=True, exist_ok=True)
        text = project.read_bytes().decode("cp949", errors="replace")
        units = [str((project.parent / p).resolve()) for p in re.findall(r'RelativePath="([^"]+\.(?:cpp|c))"', text, re.I)]
        for unit in units:
            if not Path(unit).is_file():
                raise RuntimeError(f"Missing source: {unit}")
        flags = ["cl", "/nologo", "/c", "/MP2", "/MT", "/EHsc", "/W0", "/Zc:forScope-",
                 "/DWIN32", "/DNDEBUG", "/D_WINDOWS", "/DWINVER=0x0601", "/D_WIN32_WINNT=0x0601"]
        if name == "TCML":
            flags.append("/D_LIB")
        flags += ["/I" + str(p) for p in includes]
        flags += ["/I" + str(project.parent)]
        build_server.run("compile-" + name, flags + units, out, env)
        objects = [str(out / (Path(p).stem + ".obj")) for p in units]
        library = libraries / (name + ".lib")
        build_server.run("archive-" + name, ["lib", "/nologo", "/OUT:" + str(library), *objects], out, env)
        if not library.read_bytes().startswith(b"!<arch>\n"):
            raise RuntimeError(f"Invalid library output: {library}")
        build_server.run("list-" + name, ["lib", "/nologo", "/list", str(library)], out, env)
        print(f"Built {library}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
