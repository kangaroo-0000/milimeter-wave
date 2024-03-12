from RsInstrument import *
import numpy as np
import time

vna = None

def test_s21():
    try:
        # Reset device and set display options
        vna.write("*RST; :DISP:ANN:FREQ ON\n")

        # Assuming app.start_freq and num_freq_points are defined
        start_freq = "10e9"  # Example start frequency
        stop_freq = "20e9"  # Example stop frequency
        num_freq_points = "101"  # Example number of points

        # Create channel, create trace of S21 on that channel
        vna.write("CALC1:PAR:SDEF 'Ch1Tr1', 'S21'\n")

        # Set start frequency of sweep
        vna.write(f"SENS:FREQ:STAR {start_freq}\n")

        # Set stop frequency of sweep
        vna.write(f"SENS:FREQ:STOP {stop_freq}\n")

        # Set number of points in frequency sweep
        vna.write(f"SWE:POIN {num_freq_points}\n")

        # give vna time to set up
        time.sleep(1)

        vna.write("CALC1:FORM PHAS\n")
        phase_data = vna.query("CALC1:DATA? FDAT\n")
        phases = np.fromstring(phase_data, dtype=float, sep=',')
        print("Printing phases:")
        print(phases)
        print()

        # format data in linear (default is dB)
        vna.write("CALC1:FORM MLIN\n")

        # Read the formatted trace data
        s21_data = vna.query("CALC1:DATA? FDAT\n")

        # Convert the formatted data to a numpy array
        mags = np.fromstring(s21_data, dtype=float, sep=',')
        print("Printing mags:")
        print(mags)
        print()

        # linspace for frequency axis
        freqs = np.linspace(float(start_freq), float(stop_freq), int(num_freq_points))

        print("end of s21")
        print()

    except Exception as e:
        print(f"Error: {e}")


def test_s11():
    vna = None
    try:
        # Connect to VNA
        vna_address = 'TCPIP::zva67-101058.mshome.net::inst0::INSTR'
        vna = RsInstrument(vna_address)

        # Assuming app.start_freq and num_freq_points are defined
        start_freq = "10e9"  # Example start frequency
        stop_freq = "20e9"  # Example stop frequency
        num_freq_points = "101"  # Example number of points

        # Create channel, create trace of S11 on that channel
        vna.write("CALC1:PAR:SDEF 'Ch1Tr2', 'S11'\n")

        # Set start frequency of sweep
        vna.write(f"SENS:FREQ:STAR {start_freq}\n")

        # Set stop frequency of sweep
        vna.write(f"SENS:FREQ:STOP {stop_freq}\n")

        # Set number of points in frequency sweep
        vna.write(f"SWE:POIN {num_freq_points}\n")

        # give vna time to set up
        time.sleep(1)

        vna.write("CALC1:FORM PHAS\n")
        phase_data = vna.query("CALC1:DATA? FDAT\n")
        phases = np.fromstring(phase_data, dtype=float, sep=',')
        print("Printing phases:")
        print(phases)
        print()

        # format data in linear (default is dB)
        vna.write("CALC1:FORM MLIN\n")

        # Read the formatted trace data
        s11_data = vna.query("CALC1:DATA? FDAT\n")

        # Convert the formatted data to a numpy array
        mags = np.fromstring(s11_data, dtype=float, sep=',')
        print("Printing mags:")
        print(mags)
        print()

        # linspace for frequency axis
        freqs = np.linspace(float(start_freq), float(stop_freq), int(num_freq_points))

        print("end of s11")

    except Exception as e:
        print(f"Error: {e}")



if __name__ == '__main__':
    vna_address = 'TCPIP::zva67-101058.mshome.net::inst0::INSTR'
    vna = RsInstrument(vna_address)
    test_s21()
    test_s11()
    vna.close()


