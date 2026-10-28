"""Bounded parser for the current OldSchool TMon.tcd layout."""
import struct

def parse(data):
    pos = 0

    def read(fmt):
        nonlocal pos
        size = struct.calcsize("<" + fmt)
        if pos + size > len(data):
            raise ValueError(f"TMon ends inside field at {pos}")
        values = struct.unpack_from("<" + fmt, data, pos)
        pos += size
        return values[0] if len(values) == 1 else values

    def string():
        nonlocal pos
        length = read("B")
        wide = False
        if length == 255:
            length = read("H")
            if length == 0xfffe:
                wide = True
                length = read("B")
                if length == 255:
                    length = read("H")
            if length == 65535:
                length = read("I")
        size = length * (2 if wide else 1)
        if length > 1000 or pos + size > len(data):
            raise ValueError(f"bad TMon string at {pos}")
        result = data[pos:pos + size].decode("utf-16le" if wide else "cp1252", "replace")
        pos += size
        return result

    count = read("H")
    records = {}
    for _ in range(count):
        start = pos
        monster_id, kind = read("HH")
        title = string()
        name_start = pos
        name = string()
        name_end = pos
        read("fff")
        obj_offset = pos - start
        obj = read("I")
        equip_offset = pos - start
        equip = read("19H")
        skill_offset = pos - start
        skills = read("4H")
        flags = read("8B")
        read("I")
        size_offset = pos - start
        size = read("f")
        read("3f11B")
        if monster_id in records:
            raise ValueError(f"duplicate TMon ID {monster_id}")
        if not 0 <= size <= 100:
            raise ValueError(f"implausible monster size {monster_id}: {size}")
        records[monster_id] = {
            "raw": data[start:pos], "kind": kind, "title": title, "name": name,
            "name_start": name_start-start, "name_end": name_end-start,
            "obj_offset": obj_offset, "obj": obj, "equip_offset": equip_offset,
            "equip": equip, "skill_offset": skill_offset, "skills": skills,
            "flags": flags, "size_offset": size_offset,
        }
    if pos != len(data):
        raise ValueError(f"TMon has {len(data)-pos} unexplained trailing bytes")
    return records

