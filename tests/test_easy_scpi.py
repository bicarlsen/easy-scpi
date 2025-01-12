import platform
import easy_scpi as scpi
import pathlib

def test_easy_scpi():
    inst = scpi.Instrument(
        port="TCPIP::0.0.0.1::3000::SOCKET", 
        port_match=False, 
        read_termination="\n", 
        write_termination="\n",
        backend=str((pathlib.Path(__file__).parent /'instrument_mock.yaml@sim').resolve()),
    )
    inst.connect()
    
    assert inst.id == "mock instrument"
    
    assert inst.query("FREQ?") == "100.00"
    assert inst.query("FREQ 1.00") == "OK"
    assert inst.query("FREQ?") == "1.00"
    
    assert inst.freq() == "1.00"
    inst.freq(100.00)
    assert inst.read() == "OK"
    assert inst.freq() == "100.00"