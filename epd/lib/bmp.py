import utime
import sys

class BMPHeader:
    SIZE = 0x2
    RESERVED = 0x6
    OFFSET = 0xa
    END = 0xe

    MAGIC_NUMBERS = {
        b'BM', # Windows 3.x, 9x, NT (3.1 to 11)
        b'BA', # OS/2 struct bitmap array
        b'CI', # OS/2 struct colour icon
        b'CP', # OS/2 const colour pointer
        b'IC', # OS/2 struct icon
        b'PT'  # OS/2 pointer
    }

    # header is only supposed to be 14 bytes so throw away all other data
    def __init__(self, header):
        if header[:self.SIZE] not in self.MAGIC_NUMBERS:
            raise ValueError("Invalid header magic number; valid magic numbers are b'BM', b'BA', b'CI', b'CP', b'IC', and b'PT'")
        self.size = header[self.SIZE:self.RESERVED]
        self.offset = header[self.OFFSET:self.END]

    
        