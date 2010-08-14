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

data_b64 = base64.b64encode(encoded)
print >> sys.stderr, '%iB ..encypt.. %i codes, %iB ..pack.. %iB' % (len(input), o, len(encoded), len(data_b64))
print >> sys.stderr, 'ratio: %f' % (len(data_b64) / float(len(input)))

print """

var d = '%s';

// given a base64-encoded string, returns a list of bytes
var from_base64 = function(s) {
	var b64 = function(c) {
		if (c.match(/[A-Z]/))
			return c.charCodeAt(0) - 'A'.charCodeAt(0);
		else if (c.match(/[a-z]/))
			return c.charCodeAt(0) - 'a'.charCodeAt(0) + 26;
		else if (c.match(/[0-9]/))
			return c.charCodeAt(0) - '0'.charCodeAt(0) + 52;
		else if (c === '+')
			return 62;
		else if (c === '/')
			return 63;
		else if (c === '=')
			return 0;
		else throw 'bad base64 encoding! (' + c + ')';
	};
	var d = [];
	for (var i = 0; i < s.length; i += 4) {
		d.push(((b64(s[i+0]) << 2) | (b64(s[i+1]) >> 4)) & 0xff);
		d.push(((b64(s[i+1]) << 4) | (b64(s[i+2]) >> 2)) & 0xff);
		d.push(((b64(s[i+2]) << 6) | (b64(s[i+3]) >> 0)) & 0xff);
	}
	return d;
};

var decode_lzw = function(d) {
	// get the header -- number of codes
	var total = (d[1] << 8) | d[0];

	// initialize the lookup table
	var table = {};
	for (var i = 0; i < 128; i++) {
		table[i] = String.fromCharCode(i);
	}

	var getBits = function(s, p, c) {
		var bits = 0;
		for (var i = 0; i < c; i++) {
			var b = (s[((p + i) / 8) >> 0] >> (7 - ((p + i) %% 8))) & 1;
			bits = bits | (b << (c - i - 1));
		}
		return bits;
	};

	// decode
	var old_c = getBits(d, 16, 7);
	var decoded = table[old_c];
	var pos = 23;
	var wid = 7;
	var c = old_c;
	var count = 128;
	for (var i = 0; i < total; i++) {
		wid = Math.ceil(Math.log(count + 1) / Math.log(2));
		var new_c = getBits(d, pos, wid);
		pos += wid;
		var s;
		if (!table[new_c]) {
			s = table[old_c] + c;
		}else{
			s = table[new_c];
		}
		decoded += s;
		c = s[0];
		table[count++] = table[old_c] + c;
		old_c = new_c;
	}
	return decoded;
};

console.log('decode_lzw(from_base64(d)) = ' + decode_lzw(from_base64(d)));

""" % data_b64;
