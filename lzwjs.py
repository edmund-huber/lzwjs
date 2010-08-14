#!/usr/bin/python

import base64
import math
import struct
import sys

# read in some ASCII

input = sys.stdin.read()
try:
    input.encode('ascii')
except:
    print >> sys.stderr, 'script was not ascii-encodable!'
    sys.exit(1)

# encode LZW

class BitWriter:
    def __init__(self):
        self.bytes = []
        self.bits = 0
        self.count = 0
	self.written = 0
    def write_bit(self, bit):
        self.bits = self.bits | (bit << (7 - self.count))
        self.count += 1
        if self.count == 8:
            self.bytes.append(self.bits)
            self.bits = 0
            self.count = 0
	self.written += 1
    def write(self, add_bits, add_count):
        for i in range(0, add_count):
            self.write_bit(1 & (add_bits >> (add_count - i - 1)))
    def __str__(self):
        s = ''.join([struct.pack('B', c) for c in self.bytes])
        if self.count > 0:
            s += struct.pack('B', self.bits)
        return s

writer = BitWriter()
w = input[0]
d = dict([(chr(c), c) for c in range(0, 128)])
c = 128
o = 0
if len(input[1:]) > 0:
    for i in input[1:]:
        wi = w + i
        if wi in d:
            w = wi
        else:
            writer.write(d[w], int(math.ceil(math.log(c, 2))))
            o += 1
            d[wi] = c
            c += 1
            w = i
    writer.write(d[w], int(math.ceil(math.log(c, 2))))
    o += 1
encoded = struct.pack('H', o) + str(writer)

# output base64/LZW decoder

base64_data = base64.b64encode(encoded)
print >> sys.stderr, '%iB ..encypt.. %i codes, %iB ..pack.. %iB' % (len(input), o, len(encoded), len(base64_data))
print >> sys.stderr, 'ratio: %f' % (len(base64_data) / float(len(input)))

decoder = open('lzwjs.js', 'r').read()
print decoder % locals()
