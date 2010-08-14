var lzwjs = {};
lzwjs.input = '%(base64_data)s';

// given a base64-encoded string, returns a list of bytes
lzwjs.from_base64 = function(s) {
    var b64 = function(c) {
        if(c.match(/[A-Z]/)) {
            return c.charCodeAt(0) - 'A'.charCodeAt(0);
        } else if(c.match(/[a-z]/)) {
            return c.charCodeAt(0) - 'a'.charCodeAt(0) + 26;
        } else if(c.match(/[0-9]/)) {
            return c.charCodeAt(0) - '0'.charCodeAt(0) + 52;
        } else if(c === '+') {
            return 62;
        } else if(c === '/') {
            return 63;
	} else if(c === '=') {
            return 0;
        } else {
            throw 'bad base64 encoding! (' + c + ')';
        }
    };
    var d = [];
    for(var i = 0; i < s.length; i += 4) {
        d.push(((b64(s[i+0]) << 2) | (b64(s[i+1]) >> 4)) & 0xff);
        d.push(((b64(s[i+1]) << 4) | (b64(s[i+2]) >> 2)) & 0xff);
        d.push(((b64(s[i+2]) << 6) | (b64(s[i+3]) >> 0)) & 0xff);
    }
    return d;
};

lzwjs.decode_lzw = function(d) {
    // get the header -- number of codes
    var total = (d[1] << 8) | d[0];

    // initialize the lookup table
    var table = {};
    for (var i = 0; i < 128; i++) {
        table[i] = String.fromCharCode(i);
    }

    var getBits = function(s, p, c) {
        var bits = 0;
        for(var i = 0; i < c; i++) {
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
    for(var i = 0; i < total - 1; i++) {
        wid = Math.ceil(Math.log(count + 1) / Math.log(2));
        var new_c = getBits(d, pos, wid);
        pos += wid;
        var s;
        if (!table[new_c]) {
            s = table[old_c] + c;
        } else {
            s = table[new_c];
        }
        decoded += s;
        c = s[0];
        table[count++] = table[old_c] + c;
        old_c = new_c;
    }
    return decoded;
};

eval(lzwjs.decode_lzw(lzwjs.from_base64(lzwjs.input)));
