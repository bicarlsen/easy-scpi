#!/usr/bin/env python
# coding: utf-8

# # SCPI Instrument Controller
# Parent class for instrument control

# ## API
# ### SCPI Commands
# Generic SCPI commands can be executed by transforming the SCPI code in to attributes via the hierarchy relationship, then calling it. Instrument properties can be queried by passing no arguments to the call. Commands with no arguments are run by passing an empty string to the call.
# 
# #### Examples
# `inst = Instrument()`
# 
# 
# ### Methods
# **Instrument(port, timeout)** Creates an instance of an instrument
# 
# **connect()** Connects the program to the instrument
# 
# **disconnect()** Disconnects the instrument from the program, closing the port
# 
# **write( msg )** Sends **msg** to the instrument 
# 
# **read()** Gets the most recent response from the instrument
# 
# **query( msg )** Sends **msg** to the instrument and returns its response
# 
# **reset()** Sets the instruemnt to its default state
# 
# **init()** Initializes the instrument for a measurement
# 
# ### Properties
# **port** The communication port
# 
# **rid** The resource id associated with the instrument [Read Only]
# 
# **timeout** The communication timeout of the instrument [Read Only]
# 
# **id** The manufacturer id of the instrument [Read Only]
# 
# **value** The current value of the instrument [Read Only]
# 
# **connected** Whether the instrument is connected or not [Read Only]

# In[1]:


# standard imports
import os
import sys
import serial
import re

# FREEZE
import logging
logging.basicConfig( level = logging.DEBUG )

# SCPI imports
import visa


# In[2]:


class Property( object ):
        """
        Represents a scpi property of the instrument 
        """
        
        #--- static variables ---
        ON  = 'ON'
        OFF = 'OFF'
        
        
        #--- class methods ---
        
        def __init__( self, inst, name ):
            self.__inst = inst # the instrument
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


# In[3]:


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
        return Property( self, name )
        
    
    def __init__( self, port = None, backend = '', **resource_params ):
        """
        Creates an instance of an Instrument, to communicate with VISA instruments
        
        :param port: The name of the port to connect to. [Default: None]
        :param backend: The pyvisa backend to use for communication.
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
        """
        if self.__inst is not None:
            self.disconnect()
            
        self.__port = port
        
        # TODO: Make backend support more robust
        if port is None:
            self.__rid = None
            
        else:
            # adjust port name for resource id to match backend
            if self.__backend == '@py':
                r_port = port
                if 'COM' not in r_port:
                    r_port = 'COM' + r_port
                
            else:
                r_port = port.replace( 'COM', '' )      
            
            self.__rid = 'ASRL{}::INSTR'.format( r_port )    

         
        
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
    def timeout( self ):
        return self.__timeout
    
    
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
            
        self.id # place instrument in remote control
        
        
    def disconnect( self ):
        """
        Disconnects from the instrument, and returns local control
        """
        if self.__inst is not None:
            self.syst.loc( '' )
            self.__inst.close()
            
            
    def write( self, msg ):
        """
        Delegates write to resource
        """
        if self.__inst is None:
            raise Exception( 'Can not write, instrument not connected.' )
            return
            
        return self.__inst.write( msg )
            
            
    def read( self ):
        """
        Delegates read to resource
        """
        if self.__inst is None:
            raise Exception( 'Can not read, instrument not connected' )
            return
            
        return self.__inst.read()
    
    
    def query( self, msg ):
        """
        Delegates query to resource
        """
        if self.__inst is None:
            raise Exception( 'Can not query, instrument not connected' )
        
        return self.__inst.query( msg )
            
        
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
        


# # CLI

# In[4]:


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


