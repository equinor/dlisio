import dlisio

from . import DWL206

def test_frame_getitem(DWL206):
    key = dlisio.core.fingerprint('FRAME', '2000T', 2, 0)
    curves = DWL206.curves(key)

    expected = [16677259.0, 852606.0, 2233.0, 852606.0]

    assert list(curves[0]) == expected

    assert curves['TIME'][0] == 16677259.0
    assert curves[0]['TIME'] == 16677259.0

    assert curves['TDEP'][0] == 852606.0
    assert curves[0]['TDEP'] == 852606.0

def test_duplicated_mnemonics_gets_unique_labels():
    time0 = dlisio.plumbing.Channel()
    time0.name = 'TIME'
    time0.origin = 0
    time0.copynumber = 0
    time0.dimension = [1]
    time0.reprc = 2 # f4

    tdep = dlisio.plumbing.Channel()
    tdep.name = 'TDEP'
    tdep.origin = 0
    tdep.copynumber = 0
    tdep.dimension = [2]
    tdep.reprc = 13 # i2

    time1 = dlisio.plumbing.Channel()
    time1.name = 'TIME'
    time1.origin = 1
    time1.copynumber = 0
    time1.dimension = [1]
    time1.reprc = 13 # i2

    frame = dlisio.plumbing.Frame()
    frame.channels = [time0, tdep, time1]

    assert 'fDDD' == frame.fmtstr()
    assert ('TIME:0:0', 'TDEP', 'TIME:1:0') == frame.dtype.names
