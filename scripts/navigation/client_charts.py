"""Bounded readers for the installed client's region/NPC/minimap/portal charts."""
from pathlib import Path
import struct


class Reader:
    def __init__(self,data):
        self.data=data;self.offset=0

    def read(self,fmt):
        size=struct.calcsize('<'+fmt)
        if self.offset+size>len(self.data):
            raise ValueError('Truncated client chart')
        value=struct.unpack_from('<'+fmt,self.data,self.offset);self.offset+=size
        return value[0] if len(value)==1 else value

    def string(self):
        length=self.read('B');wide=False
        if length==255:
            length=self.read('H')
            if length==0xfffe:
                wide=True;length=self.read('B')
                if length==255:length=self.read('H')
            if length==65535:length=self.read('I')
        size=length*(2 if wide else 1)
        if length>8192 or self.offset+size>len(self.data):
            raise ValueError('Invalid chart string')
        value=self.data[self.offset:self.offset+size].decode('utf-16le' if wide else 'cp1252',errors='strict')
        self.offset+=size
        return value

    def finish(self):
        if self.offset!=len(self.data):
            raise ValueError('Client chart has trailing bytes')


def regions(path:Path):
    r=Reader(path.read_bytes());out={}
    for _ in range(r.read('H')):
        ident=r.read('I');name=r.string();country,fly,local=r.read('BBH')
        thumbs=r.read('9f');r.read('BIIIB')
        if ident in out:raise ValueError('Duplicate region ID')
        out[ident]={'id':ident,'name':name,'country':country,'thumbs':thumbs}
    r.finish();return out


def npcs(path:Path):
    r=Reader(path.read_bytes());out=[];seen=set()
    for _ in range(r.read('H')):
        ident,temp=r.read('IH');name=r.string();title=r.string();flags=r.read('12B')
        r.read('4I');r.read('HI');numbers=r.read('10f');r.read('B')
        if ident in seen:raise ValueError('Duplicate NPC ID')
        seen.add(ident)
        out.append({'id':ident,'template':temp,'name':name,'title':title,'type':flags[0],
                    'country':flags[3],'position':list(numbers[1:4])})
    r.finish();return out


def minimaps(path:Path):
    r=Reader(path.read_bytes());out={}
    for _ in range(r.read('H')):
        ident,texture,scale,x,z,world,button,level=r.read('IIfffBIB')
        if ident in out:raise ValueError('Duplicate minimap ID')
        out[ident]={'id':ident,'texture':texture,'scale':scale,'x':x,'z':z,'world':world,'button':button,'level':level}
    r.finish();return out


def portals(path:Path):
    r=Reader(path.read_bytes());out={}
    for _ in range(r.read('H')):
        ident=r.read('H');name=r.string();region=r.read('H')
        if ident in out:raise ValueError('Duplicate portal ID')
        out[ident]={'id':ident,'name':name,'portalRegion':region}
    r.finish();return out


def maps(path:Path):
    r=Reader(path.read_bytes());out={}
    for _ in range(r.read('H')):
        ident,resource=r.read('II');transform=r.read('9f');dungeon,call=r.read('BB')
        out[ident]={'id':ident,'resource':resource,'transform':transform,'dungeon':dungeon}
    r.finish();return out
