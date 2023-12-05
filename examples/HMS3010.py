# -*- coding: utf-8 -*-
"""Example file for the HAMEG HMS3010
Using PyVISA.

:author: 2023 Gilles Callebaut

"""

# import package
import easy_scpi as scpi

ip = "192.108.0.220"
port = "50000" # default is 5025

# Define an instrument
inst = scpi.Instrument(read_termination='\n', write_termination='\n', timeout=5000) # include a timeout for reading the power level (obtained by trial-and-error)
inst.rid=f"TCPIP::{ip}::{port}::SOCKET" # define IP PORT


# Connect to an instrument
inst.connect()


# Some commands
print(inst.system.mode("RMODe"))
print(inst.RMODe.detector("AVG"))

print(inst.query("RMODe:LEVel?"))
