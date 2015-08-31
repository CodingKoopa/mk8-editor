"""
Copyright (C) 2015, NWPlayer123
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, pulverize, distribute,
synergize, compost, defenestrate, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO BLAH BLAH BLAH ISN'T IT FUNNY
HOW UPPER-CASE MAKES IT SOUND LIKE THE LICENSE IS ANGRY AND SHOUTING AT YOU."""

############################################################
### This script is based on SARCUnpack v0.2 by NWPlayer. ###
### It was modified by Kinnay in order to get much       ###
### faster decompression speeds.                         ###
############################################################

import struct
unpack = struct.unpack

def uint16(data, pos):
    return unpack(">H", data[pos:pos + 2])[0]
def uint24(data, pos):
    return unpack(">I", "\00" + data[pos:pos + 3])[0] #HAX
def uint32(data, pos):
    return unpack(">I", data[pos:pos + 4])[0]

def decompress(data):
    assert data[:4] == "Yaz0"
    pos = 16
    size = uint32(data, 4)
    out = [];dstpos = 0
    bits = 0
    while len(out) < size: #Read Entire File
        if bits == 0:
            code = ord(data[pos]);pos += 1;bits = 8
        if (code & 0x80) != 0: #Copy 1 Byte
            out.append(data[pos]);pos += 1
        else:
            rle = uint16(data, pos);pos += 2
            dist = rle & 0xFFF
            dstpos = len(out) - (dist + 1)
            read = (rle >> 12)
            if read == 0:
                read = ord(data[pos])+0x12;pos += 1
            else:
                read += 2
            for x in xrange(read):
                out.append(out[dstpos + x])
        code <<= 1;bits -= 1
    return ''.join(out)
