from pathlib import Path

root = Path(__file__).resolve().parent
source = root / "Source 3.3" / "TServer"
output = root / "build-probe" / "RuntimePatched"
output.mkdir(parents=True, exist_ok=True)

services = {
    "TControlSvr": "TCTRL_PM33_PROBE",
    "TLoginSvr": "TLOGIN_PM33_PROBE",
    "TMapSvr": "TMAP_PM33_PROBE",
    "TWorldSvr": "TWORLD_PM33_PROBE",
}

for project, service_name in services.items():
    original = (source / project / f"{project}.cpp").read_bytes()
    data = original
    winmain = b"return _AtlModule.WinMain(nShowCmd);"
    if data.count(winmain) != 1:
        raise RuntimeError(f"Unexpected WinMain count: {project}")
    data = data.replace(winmain, b"return _AtlModule.Run(nShowCmd);")

    constructor = f"C{project}Module::C{project}Module()\r\n{{\r\n".encode("ascii")
    if data.count(constructor) != 1:
        raise RuntimeError(f"Unexpected constructor count: {project}")
    insertion = (
        constructor
        + b"\tm_bService = FALSE;\r\n"
        + f'\tstrcpy(m_szServiceName, "{service_name}");\r\n'.encode("ascii")
    )
    data = data.replace(constructor, insertion)

    registry_branch = b"#ifdef _DEBUG\r\n\tHKEY hOpenKey = HKEY_CURRENT_USER;"
    if data.count(registry_branch) != 1:
        raise RuntimeError(f"Unexpected registry branch count: {project}")
    data = data.replace(registry_branch, b"#if 1\r\n\tHKEY hOpenKey = HKEY_CURRENT_USER;")

    path = output / f"{project}.cpp"
    path.write_bytes(data)
    print(f"{project}: isolated local runtime source created")

session_original = (source / "TNetLib" / "Session.cpp").read_bytes()
listen_marker = b"BOOL CSession::Listen( WORD wPort)"
if session_original.count(listen_marker) != 1:
    raise RuntimeError("Unexpected Listen definition count")
start = session_original.index(listen_marker)
target = b"addr.sin_addr.s_addr = INADDR_ANY;"
position = session_original.index(target, start)
end = session_original.index(b"BOOL CSession::Connect", start)
if position >= end:
    raise RuntimeError("Listen bind target outside Listen implementation")
session_patched = (
    session_original[:position]
    + b'addr.sin_addr.s_addr = inet_addr("127.0.0.1");'
    + session_original[position + len(target):]
)
(output / "Session.localdb.cpp").write_bytes(session_patched)
print("TNetLib: isolated loopback listener source created")
