from RsInstrument import *
import time
import os

# ip_address = '192.168.0.1'
# rm = visa.ResourceManager()  # Setting up our resource
# vna = rm.open_resource('TCPIP0::{ip_address}:inst0::INSTR')  # Sets up a standard LAN connection for our instrument
# external_hard_drive_path = "/name/to/external/hard/drive"
# def antenna_test(ip_address, starting_frequency, ending_frequency, num_points):

#     vna.write(':SENS:FREQ:STAR {starting_frequency}GHz')  # Setting measurement parameters
#     vna.write(':SENS:FREQ:STOP {ending_frequency}GHz')  # Setting measurement parameters
#     vna.write(':SWE:POIN {num_points}')  # Setting a sweep of points during test

#     vna.write(':CALC:PAR:DEF "S11",S11')  # Calculating our S21 Parameter Defined as MyTrace
#     vna.write(':CALC:FORM: POL')  # Gives Polar Coordinates of S21 Parameter
#     vna.write(':CALC:FORM: LOGP')  # Gives magnitude of our S21 Parameter (dB)
#     vna.write(':CALC:PAR:MEAS "S11",S11')  # Measuring the S21 Parameter
#     vna.write(':DISP:WIND:TRAC:FEED "S11"')  # Feeding MyTrace Measurements & Display on Window

#     vna.write(':CALC:PAR:DEF "S21",S21')  # Calculating our S21 Parameter Defined as MyTrace
#     vna.write(':CALC:FORM: POL')  # Gives Polar Coordinates of S21 Parameter
#     vna.write(':CALC:FORM: LOGP') # Gives magnitude of our S21 Parameter (dB)
#     vna.write(':CALC:PAR:MEAS "S21",S21')  # Measuring the S21 Parameter
#     vna.write(':DISP:WIND2:TRAC:FEED "S21"')  # Feeding MyTrace Measurements & Display on Window


#     vna.write('INIT:IMM')  # Initiating an immediate Sweep

#     time.sleep(1)  # Allow time for Sweep

#     # Querying our Data
#     s11_data = vna.query_bin_or_ascii_float_list('CALC:DATA? SDAT')
#     s21_data = vna.query_bin_or_ascii_float_list('CAL2C:DATA? SDAT')
#     data = vna.query_bin_or_ascii_float_list('CALC:DATA? SDAT')
#     data = vna.query_bin_or_ascii_float_list(':SENS:FREQ:DATA?')

#     # Creating our files
#     filename = f"Antenna_{angle}_degrees_S11_S12.csv"
#     file_path = os.path.join(external_hard_drive_path, filename)




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # starting_frequency = 20  # Initializing and assigning value to Start Frequency
    # ending_frequency = 25  # Initializing and assigning value to End Frequency
    # num_of_test_points = 50  # Initializing and assigning value to number of points
    # angle = 0
    # for angle in range (181): antenna_test(ip_address, starting_frequency, ending_frequency, num_of_test_points)
    # vna.close()  # Closing 'communication' between computer & instrument
    RsInstrument.assert_minimum_version('1.50.0')
    instr = RsInstrument('TCPIP::zva67-101058.mshome.net::inst0::INSTR')
    idn = instr.query('*IDN?')
    print(f"\nHello, I am: '{idn}'")
    print(f'RsInstrument driver version: {instr.driver_version}')
    print(f'Visa manufacturer: {instr.visa_manufacturer}')
    print(f'Instrument full name: {instr.full_instrument_model_name}')
    print(f'Instrument installed options: {",".join(instr.instrument_options)}')

    instr.close()

