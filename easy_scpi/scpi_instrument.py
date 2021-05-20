#!/usr/bin/env python
# coding: utf-8

# # SCPI Instrument Controller
# Parent class for instrument control

# ## API
# ### SCPI Commands
# Generic SCPI commands can be executed by transforming the SCPI code in to attributes via the hierarchy relationship, then calling it. Instrument properties can be queried by passing no arguments to the call. Commands with no arguments are run by passing an empty string to the call.
#
# #### Examples
# `inst = SCPI_Instrument()`
#
#
# ### Methods
# **SCPI_Instrument( &lt;port&gt;, backend = '', \*\*resource_params ):** Creates an instance of a SCPI instrument. The **backend** is used to create the [VISA Resource Manager](https://pyvisa.readthedocs.io/en/latest/introduction/getting.html#backend). Upon connection, the **resource_params** are passed to the [VISA resource](https://pyvisa.readthedocs.io/en/latest/introduction/resources.html).
#
# **connect():** Connects the object instance to the actual instrument on the specified port.
#
# **disconnect():** Disconnects the instrument from the program, closing the port.
#
# **write( \<msg\> ):** Sends **msg** to the instrument .
#
# **read():** Gets the most recent response from the instrument.
#
# **query( \<msg\> ):** Sends **msg** to the instrument and returns its response.
#
# **reset():** Sets the instrument to its default state.
#
# **init():** Initializes the instrument for a measurement.
#
# ### Properties
# **backend:** Returns the name of the VISA backend used. [Read Only]
#
# **inst:** Returns the resource used by the instance. [Read Only]
#
# **port:** The communication port.
#
# **handshake:** Handshake mode of the device. If a string is provided a handshake message will be read after every command or query. If the message matches the string, nothing occurs, otherwise an error is raised. If True a default message of 'OK' is used. If False no message is read. [Default: False]
#
# **rid:** The resource id associated with the instrument. [Read Only]
#
# **resource_params:** Returns the resource parameters passed on creation. [Read Only]
#
# **timeout:** The communication timeout of the instrument. [Read Only]
#
# **id:** The manufacturer id of the instrument. [Read Only]
#
# **value:** The current value of the instrument. [Read Only]
#
# **connected:** Whether the instrument is connected or not. [Read Only]
#
# **is_connected:** Alias for **connected**.


import re

import pyvisa as visa


class Property( object ):
        """
        Represents a scpi property of the instrument
        """

        #--- static variables ---
        ON  = 'ON'
        OFF = 'OFF'


        #--- class methods ---

        def __init__( self, inst, name ):
            self.__inst = inst  # the instrument
            self.name = name.upper()


        def __getattr__( self, name ):
            return Property(
                self.__inst,
                ':'.join( ( self.name, name.upper() ) )
            )


        def __call__( self, value = None ):
            if value is None:
                # get property
                return self.__inst.query( self.name + '?')

            else:
                # set value
                if not isinstance( value, str ):
                    # try to convert value to string
                    value = str( value )

                return self.__inst.write( self.name + ' ' + value )


        #--- static methods ---

        @staticmethod
        def val2bool( val ):
            """
            Converts standard input to boolean values

            True:  'on',  '1', 1, True
            False: 'off', '0', 0, False
            """
            if isinstance( val, str ):
                # parse string input
                val = val.lower()

                if val == 'on' or val == '1':
                    return True

                elif val == 'off' or val == '0':
                    return False

                else:
                    raise ValueError( 'Invalid input' )

            return bool( val )


        @staticmethod
        def val2state( val ):
            """
            Converts standard input to scpi state

            ON:  True,  '1', 1, 'on',  'ON'
            OFF: False, '0', 0, 'off', 'OFF'
            """
            state = Property.val2bool( val )
            if state:
                return 'ON'

            else:
                return 'OFF'


class SCPI_Instrument():
    """
    Represents an instrument

    Arbitrary SCPI commands can be performed
    treating the hieracrchy of the command as attributes.

    To read an property:  inst.p1.p2.p3()
    To call a function:   inst.p1.p2( 'value' )
    To execute a command: inst.p1.p2.p3( '' )
    """

    #--- methods ---


    def __getattr__( self, name ):
        resp = Property( self, name )
        return resp


    def __init__(
        self,
        port = None,
        backend = '',
        handshake = False,
        **resource_params
    ):
        """
        Creates an instance of an Instrument, to communicate with VISA instruments

        :param port: The name of the port to connect to. [Default: None]
        :param backend: The pyvisa backend to use for communication.
        :param handshake: Handshake mode. [Default: False]
        :param resource_params: Arguments based to the resource upon connection.
            https://pyvisa.readthedocs.io/en/latest/api/resources.html?highlight=baud#pyvisa.resources.SerialInstrument
        :returns: An Instrument communicator.
        """
        #--- private instance vairables ---
        self.__backend = backend
        self.__rm = visa.ResourceManager( backend ) # the VISA resource manager
        self.__inst = None # the device
        self.__port = None
        self.__rid = None # the resource id of the instrument
        self.__resource_params = resource_params # options for connection

        # init connection
        self.port = port # initilaize port

        if handshake is True:
            handshake = 'OK'

        self.handshake = handshake


    def __del__( self ):
        """
        Disconnects and deletes the Instrument
        """
        if self.connected:
            self.disconnect()

        del self.__inst
        del self.__rm

    #--- private methods ---


    #--- public methods ---

    @property
    def backend( self ):
        return self.__backend


    @property
    def instrument( self ):
        return self.__inst


    @property
    def port( self ):
        return self.__port


    @port.setter
    def port( self, port ):
        """
        Disconnects from current connection and updates port and id.
        Does not reconnect.

        :raises ValueError: If connection type is not specified.
        :raises RuntimeError: If resource matching specified port could not be found.
        :raises RuntimeError: If more than 1 matching resource is found.
        """
        if port is None:
            self.__port = None
            self.__rid = None
            return

        port_name = port.upper()

        if (
            ( not port_name.startswith( 'COM' ) ) and
            ( not port_name.startswith( 'USB' ) )
        ):
            raise ValueError( "'COM' or 'USB' must be in port name." )

        if self.__inst is not None:
            self.disconnect()

        self.__port = port

        # search for resource
        if port_name.startswith( 'USB' ): 
            resource_pattern = (
                port
                if port_name.endswith( 'INSTR' ) else
                f'{ port }::.*::INSTR'
            )

        else:
            r_port = port.replace( 'COM', '' )
            resource_pattern = f'ASRL((?:COM)?{ r_port })::INSTR'

        rm = visa.ResourceManager( self.backend )
        matches = list( map(
            lambda resource: re.match( resource_pattern, resource ),
            rm.list_resources()
        ) )

        matches = [ match for match in matches if match is not None ]
        if len( matches ) == 0:
            # no matching resources found
            raise RuntimeError( f'Could not find resource matching port {port}' )

        elif len( matches ) > 1:
            # multiple matching resource
            raise RuntimeError( f'Found multiple resources matching port {port}' )

        # single matching resource
        self.__rid = matches[ 0 ].group( 0 )

        # adjust port name for resource id to match backend
        # if self.backend == '@py':
        #     r_port = port
        #     if 'COM' not in r_port:
        #         r_port = 'COM' + r_port

        # else:
        #     r_port = port.replace( 'COM', '' )

        # self.__rid = f'ASRL{ r_port }::INSTR'


    @property
    def rid( self ):
        """
        Return the resource id of the instrument
        """
        return self.__rid


    @rid.setter
    def rid( self, rid ):
        self.__rid = rid


    @property
    def resource_params( self ):
        return self.__resource_params


    @property
    def id( self ):
        """
        Returns the id of the ammeter
        """
        return self.query( '*IDN?' )


    @property
    def value( self ):
        """
        Get current value
        """
        return self.query( 'READ?' )


    @property
    def connected( self ):
        """
        Returns if the instrument is connected
        """
        if self.__inst is None:
            return False

        try:
            # session throws excpetion if not connected
            self.__inst.session
            return True

        except visa.InvalidSession:
            return False


    @property
    def is_connected( self ):
        """
        Alias for connected
        """
        return self.connected


    def connect( self ):
        """
        Connects to the instrument on the given port.
        """
        if not self.rid:
            # no resource id
            raise RuntimeError( 'Can not connect. No resource id provided.' )

        if self.__inst is None:
            self.__inst = self.__rm.open_resource( self.rid )

            # set resource parameters
            for param, val in self.__resource_params.items():
                setattr( self.__inst, param, val )

        else:
            self.__inst.open()

        self.id  # place instrument in remote control


    def disconnect( self ):
        """
        Disconnects from the instrument, and returns local control
        """
        if self.__inst is not None:
            self.__inst.close()


    def write( self, msg ):
        """
        Delegates write to resource
        """
        if self.__inst is None:
            raise RuntimeError( 'Can not write, instrument not connected.' )

        resp = self.__inst.write( msg )
        self._handle_handshake()

        return resp


    def read( self ):
        """
        Delegates read to resource
        """
        if self.__inst is None:
            raise RuntimeError( 'Can not read, instrument not connected' )

        resp = self.__inst.read()
        return resp


    def query( self, msg ):
        """
        Delegates query to resource
        """
        if self.__inst is None:
            raise RuntimeError( 'Can not query, instrument not connected' )

        resp = self.__inst.query( msg )
        self._handle_handshake()

        return resp


    def reset( self ):
        """
        Resets the meter to inital state
        """
        return self.write( '*RST' )


    def init( self ):
        """
        Initialize the instrument
        """
        return self.write( 'INIT' )


    def _handle_handshake( self ):
        """
        Handles handshaking if enabled.

        :raises RuntimeError: If the response message does not match the handshake message.
        """
        if self.handshake:
            hs = self.read()
            if hs != self.handshake:
                raise RuntimeError( hs )


# --- CLI


if __name__ == '__main__':
    import getopt

    #--- helper functions ---

    def print_help():
        print( """
Instrument Controller CLI

Use:
python instrument_controller.py [port=<COM>] <function> [arguments]
<COM> is the port to connect to [Default: COM14]
<function> is the ammeter command to run
[arguments] is a space separated list of the arguments the function takes

API:
+ write()
+ query()

        """)

    #--- main ---
    raise NotImplementedError()
