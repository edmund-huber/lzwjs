#!/usr/bin/python

import base64
import struct
import sys

# read in some ASCII

input = sys.stdin.read()
print >> sys.stderr, 'read %s characters' % len(input)
try:
    input.encode('ascii')
except:
    print >> sys.stderr, 'script was not ascii-encodable!'
    sys.exit(1)

# encode LZW

encoded = []
w = input[0]
d = dict([(chr(c), c) for c in range(0, 256)])
c = 256
if len(input[1:]) > 0:
    for i in input[1:]:
        wi = w + i
        if wi in d:
            w = wi
        else:
            encoded.append(d[w])
            d[wi] = c
            c += 1
            w = i
    encoded.append(d[w])

# output base64/LZW decoder

data_b64 = base64.b64encode(''.join([struct.pack('H', c) for c in encoded]))

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
	var table = {};
	for (var i = 0; i < 256; i++) {
		table[i] = String.fromCharCode(i);
	}
	var old_c = (d[1] << 8) | d[0];
	var decoded = table[old_c];
	var c = old_c;
	var count = 256;
	for (var i = 2; i < d.length; i+=2) {
		var new_c = (d[i+1] << 8) | d[i+0];
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
