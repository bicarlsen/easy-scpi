# Easy SCPI
A simple and robust library making communication with [SCPI](https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments) (Standard Control of Programmbale Instruments) instruments easy. After creating an instrument object that connects to an actual instrument, commands are sent to the instrument using a property-like format. This class is useful for inheritance when creating a controller for a specific instrument. Communication with instruments is done with [PyVISA](https://pyvisa.readthedocs.io).

## Install
`python -m pip install easy-scpi`

## API
### SCPI Commands
Generic SCPI commands can be executed by transforming the SCPI code in to attributes via the hierarchy relationship, then calling it. Instrument properties can be queried by passing no arguments to the call (or specifying query=True). Commands with no arguments are run by passing an empty string to the call.

## Examples
For more examples see the [`examples`](./examples) folder.

### Basic
```python
# import package
import easy_scpi as scpi 

# Connect to an instrument
inst = scpi.Instrument(<port>)
inst.connect()

# Read the voltage [MEASure:VOLTage:DC?]
inst.measure.voltage.dc()
# or
inst.meas.volt.dc()

# Passing args to a query [MEASure:VOLTage:DC? MIN]
inst.measure.voltage.dc("MIN", query=True)

# Set the voltage to 1 V [MEASure:VOLTage:DC 1]
inst.measure.voltage.dc(1)
# or
inst.source.voltage('1')

# Execute a command to take a reading [SYSTem:ZCORrect:ACQuire]
inst.syst.zcor.aqc('')
```

### Full 
#### For use with Tektronix PWS4305
```python
import easy_scpi as scpi

class PowerSupply( scpi.Instrument ):
    def __init__( self ):
        super().__init__( 
            port = None, 
            timeout = 5000,
            read_termination = '\n', 
            write_termination = '\n' 
        )

        # other initialization code...

    @property        
    def voltage(self):
        """
        Returns the voltage setting.
        """
        return self.source.volt.level()
    
    @voltage.setter
    def voltage(self, volts):
        """
        Sets the voltage of the instrument.
        """
        self.source.volt.level(volts)
    
    @property
    def current(self):
        """
        Returns the current setting in Amps
        """
        return self.source.current.level()
        
    @current.setter
    def current(self, amps):
        """
        Set the current of the instrument
        """
        self.source.current.level(amps)
    
    def on(self):
        """
        Turns the output on
        """
        self.output.state('on')
        
    def off(self):
        """
        Turns the output off
        """
        self.output.state('off')
```
