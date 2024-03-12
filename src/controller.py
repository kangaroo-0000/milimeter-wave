import serial
import threading
import time
from queue import Queue
import os
import struct
import tkinter as tk
from RsInstrument import *
from tkinter import filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from decimal import Decimal

"""
    TODO: 
    show how many steps taken on the gui. @@done 
    reserve space in the start measurement function for synchronization with vna and closing vna.
    at the end of function, it should output a file of all scan results. 
    test connection with vna. show error message on gui for failed connection.
    prompt user for port connection to arduino, and test connection. show error if failed. 
    make antenna test funciton non blocking.
    change step angle tenth to hundredth.
    change struct pack to pack int. 
    plot the s11 and s21 on the same plot. 
    determine how frequency is gonna be stored as. for instance, as 18, or as 18e9, or maybe 18GHz? 
"""

class ActionLog:
    def __init__(self):
        self.log = []

    def log_action(self, action, status="started"):
        timestamp = time.time()
        log_entry = {'timestamp': timestamp, 'action': action, 'status': status}
        self.log.append(log_entry)

    def mark_action_complete(self, action):
        timestamp = time.time()
        for entry in reversed(self.log):
            if entry['action'] == action and entry['status'] == "started":
                entry['status'] = "done"
                entry['done_timestamp'] = timestamp
                break

    def check_action_completed(self, action):
        for entry in reversed(self.log):
            if entry['action'] == action and entry['status'] == "done":
                return True
        return False

class MotorControlModule:
    def __init__(self, port='/dev/cu.usbmodem101', baudrate=115200):
        self.ser = serial.Serial(port, baudrate)

    def send_command(self, command, num_steps=0, step_angle_tenths=0):
        command_bytes = struct.pack('>BHB', command, num_steps, step_angle_tenths)
        self.ser.write(command_bytes)


    def wait_for_acknowledgement(self, expected_command):
        while True:
            if self.ser.in_waiting:
                response = self.ser.read(1)
                print(f"Received response: {response}")
                if int.from_bytes(response, 'big') == expected_command:
                    break


class StoreVNADataAsCSV:
    def __init__(self, external_hard_drive_path):
        self.external_hard_drive_path = external_hard_drive_path
    
    def store_data(self, vna_data):
        filename = f"Antenna_{vna_data['degree']}_degrees_S11_S12.csv"
        file_path = os.path.join(self.external_hard_drive_path, filename)
        with open(file_path, 'w') as f:
            f.write('Frequency, S11, S21\n')
            for i in range(len(vna_data['frequency'])):
                f.write(f"{vna_data['frequency'][i]}, {vna_data['s11_data'][i]}, {vna_data['s21_data'][i]}\n")

class VNAModule:
    def __init__(self, ip_address):
        try:
            self.vna = RsInstrument('TCPIP::' + ip_address + '::INSTR', True, True)
        except Exception as e:
            print(f"Error: {e}")
            self.vna = None
        self.sweep_data = {}

    def antenna_test(self, start_freq, end_freq, num_of_points):
        if self.vna is None:
            return

        try:
            # Reset device and set display options
            self.vna.write("*RST; :DISP:ANN:FREQ ON\n")

            # Parameters for S11, S21, and S22 measurements
            s_parameters = ['S11', 'S21', 'S22']

            for s_param in s_parameters:
                # Assign trace name based on S-parameter
                if s_param == 'S21':
                    trace_name = 'Ch1Tr1'
                elif s_param == 'S11':
                    trace_name = 'Ch1Tr2'
                elif s_param == 'S22':
                    trace_name = 'Ch1Tr3'  # Assuming 'Ch1Tr3' for S22, adjust as needed
                
                # Create trace for the S-parameter on the channel
                self.vna.write(f"CALC1:PAR:SDEF '{trace_name}', '{s_param}'\n")

                # Set start and stop frequencies of sweep
                self.vna.write(f"SENS:FREQ:STAR {start_freq}e9\n")
                self.vna.write(f"SENS:FREQ:STOP {end_freq}e9\n")

                # Set number of points in frequency sweep
                self.vna.write(f"SWE:POIN {num_of_points}\n")
                time.sleep(1)  # Allow time for the VNA to apply settings

                # Fetch and print phase data
                self.vna.write("CALC1:FORM PHAS\n")
                phase_data = self.vna.query("CALC1:DATA? FDAT\n")
                phases = np.fromstring(phase_data, dtype=float, sep=',')

                # Fetch and print magnitude data
                self.vna.write("CALC1:FORM MLIN\n")
                magnitude_data = self.vna.query("CALC1:DATA? FDAT\n")
                magnitudes = np.fromstring(magnitude_data, dtype=float, sep=',')


            # Generate and print frequency axis
            freqs = np.linspace(start_freq, end_freq, num_of_points)

        except Exception as e:
            print(f"Error: {e}")
        
        # store the data in sweep_data 
        self.sweep_data[f"{s_param}_data"] = magnitudes
        self.sweep_data['frequency'] = freqs

        # Notify sweep completion
        self.on_sweep_complete()
        
    
    def on_sweep_complete(self):
        pass


class SystemController:
    def __init__(self, log):
        self.motor_control = MotorControlModule()
        # self.vna_control = VNAModule(ip_address='192.168.2.100')
        # self.vna_control.on_sweep_complete = self.handle_sweep_complete
        self.command_queue = Queue()
        self.process_thread = None
        self.current_position = 0
        self.sweep_data_all = []
        self.log = log
        self.start_frequency = 0
        self.end_frequency = 0
        self.num_points = 0

    def update_motor_state(self, command, num_steps=1, step_angle_tenths=9):
        # update current position
        if command == 1:
            self.current_position -= step_angle_tenths * num_steps / 10
            self.log.log_action("Moving CCW")
        elif command == 2:
            self.current_position += step_angle_tenths * num_steps / 10
            self.log.log_action("Moving CW")
        elif command == 3:
            self.log.log_action("Emergency Stop")
            # disconnect and connect to the motor
            self.motor_control.ser.close()
            time.sleep(1)
            self.motor_control.ser.open()

        # Enqueue commands based on the state
        self.command_queue.put((command, num_steps, step_angle_tenths))

        

    def process_queue(self):
        while True:
            try:
                command, num_steps, step_angle_tenths = self.command_queue.get()            
                print(f"Processing command: {command}")
                self.motor_control.send_command(command, num_steps, step_angle_tenths)
                self.motor_control.wait_for_acknowledgement(command)
                self.log.mark_action_complete("Moving CCW" if command == 1 else "Moving CW")
                self.command_queue.task_done()
                # self.vna_control.antenna_test(starting_frequency=self.start_frequency, ending_frequency=self.end_frequency, num_points=self.num_points)
            except Exception as e:
                print(f"Error: {e}")
                # restart thread and clean up queue
                self.command_queue.task_done()
                self.command_queue = Queue()
                self.process_thread = threading.Thread(target=self.process_queue, daemon=True)
                self.process_thread.start()


    def handle_sweep_complete(self):
        print("In function handle sweep complete")
        self.vna_control.sweep_data['degree'] = self.current_position
        store_data = StoreVNADataAsCSV(external_hard_drive_path="/name/to/external/hard/drive")
        store_data.store_data(self.vna_control.sweep_data)
        self.sweep_data_all.append(self.vna_control.sweep_data)

    def start(self):
        self.process_thread = threading.Thread(target=self.process_queue, daemon=True)
        self.process_thread.start()

    def set_current_position(self, position):
        self.current_position = position

class Application:
    def __init__(self, controller):
        self.controller = controller
        # create an example sweep_data_all list
        self.sweep_data_all = [
            {
                'degree': 0,
                'frequency': [10.0, 20.0, 30.0],
                's11': [-20, -21, -22],
                's21': [-30, -31, -32]
            },
            {
                'degree': 45,
                'frequency': [10.0, 20.0, 30.0],
                's11': [-20, -21, -22],
                's21': [-30, -31, -32]
            },
            {
                'degree': 90,
                'frequency': [10.0, 20.0, 30.0],
                's11': [-20, -21, -22],
                's21': [-30, -31, -32]
            }, 
            {
                'degree': 180,
                'frequency': [10.0, 20.0, 30.0],
                's11': [-20, -21, -22],
                's21': [-30, -31, -32]
            }
        ]
        self.root = tk.Tk()
        self.root.title("System Control")

        # Calibration Section
        calibration_frame = tk.LabelFrame(self.root, text="Calibration Mode", padx=5, pady=5)
        calibration_frame.pack(padx=10, pady=10, fill="x")

        # Calibration instructions
        self.calibration_instruction = tk.Label(calibration_frame, 
                                                text="Calibrate the arm with the buttons below until arm is at desired location for")
        self.calibration_instruction.grid(row=0, column=0, columnspan=4, sticky="w")

        # Dropdown selection
        self.calibration_degree = tk.StringVar(value="0")
        self.degree_options = ['0', '90', '-90']
        self.calibration_menu = tk.OptionMenu(calibration_frame, self.calibration_degree, *self.degree_options)
        self.calibration_menu.grid(row=0, column=4)

        # Degree label
        self.degree_label = tk.Label(calibration_frame, text="degrees. Turn OFF calibration mode when done.")
        self.degree_label.grid(row=0, column=5, sticky="w")

        # CCW button
        ccw_button = tk.Button(calibration_frame, text="CCW", command=self.move_ccw)
        ccw_button.grid(row=1, column=0, padx=2, pady=2, sticky="w")

        # CW button
        cw_button = tk.Button(calibration_frame, text="CW", command=self.move_cw)
        cw_button.grid(row=1, column=1, padx=2, pady=2, sticky="w")

        # Calibration mode toggle
        calibration_mode_label = tk.Label(calibration_frame, text="Calibration Mode")
        calibration_mode_label.grid(row=1, column=2, padx=(10, 2), pady=2, sticky="w")

        self.calibration_mode = tk.BooleanVar(value=True)
        calibration_toggle = tk.Checkbutton(calibration_frame, text="On/Off", variable=self.calibration_mode, command=self.toggle_calibration_mode)
        calibration_toggle.grid(row=1, column=3, padx=2, pady=5, sticky="w")
        calibration_toggle.select()


        # Arm Setup Section
        arm_frame = tk.LabelFrame(self.root, text="Arm Setup", padx=5, pady=5)
        arm_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(arm_frame, text="Start angle (degrees)").grid(row=0, column=0)
        self.start_angle_entry = tk.Entry(arm_frame)
        self.start_angle_entry.grid(row=0, column=1)

        tk.Label(arm_frame, text="Stop angle (degrees)").grid(row=1, column=0)
        self.stop_angle_entry = tk.Entry(arm_frame)
        self.stop_angle_entry.grid(row=1, column=1)

        # label for stepping angle
        tk.Label(arm_frame, text="Stepping angle (in multiples of 0.18 degrees)").grid(row=2, column=0)
        self.stepping_angle_entry = tk.Entry(arm_frame)
        self.stepping_angle_entry.grid(row=2, column=1)
        # default values
        self.stepping_angle_entry.insert(0, "0.9")
    
        # label that shows how many steps the arm will move
        self.steps_label = tk.Label(arm_frame, text="0 steps")
        self.steps_label.grid(row=5, column=0, columnspan=2)

        # label for current arm position 
        tk.Label(arm_frame, text="Current Arm Position").grid(row=6, column=0)
        self.current_position_label = tk.Label(arm_frame, text="0")
        self.current_position_label.grid(row=6, column=1)

        tk.Button(arm_frame, text="Start Position", command=self.take_arm_inputs).grid(row=7, column=0, columnspan=2)

        # VNA Setup Section
        vna_frame = tk.LabelFrame(self.root, text="VNA Setup (Horn Frequency Range: 18 Ghz to 25 GHz)", padx=5, pady=5)
        vna_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(vna_frame, text="Start Frequency").grid(row=0, column=0)
        self.start_frequency_entry = tk.Entry(vna_frame)
        self.start_frequency_entry.grid(row=0, column=1)
        # default values
        self.start_frequency_entry.insert(0, "18")

        tk.Label(vna_frame, text="Stop Frequency").grid(row=1, column=0)
        self.stop_frequency_entry = tk.Entry(vna_frame)
        self.stop_frequency_entry.grid(row=1, column=1)
        # default values
        self.stop_frequency_entry.insert(0, "20")

        tk.Label(vna_frame, text="No. of Points in Frequency Sweep").grid(row=2, column=0)
        self.num_points_entry = tk.Entry(vna_frame)
        self.num_points_entry.grid(row=2, column=1)
        # default values
        self.num_points_entry.insert(0, "101")

        # Create a button that will show the dropdown options when clicked
        self.dropdown_button_text = tk.StringVar()
        self.dropdown_button_text.set("Select Frequency to be plotted")
        self.dropdown_button = tk.Button(vna_frame, textvariable=self.dropdown_button_text, command=self.show_dropdown)
        self.dropdown_button.grid(row=3, column=1)

        # Create a Menu that will act as the dropdown options
        self.dropdown_menu = tk.Menu(vna_frame, tearoff=0)

        # Start Mesaurement Button
        tk.Button(vna_frame, text="Start Measurement", command=self.start_measurement).grid(row=4, column=0, columnspan=2)
        # Emergency Stop Button. 
        tk.Button(vna_frame, text="EMERGENCY STOP!", bg="red", command=self.emergency_stop).grid(row=5, column=0, columnspan=2)

        # Plot Section
        plot_frame = tk.LabelFrame(self.root, text="Plot", padx=5, pady=5)
        plot_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Create a figure for the s11 and s21 on the same plot, degree ranges froms -90 to 90
        self.fig = Figure(figsize=(5, 4), dpi=66)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Angle (degrees)")
        self.ax.set_ylabel("Magnitude")
        self.ax.set_title("S11 and S21")
        self.ax.set_xlim(-90, 90)
        self.ax.set_ylim(0, 200)
        self.ax.grid()
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # new section that contains the following buttons: export data, clear plot
        button_frame = tk.Frame(self.root)
        button_frame.pack(padx=1, pady=1, fill="x")

        # Export Data Button
        tk.Button(button_frame, text="Export Data", command=self.export_data).pack(side="left", padx=5, pady=5)

        # Clear Plot Button
        tk.Button(button_frame, text="Clear Plot", command=self.clear_plot).pack(side="left", padx=5, pady=5)


    def clear_plot(self):
        self.ax.clear()
        self.ax.set_xlabel("Angle (degrees)")
        self.ax.set_ylabel("Magnitude")
        self.ax.set_title("S11 and S21")
        self.ax.set_xlim(-90, 90)
        self.ax.set_ylim(0, 200)
        self.ax.grid()
        self.canvas.draw()

    def show_dropdown(self):
        self.update_dropdown_menu()
        self.dropdown_menu.tk_popup(self.dropdown_button.winfo_rootx(), self.dropdown_button.winfo_rooty() + self.dropdown_button.winfo_height(), 0)

    def update_dropdown_menu(self):
        self.dropdown_menu.delete(0, tk.END)
        start_freq = int(self.start_frequency_entry.get())
        stop_freq = int(self.stop_frequency_entry.get())
        num_points = int(self.num_points_entry.get())
        freqs = np.linspace(start_freq, stop_freq, num_points)
        freqs = [round(freq, 2) for freq in freqs]
        
        # Repopulate the dropdown menu with new items
        for freq in freqs:
            self.dropdown_menu.add_command(label=f"{freq} GHz", command=lambda f=freq: self.select_option(f"{f} GHz"))

    def select_option(self, option):
        self.dropdown_button_text.set(option)

    def export_data(self):
        # Create a popup window for export options
        export_popup = tk.Toplevel()
        export_popup.title("Export VNA Data")
        export_popup.geometry("400x350")  # Width x Height

        # Label
        label = tk.Label(export_popup, text="Select data to export (default saved to scan_results directory):")
        label.pack(pady=10)

        # enumerate the sweep_data_all list and add all combinations of degree and frequency to the listbox
        listbox = tk.Listbox(export_popup)
        for data in self.sweep_data_all:
            for freq in data['frequency']:
                listbox.insert(tk.END, f"Degree: {data['degree']} - Frequency: {freq}")
        listbox.pack(pady=8)

        # Export Button
        export_button = tk.Button(export_popup, text="Export",
                                  command=lambda: self.save_data(listbox.curselection()))
        export_button.pack(pady=10)

        # Cancel Button
        cancel_button = tk.Button(export_popup, text="Cancel", command=export_popup.destroy)
        cancel_button.pack(pady=5)
    
    def save_data(self, selected):
        if not selected:
            message = "Please select the data to export."
            tk.messagebox.showwarning("No Data Selected", message)
            return
        # Ask the user for the filename and path to save the file
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                    filetypes=[("CSV files", "*.csv")], initialdir="scan_results", title="Save VNA Scan Results")
        if file_path:
            # Get the selected data from the listbox
            # get degree and frequency from the selected string
            selected = selected.split(" - ")
            selected_degree = int(selected[0].split(": ")[1])
            selected_frequency = int(selected[1].split(": ")[1])
            # find the index of the selected data in the sweep_data_all list
            selected_indices = [i for i, data in enumerate(self.sweep_data_all) if data['degree'] == selected_degree]
            # get the data from the sweep_data_all list
            selected_data = self.sweep_data_all[selected_indices[0]]
            # find the index of the selected frequency in the selected data
            selected_freq_index = selected_data['frequency'].index(selected_frequency)
            # create a filename
            filename = f"Antenna_{selected_degree}_degrees_Frequency_{selected_frequency}.csv"
            # create the file
            with open(file_path, 'w') as f:
                f.write('Degree, Frequency, S11, S21\n')
                f.write(f"{selected_degree}, {selected_frequency}, {selected_data['s11'][selected_freq_index]}, {selected_data['s21'][selected_freq_index]}\n")
            # show a message to the user
            message = f"The data has been saved to {file_path}"
            tk.messagebox.showinfo("Data Exported", message)

    def move_cw(self):
        if self.calibration_mode.get():
            self.controller.update_motor_state(2, 1, 9)
            print("CW clicked")
        else:
            message = "Please turn on calibration mode to move the arm."
            tk.messagebox.showwarning("Calibration Mode Off", message)

    def move_ccw(self):
        if self.calibration_mode.get():
            self.controller.update_motor_state(1, 1, 9)
            print("CCW clicked")
        else: 
            message = "Please turn on calibration mode to move the arm."
            tk.messagebox.showwarning("Calibration Mode Off", message)

    def take_arm_inputs(self):
        if self.calibration_mode.get():
            message = "Please turn off calibration mode to take arm inputs."
            tk.messagebox.showwarning("Calibration Mode On", message)
            return
        print("Starting measurements...")
        start_angle = Decimal(self.start_angle_entry.get())
        stop_angle = Decimal(self.stop_angle_entry.get())
        stepping_angle = Decimal(self.stepping_angle_entry.get())
        epsilion = Decimal('0.00001')

        # if stepping angle is not multiple of 0.18
        if stepping_angle % Decimal('0.18') > epsilion:
            print("result: ", stepping_angle % Decimal('0.18'))
            message = "Stepping angle should be a multiple of 0.18"
            tk.messagebox.showwarning("Invalid Stepping Angle", message)
            return
        
        # if difference between start and stop frequency is not multiple of stepping angle
        angle_difference = stop_angle - start_angle
        if angle_difference % stepping_angle > epsilion:
            print("result: ", angle_difference % stepping_angle)
            message = "The difference between start and stop angle should be a multiple of the stepping angle."
            tk.messagebox.showwarning("Invalid Angle Range", message)
            return

        print(f"Start Angle: {start_angle}")
        print(f"Stop Angle: {stop_angle}")
        print()

        step = stepping_angle
        if start_angle < self.controller.current_position:
            step = -stepping_angle
            
        # Calculate the number of steps needed
        num_steps = int(abs((start_angle - Decimal(self.controller.current_position)) / step))
        print("Current Position: " + str(self.controller.current_position))
        print(f"Number of steps: {num_steps}")

        # update the steps label
        self.steps_label.config(text=f"{num_steps} steps")

        # Check the direction and update the motor state accordingly
        if step > 0:
            self.controller.update_motor_state(2, num_steps, int(stepping_angle*10))
        else:
            self.controller.update_motor_state(1, num_steps, int(stepping_angle*10))
        
        # pop up message saying that the arm is at the start angle
        message = f"The arm is turning to start angle: {start_angle} degrees."
        tk.messagebox.showinfo("Arm Position", message)
        # update the current position label
        self.current_position_label.config(text=str(start_angle))


    def start_measurement(self):
        self.plot_s11_s21()
        # move to stop angle
        if self.calibration_mode.get():
            message = "Please turn off calibration mode to start measurements."
            tk.messagebox.showwarning("Calibration Mode On", message)
            return
        
        # if entries are empty, show a message to user
        if not self.start_frequency_entry.get() or not self.stop_frequency_entry.get() or not self.num_points_entry.get():
            message = "Please enter the start frequency, stop frequency, and number of points."
            tk.messagebox.showwarning("Missing Input", message)
            return
        
        # if arm section entries are empty, show a message to user
        if not self.start_angle_entry.get() or not self.stop_angle_entry.get() or not self.stepping_angle_entry.get():
            message = "Please enter the start angle, stop angle, and stepping angle."
            tk.messagebox.showwarning("Missing Input", message)
            return
        
        # get the start and stop frequency and number of points
        self.controller.start_frequency = int(self.start_frequency_entry.get()) * 1e9
        self.controller.end_frequency = int(self.stop_frequency_entry.get()) * 1e9
        self.controller.num_points = int(self.num_points_entry.get())

        # get the start and stop angle and stepping angle
        start_angle = float(self.start_angle_entry.get())
        stop_angle = float(self.stop_angle_entry.get())
        stepping_angle = float(self.stepping_angle_entry.get())
        print(f"Start Angle: {start_angle}")
        print(f"Stop Angle: {stop_angle}")
        print()

        # current position should now be start angle, move from start angle to stop angle
        step = stepping_angle
        if start_angle < self.controller.current_position:
            step = -stepping_angle
        
        # Calculate the number of steps needed
        num_steps = int(abs((start_angle - stop_angle) / step))
        print("Current Position: " + str(self.controller.current_position))
        print(f"Number of steps: {num_steps}")

        # Check the direction and update the motor state accordingly
        if step > 0:
            self.controller.update_motor_state(2, num_steps, int(stepping_angle*10))
        else:
            self.controller.update_motor_state(1, num_steps, int(stepping_angle*10))

        # update the current position label
        self.current_position_label.config(text=str(self.controller.current_position))

        # plot the s11 and s21 on the same plot
        

        # wait for arm to reach stop and export a file of all scan results. then pop up a message to user.

    def plot_s11_s21(self):
        selected_freq = int(float(self.dropdown_button_text.get().split(" ")[0]))
        print(selected_freq)
        # get the data from the sweep_data_all list
        selected_indices = [i for i, data in enumerate(self.sweep_data_all) if data['frequency'] == selected_freq]
        print(selected_indices)
        selected_data = self.sweep_data_all[selected_indices[0]]
        # find the index of the selected frequency in the selected data
        selected_freq_index = selected_data['frequency'].index(selected_freq)
        # plot the s11 and s21 on the same plot
        self.ax.plot(selected_data['degree'], selected_data['s11'][selected_freq_index], 'ro', label="S11")
        self.ax.plot(selected_data['degree'], selected_data['s21'][selected_freq_index], 'bo', label="S21")
        self.ax.legend()
        self.canvas.draw()

    def emergency_stop(self):
        # pop up a message box to confirm the user wants to stop the arm
        message = "Are you sure you want to stop the arm?"
        answer = tk.messagebox.askyesno("Confirm", message)
        if answer:
            print("Stopping the arm")
            # stop the arm
            self.controller.update_motor_state(3)
            # pop up a message to inform the user that the arm has stopped
            message = "The arm has stopped. Please turn on calibration mode to re-calibrate arm."
            tk.messagebox.showinfo("Arm Stopped", message)

    def toggle_calibration_mode(self):
        mode = self.calibration_mode.get()
        if mode:
            # pop up a message box to confirm the user wants to turn on calibration mode
            message = "Are you sure you want to turn on calibration mode?"
            answer = tk.messagebox.askyesno("Confirm", message)
            if answer:
                self.calibration_mode.set(True)
                print("Calibration mode ON")
        else:
            # pop up a message box to confirm the user wants to turn off calibration mode
            message = "Are you sure you want to turn off calibration mode? Is the arm at the desired location?"
            answer = tk.messagebox.askyesno("Confirm", message)
            if answer:
                print("Calibration mode OFF")
                self.calibration_mode.set(False)
                self.controller.set_current_position(int(self.calibration_degree.get()))
                # update the current position label
                print(f"Current Position: {self.controller.current_position}")
                self.current_position_label.config(text=str(self.controller.current_position))
            else:
                self.calibration_mode.set(True)

    def check_action_and_show_popup(self, action):
        # use threading to call this function; avoid blocking the main thread. Ideally, after every action, we should pop up a message to user.
        while not self.controller.log.is_action_completed(action):
            time.sleep(0.5)  # Check every half second
        self.root.after(0, lambda: tk.messagebox.showinfo("Notification", f"Action '{action}' completed."))


    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    log = ActionLog()
    controller = SystemController(log)
    app = Application(controller)
    controller.start()
    app.run()
    