# -*- coding: utf-8 -*-
"""Example file for the HAMEG HMS3010
Using PyVISA.

:author: 2023 Gilles Callebaut

"""

# import package
import easy_scpi as scpi

ip = "192.108.0.220"
port = "50000"

# Define an instrument
inst = scpi.Instrument(
    port = f"TCPIP::{ip}::{port}::SOCKET",
    read_termination="\n", 
    write_termination="\n", 
    timeout=5000,
) 

# Connect to an instrument
inst.connect()

# Some commands
print(inst.system.mode("RMODe"))
print(inst.RMODe.detector("AVG"))

print(inst.query("RMODe:LEVel?"))
