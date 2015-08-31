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
### It was modified by Kinnay to fit the SM3DW editor    ###
############################################################

import struct

def uint16(data, pos):
    return struct.unpack(">H", data[pos:pos + 2])[0]
def uint24(data, pos):
    return struct.unpack(">I", "\00" + data[pos:pos + 3])[0] #HAX
def uint32(data, pos):
    return struct.unpack(">I", data[pos:pos + 4])[0]
def getstr(data):
    x = data.find("\x00")
    if x != -1:
        return data[:x]
    else:
        return data
 
def extract(data,fn):
    pos = 6
    magic = data[:4]
    assert magic == 'SARC'
    if uint16(data,pos) != 0xFEFF: #Big Endian
        raise ValueError,"Little endian not supported!"
    pos+=6
    doff = uint32(data, pos);pos += 8 #Start of data section
    #---------------------------------------------------------------
    magic2 = data[pos:pos + 4];pos += 6
    assert magic2 == 'SFAT'
    nodec = uint16(data, pos);pos += 6 #Node Count
    nodes = []
    for x in xrange(nodec):
        pos+=8
        srt  = uint32(data, pos);pos += 4 #File Offset Start
        end  = uint32(data, pos);pos += 4 #File Offset End
        nodes.append([srt, end])
    #---------------------------------------------------------------
    magic3 = data[pos:pos + 4];pos += 8
    assert magic3 == 'SFNT'
    strings = []
    for x in xrange(nodec):
        string = getstr(data[pos:]);pos += len(string)
        while ord(data[pos]) == 0: pos += 1 #Move to the next string
        strings.append(string)
    x = strings.index(fn)
    return data[nodes[x][0]+doff:nodes[x][1]+doff]

def contains(data,fn):
    try:
        extract(data,fn)
        return True
    except ValueError:
        return False
