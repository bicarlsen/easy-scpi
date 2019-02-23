# Easy SCPI
A simple and robust library making communication with [SCPI](https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments) (Standard Control of Programmbale Instruments) instruments easy. After creating an instrument object that connects to an actual instrument, commands are sent to the instrument using a property-like format. This class is very useful for inheritance when creating a controller for a specific instrument.

## API
### SCPI Commands
Generic SCPI commands can be executed by transforming the SCPI code in to attributes via the hierarchy relationship, then calling it. Instrument properties can be queried by passing no arguments to the call. Commands with no arguments are run by passing an empty string to the call.

#### Examples
~~~
# Connect to an instrument
inst = Instrument( <port> )

# Read the voltage [MEASure:VOLTage:DC?]
inst.measure.voltage.dc()
# or
inst.meas.volt.dc()

# Set the voltage to 1 V [MEASure:VOLTage:DC 1]
inst.measure.voltage.dc( 1 )
# or
inst.source.voltage( '1' )

# Execute a command to take a reading [SYSTem:ZCORrect:ACQuire]
inst.syst.zcor.aqc( '' )
~~~

### Methods
**Instrument( \<port\>, \<timeout\>, read_terminator = None, write_terminator = None, backend = '' ):** Creates an instance of an instrument

**connect():** Connects the object instance to the actual instrument on the specified port

**disconnect():** Disconnects the instrument from the program, closing the port

**write( \<msg\> ):** Sends **msg** to the instrument 

**read():** Gets the most recent response from the instrument

**query( \<msg\> ):** Sends **msg** to the instrument and returns its response

**reset():** Sets the instrument to its default state

**init():** Initializes the instrument for a measurement

### Properties
**port:** The communication port

**rid:** The resource id associated with the instrument [Read Only]

**timeout:** The communication timeout of the instrument [Read Only]

**id:** The manufacturer id of the instrument [Read Only]

**value:** The current value of the instrument [Read Only]

**connected:** Whether the instrument is connected or not [Read Only]

## Full Example
#### For use with Tektronix PWS4305
~~~
#standard imports
import os
import sys

#SCPI imports
import usb
import visa

#instrument controller
import instrument_controller as ic


class PowerSupply( ic.Instrument ):
    
    def __init__( self, timeout = 10, rid = None ):
        ic.Instrument.__init__( self, None, timeout, '\n', '\n' )
        self.rid = '<default resource id>' if ( rid is None ) else rid
        
    #--- public methods ---
    
    @property        
    def voltage( self ):
        """
        Returns the voltage setting
        """
        return self.source.volt.level()
    
    
    @voltage.setter
    def voltage( self, volts ):
        """
        Sets the voltage of the instrument
        """
        self.source.volt.level( volts )
        
    
    @property
    def current( self ):
        """
        Returns the current setting in Amps
        """
        return self.source.current.level()
        
        
    @current.setter
    def current( self, amps ):
        """
        Set the current of the instrument
        """
        self.source.current.level( amps )
        
    
    def on( self ):
        """
        Turns the output on
        """
        self.output.state( 'on' )
        
        
    def off( self):
        """
        Turns the output off
        """
        self.output.state( 'off' )
        
~~~