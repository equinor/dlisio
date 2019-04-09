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
