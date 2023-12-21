import can
import logging

def send_msg(bus, msg):
    try:
        bus.send(msg)
        logging.debug(f"Message sent on {bus.channel_info}")
        return True
    except can.CanError as e:
        logging.error(f"Message NOT sent: {e}")
        return False

def open_can(iface, dev):
    try:
        bus = can.Bus(interface=iface, channel=dev)
    except Exception as e:
        logging.error(f'Unable to open CAN bus: {iface}/{dev}')
        logging.error(str(e))
        return None
    return bus

def create_msg(id, data):
    return can.Message(is_extended_id=False, arbitration_id=id, data=data)
