import struct

from hacbi.canbus import create_msg

def create_limits_msg(max_charge_voltage, min_discharge_voltage, max_charge_current, max_discharge_current):
    data = struct.pack('<HHHH', int(round(max_charge_voltage * 10)), int(round(max_charge_current * 10)),
                       int(round(max_discharge_current * 10)), int(round(min_discharge_voltage * 10)))
    return create_msg(0x351, data)

def create_soc_msg(soc, soh):
    data = struct.pack('<HH', int(round(soc)), int(round(soh)))
    return create_msg(0x355, data)

def create_state_msg(voltage, current, temperature):
    data = struct.pack('<Hhh', int(round(voltage * 100)), int(round(current * 10)), int(round(temperature * 10)))
    return create_msg(0x356, data)

def create_charge_msg(force_charge_1, force_charge_2, charge, discharge, full_charge=False):
    val = 0x00000
    if full_charge:
        val |= 0x80
    if force_charge_2:
        val |= 0x10
    if force_charge_1:
        val |= 0x20
    if discharge:
        val |= 0x40
    if charge:
        val |= 0x80
    data = struct.pack('<H', val)
    return create_msg(0x35C, data)

def create_cell_stats_msg(max_cell_temp, min_cell_temp, max_cell_voltage, min_cell_voltage):
    data = struct.pack('<hhHH', int(round(max_cell_temp * 10)), int(round(min_cell_temp * 10)), int(round(max_cell_voltage * 100)), int(round(min_cell_voltage * 100)))
    return create_msg(0x70, data)

def create_cell_stats_id_msg(max_temp_cell, min_temp_cell, max_voltage_cell, min_voltage_cell):
    data = struct.pack('<hhHH', int(round(max_temp_cell)), int(round(min_temp_cell)), int(round(max_voltage_cell)), int(round(min_voltage_cell)))
    return create_msg(0x371, data)

def create_inverter_type_msg():
    #GOODWE
    data = [0x47, 0x4F, 0x4F, 0x44, 0x57, 0x45, 0x20, 0x20]
    return create_msg(0x35E, data)
