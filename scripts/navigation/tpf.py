"""Read the DWORD/float path flags consumed by CTClientMAP::LoadTFLAG.

TPF flag heights are navigation positions, not automatically ground heights.
The source generator adds TPATH_HEIGHT (0.3) to sampled ground heights.
"""
from dataclasses import dataclass
import math
from pathlib import Path
import struct

PATH_HEIGHT = 0.3


@dataclass(frozen=True)
class Flag:
    position: tuple[float, float, float]
    neighbors: tuple[int, ...]


def decode(data: bytes) -> dict[int, Flag]:
    if len(data) < 4 or len(data) > 64 * 1024 * 1024:
        raise ValueError('Invalid TPF byte length')
    count, = struct.unpack_from('<I', data)
    if count > 200_000 or count > (len(data) - 4) // 20:
        raise ValueError('TPF count exceeds bounded record space')
    flags = {}
    offset = 4
    for _ in range(count):
        if offset + 20 > len(data):
            raise ValueError('Truncated TPF flag')
        ident, x, y, z, degree = struct.unpack_from('<IfffI', data, offset)
        offset += 20
        if ident in flags:
            raise ValueError('Duplicate TPF flag ID')
        if not all(math.isfinite(v) and abs(v) < 1_000_000 for v in (x, y, z)):
            raise ValueError('Nonfinite or implausible TPF position')
        if degree > 16384 or degree > (len(data) - offset) // 4:
            raise ValueError('TPF adjacency exceeds remaining bytes')
        neighbors = struct.unpack_from('<' + 'I' * degree, data, offset)
        offset += 4 * degree
        flags[ident] = Flag((x, y, z), neighbors)
    if offset != len(data):
        raise ValueError('Unexplained trailing TPF bytes')
    return flags


def encode(flags: dict[int, Flag]) -> bytes:
    parts = [struct.pack('<I', len(flags))]
    for ident, flag in flags.items():
        parts.append(struct.pack('<IfffI', ident, *flag.position, len(flag.neighbors)))
        parts.append(struct.pack('<' + 'I' * len(flag.neighbors), *flag.neighbors))
    return b''.join(parts)


def read(path: Path) -> dict[int, Flag]:
    data = path.read_bytes()
    flags = decode(data)
    if encode(flags) != data:
        raise ValueError('TPF field roundtrip differs')
    return flags
