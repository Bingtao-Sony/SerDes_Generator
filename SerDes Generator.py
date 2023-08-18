import tkinter as tk
from tkinter import ttk
import re
import os
from tkinter import messagebox

global selected_serializer, selected_deserializer
global ser_add
global selected_format
global info, name, brand
global fsync_pin, reset_pin

des_add = f"0x48"
ohm_symbol = "\u03A9"  # Unicode for the Ohm symbol
low = "0x80"
high = "0x90"
blk_break = f"//--------------------------------------------"

def judgment(r1_value, r2_value):# V-devidor calculation
    if r1_value.endswith("k"):
        r1_float = float(r1_value[:-1]) * 1000 # k to 1,000 save as float
    elif r1_value == "open": # Pull down, V = 0
        v_devider = 0
    else:
        r1_float = float(r1_value)
    
    if r2_value.endswith("k"):
        r2_float = float(r2_value[:-1]) * 1000 # k to 1,000 save as float
    elif r2_value == "open": # Pull up, v = 1
        v_devider = 1
    else:
        r2_float = float(r2_value)

    if r1_value == "open" and r2_value == "open":# Both open, return 9.999 to indicate problem
        v_devider = 9.999   
    
    if r1_value != "open" and r2_value != "open":# Neither open, calculate the value
        v_devider = r2_float / (r1_float + r2_float)
    
    return v_devider

def determine(v_devider, mode1_1, mode1_2, mode2_1,mode2_2, mode3_1, mode3_2, type, pin): # Determine mode
    if type == "MAX_96717F":
        if pin == "CFG0":
            if 0 <= v_devider <= 0.117:
                return (mode1_1, mode2_1, mode3_1)
            elif 0.169 <= v_devider <= 0.236:
                return (mode1_1, mode2_1, mode3_2)
            elif 0.288 <= v_devider <= 0.355:
                return (mode1_1, mode2_2, mode3_1)
            elif 0.407 <= v_devider <= 0.474:
                return (mode1_1, mode2_2, mode3_2)
            elif 0.526 <= v_devider <= 0.593:
                return (mode1_2, mode2_1, mode3_2)
            elif 0.645 <= v_devider <= 0.712:
                return (mode1_2, mode2_1, mode3_1)
            elif 0.764 <= v_devider <= 0.831:
                return (mode1_2, mode2_2, mode3_2)
            elif 0.883 <= v_devider <= 1:
                return (mode1_2, mode2_2, mode3_1)
            elif 1 < v_devider :
                return (9999, 9999, 9999)# Both Open
            else:
                return (0000, 0000, 0000)# V-devidor falls in an undifined region
        elif pin == "CFG1":
            if 0 <= v_devider <= 0.117:
                return (mode1_1, mode2_1, mode3_1)
            elif 0.169 <= v_devider <= 0.236:
                return (mode1_1, mode2_1, mode3_1)
            elif 0.288 <= v_devider <= 0.355:
                return (mode1_1, mode2_1, mode3_2)
            elif 0.407 <= v_devider <= 0.474:
                return (mode1_1, mode2_1, mode3_2)
            elif 0.526 <= v_devider <= 0.593:
                return (mode1_2, mode2_1, mode3_1)
            elif 0.645 <= v_devider <= 0.712:
                return (mode1_2, mode2_1, mode3_1)
            elif 0.764 <= v_devider <= 0.831:
                return (mode1_2, mode2_1, mode3_2)
            elif 0.883 <= v_devider <= 1:
                return (mode1_2, mode2_1, mode3_2)
            elif 1 < v_devider :
                return (9999, 9999, 9999)
            else:
                return (0000, 0000, 0000)
            
    elif type == "MAX_96717":
        if pin == "CFG0":
            if 0 <= v_devider <= 0.117:
                return (mode1_1, mode2_1, mode3_1)
            elif 0.169 <= v_devider <= 0.236:
                return (mode1_1, mode2_1, mode3_2)
            elif 0.288 <= v_devider <= 0.355:
                return (mode1_1, mode2_2, mode3_1)
            elif 0.407 <= v_devider <= 0.474:
                return (mode1_1, mode2_2, mode3_2)
            elif 0.526 <= v_devider <= 0.593:
                return (mode1_2, mode2_1, mode3_2)
            elif 0.645 <= v_devider <= 0.712:
                return (mode1_2, mode2_1, mode3_1)
            elif 0.764 <= v_devider <= 0.831:
                return (mode1_2, mode2_2, mode3_2)
            elif 0.883 <= v_devider <= 1:
                return (mode1_2, mode2_2, mode3_1)
            elif 1 < v_devider :
                return (9999, 9999, 9999)
            else:
                return (0000, 0000, 0000)
        elif pin == "CFG1":
            if 0 <= v_devider <= 0.117:
                return (mode1_1, mode2_1, mode3_1)
            elif 0.169 <= v_devider <= 0.236:
                return (mode1_1, mode2_2, mode3_1)
            elif 0.288 <= v_devider <= 0.355:
                return (mode1_1, mode2_1, mode3_2)
            elif 0.407 <= v_devider <= 0.474:
                return (mode1_1, mode2_2, mode3_2)
            elif 0.526 <= v_devider <= 0.593:
                return (mode1_2, mode2_1, mode3_1)
            elif 0.645 <= v_devider <= 0.712:
                return (mode1_2, mode2_2, mode3_1)
            elif 0.764 <= v_devider <= 0.831:
                return (mode1_2, mode2_1, mode3_2)
            elif 0.883 <= v_devider <= 1:
                return (mode1_2, mode2_2, mode3_2)
            elif 1 < v_devider :
                return (9999, 9999, 9999)
            else:
                return (0000, 0000, 0000)
        
        # Add other Ser here

    else:
            return (9998, 9998, 9998)# When no Ser is selected

def ASCII_art(r1_value, r2_value, cfg_name, determine,voltage, pin):# Generate Art
    if determine == (0000,0000,0000):# 如果分压落入了没有被定义的空间
        updated_text = (
            f"There is no such combination\n"
            f"of R1 & R2, please check the\n"
            f"provided circuit\n"
            )

    elif determine == (9999,9999,9999):# 如果上下都是开路
        updated_text = (
            f"The Resistors cannot be both open \n"
            f"Please check the provided circuit\n"
        )

    elif determine == (9998,9998,9998):# 如果没有选择串行器
        updated_text = (
            f"Please Select a Serilizer\n"
        )

    else:# 如果分压正确
        if pin == "CFG0":
            mode_info = f"{determine[0]},{determine[1]},Slave Address = {determine[2]}"
        elif pin == "CFG1":
            mode_info = f"{determine[0]},Data Rate = {determine[1]},{determine[2]}"
        percentage = voltage * 100
        formatted_percentage = f"{percentage:.1f}%"
        updated_text = (
            f"       ————————  VDD\n"
            f"   |\n"
            f"   |\n"
            f"   ———\n"
            f"             |  | R1={r1_value.rjust(5)}{ohm_symbol}\n"
            f"   |  |\n"
            f"   ———\n"
            f"               |________{cfg_name}\n"
            f"   |\n"
            f"   ———\n"
            f"             |  | R2={r2_value.rjust(5)}{ohm_symbol}\n"
            f"   |  |\n"
            f"   ———\n"
            f"   |\n"
            f"   |\n"
            f"   -----\n"
            f"          ---    GND\n"
            f"   -\n"
            f"V Devider Rule Gives:{formatted_percentage}\n"
            f"{mode_info} "
        )

    return updated_text

def update_left_text():# CFG0 Art
    CFG0_r1_value = r1_entry_left.get().strip().lower()  # Convert to lowercase and remove leading/trailing spaces
    CFG0_r2_value = r2_entry_left.get().strip().lower()  # Convert to lowercase and remove leading/trailing spaces
    
    global selected_serializer
    selected_serializer = serial_combobox_Ser.get()

    v_devider_CFG0 = judgment(CFG0_r1_value, CFG0_r2_value)
    Mode = determine(v_devider_CFG0, "I2C", "UART", "ROR","Xart", "0x80", "0x84",selected_serializer,"CFG0")
    updated_text_CFG0 = ASCII_art(CFG0_r1_value, CFG0_r2_value,"CFG0", Mode,v_devider_CFG0,"CFG0")

    display_label1.config(text = updated_text_CFG0)

    return Mode[2] # Return Ser address

def update_right_text():# CFG1 art
    CFG1_r1_value = r1_entry_right.get().strip().lower()  # Convert to lowercase and remove leading/trailing spaces
    CFG1_r2_value = r2_entry_right.get().strip().lower()  # Convert to lowercase and remove leading/trailing spaces

 
    v_devider_CFG1 = judgment(CFG1_r1_value, CFG1_r2_value)
    Mode = determine(v_devider_CFG1, "STP", "COAX", "3","6", "Tunnel", "Pixel",selected_serializer,"CFG1")
    updated_text_CFG1 = ASCII_art(CFG1_r1_value, CFG1_r2_value,"CFG1", Mode,v_devider_CFG1,"CFG1")
    
    display_label2.config(text=updated_text_CFG1)

    return Mode[1] # Retrun trans rate

def deserialiser_select():# Get Des type
    return serial_combobox_Des.get()  

def brand_select():# Get Sensor type
    return serial_combobox_brand.get()

def update_serializer_selection(event):# Auto refresh CFG0 CFG1 when reselect Ser
    update_left_text()
    update_right_text()

def i2c (slv_add, reg_add, value):# I2C Cmd \n
    return f"$i2c, 1, {slv_add}, {reg_add}, 1, {value}\n"

def wait (time):# Wait Cmd \n\n
    return (f"$wait, {time}\n\n")

def center_and_fill (text, width, fill_char='-'): # Center the str
    return text.center(width, fill_char)

def get_spd(type, trans_speed, value_1, value_2):
    if type == "MAX_96717F":
        spd_1 = "3"
        spd_2 = "3"
    elif type == "MAX_96717" or type == "MAX_9296":
        spd_1 = "3"
        spd_2 = "6"
        # Add other SerDes here

    if trans_speed == spd_1:
        ser_speed = (type, value_1, spd_1, spd_2)
    elif trans_speed == spd_2:
        ser_speed = (type, value_2, spd_1, spd_2)
    return ser_speed

def extract_number (text):# 使用正则表达式匹配数字部分
    match = re.search(r'\d+', text)
    if match:
        return int(match.group())
    else:
        return None

def add_mapping (num):# Use the table to associate pin# to address
    hex_mapping = {
        0: ("0x02DF","0x02DE","0x02BF","0x02BE"),
        1: ("0x02D0","0x02DF","0x02B0","0x02BF"),
        2: ("0x02D1","0x02D0","0x02B1","0x02B0"),
        3: ("0x02D2","0x02D1","0x02B2","0x02B1"),
        4: ("0x02D3","0x02D2","0x02B3","0x02B2"),
        5: ("0x02D4","0x02D3","0x02B4","0x02B3"),
        6: ("0x02D5","0x02D4","0x02B5","0x02B4"),
        7: ("0x02D6","0x02D5","0x02B6","0x02B5"),
        8: ("0x02D7","0x02D6","0x02B7","0x02B6"),
        9: ("0x02D8","0x02D7","0x02B8","0x02B7"),
        10: ("0x02D9","0x02D8","0x02B9","0x02B8"),
    }
    return hex_mapping.get(num, ("Invalid","Invalid","Invalid","Invalid"))

def output_header ():# Write Header part
    global info, name, brand, fsync_pin, reset_pin, selected_deserializer
    info = module.get()
    name = author.get()
    brand = brand_select()
    fsync_pin = serial_combobox_fsync.get()
    reset_pin = serial_combobox_reset.get()
    selected_deserializer = deserialiser_select()
    output_header_txt = (
        f"{blk_break}\n\n"
        f"//Command,VALUE\n"
        f"//ID = {brand}{info}\n"
        f"//作者：{name}\n"
        f"//FSYNC——{fsync_pin}\n"
        f"//RESET——{reset_pin}\n"
        f"\n"
        f"//Serializer / Deserializer\n"
        f"//{selected_serializer} / {selected_deserializer}\n"
        f"{blk_break}\n\n"
    )
    return output_header_txt

def ouput_des ():# Write Des MAX_96717F MAX_96717 MAX_9296
    speed = get_spd(selected_deserializer, update_right_text(), "0x01", "0x02")

    output_des_cmd = (
        f"{blk_break}\n\n"
        f"//{center_and_fill('Set Data rate for Des',40)}\n"
        f"//{speed[0]}: 1:{speed[2]}G  2:{speed[3]}G\n"
        f"{i2c(des_add, '0x01',speed[1])}"
        f"{wait(100)}"
        f"//{center_and_fill('stream ID选择, 不用修改',40)}\n"
        f"{i2c(des_add, '0x51','0x02')}"
        f"{i2c(des_add, '0x52','0x01')}"
        f"{wait(100)}"
        f"//{center_and_fill('Reset DeSerializer Datapath',40)}\n"
        f"{i2c(des_add, '0x10','0x31')}"
        f"{wait(100)}"
        f"{blk_break}\n\n"
    )

    return output_des_cmd

def output_ser ():# Write Ser MAX_96717F MAX_96717
    global ser_add
    ser_add = update_left_text()
    speed = get_spd(selected_serializer, update_right_text(), "0x04", "0x08")

    output_ser_cmd = (
        f"{blk_break}\n\n"
        f"//{center_and_fill('Set Data rate for Ser',40)}\n"
        f"//{speed[0]}: 4:{speed[2]}G  8:{speed[3]}G\n"
        f"{i2c(ser_add, '0x01',speed[1])}"
        f"{wait(100)}"
        #  f"//{center_and_fill('stream ID选择，不用修改',40)}\n"
        #  f"{i2c({ser_add}, '0x51','0x02')}"
        #  f"{i2c({ser_add}, '0x52','0x01')}"
        #  f"{wait(100)}"
        f"//{center_and_fill('Reset Serializer Datapath',40)}\n"
        f"{i2c(ser_add, '0x10','0x21')}"
        f"{wait(100)}"
        f"{blk_break}\n\n"
    )

    return output_ser_cmd

def output_format ():# Write output format
    global selected_format
    selected_format = serial_combobox_Format.get()

    if selected_format == "RAW-12":
        value = "0x6C"
    elif selected_format == "RAW-10":
        value = "0x6B"
    elif selected_format == "YUV":
        value = "0x5E"

    output_format_cmd = (
        f"{blk_break}\n\n"
        f"//Raw12 format setting;0x6C:RAW12;0x6B:RAW10;0x5E:YUV;\n"
        f"{i2c(ser_add, '0x0318',value)}\n"
        f"{blk_break}\n\n"
    )

    return output_format_cmd

def output_sensor_add ():# FSYNC sets the sensor address L——0x1A H——0x1B
    pin = serial_combobox_fsync.get()
    pin_num = extract_number(pin)
    add = add_mapping(pin_num)
    slv_add = serial_combobox_fsync_LH.get()

    if slv_add == "0x1A":
        voltage = low
    elif slv_add == "0x1B":
        voltage = high

    output_fsync_cmd = (
        f"{blk_break}\n\n"
        f"//{pin}-FSYNC outputs : L→0x1A H→0x1B\n"
        f"{i2c(ser_add, add[0],'0x68')}"
        f"{wait(100)}"
        f"{i2c(ser_add, add[1],voltage)}"
        f"{wait(100)}"
        f"{blk_break}\n\n"
    )

    return output_fsync_cmd

def output_reset(): # RESET provides a trigger edge L→0x80 H→0x90
    pin = serial_combobox_reset.get()
    pin_num = extract_number(pin)
    add = add_mapping(pin_num)
    tgg_edge = serial_combobox_reset_LH.get()

    if tgg_edge == "Rising Edge L → H":
        voltage = (low, high, "Rising Edge")
    elif tgg_edge == "Falling Edge H → L":
        voltage = (high, low, "Falling Edge")


    output_reset_cmd = (
        f"{blk_break}\n\n"
        f"//{pin}-RESET provides : {voltage[2]};\n"
        f"{i2c(ser_add, add[2],'0x68')}"
        f"{wait(100)}"
        f"{i2c(ser_add, add[3],voltage[0])}"
        f"{wait(100)}"
        f"{i2c(ser_add, add[3],voltage[1])}"
        f"{wait(100)}"
        f"{blk_break}\n\n"
    )

    return output_reset_cmd

def compile_button_callback():  # Outpu .txt
    # Run all the output_XXx
    header_output = output_header()
    des_output = ouput_des()
    ser_output = output_ser()
    format_output = output_format()
    sensor_add_output = output_sensor_add()
    reset_output = output_reset()

    # Get file path
    global file_name
    file_name = f"{brand}_{info}_{name}_Fsync-{fsync_pin}_Reset-{reset_pin}_Ser-{selected_serializer}_Des-{selected_deserializer}.txt"
    current_folder = os.getcwd()  # Get .py folder path
    global file_path
    file_path = os.path.join(current_folder, file_name)

    # Write output to .txt
    with open(file_path, "w") as f:  # 修改为使用 file_path
        f.write(header_output)
        f.write(des_output)
        f.write(ser_output)
        f.write(format_output)
        f.write(sensor_add_output)
        f.write(reset_output)

    # Save file path
    file_location_label.config(text=f"File Saved to: {file_path}")

def open_file():  # open output file
    if os.path.exists(file_path):
        os.system("start " + file_path)  # Open in windows
    else:
        messagebox.showerror("Erroe", "No such file")

root = tk.Tk()
root.title("SerDes file generator")

frame = tk.Frame(root)
frame.pack()

"""
       0      1       2      3
0  |模组信息|输入框|作者信息|输入框|
1  | 串行器 |下拉框| 解串器 |下拉框|
2  |  CFG0字符画  |  CFG1字符画  |
3  |CFG0R1=|输入框|CFG0R1=|输入框|
4  |CFG0R2=|输入框|CFG0R2=|输入框|
5  |   更新按钮   |   更新按钮    |
6  | FSYNC |下拉框|地址选择|下拉框|
7  | RESET |下拉框|触发状态|下拉框|
8  | 输出格 |下拉框|模组选择|下拉框|
8  |   生成按钮   |   打开文件夹   |
10 |           生成路径           |
"""

# Manufacturer Info
module_info = tk.Label(frame, text="Manufacturer:")
module_info.grid(row=0, column=0, sticky="w", padx=10)# 0-0

module = tk.Entry(frame)
module.grid(row=0, column=1, sticky="w")# 0-1

# Auther Info
author_info = tk.Label(frame, text="Author:")
author_info.grid(row=0, column=2, sticky="w", padx=10)# 0-2

author = tk.Entry(frame)
author.grid(row=0, column=3, sticky="w")# 0-3

# Select Ser
serial_label = tk.Label(frame, text="Serializer:")
serial_label.grid(row=1, column=0, sticky="w", padx=10)# 1-0

serial_combobox_Ser = ttk.Combobox(frame, values=["MAX_96717F", "MAX_96717"]) # Add other Ser
serial_combobox_Ser.grid(row=1, column=1, sticky="w")# 1-1
serial_combobox_Ser.set("Plz Select a Serializer")# Default: "Plz Select a Serializer"
serial_combobox_Ser.bind("<<ComboboxSelected>>", update_serializer_selection)  # 绑定选择事件

# Select Des
deserial_label = tk.Label(frame, text="Deserializer:")
deserial_label.grid(row=1, column=2, sticky="w", padx=10)# 1-2

serial_combobox_Des = ttk.Combobox(frame, values=["MAX_96717F", "MAX_96717", "MAX_9296"]) # Add other Des
serial_combobox_Des.grid(row=1, column=3, sticky="w")# 1-3
serial_combobox_Des.set("MAX_9296")# Default: "MAX_9296"

# CFG0 art display
display_label1 = tk.Label(frame, font=("Courier", 10))
display_label1.grid(row=2, column=0, columnspan=2, padx=10, pady=10)# 2-0

# CFG1 art display
display_label2 = tk.Label(frame, font=("Courier", 10))
display_label2.grid(row=2, column=2, columnspan=2, padx=10, pady=10)# 2-2

# CFG0 R input
r1_label_left = tk.Label(frame, text="CFG0|R1=")
r1_label_left.grid(row=3, column=0, sticky="w", padx=10)# 3-0

r1_entry_left = tk.Entry(frame)
r1_entry_left.grid(row=3, column=1, sticky="w")# 3-1

r2_label_left = tk.Label(frame, text="CFG0|R2=")
r2_label_left.grid(row=4, column=0, sticky="w", padx=10)# 4-0

r2_entry_left = tk.Entry(frame)
r2_entry_left.grid(row=4, column=1, sticky="w")# 4-1

# Refresh CFG0 Art Manully
update_button_left = tk.Button(frame, text="Check CFG0", command=update_left_text)
update_button_left.grid(row=5, column=0, columnspan=2, pady=10)# 5-0

# CFG1 R input
r1_label_right = tk.Label(frame, text="CFG1|R1=")
r1_label_right.grid(row=3, column=2, sticky="w", padx=10)# 3-2

r1_entry_right = tk.Entry(frame)
r1_entry_right.grid(row=3, column=3, sticky="w")# 3-3

r2_label_right = tk.Label(frame, text="CFG1|R2=")
r2_label_right.grid(row=4, column=2, sticky="w", padx=10)# 4-2

r2_entry_right = tk.Entry(frame)
r2_entry_right.grid(row=4, column=3, sticky="w")# 4-3

# Refresh CFG1 Art Manully
update_button_right = tk.Button(frame, text="Check CFG1", command=update_right_text)
update_button_right.grid(row=5, column=2, columnspan=2, pady=10)# 5-2

# FSYNC Pin
fsync_label = tk.Label(frame, text="FSYNC PIN:")
fsync_label.grid(row=6, column=0, sticky="w", padx=10)# 6-0

serial_combobox_fsync = ttk.Combobox(frame, values=["MFP0", "MFP1", "MFP2", "MFP3", 
                                                    "MFP4", "MFP5", "MFP6", "MFP7", 
                                                    "MFP8", "MFP9", "MFP10"]) # Add other pin
serial_combobox_fsync.grid(row=6, column=1, sticky="w")# 6-1
serial_combobox_fsync.set("Plz Select a PIN")# Defualt: "Plz Select a PIN"

# FSYNC Pin —— H 0x1A L 0x1B
fsync_LH_label = tk.Label(frame, text="Sensor Address:")
fsync_LH_label.grid(row=6, column=2, sticky="w", padx=10)# 6-2

serial_combobox_fsync_LH = ttk.Combobox(frame, values=["0x1A", "0x1B"]) # Add other address
serial_combobox_fsync_LH.grid(row=6, column=3, sticky="w")# 6-3
serial_combobox_fsync_LH.set("0x1A")# Defualt: "0x1A"

# RESET Pin 
reset_label = tk.Label(frame, text="RESET PIN")
reset_label.grid(row=7, column=0, sticky="w", padx=10)# 7-0

serial_combobox_reset = ttk.Combobox(frame, values=["MFP0", "MFP1", "MFP2", "MFP3", 
                                                    "MFP4", "MFP5", "MFP6", "MFP7", 
                                                    "MFP8", "MFP9", "MFP10"]) # Add other pin
serial_combobox_reset.grid(row=7, column=1, sticky="w")# 7-1
serial_combobox_reset.set("Plz Select a PIN")# Defualt: "Plz Select a PIN"

# RESET Pin —— LH Positive Edge HL Negative Edge
reset_label_LH = tk.Label(frame, text="Trigger Edge:")
reset_label_LH.grid(row=7, column=2, sticky="w", padx=10)# 7-2

serial_combobox_reset_LH = ttk.Combobox(frame, values=["Rising Edge L → H", "Falling Edge H → L"]) # Add other pattern
serial_combobox_reset_LH.grid(row=7, column=3, sticky="w")# 7-3
serial_combobox_reset_LH.set("Rising Edge L → H")# Defualt: "Plz Select a PIN"

# Select Output Format
Format_label = tk.Label(frame, text="Output Format:")
Format_label.grid(row=8, column=0, sticky="w", padx=10)# 8-0

serial_combobox_Format = ttk.Combobox(frame, values=["RAW-12", "RAW-10", "YUV"]) # Add other format
serial_combobox_Format.grid(row=8, column=1, sticky="w")# 8-1
serial_combobox_Format.set("Plz Select a output format")# Defualt: "Plz Select a output format"

# Select Sensor Type
brand_label = tk.Label(frame, text="Sensor Type:")
brand_label.grid(row=8, column=2, sticky="w", padx=10)# 8-2

serial_combobox_brand = ttk.Combobox(frame, values=["ISX031", "IMX623", "ISX728"]) # Add other type
serial_combobox_brand.grid(row=8, column=3, sticky="w")# 8-3
serial_combobox_brand.set("Plz Select a sensor type")# Defualt: "Plz Select a sensor type"

# Generate File
compile_button = tk.Button(frame, text="Compile Now", command=compile_button_callback)
compile_button.grid(row=9, column=0, columnspan=2, pady=10)# 9-0

# Open File
compile_button = tk.Button(frame, text="Open File", command=open_file)
compile_button.grid(row=9, column=2, columnspan=2, pady=10)# 9-2

# Show File Path
file_location_label = tk.Label(frame, text="File Saved as:")
file_location_label.grid(row=10, column=0, columnspan=4, sticky="w", padx=10)# 10

root.mainloop()
