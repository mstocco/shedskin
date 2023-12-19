import struct


def test_unpack():
    a, = struct.unpack("<h", b'\x00\n')
    assert a == 2560

    a, b, c = struct.unpack('>bhl', b'\x01\x00\x02\x00\x00\x00\x03')
    assert (a, b, c) == (1, 2, 3)

    a, b, c, d, e, f, g, h = struct.unpack("<BBHHHII16s", 32 * b"0")
    assert (a, b, c, d, e, f, g) == (48, 48, 12336, 12336, 12336, 808464432, 808464432)
    assert h == b'0000000000000000'

    header_format = "<32s2BHHH24s"
    h, a, b, c, d, e, i = struct.unpack(header_format, 64 * b"0")
    assert h == b'00000000000000000000000000000000'
    assert (a, b, c, d, e) == (48, 48, 12336, 12336, 12336)
    assert i == b'000000000000000000000000'

    version = [0, 0]
    (
         magic,
         version[0],
         version[1],
         max_files,
         cur_files,
         reserved,
         user_description,
    ) = struct.unpack(header_format, 64 * b"0")
    assert magic == b'00000000000000000000000000000000'
    assert version == [48, 48]
    assert cur_files == 12336


def test_int():
    assert struct.pack(">h", 10) == b'\x00\n'

    packer = struct.pack(">HH", 1, 2)
    assert packer == b'\x00\x01\x00\x02'

    packer = struct.pack("<HH", 1, 2)
    assert packer == b'\x01\x00\x02\x00'
    (p0, p1) = struct.unpack("<HH", packer)
    assert p0 == 1
    assert p1 == 2

    packer = struct.pack('!I', True)
    ii, = struct.unpack('!I', packer)
    assert ii == 1
    packer = struct.pack('!I', False)
    ii, = struct.unpack('!I', packer)
    assert ii == 0


def test_d():
    packer = struct.pack("<d", 949.1)
    d, = struct.unpack("<d", packer)
    assert d == 949.1

    packer = struct.pack("<d", 12)
    d, = struct.unpack("<d", packer)
    assert d == 12.0


def test_c():
    packer = struct.pack(">c", b'a')
    a, = struct.unpack(">c", packer)
    assert a == b'a'


def test_s():
    packer = struct.pack("!12s", b'abcdefghijkl')
    s, = struct.unpack("!12s", packer)
    assert s == b'abcdefghijkl'


def test_p():
    # combinations of digits, arg lengths..
    packer = struct.pack('0p', b'wop')
    assert packer == b''
#x, = struct.unpack('0p', packer)
#assert x == b''

    packer = struct.pack('1p', b'wop')
    assert packer == b'\x00'
    x, = struct.unpack('1p', packer)
    assert x == b''

    packer = struct.pack('p', b'wop')
    assert packer == b'\x00'
    x, = struct.unpack('p', packer)
    assert x == b''

    packer = struct.pack('2p', b'wop')
    assert packer == b'\x01w'
    x, = struct.unpack('2p', packer)
    assert x == b'w'

    packer = struct.pack('3p', b'wop')
    assert packer == b'\x02wo'
    x, = struct.unpack('3p', packer)
    assert x == b'wo'

    packer = struct.pack('4p', b'wop')
    assert packer == b'\x03wop'
    x, = struct.unpack('4p', packer)
    assert x == b'wop'

    packer = struct.pack('5p', b'wop')
    assert packer == b'\x03wop\x00'
    x, = struct.unpack('5p', packer)
    assert x == b'wop'

    packer = struct.pack('10p', b'wop')
    assert packer == b'\x03wop\x00\x00\x00\x00\x00\x00'
    orig, = struct.unpack('10p', packer)
    assert orig == b'wop'

    # 255 char limit
    packer = struct.pack('300p', 290*b'w')
    assert packer == b'\xff' + 290*b'w' + 9 * b'\x00'
    p, = struct.unpack('300p', packer)
    assert p == 255*b'w'


def test_unpack_issue():
    s = struct.pack('>I', 12000)
    n, = struct.unpack('>I', s)
    assert n == 12000

    s = struct.pack('>i', -12000)
    n, = struct.unpack('>i', s)
    assert n == -12000


def test_unpack_from():
    data = b'\xf0\x04\x00\x00\x01\x02'
    n, = struct.unpack_from('<I', data)
    assert n == 1264


def test_pack_into():
    bla = bytearray(10)
    struct.pack_into('<hh', bla, 4, 17, 18)
    a, b = struct.unpack_from('<hh', bla, 4)
    assert a == 17 and b == 18


def test_calcsize():
    assert struct.calcsize('>bhl') == 7
    assert struct.calcsize(">HH") == 4
    assert struct.calcsize("<32s2BHHH24s") == 64
    assert struct.calcsize("!c3q2b3d") == 51


def test_repeat():
    packer = struct.pack("<3c", b'a', b'a', b'p')
    d, e, f, = struct.unpack("<3c", packer)
    assert b''.join([d, e, f]) == b'aap'


def test_errors():
    error = ''
    try:
        packer = struct.pack("!H", b'hop')
    except struct.error as e:
        error = str(e)
    assert error == 'required argument is not an integer'

    error = ''
    try:
        packer = struct.pack("d", b'hop')
    except struct.error as e:
        error = str(e)
    assert error == 'required argument is not a float'

    error = ''
    try:
        packer = struct.pack("p", 18.8)
    except struct.error as e:
        error = str(e)
    assert error == "argument for 'p' must be a bytes object"

    error = ''
    try:
        struct.pack('hh', 1, 2, 3)
    except struct.error as e:
        error = str(e)
    assert error == 'pack expected 2 items for packing (got 3)'

    error = ''
    try:
        struct.pack('hh', 1)
    except struct.error as e:
        error = str(e)
    assert error == 'pack expected 2 items for packing (got 1)'

    error = ''
    try:
        struct.pack('c', 18)
    except struct.error as e:
        error = str(e)
    assert error == 'char format requires a bytes object of length 1'

    error = ''
    try:
        struct.pack('c', b'bla')
    except struct.error as e:
        error = str(e)
    assert error == 'char format requires a bytes object of length 1'


def test_multi_1():
    packer = struct.pack("<c3q2b3d", b"\xd5", 39, 77, 77, 55, 50, 949.0, 544.2, 444.3)
    (a, b, c, d, e, f, g, h, i) = struct.unpack("<c3q2b3d", packer)
    assert a == b"\xd5"
    assert (b, c, d, e, f) == (39, 77, 77, 55, 50)
    assert (g, h, i) == (949.0, 544.2, 444.3)


def test_order():
    a = struct.pack('<H', 19)
    assert a[0] == 19
    assert a[1] == 0

    b = struct.pack('>H', 19)
    assert b[0] == 0
    assert b[1] == 19

    a = struct.pack('<d', 19.20)
    b = struct.pack('>d', 19.20)
    assert a == b[::-1]


def test_all():
    test_unpack()
    test_unpack_from()
    test_unpack_issue()
    test_int()
    test_d()
    test_c()
    test_s()
    test_p()
    test_repeat()
    test_pack_into()
    test_calcsize()
    test_errors()
    test_multi_1()
    test_order()


if __name__ == '__main__':
    test_all()
