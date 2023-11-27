import serial

# Initialize Serial Connection
ser = serial.Serial('/dev/ttyACM0', 9600)  # Replace 

def send_command(command):
    ser.write(command.to_bytes(1, byteorder='big'))

def send_angle_command(command, angle):
    angle_bytes = angle.to_bytes(2, byteorder='big')
    ser.write(command.to_bytes(1, byteorder='big') + angle_bytes)

def wait_for_acknowledgement(expected_command):
    while True:
        if ser.in_waiting:
            ack = ser.read(1)
            if ack == expected_command.to_bytes(1, byteorder='big'):
                print(f"Command {expected_command} executed.")
                position_data = ser.readline().decode('utf-8').rstrip()
                print(f"Current Position: {position_data}")
                break

def rotate_ccw():
    command = 0b001
    send_command(command)
    wait_for_acknowledgement(command)

def rotate_cw():
    command = 0b010
    send_command(command)
    wait_for_acknowledgement(command)

def stop_motor():
    command = 0b011
    send_command(command)
    wait_for_acknowledgement(command)

def return_to_origin():
    command = 0b100
    send_command(command)
    wait_for_acknowledgement(command)

def set_start_angle(angle):
    command = 0b101
    send_angle_command(command, angle)
    wait_for_acknowledgement(command)

def set_end_angle(angle):
    command = 0b110
    send_angle_command(command, angle)
    wait_for_acknowledgement(command)