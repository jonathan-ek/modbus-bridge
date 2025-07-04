import argparse
import logging
import minimalmodbus
import serial
from pyModbusTCP.server import DataBank, ModbusServer

# Configure logging
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class TCP2SerialDataBank(DataBank):
    def __init__(self, serial_port, slave_id, baudrate=9600):
        self._gateway = minimalmodbus.Instrument(serial_port, slave_id)
        self._gateway.serial.baudrate = baudrate
        self._gateway.serial.bytesize = 8
        self._gateway.serial.parity = serial.PARITY_NONE
        self._gateway.serial.stopbits = 1
        self._gateway.serial.timeout = 0.4
        self._gateway.mode = minimalmodbus.MODE_RTU
        self._gateway.precalculate_read_size = False
        self._gateway.clear_buffers_before_each_transaction = True
        self._gateway.close_port_after_each_call = True
        super().__init__(virtual_mode=True)

    def get_holding_registers(self, address, number=1, srv_info=None):
        try:
            logger.debug(f'Reading holding registers at {address}, count={number}')
            return self._gateway.read_registers(address, number_of_registers=number, functioncode=3)
        except Exception as e:
            logger.error(f'Error reading holding registers: {e}')
            return None

    def set_holding_registers(self, address, word_list, srv_info=None):
        try:
            word_list = [int(w) & 0xFFFF for w in word_list]
            logger.debug(f'Writing holding registers at {address}, values={word_list}')
            self._gateway.write_registers(address, word_list)
            return True
        except Exception as e:
            logger.error(f'Error writing holding registers: {e}')
            return None

    def get_input_registers(self, address, number=1, srv_info=None):
        try:
            logger.debug(f'Reading input registers at {address}, count={number}')
            return self._gateway.read_registers(address, number_of_registers=number, functioncode=4)
        except Exception as e:
            logger.error(f'Error reading input registers: {e}')
            return None

def main():
    parser = argparse.ArgumentParser(description='Modbus TCP to RTU gateway')
    parser.add_argument('-H', '--host', type=str, default='localhost', help='TCP host (default: localhost)')
    parser.add_argument('-p', '--port', type=int, default=502, help='TCP port (default: 502)')
    parser.add_argument('--serial', type=str, default='/dev/ttyAMA0', help='Serial port for RTU (default: /dev/ttyAMA0)')
    parser.add_argument('--slave-id', type=int, default=1, help='Modbus slave ID (default: 1)')
    parser.add_argument('--baudrate', type=int, default=9600, help='Serial baudrate (default: 9600)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.info(f"Starting Modbus TCP server on {args.host}:{args.port}")
    logger.info(f"Connecting to RTU device on {args.serial}, slave ID: {args.slave_id}")

    data_bank = TCP2SerialDataBank(args.serial, args.slave_id, args.baudrate)
    server = ModbusServer(host=args.host, port=args.port, data_bank=data_bank)

    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down Modbus TCP server...")
        server.stop()

if __name__ == '__main__':
    main()
