import platform
import pytest
import easy_scpi as scpi
import pathlib

@pytest.fixture
def blank_inst():
    # Blank Instrument
    return scpi.Instrument()

@pytest.fixture
def inst():
    inst = scpi.Instrument(
        port="TCPIP::0.0.0.1::3000::SOCKET",
        port_match=False,
        read_termination="\n",
        write_termination="\n",
        backend=str((pathlib.Path(__file__).parent /'instrument_mock.yaml@sim').resolve()),
    )
    inst.connect()
    return inst

def test_property_syntax(blank_inst):
    # Assert naming conventions work as expected.
    assert blank_inst.a.name == "A"
    assert blank_inst.a.b.name == "A:B"
    assert blank_inst.a.b.c.name == "A:B:C"

def test_prefix_syntax(blank_inst):
    # Assert that prefixing of commands work.
    blank_inst.prefix_cmds = True
    assert blank_inst.a.name == ":A"
    assert blank_inst.a.b.name == ":A:B"
    assert blank_inst.a.b.c.name == ":A:B:C"

def test_easy_scpi(inst):
    assert inst.id == "mock instrument"
    
    assert inst.query("FREQ?") == "100.00"
    assert inst.query("FREQ 1.00") == "OK"
    assert inst.query("FREQ?") == "1.00"
    
    assert inst.freq() == "1.00"
    inst.freq(100.00)
    assert inst.read() == "OK"
    assert inst.freq() == "100.00"

def test_argument_query(inst):
    assert inst.query('FREQ? MAX') == "100000.00"
    assert inst.freq('MAX', query=True) == "100000.00"
    assert inst.query('FREQ? MIN') == "1.00"
    assert inst.freq('MIN', query=True) == "1.00"