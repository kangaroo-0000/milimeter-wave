import serial

ser = serial.Serial('/dev/ttyACM0', 9600) # replace with your port
ser.write(b'a')

