class BMPHeader:
    offsets = {
        'SIZE': 0x2,
        'RESERVED': 0x6,
        'OFFSET': 0xa,
        'END': 0xe,
        'WIDTH': 0x12,
        'HEIGHT': 0x16,
        'COLOUR_PLANE': 0x1a,
        'COLOUR_BIT_DEPTH': 0x1c,
        'COMPRESSION': 0x1e,
        'IMAGE_SIZE': 0x22,
        'X_PPM': 0x26,
        'Y_PPM': 0x2a,
        'NUM_COLOURS': 0x2e,
        'SIG_COLOURS': 0x32,
        'STOP': 0x36
    }

    MAGIC_NUMBER = b'BM'

    # header is actually 54 bytes
    def __init__(self, header):
        if header[:self.offsets['SIZE']] != self.MAGIC_NUMBER:
            raise ValueError("Invalid header magic number")
        if header[self.offsets['COLOUR_PLANE']:self.offsets['COLOUR_BIT_DEPTH']] != 1:
            raise ValueError("Bitmap headers specify only one colour plane")
        if header[self.offsets['COLOUR_BIT_DEPTH']:self.offsets['COMPRESSION']] != 1:
            raise ValueError("Monochrome display; only two colours")
        if header[self.offsets['COMPRESSION']:self.offsets['IMAGE_SIZE']] != 0:
            raise ValueError("Compression is not supported on this device")
        if header[self.offsets['NUM_COLOURS']:self.offsets['SIG_COLOURS']] > 1:
            raise ValueError("Monochrome display; only two colours max")
        if header[self.offsets['SIG_COLOURS']:self.offsets['STOP']] > 1:
            raise ValueError("CMonochrome display; only two significant colours max")
        
        self.size = int.from_bytes(header[self.offsets['SIZE']:self.offsets['RESERVED']], 'little')
        self.offset = int.from_bytes(header[self.offsets['OFFSETS']:self.offsets['END']], 'little')
        self.width = int.from_bytes(header[self.offsets['WIDTH']:self.offsets['HEIGHT']], 'little')
        self.height = int.from_bytes(header[self.offsets['HEIGHT']:self.offsets['COLOUR_PLANE']], 'little')