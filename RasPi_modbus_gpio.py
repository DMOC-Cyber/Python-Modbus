#!/usr/bin/env python
"""
Pymodbus Server With Callbacks
--------------------------------------------------------------------------

This is an example of adding callbacks to a running modbus server
when a value is written to it. In order for this to work, it needs
a device-mapping file.
"""
# ---------------------------------------------------------------------------#
# import the modbus libraries we need
# ---------------------------------------------------------------------------#
from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer

# ---------------------------------------------------------------------------#
# import the python libraries we need
# ---------------------------------------------------------------------------#
from gpiozero import LED


class CallbackDataBlock(ModbusSparseDataBlock):
    def __init__(self, devices):
        self.devices = devices

        values = {k: 0 for k in devices.keys()}
        values[0xbeef] = len(values)  # the number of devs
        super(CallbackDataBlock, self).__init__(values)

    def setValues(self, address, value):
        self.devices[address].value = value[0]
        super(CallbackDataBlock, self).setValues(address, value)

    def getValues(self, address, count=1):
        values = [self.devices[k].value for k in list(self.devices.keys())][address:address + count]
        return values


# ---------------------------------------------------------------------------#
# initialize your device map
# ---------------------------------------------------------------------------#
def gpo_read_device_map():
    """ A helper method to read the device
    path to address mapping from file::

       0x0001,led1
       0x0002,led2
       ...

    :returns: The input mapping file
    """
    devices = {
        0x0001: LED(17),  # LED 1
        0x0002: LED(27),  # LED 2
        0x0003: LED(22),  # LED 3
        0x0004: LED(5),  # LED 4
        0x0005: LED(6),  # LED 5
        0x0006: LED(13),  # LED 6
        0x0007: LED(19),  # LED 7
        0x0008: LED(26),  # LED 8
    }

    return devices


# ---------------------------------------------------------------------------#
# initialize your data store
# ---------------------------------------------------------------------------#
devs = gpo_read_device_map()
block = CallbackDataBlock(devs)
store = ModbusSlaveContext(di=None, co=block, hr=None, ir=None)
context = ModbusServerContext(slaves=store, single=True)

# ---------------------------------------------------------------------------#
# run the server you want
# ---------------------------------------------------------------------------#
StartTcpServer(context, address=("192.168.0.118", 5020))
