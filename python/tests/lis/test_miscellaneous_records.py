import pytest

from dlisio import lis

@pytest.fixture(scope="module")
def fpath(tmpdir_factory, merge_lis_prs):
    """
    Resulted file contains examples of miscellaneous records known to dlisio.lis
    """
    path = str(tmpdir_factory.mktemp('lis-semantic').join('misc.lis'))
    content = [
        'data/lis/records/RHLR-1.lis.part',
        'data/lis/records/THLR-1.lis.part',
        'data/lis/records/FHLR-1.lis.part',
        'data/lis/records/op-command-inputs.lis.part',
        'data/lis/records/op-response-inputs.lis.part',
        'data/lis/records/system-outputs.lis.part',
        'data/lis/records/flic-comment.lis.part',
        'data/lis/records/FTLR-1.lis.part',
        'data/lis/records/TTLR-1.lis.part',
        'data/lis/records/RTLR-1.lis.part',
    ]
    merge_lis_prs(path, content)
    return path

@pytest.fixture(scope="module")
def f(fpath):
    with lis.load(fpath) as (f, *_):
        yield f


@pytest.mark.xfail(strict=True)
def test_operator_command_inputs(f):
    exp = "Operator Command Inputs: this can be trash or something readable"
    assert len(f.operator_command_inputs()) == 1
    assert f.operator_command_inputs()[0].message == exp

@pytest.mark.xfail(strict=True)
def test_operator_response_inputs(f):
    exp = "Operator Response Inputs: this can be trash or something readable."
    assert len(f.operator_response_inputs()) == 1
    assert f.operator_response_inputs()[0].message == exp

@pytest.mark.xfail(strict=True)
def test_system_outputs_to_operator(f):
    exp = "System Outputs to Operator: trash or not trash?"
    assert len(f.system_outputs_to_operator()) == 1
    assert f.system_outputs_to_operator()[0].message == exp

@pytest.mark.xfail(strict=True)
def test_flic_comment(f):
    exp = "FLIC Comment: good comment"
    assert len(f.flic_comment()) == 1
    assert f.flic_comment()[0].message == exp

