import sys
sys.dont_write_bytecode = True
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from comms.serial_handler import SerialHandler