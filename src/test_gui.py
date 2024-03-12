import controller
import tkinter as tk
from tkinter import filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from numpy import linspace
from time import sleep
from decimal import Decimal


class ApplicationGUI:

    def __init__(self):
        # create an example sweep_data_all list
        self.sweep_data_all = [
            {
                'degree': 0,
                'frequency': [10, 20, 30],
                's11': [-20, -21, -22],
                's21': [-30, -31, -32]
            },
            {
                'degree': 45,
                'frequency': [10, 20, 30],
                's11': [-20, -21, -22],
                's21': [-30, -31, -32]
            },
            {
                'degree': 90,
                'frequency': [10, 20, 30],
                's11': [-20, -21, -22],
                's21': [-30, -31, -32]
            }, 
            {
                'degree': 180,
                'frequency': [10, 20, 30],
                's11': [-20, -21, -22],
                's21': [-30, -31, -32]
            }
        ]
        self.root = tk.Tk()
        self.root.title("System Control")
        # Callibrate Section
        calibration_frame = tk.LabelFrame(self.root, text="Calibration Mode", padx=5, pady=5)
        calibration_frame.pack(padx=10, pady=10, fill="x")
        # Calibration instructions
        # Create the calibration instruction label
        self.calibration_instruction = tk.Label(calibration_frame, text="Calibrate the arm with the buttons below until arm is at desired location for")
        self.calibration_instruction.pack(side=tk.LEFT)
        
        # Variable to hold the dropdown selection
        self.calibration_degree = tk.StringVar(value="0")  # default value as 0
        
        # Create the dropdown menu with options for calibration
        self.degree_options = ['0', '90', '-90']
        self.calibration_menu = tk.OptionMenu(calibration_frame, self.calibration_degree, *self.degree_options)
        self.calibration_menu.pack(side=tk.LEFT)

        # Label for "degrees. Turn OFF calibration mode when done."
        self.degree_label = tk.Label(calibration_frame, text="degrees. Turn OFF calibration mode when done.")
        self.degree_label.pack(side=tk.LEFT)

        # CCW and CW buttons
        ccw_button = tk.Button(calibration_frame, text="CCW", command=self.move_ccw)
        ccw_button.pack(side="left", padx=5, pady=5)
        
        cw_button = tk.Button(calibration_frame, text="CW", command=self.move_cw)
        cw_button.pack(side="left", padx=5, pady=5)
        
        # Calibration Mode Toggle
        calibration_mode_label = tk.Label(calibration_frame, text="Calibration Mode")
        calibration_mode_label.pack(side="left", padx=(10, 2), pady=5)
        
        # check button default is on
        self.calibration_mode = tk.BooleanVar(value=True)
        calibration_toggle = tk.Checkbutton(calibration_frame, text="On/Off", variable=self.calibration_mode, command=self.toggle_calibration_mode)
        calibration_toggle.pack(side="left", padx=2, pady=5)
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

        tk.Label(arm_frame, text="Current Arm Position").grid(row=6, column=0)
        self.current_position_label = tk.Label(arm_frame, text="0")
        self.current_position_label.grid(row=6, column=1)

        # label that shows how many steps the arm will move
        self.steps_label = tk.Label(arm_frame, text="0 steps")
        self.steps_label.grid(row=5, column=0, columnspan=2)

        tk.Button(arm_frame, text="Start Position", command=self.take_arm_inputs).grid(row=7, column=0, columnspan=2)

        # VNA Setup Section
        vna_frame = tk.LabelFrame(self.root, text="VNA Setup (Frequency Range: 10 Mhz to 67 GHz)", padx=5, pady=5)
        vna_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(vna_frame, text="Start Frequency").grid(row=0, column=0)
        self.start_frequency_entry = tk.Entry(vna_frame)
        self.start_frequency_entry.grid(row=0, column=1)
        # default values
        self.start_frequency_entry.insert(0, "10")

        tk.Label(vna_frame, text="Stop Frequency").grid(row=1, column=0)
        self.stop_frequency_entry = tk.Entry(vna_frame)
        self.stop_frequency_entry.grid(row=1, column=1)
        # default values
        self.stop_frequency_entry.insert(0, "67")

        tk.Label(vna_frame, text="No. of Points in Frequency Sweep").grid(row=2, column=0)
        self.num_points_entry = tk.Entry(vna_frame)
        self.num_points_entry.grid(row=2, column=1)
        # default values
        self.num_points_entry.insert(0, "100")

        # Create a button that will show the dropdown options when clicked
        self.dropdown_button_text = tk.StringVar()
        self.dropdown_button_text.set("Select Frequency")
        self.dropdown_button = tk.Button(vna_frame, textvariable=self.dropdown_button_text, command=self.show_dropdown)
        self.dropdown_button.grid(row=3, column=1)

        # Create a Menu that will act as the dropdown options
        self.dropdown_menu = tk.Menu(vna_frame, tearoff=0)

        # # create dropdown menu 
        # tk.Label(vna_frame, text="Select a Frequency from Below to be Plotted (GHz)").grid(row=3, column=0)
        # self.frequency2show = tk.StringVar(vna_frame)
        # self.frequency2show.set("Select Frequency")
        # freqs = linspace(int(self.start_frequency_entry.get()), int(self.stop_frequency_entry.get()), int(self.num_points_entry.get()))
        # self.freq_menu = tk.OptionMenu(vna_frame, self.frequency2show, *freqs)
        # self.freq_menu.grid(row=3, column=1)
        # # trigger the update of the dropdown menu when the dropdown button is clicked
        # self.frequency2show.trace_add('write', self.update_dropdown_menu)
        # Start Mesaurement Button
        tk.Button(vna_frame, text="Start Measurement", command=self.start_measurement).grid(row=4, column=0, columnspan=2)
        # Emergency Stop Button. 
        tk.Button(vna_frame, text="EMERGENCY STOP!", bg="red", command=self.emergency_stop).grid(row=5, column=0, columnspan=2)


        # Plot Section
        plot_frame = tk.LabelFrame(self.root, text="Plot", padx=5, pady=5)
        plot_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Create a figure for the s11 and s21 on the same plot, degree ranges froms -90 to 90
        self.fig = Figure(figsize=(5, 4), dpi=85)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Angle (degrees)")
        self.ax.set_ylabel("Magnitude (dB)")
        self.ax.set_title("S11 and S21")
        self.ax.set_xlim(-90, 90)
        self.ax.set_ylim(-50, 0)
        self.ax.grid()
        self.ax.plot([-90, 90], [-20, -20], label="S11", color="blue")
        self.ax.plot([-90, 90], [-30, -30], label="S21", color="green")
        self.ax.legend()
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # add a export button to the top right of the plot
        tk.Button(plot_frame, text="Export Data", command=self.export_data).pack(side="bottom")

    def emergency_stop(self):
        pass

    def show_dropdown(self):
        self.update_dropdown_menu()
        self.dropdown_menu.tk_popup(self.dropdown_button.winfo_rootx(), self.dropdown_button.winfo_rooty() + self.dropdown_button.winfo_height(), 0)

    def update_dropdown_menu(self):
        self.dropdown_menu.delete(0, tk.END)
        start_freq = int(self.start_frequency_entry.get())
        stop_freq = int(self.stop_frequency_entry.get())
        num_points = int(self.num_points_entry.get())
        freqs = linspace(start_freq, stop_freq, num_points)
        freqs = [round(freq, 2) for freq in freqs]
        
        # Repopulate the dropdown menu with new items
        for freq in freqs:
            self.dropdown_menu.add_command(label=f"{freq} GHz", command=lambda f=freq: self.select_option(f"{f} GHz"))

    def select_option(self, option):
        self.dropdown_button_text.set(option)


    # def update_dropdown_menu(self, *args):
    #     # update the dropdown menu with the frequency values
    #     freqs = linspace(int(self.start_frequency_entry.get()), int(self.stop_frequency_entry.get()), int(self.num_points_entry.get()))
    #     self.freq_menu['menu'].delete(0, 'end')
    #     for freq in freqs:
    #         self.freq_menu['menu'].add_command(label=freq, command=tk._setit(self.frequency2show, freq))

    def export_data(self):
        # Create a popup window for export options
        export_popup = tk.Toplevel()
        export_popup.title("Export VNA Data")
        export_popup.geometry("400x350")  # Width x Height

        # Label
        label = tk.Label(export_popup, text="Select the data to export:")
        label.pack(pady=10)

        # enumerate the sweep_data_all list and add all combinations of degree and frequency to the listbox
        listbox = tk.Listbox(export_popup)
        for data in self.sweep_data_all:
            for freq in data['frequency']:
                listbox.insert(tk.END, f"Degree: {data['degree']} - Frequency: {freq}")
        listbox.pack(pady=8)

        # Export Button
        export_button = tk.Button(export_popup, text="Export",
                                  command=lambda: self.save_data(listbox.get(listbox.curselection())))
        export_button.pack(pady=10)

        # Cancel Button
        cancel_button = tk.Button(export_popup, text="Cancel", command=export_popup.destroy)
        cancel_button.pack(pady=5)
    
    def save_data(self, selected):
        if not selected:
            message = "Please select the data to export."
            tk.messagebox.showwarning("No Data Selected", message)
            return
        # Ask the user for the filename and path to save the file, default file path is the scan_results folder
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                    filetypes=[("CSV files", "*.csv")], initialdir="scan_results", title="Save Scan Data")
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
            self.controller.update_motor_state('MOVE_CW')
            print("CW clicked")
        else:
            message = "Please turn on calibration mode to move the arm."
            tk.messagebox.showwarning("Calibration Mode Off", message)

    def move_ccw(self):
        if self.calibration_mode.get():
            self.controller.update_motor_state('MOVE_CCW')
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
        start_angle = Decimal((self.start_angle_entry.get()))
        stop_angle = Decimal((self.stop_angle_entry.get()))
        stepping_angle = Decimal((self.stepping_angle_entry.get()))
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
        num_steps = int(abs((start_angle - self.controller.current_position) / step))
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
        print("Starting measurements...")
        print("...")

    def toggle_calibration_mode(self):
        mode = self.calibration_mode.get()
        if mode:
            # pop up a message box to confirm the user wants to turn on calibration mode
            message = "Are you sure you want to turn on calibration mode?"
            answer = tk.messagebox.askyesno("Confirm", message)
            if answer:
                self.calibration_mode.set(True)
                print("Calibration mode ON")
                self.controller.update_motor_state('CALIBRATE')
        else:
            # pop up a message box to confirm the user wants to turn off calibration mode
            message = "Are you sure you want to turn off calibration mode?"
            answer = tk.messagebox.askyesno("Confirm", message)
            if answer:
                print("Calibration mode OFF")
                self.calibration_mode.set(False)
                self.controller.current_position = self.calibration_degree.get()
            else:
                self.calibration_mode.set(True)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    # arduino = serial.Serial(port="COM5", baudrate=9600, timeout=.1)
    gui = ApplicationGUI()
    gui.run()