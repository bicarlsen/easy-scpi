# Easy SCPI
A simple and robust library making communication with [SCPI](https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments) (Standard Control of Programmbale Instruments) instruments easy. After creating an instrument object that connects to an actual instrument, commands are sent to the instrument using a property-like format. This class is useful for inheritance when creating a controller for a specific instrument. Communication with instruments is done with [PyVISA](https://pyvisa.readthedocs.io).

> Install with `python -m pip install easy-scpi`

## API
### SCPI Commands
Generic SCPI commands can be executed by transforming the SCPI code in to attributes via the hierarchy relationship, then calling it. Instrument properties can be queried by passing no arguments to the call. Commands with no arguments are run by passing an empty string to the call.

#### Examples
~~~python
# import package
import easy_scpi as scpi 

# Connect to an instrument
inst = scpi.Instrument( <port> )

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
**Instrument( &lt;port&gt;, backend = '', \*\*resource_params ):** Creates an instance of a SCPI instrument. The **backend** is used to create the [VISA Resource Manager](https://pyvisa.readthedocs.io/en/latest/introduction/getting.html#backend). Upon connection, the **resource_params** are passed to the [VISA resource](https://pyvisa.readthedocs.io/en/latest/introduction/resources.html).

**connect():** Connects the object instance to the actual instrument on the specified port.

**disconnect():** Disconnects the instrument from the program, closing the port.

**write( &lt;msg&gt; ):** Sends **msg** to the instrument.

**read():** Gets the most recent response from the instrument.

**query( &lt;msg&gt; ):** Sends **msg** to the instrument and returns its response.

**reset():** Sets the instrument to its default state.

**init():** Initializes the instrument for a measurement.

### Properties
**backend:** Returns the name of the VISA backend used. [Read Only]

**inst:** Returns the resource used by the instance. [Read Only]

**port:** The communication port.

**handshake:** Handshake mode of the device. If a string is provided a handshake message will be read after every command or query. If the message matches the string, nothing occurs, otherwise an error is raised. If True a default message of 'OK' is used. If False no message is read. [Default: False]

**rid:** The resource id associated with the instrument. [Read Only]

**resource_params:** Returns the resource parameters passed on creation. [Read Only]

**timeout:** The communication timeout of the instrument. [Read Only]

**id:** The manufacturer id of the instrument. [Read Only]

**value:** The current value of the instrument. [Read Only]

**connected:** Whether the instrument is connected or not. [Read Only]

**is_connected:** Alias for **connected**.

## Full Example
#### For use with Tektronix PWS4305
~~~python
# scpi controller
import easy_scpi as scpi

class PowerSupply( scpi.Instrument ):
    
    def __init__( self ):
        super().__init__( 
            port = None, 
            timeout = 5,
            read_termination = '\n', 
            write_termination = '\n' 
        )

        # other initialization code...

        
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
