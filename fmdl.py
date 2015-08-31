
"""
Copyright (C) 2015 Yannik Marchand
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY Yannik Marchand ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Yannik Marchand BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation 
are those of the authors and should not be interpreted as representing
official policies, either expressed or implied, of Yannik Marchand.
"""

import struct, math

def String(offs):
    s = ''
    while data[offs] != '\x00':
        s+=data[offs]
        offs+=1
    return s

def UI8(offs):
    return ord(data[offs])

def UI16(offs):
    return struct.unpack_from('>H',data,offs)[0]

def UI24(offs):
    return struct.unpack('>I','\x00'+data[offs:offs+3])[0]

def UI32(offs):
    return struct.unpack_from('>I',data,offs)[0]

## The following HalfToFloat function was made by this guy here:
##   http://forums.devshed.com/python-programming-11/converting-half-precision-floating-hexidecimal-decimal-576842.html
def HalfToFloat(h):
    s = int((h >> 15) & 0x00000001)    # sign
    e = int((h >> 10) & 0x0000001f)    # exponent
    f = int(h & 0x000003ff)            # fraction

    if e == 0:
       if f == 0:
          return int(s << 31)
       else:
          while not (f & 0x00000400):
             f <<= 1
             e -= 1
          e += 1
          f &= ~0x00000400
    elif e == 31:
       if f == 0:
          return int((s << 31) | 0x7f800000)
       else:
          return int((s << 31) | 0x7f800000 | (f << 13))

    e = e + (127 -15)
    f = f << 13

    return int((s << 31) | (e << 23) | f)

def float16(data):
    floats = []
    for i in range(3):
        v = struct.unpack_from('>H',data,i*2)[0]
        x = HalfToFloat(v)
        str = struct.pack('I',x)
        f = struct.unpack('f',str)[0]
        floats.append(f)
    return floats

class FSKL:
    def parse(self,offs):
        self.scale = struct.unpack_from('>fff',data,offs+20)
        self.rot = [math.degrees(r) for r in struct.unpack_from('>fff',data,offs+32)]
        self.trans = struct.unpack_from('>fff',data,offs+48)
        #print self.scale,self.rot,self.trans

class FVTX:
    def parse(self,offs):
        assert data[offs:offs+4] == 'FVTX'
        attrnum = UI8(offs+4)
        buffnum = UI8(offs+5)
        vertnum = UI32(offs+8)
        attroff = offs+16+UI32(offs+16)
        buffoff = offs+24+UI32(offs+24)

        self.parseBuffers(buffoff,buffnum,vertnum)
        self.parsePolygons(attroff,attrnum)

    def parseBuffers(self,offs,bnum,vnum):
        self.buffers = []
        for i in range(bnum):
            size = UI32(offs+4)
            stride = UI16(offs+12)
            dataoff = offs+20+UI32(offs+20)
            buffer = data[dataoff:dataoff+size]
            elements = []
            for j in range(vnum):
                elements.append(buffer[stride*j:stride*(j+1)])
            self.buffers.append(elements)
            offs+=24

    def parsePolygons(self,offs,num):
        self.polygons = []
        self.indices = []
        self.weights = []
        self.transform = False
        for i in range(num):
            nameoff = offs+UI32(offs)
            buffidx = UI8(offs+4)
            buffoff = UI24(offs+5)
            format = UI32(offs+8)
            name = String(nameoff)
            
            if name == '_i0' and format == 0x100:
                self.transform = True

            elif name in ['_p0','_i0','_w0']:
                attributes = []
                elements = self.buffers[buffidx]
                for element in elements:
                    if format == 0x811:
                        attributes.append(struct.unpack_from('>fff',element,buffoff))
                    elif format == 0x80F:
                        attributes.append(float16(element[buffoff:buffoff+6]))
                    elif format == 0x104:
                        attributes.append(struct.unpack_from('BB',element,buffoff))
                    elif format == 0x4:
                        attributes.append([ord(c)/255.0 for c in element[buffoff:buffoff+2]])
                    elif format == 0x10A:
                        attributes.append(struct.unpack_from('BBBB',element,buffoff))
                    elif format == 0xA:
                        attributes.append([ord(c)/255.0 for c in element[buffoff:buffoff+4]])
                    else:
                        raise ValueError,"Unsupported buffer format "+hex(format)
                if name == '_p0': self.polygons.append(attributes)
                elif name == '_i0': self.indices.append(attributes)
                elif name == '_w0': self.weights.append(attributes)
            offs+=12

class FMDL:
    def parse(self,offs):
        skloffs = offs+12+UI32(offs+12)
        vtxoffs = offs+16+UI32(offs+16)
        shpoffs = offs+20+UI32(offs+20)
        vtxcount = UI16(offs+32)
        shpcount = UI16(offs+34)

        self.parseBones(skloffs)
        self.parseVertices(vtxoffs,vtxcount)
        self.parseShapes(shpoffs,shpcount)

    def parseBones(self,offs):
        self.bones = []
        assert data[offs:offs+4] == 'FSKL'
        bonecount = UI16(offs+8)
        boneoffs = offs+20+UI32(offs+20)
        for i in range(bonecount):
            bone = FSKL()
            bone.parse(boneoffs+i*0x40)
            self.bones.append(bone)

    def parseVertices(self,offs,count):
        self.vertices = []
        for i in range(count):
            vertex = FVTX()
            vertex.parse(offs+i*32)
            self.vertices.append(vertex)

    def parseShapes(self,offs,count):
        self.shapes = []
        num = UI32(offs+4)
        assert num == count
        offs+=36
        for i in range(num):
            shape = FSHP(self.bones,self.vertices,i)
            shape.parse(offs+UI32(offs))
            self.shapes.append(shape)
            offs+=16

class FSHP:
    def __init__(self,bones,vertices,x):
        fvtx = vertices[x]
        self.vertices = fvtx.polygons[0]
        self.transform = fvtx.transform
        self.bones = bones

    def parse(self,offs):
        assert data[offs:offs+4] == 'FSHP'
        sectionidx = UI16(offs+12)

        mdloffs = offs+36+UI32(offs+36)
        idxoffs = mdloffs+20+UI32(mdloffs+20)
        size = UI32(idxoffs+4)
        buffoff = idxoffs+20+UI32(idxoffs+20)
        indexbuffer = data[buffoff:buffoff+size]

        self.indices = []
        for i in range(0,size,2):
            index = struct.unpack_from('>H',indexbuffer,i)[0]
            self.indices.append(index)

        if self.transform:
            skloffs = offs+0x28+UI32(offs+0x28)
            bone = self.bones[UI16(skloffs)]
            self.rotation = bone.rot
        else:
            self.rotation = (0,0,0)

def parse(content):
    global data,bytepos
    data = content
    mdlstart = data.index('FMDL')
    mdl = FMDL()
    mdl.parse(mdlstart)
    return mdl