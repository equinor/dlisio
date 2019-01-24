import pytest

import dlisio

def test_sul():
    label = ''.join([
                '   1',
                'V1.00',
                'RECORD',
                ' 8192',
                'Default Storage Set                                         ',
            ])

    sul = dlisio.core.sul(label)
    d = {
        'sequence': 1,
        'version': '1.0',
        'maxlen': 8192,
        'layout': 'record',
        'id': 'Default Storage Set                                         ',
    }

    assert sul == d

    with dlisio.load('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS') as f:
        assert f.sul == d

def test_file_properties():
    with dlisio.load('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS') as f:
        assert len(f.bookmarks) == 3252

# The example record from the specification
stdrecord = bytearray([
    # The eflr function assumes unsegmented record
    # # segment header #1
    # 0x00, 0x68, # length = 104
    # 0xA6,       # attributes
    # 0x03,       # type = CHANNL

    # channel set
    0xF8,       # SET:TN
    0x07, 0x43, 0x48, 0x41, 0x4E, 0x4E, 0x45, 0x4C, # "CHANNEL"
    0x01, 0x30, # "0"

    # template
    0x34,       # ATTRIB:LR
    # "LONG-NAME"
    0x09, 0x4C, 0x4F, 0x4E, 0x47, 0x2D, 0x4E, 0x41, 0x4D, 0x45,
    0x17,       # OBNAME

    0x35,       # ATTRIB:LRV
    # "ELEMENT-LIMIT"
    0x0D, 0x45, 0x4C, 0x45, 0x4D, 0x45, 0x4E, 0x54, 0x2D, 0x4C,
    0x49, 0x4D, 0x49, 0x54,
    0x12,       # UVARI
    0x01,       # 1

    0x35,       # ATTRIB: LRV
    # "REPRESENTATION-CODE
    0x13, 0x52, 0x45, 0x50, 0x52, 0x45, 0x53, 0x45, 0x4E, 0x54,
    0x41, 0x54, 0x49, 0x4F, 0x4E, 0x2D, 0x43, 0x4F, 0x44, 0x45,
    0x0F,       # USHORT
    0x02,       # FSINGL

    0x30,       # ATTRIB: L
    0x05, 0x55, 0x4E, 0x49, 0x54, 0x53, # "UNITS"

    0x35,       # ATTRIB: LRV
    # "DIMENSION"
    0x09, 0x44, 0x49, 0x4D, 0x45, 0x4E, 0x53, 0x49, 0x4F, 0x4E,
    0x12,       # UVARI
    0x01,       # 1

    # object #1
    0x70,       # OBJECT:N
    0x00, 0x00, 0x04, 0x54, 0x49, 0x4D, 0x45, # (0, 0, "TIME")
    0x21, 0x00, 0x00, 0x01, 0x31,             # "1"

    # # segment trailer #1
    # 0x00, 0x00, # CHECKSUM, not checked yet
    # 0x00, 0x68, # length = 104

    # # segment header #2
    # 0x00, 0x26, # length = 38
    # 0xE7,
    # 0x03,

    # ATTRIB: x2
    0x20,
    0x20,

    0x21,       # ATTRIB: V
    0x01, 0x73, # 1

    # object #2
    0x70,
    # (1, 0, "PRESSURE")
    0x01, 0x00, 0x08, 0x50, 0x52, 0x45, 0x53, 0x53, 0x55, 0x52, 0x45,

    0x21,   # 0,0, "2"
    0x00, 0x00, 0x01, 0x32,

    0x20,   # ATTRIB:

    0x21, 0x07,

    0x21,
    0x03, 0x70, 0x73, 0x69, # "psi"

    # # segment trailer #2
    # 0x00, 0x00, # CHECKSUM, not cheched yet
    # 0x00, 0x26, # length = 38

    # # segment header #3
    # 0x00, 0x26, # length = 38
    # 0xC7,
    # 0x03,

    0x70,
    # "PAD-ARRAY"
    0x00, 0x01, 0x09, 0x50, 0x41, 0x44, 0x2D, 0x41, 0x52, 0x52, 0x41, 0x59,

    0x21,
    0x00, 0x00, 0x01, 0x33, # 0, 0, "3"

    0x29,
    0x02,
    0x08, 0x14, # [8, 20]

    0x21,
    0x0D,       # UNORM

    0x00,       # ABSENT

    0x29,
    0x02,
    0x08, 0x0A, # [8, 10]

    # # segment trailer #3
    # 0x01, # pad-count
    # 0x00, 0x00,
    # 0x00, 0x26, # length = 38
])

def test_parse_eflr_bytes():
    objects = dlisio.core.eflr(stdrecord)['objects']
    names = set([ (0, 0, 'TIME'),
                  (1, 0, 'PRESSURE'),
                  (0, 1, 'PAD-ARRAY'),
                ])
    assert set(objects.keys()) == names

    def dictify(xs):
        return { x['label']: x.get('value') for x in xs }

    time = dictify(objects[(0, 0, 'TIME')])
    dtime = {
        'LONG-NAME': [(0, 0, '1')],
        'ELEMENT-LIMIT': [1],
        'REPRESENTATION-CODE': [2],
        'UNITS': ['s'],
        'DIMENSION': [1],
    }

    assert dtime == time

    pressure = dictify(objects[(1, 0, 'PRESSURE')])
    dpressure = {
        'LONG-NAME': [(0, 0, '2')],
        'ELEMENT-LIMIT': [1],
        'REPRESENTATION-CODE': [7],
        'UNITS': ['psi'],
        'DIMENSION': [1],
    }

    assert dpressure == pressure

    pad = dictify(objects[(0, 1, 'PAD-ARRAY')])
    dpad = {
        'LONG-NAME': [(0, 0, '3')],
        'ELEMENT-LIMIT': [8, 20],
        'REPRESENTATION-CODE': [13],
        'UNITS': None,
        'DIMENSION': [8, 10],
    }

    assert dpad == pad

def test_parse_eflr_bytes_truncated():
    with pytest.raises(ValueError):
        empty = dlisio.core.eflr(bytes([]))

    with pytest.raises(ValueError):
        only_set = dlisio.core.eflr(stdrecord[:1])

def test_read_eflr_metadata():
    with dlisio.load('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS') as f:
        record = f.fp.eflr(f.bookmarks[2])
        assert record.name == '51'
        assert record.type == 'EQUIPMENT'

        record = f.fp.eflr(f.bookmarks[5])
        assert record.name == '54'
        assert record.type == 'TOOL'

        record = f.fp.eflr(f.bookmarks[8])
        assert record.name == '57'
        assert record.type == '440-CHANNEL'

        record = f.fp.eflr(f.bookmarks[9])
        assert record.name == '58'
        assert record.type == 'PARAMETER'

        record = f.fp.eflr(f.bookmarks[11])
        assert record.name == '60'
        assert record.type == 'PARAMETER'

        record = f.fp.eflr(f.bookmarks[13])
        assert record.name == '62'
        assert record.type == 'PARAMETER'

        record = f.fp.eflr(f.bookmarks[15])
        assert record.name == '64'
        assert record.type == 'CALIBRATION-MEASUREMENT'

        record = f.fp.eflr(f.bookmarks[17])
        assert record.name == '72'
        assert record.type == 'CALIBRATION-COEFFICIENT'

        record = f.fp.eflr(f.bookmarks[18])
        assert record.name == '73'
        assert record.type == 'CALIBRATION-COEFFICIENT'

        record = f.fp.eflr(f.bookmarks[19])
        assert record.name == '74'
        assert record.type == 'CALIBRATION'

        record = f.fp.eflr(f.bookmarks[23])
        assert record.name == '78'
        assert record.type == 'PROCESS'

        record = f.fp.eflr(f.bookmarks[24])
        assert record.name == '79'
        assert record.type == '440-OP-CORE_TABLES'

        record = f.fp.eflr(f.bookmarks[25])
        assert record.name == '330'
        assert record.type == '440-OP-CORE_REPORT_FORMAT'

def test_conv():
    dim = bytearray([0x09, 0x44, 0x49, 0x4D, 0x45,
                     0x4E, 0x53, 0x49, 0x4F, 0x4E,
                    ])

    assert dlisio.core.conv(19, dim) == "DIMENSION"

def test_channel_metadata():
    with dlisio.load('data/only-channels.dlis') as f:
        channels = [x for x in f.channels if x.name.id == 'TDEP']
        assert len(channels) == 6
        for ch in channels:
            assert ch.name.id == 'TDEP'

def test_frames_metadata():
    with dlisio.load('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS') as f:
        frames = [fr for fr in f.frames if fr.name.id == '2000T']
        assert len(frames) == 1
        assert frames[0].name.id         == '2000T'
        assert frames[0].name.copynumber == 0
        assert frames[0].name.origin     == 2

def test_channel_matching():
    with dlisio.load('data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS') as f:
        frames = [fr for fr in f.frames if fr.haschannel(id='TDEP')]
        assert len(frames) == 2

        frames = [fr for fr in f.frames if fr.haschannel(origin=2)]
        assert len(frames) == 2

        frames = [fr for fr in f.frames if fr.haschannel(id='TDEP', origin=2)]
        assert len(frames) == 2

        frames = [fr for fr in f.frames if fr.haschannel(id='TDEP', origin=2, copy=4)]
        assert len(frames) == 1
