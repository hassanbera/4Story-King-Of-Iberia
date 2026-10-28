from pathlib import Path

root = Path(__file__).resolve().parent
source = root / "Source 3.3" / "TServer" / "TMapSvr" / "SSHandler.cpp"
output = root / "build-probe" / "TMapSvr" / "SSHandler.patched.cpp"
data = source.read_bytes()

changes = [
    (b"static bCurStatus = BS_NORMAL;", b"static BYTE bCurStatus = BS_NORMAL;", 3),
    (b"static dwCurStart = 0;", b"static DWORD dwCurStart = 0;", 1),
    (
        b"CTime next = CTime(now.GetYear(), now.GetMonth(), now.GetDay(), 0, 0, dwAdd);",
        b"CTime midnight(now.GetYear(), now.GetMonth(), now.GetDay(), 0, 0, 0);\r\n"
        b"\t\t\tCTime next(midnight.GetTime() + dwAdd);",
        1,
    ),
]
for old, new, expected in changes:
    if data.count(old) != expected:
        raise RuntimeError(f"Unexpected source site count for {old!r}")
    data = data.replace(old, new)

output.write_bytes(data)
print("Created clean Map handler copy with four declarations and mission time fix")
