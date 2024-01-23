import serial
import threading
from time import sleep 
from queue import Queue
from RsInstrument import *

class MotorControlModule:
    def __init__(self, port='/dev/ttyACM0', baudrate=9600):
        self.ser = serial.Serial(port, baudrate)
        self.current_position = 0

    def send_command(self, command):
        self.ser.write(command.to_bytes(1, byteorder='big'))

    def send_angle_command(self, command, angle):
        angle_bytes = angle.to_bytes(2, byteorder='big')
        self.ser.write(command.to_bytes(1, byteorder='big') + angle_bytes)

    def wait_for_acknowledgement(self, expected_command):
        while True:
            if self.ser.in_waiting:
                ack = self.ser.read(1)
                if ack == expected_command.to_bytes(1, byteorder='big'):
                    print(f"Command {expected_command} executed.")
                    position_data = self.ser.readline().decode('utf-8').rstrip()
                    print(f"Current Position: {position_data}")
                    break

    def rotate_ccw(self):
        command = 0b001
        self.send_command(command)
        self.wait_for_acknowledgement(command)

    def rotate_cw(self):
        command = 0b010
        self.send_command(command)
        self.wait_for_acknowledgement(command)

    def stop_motor(self):
        command = 0b011
        self.send_command(command)
        self.wait_for_acknowledgement(command)

    def return_to_origin(self):
        command = 0b100
        self.send_command(command)
        self.wait_for_acknowledgement(command)

    def set_start_angle(self, angle):
        command = 0b101
        self.send_angle_command(command, angle)
        self.wait_for_acknowledgement(command)

    def set_end_angle(self, angle):
        command = 0b110
        self.send_angle_command(command, angle)
        self.wait_for_acknowledgement(command)

class ApplicationGUI:
    # GUI setup and event handling goes here
    pass

class VNAModule:
    def __init__(self, ip_address):
        self.vna = RsInstrument('TCPIP::' + ip_address + '::INSTR', True, True)

    def antenna_test(self, starting_frequency, ending_frequency, num_points):
        self.vna.write(':SENS:FREQ:STAR {starting_frequency}GHz')  # Setting measurement parameters
        self.vna.write(':SENS:FREQ:STOP {ending_frequency}GHz')  # Setting measurement parameters
        self.vna.write(':SWE:POIN {num_points}')  # Setting a sweep of points during test

        self.vna.write(':CALC1:PAR:SDEF "Trace1",S21')  # Calculating our S21 Parameter Defined as Trace1
        self.vna.write('CALC2:PAR:SDEF "Trace2",S11')  # Calculating our S11 Parameter Defined as Trace2
        self.vna.write(':CALC:FORM SMIT')  # Making a Smith Chart for our S21 Parameter
        self.vna.write(':CALC:PAR:MEAS "Trace1",S21')  # Measuring the S21 Parameter
        self.vna.write(':DISP:WIND:TRAC:FEED "Trace1"')  # Feeding MyTrace Measurements & Display on Window
        self.vna.write('INIT:IMM')  # Initiating an immediate Sweep
        # Start the sweep process in a separate thread
        sweep_thread = threading.Thread(target=self.perform_sweep)
        sweep_thread.start()

    def perform_sweep(self):
        sleep(10) 
        s21_data = self.vna.query_bin_or_ascii_float_list(':CALC:DATA? SDAT')  # Querying our data
        s11data = self.vna.query_bin_or_ascii_float_list(':CALC2:DATA? SDAT')  # Querying our data
        data = self.vna.query_bin_or_ascii_float_list('CALC:DATA? SDATA')  # Querying our data
        frequency = self.vna.query_bin_or_ascii_float_list(':SENS:FREQ:DATA?')  # Querying our frequency
        self.vna.close()  # Closing 'communication' between computer & instrument

class SystemController:
    def __init__(self):
        self.motor_control = MotorControlModule()
        self.vna_control = VNAModule(ip_address='192.168.2.100')
        # self.gui = ApplicationGUI()
        self.state = 'IDLE'  # Initial state of the motor
        self.command_queue = Queue()
        self.process_thread = None

    def update_motor_state(self, new_state):
        self.state = new_state
        # Enqueue commands based on the state
        if self.state == 'MOVE_CCW':
            self.command_queue.put(0b001)  # CCW command
        elif self.state == 'MOVE_CW':
            self.command_queue.put(0b010)  # CW command
        # ... handle other states ...

    def process_queue(self):
        while True:
            command = self.command_queue.get()
            self.motor_control.send_command(command)
            self.motor_control.wait_for_acknowledgement(command)
            self.command_queue.task_done()

    def start(self):
        self.process_thread = threading.Thread(target=self.process_queue, daemon=True)
        self.process_thread.start()