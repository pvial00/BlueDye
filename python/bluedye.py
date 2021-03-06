class BlueDye:
    keylen = 32
    noncelen = 16
    def keysetup(self, key, nonce):
        s = range(256)
        k = [0] * self.keylen
        j = 0
        klen = self.keylen
        for c, char in enumerate(key):
            k[c] = (k[c] + ord(char)) & 0xff
            j = (j + k[c]) & 0xff
        for c in range(768):
            k[c % klen] = (k[c % klen] + j) & 0xff
            j = (j + k[c % klen]) & 0xff
            s[c], s[j] = s[j], s[c]
        if nonce != "":
            for c, char in enumerate(nonce):
                k[c] = (k[c] + ord(char)) & 0xff
                j = (j + k[c]) & 0xff
            for c in range(256):
                k[c % klen] = (k[c % klen] + j) & 0xff
                j = (j + k[c % klen]) & 0xff
                s[c], s[j] = s[j], s[c]
        return k, j, s

    def crypt(self, data, key, nonce="", test=1):
        ctxt = []
        k, j, s = self.keysetup(key, nonce)
        klen = len(k)
        c = i = 0
        for byte in data:
            k[i] = (k[i] + k[(i + 1) % klen] + j) & 0xff
            j = (j + k[i] + c) & 0xff
            output = s[j] ^ k[i]
            s[c], s[j] = s[j], s[c]
            sub = ((ord(byte)) ^ output) & 0xff
            c = (c + 1) & 0xff
            ctxt.append(chr(sub))
        return "".join(ctxt)
    
    def kdf(self, key, iterations=10):
        if len(key) < self.keylen:
            for x in range(self.keylen - len(key)):
                key += chr(0)
        for i in range(iterations):
            key = self.crypt(key, key)
        return key

    def mac(self, data, key):
        h = [0] * 32
        c = 0
        for x in range(2):
            key = self.kdf(key)
            key = self.kdf(key)
        for byte in data:
            h[c] = (h[c] + ord(byte)) & 0xff
            c = (c + 1) % 32
        return mac

    def random(self, num_bytes=1):
        from os import urandom
        char = chr(0)
        key = urandom(self.keylen)
        nonce = urandom(self.noncelen)
        key = self.kdf(key)
        ptxt = []
        for x in range(num_bytes):
            ptxt.append(char)
        return self.crypt("".join(ptxt), key, nonce)
