import serial

# Initialize variables
arm_position = 0  

def update_arm_position_display():
    # reserved for GUI design
    pass

def ccw_button_pushed():
    ser.write(b'a')  # turn arm CCW 0.9 degree

def cw_button_pushed():
    ser.write(b'b')  # turn arm CW 0.9 degree

ser = serial.Serial('/dev/ttyACM0', 9600) # replace with your port

while True:
    if ser.in_waiting:
        encoder_position = ser.readline().decode('utf-8').rstrip()
        print(f"Position: {encoder_position}")
        arm_position = float(encoder_position)
        update_arm_position_display()
