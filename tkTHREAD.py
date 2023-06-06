
#!/usr/bin/python3

import numpy as np
import pathlib
import tkinter as tk
import tkinter.ttk as ttk
import os
PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "tkthread.ui"
directory = "output"
path = os.path.join(PROJECT_PATH, directory)

units = None
flank = None
threadClass = None
majorDia = None
feed = None
threadCenter = None
zFinal = None
numPass = None
infeedAngle = None
threadDepth = None
tool = None
workOffset = None
spindleSpeed = None
maxSpindlespeed = None
xClearance = None
z_Offset = None
zInitialFlank = None
zInitial = None
filename = None
fileType = None


def generate_code():

    def get_output(out):
        output_str = out
        print(output_str)
        f.write(f'{output_str}\n')

    def write_tool():
        get_output(f'G50 S{maxSpindlespeed} T{tool}')

    def start_spindle():
        get_output(f'G97 S{spindleSpeed} M3 P11')   
        
    def stop_spindle():
        get_output(f'M5')
         
    def write_units():
        if units == "Inch":
            get_output('G20')
        elif units == "MM":
            get_output('G21')
        
    def program_reset():
        get_output(F'M30\n%')
        
    def program_start():
        get_output(f'%\nO1000 ({filename})')

    def home_x():
        get_output(f'G28 U0.0')

    def home_z():
        get_output(f'G28 W0.0')     

    units = app.units.get() #get_input('Inch (I) or MM (M)\nDefault Inch: ', 'i').lower()
    flank = app.flank.get() #get_input('Flanking infeed? Y/N\nDefault No: ', 'n').lower()
    threadClass = app.threadClass.get() #"E"  # internal (I) or external (E) hard-coded default value
    #threadClass = "Internal"
    majorDia = float(app.majorDia.get()) #float(get_input('Major Diameter: ', 0))
    feed = float(app.feed.get()) #float(get_input('Thread Pitch: ', 0))
    threadCenter = float(app.threadCenter.get()) #float(get_input('Z Initial Position: ', 0))
    zFinal = float(app.zFinal.get()) #float(get_input('Z Final Position: ', 0))
    numPass = abs(app.numPass.get()) #abs(int(get_input('Number of Passes\nDefault 1: ', 1)))
    infeedAngle = float(app.infeedAngle.get()) #float(get_input('Infeed Angle\nDefault 29.5: ', 29.5))
    threadDepth = float(app.threadDepth.get()) #float(get_input('Radial Thread Depth\nDefault 0: ', 0))
    tool = str(app.tool.get()) #str(get_input('Tool#\nDefault 0000: ', '0000'))
    workOffset = int(app.workOffset.get()) #int(get_input('Work Offset\nDefault 54: ', 54))
    spindleSpeed = int(app.spindleSpeed.get()) #int(get_input('Cutting Speed\nDefault 100: ', 100))

    maxSpindlespeed = 250
    xClearance = .1
    z_Offset = np.tan(np.deg2rad(infeedAngle))
    zInitialFlank = (threadCenter - round(threadDepth * z_Offset,4))
    zInitial = (threadCenter + round(threadDepth * z_Offset,4))
    filename = f'{majorDia} X {feed} {units} {infeedAngle*2} DEG THREAD'
    fileType = '.nc'

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(f'{directory}/{filename}{fileType}', 'w') as f:
        
        program_start()
        write_units()
        home_x()
        home_z()
        write_tool()
        start_spindle()    
        if threadClass == "External":
            xApproach = round(majorDia + xClearance, 1) # APPROACH DIAMETER
            if numPass == 1:
                doC = threadDepth #SINGLE PASS
            else:
                doC = (threadDepth / numPass) # doC FIRST PASS
            diaFirstpass = round(majorDia - (2 * doC), 4) # DIAMETER OF FIRST PASS
            zInitial = round(zInitial - (doC * z_Offset),4)
            get_output(f'G0 G{workOffset} X{xApproach} Z{threadCenter}\nX{diaFirstpass} Z{zInitial}\nG32 Z{zFinal} F{feed}\nG0 X{xApproach}\nZ{threadCenter}')
            i = 2

        if threadClass == "Internal":
            xApproach = round(majorDia - (threadDepth * 2) - xClearance, 4)
            if numPass == 1:
                doC = threadDepth
            else:
                doC = (threadDepth / numPass)
            diaFirstpass = round(majorDia - (threadDepth * 2) + (2*doC),4)
            get_output(f'G0 G{workOffset} X{xApproach} Z{threadCenter}\nX{diaFirstpass} Z{zInitial}\nG32 Z{zFinal} F{feed}\nG0 X{xApproach}\nZ{threadCenter}')
            i = 2

        if numPass >= 2:
            while i <= numPass:
                if flank == "Yes": #LH
                    if i <= numPass:
                        apx = (threadDepth / numPass) * (i)
                        if threadClass == "External":
                            xpF = round(majorDia - (2 * apx), 4)
                        if threadClass == "Internal":
                            xpF = round(majorDia - (threadDepth * 2) + (2 * apx), 4)
                        zShift = (apx) * z_Offset # SHIFT ON Z
                        zF = round(zInitialFlank + zShift, 4) # Z SHIFTED FROM INITIAL Z
                        i += 1
                        get_output(f'GO X{xpF} Z{zF}\nG32 z{zFinal} F{feed}\nG0 X{xApproach}\nZ{threadCenter}')
                if i <= numPass:    
                    apx = (threadDepth / numPass) * (i)
                    if threadClass == "External":
                        xp = round(majorDia - (2 * apx), 4)
                    if threadClass == "Internal":
                        xp = round(majorDia - (threadDepth * 2) + (2 * apx), 4)
                    zShift = (apx - doC) * z_Offset # SHIFT ON Z
                    z = round(zInitial - zShift, 4) # Z SHIFTED FROM INITIAL Z
                    i += 1
                    get_output(f'G0 X{xp} Z{z}\nG32 Z{zFinal} F{feed}\nG0 X{xApproach}\nZ{threadCenter}')

        home_x()
        home_z()
        stop_spindle()
        program_reset()


class TkthreadApp:
    def __init__(self, master=None):
        # build ui
        toplevel1 = tk.Tk() if master is None else tk.Toplevel(master)
        toplevel1.configure(borderwidth=5, height=200, width=200)
        toplevel1.title("Thread")
        frame1 = ttk.Frame(toplevel1)
        frame1.configure(borderwidth=10, height=200, width=200)
        self.units_label = ttk.Label(frame1)
        self.units_label.configure(text='Units')
        self.units_label.grid(column=0, padx="0 5", row=1, sticky="w")
        self.units = tk.StringVar(value='Inch')
        __values = ['Inch', 'MM']
        self.opt_units = ttk.OptionMenu(
            frame1, self.units, "Inch", *__values, command=self.on_units)
        self.opt_units.grid(column=1, row=1, sticky="w")
        self.flank_label = ttk.Label(frame1)
        self.flank_label.configure(text='Flanking Infeed')
        self.flank_label.grid(column=0, row=2, sticky="w")
        self.majorDia_label = ttk.Label(frame1)
        self.majorDia_label.configure(text='Major Diameter')
        self.majorDia_label.grid(column=0, row=4, sticky="w")
        self.feed_label = ttk.Label(frame1)
        self.feed_label.configure(text='Thread Pitch')
        self.feed_label.grid(column=0, row=5, sticky="w")
        self.threadCenter_label = ttk.Label(frame1)
        self.threadCenter_label.configure(text='Z Initial Position')
        self.threadCenter_label.grid(column=0, row=6, sticky="w")
        self.zFinal_label = ttk.Label(frame1)
        self.zFinal_label.configure(text='Z Final Position')
        self.zFinal_label.grid(column=0, row=7, sticky="w")
        self.numPass_label = ttk.Label(frame1)
        self.numPass_label.configure(text='Number of Passes')
        self.numPass_label.grid(column=0, row=8, sticky="w")
        self.infeedAngle_label = ttk.Label(frame1)
        self.infeedAngle_label.configure(text='Infeed Angle')
        self.infeedAngle_label.grid(column=0, row=9, sticky="w")
        self.threadDepth_label = ttk.Label(frame1)
        self.threadDepth_label.configure(text='Thread Depth')
        self.threadDepth_label.grid(column=0, row=10, sticky="w")
        self.tool_label = ttk.Label(frame1)
        self.tool_label.configure(text='Tool#')
        self.tool_label.grid(column=0, row=11, sticky="w")
        self.workOffset_label = ttk.Label(frame1)
        self.workOffset_label.configure(text='Work Offset')
        self.workOffset_label.grid(column=0, row=12, sticky="w")
        self.threadClass_label = ttk.Label(frame1)
        self.threadClass_label.configure(text='Thread Class')
        self.threadClass_label.grid(column=0, row=3, sticky="w")
        self.spindleSpeed_label = ttk.Label(frame1)
        self.spindleSpeed_label.configure(text='Cutting Speed')
        self.spindleSpeed_label.grid(column=0, row=13, sticky="w")
        self.flank = tk.StringVar(value='No')
        __values = ['No', 'Yes']
        self.op_flank = ttk.OptionMenu(
            frame1, self.flank, "No", *__values, command=self.on_flank)
        self.op_flank.grid(column=1, row=2, sticky="w")
        self.threadClass = tk.StringVar(value='External')
        __values = ['External', 'Internal']
        self.opt_threadClass = ttk.OptionMenu(
            frame1,
            self.threadClass,
            "External",
            *__values,
            command=self.on_threadClass)
        self.opt_threadClass.grid(column=1, row=3, sticky="w")
        self.ent_majorDia = ttk.Entry(frame1)
        self.majorDia = tk.DoubleVar(value=0)
        self.ent_majorDia.configure(textvariable=self.majorDia)
        _text_ = '0'
        self.ent_majorDia.delete("0", "end")
        self.ent_majorDia.insert("0", _text_)
        self.ent_majorDia.grid(column=1, row=4)
        self.ent_feed = ttk.Entry(frame1)
        self.feed = tk.DoubleVar(value=0)
        self.ent_feed.configure(textvariable=self.feed)
        _text_ = '0'
        self.ent_feed.delete("0", "end")
        self.ent_feed.insert("0", _text_)
        self.ent_feed.grid(column=1, row=5, sticky="w")
        self.ent_zFinal = ttk.Entry(frame1)
        self.zFinal = tk.DoubleVar(value=0)
        self.ent_zFinal.configure(textvariable=self.zFinal)
        _text_ = '0'
        self.ent_zFinal.delete("0", "end")
        self.ent_zFinal.insert("0", _text_)
        self.ent_zFinal.grid(column=1, row=7, sticky="w")
        self.ent_numPass = ttk.Entry(frame1)
        self.numPass = tk.IntVar(value=1)
        self.ent_numPass.configure(textvariable=self.numPass)
        _text_ = '1'
        self.ent_numPass.delete("0", "end")
        self.ent_numPass.insert("0", _text_)
        self.ent_numPass.grid(column=1, row=8, sticky="w")
        self.ent_infeedAngle = ttk.Entry(frame1)
        self.infeedAngle = tk.DoubleVar(value=0)
        self.ent_infeedAngle.configure(textvariable=self.infeedAngle)
        _text_ = '0'
        self.ent_infeedAngle.delete("0", "end")
        self.ent_infeedAngle.insert("0", _text_)
        self.ent_infeedAngle.grid(column=1, row=9, sticky="w")
        self.threadDepth_lab = ttk.Entry(frame1)
        self.threadDepth = tk.DoubleVar(value=0)
        self.threadDepth_lab.configure(textvariable=self.threadDepth)
        _text_ = '0'
        self.threadDepth_lab.delete("0", "end")
        self.threadDepth_lab.insert("0", _text_)
        self.threadDepth_lab.grid(column=1, row=10, sticky="w")
        self.ent_tool = ttk.Entry(frame1)
        self.tool = tk.StringVar(value='0000')
        self.ent_tool.configure(textvariable=self.tool)
        _text_ = '0000'
        self.ent_tool.delete("0", "end")
        self.ent_tool.insert("0", _text_)
        self.ent_tool.grid(column=1, row=11, sticky="w")
        entry10 = ttk.Entry(frame1)
        entry10.grid(column=1, row=12, sticky="w")
        self.ent_workOffset = ttk.Entry(frame1)
        self.workOffset = tk.IntVar(value=54)
        self.ent_workOffset.configure(textvariable=self.workOffset)
        _text_ = '54'
        self.ent_workOffset.delete("0", "end")
        self.ent_workOffset.insert("0", _text_)
        self.ent_workOffset.grid(column=1, row=12, sticky="w")
        self.ent_threadCenter = ttk.Entry(frame1)
        self.threadCenter = tk.DoubleVar(value=0)
        self.ent_threadCenter.configure(textvariable=self.threadCenter)
        _text_ = '0'
        self.ent_threadCenter.delete("0", "end")
        self.ent_threadCenter.insert("0", _text_)
        self.ent_threadCenter.grid(column=1, row=6, sticky="w")
        self.ent_spindleSpeed = ttk.Entry(frame1)
        self.spindleSpeed = tk.IntVar(value=100)
        self.ent_spindleSpeed.configure(textvariable=self.spindleSpeed)
        _text_ = '100'
        self.ent_spindleSpeed.delete("0", "end")
        self.ent_spindleSpeed.insert("0", _text_)
        self.ent_spindleSpeed.grid(column=1, row=13, sticky="w")
        frame1.pack(side="top")
        self.buttons = ttk.Frame(toplevel1)
        self.buttons.configure(height=200, width=200)
        self.generate_button = ttk.Button(self.buttons)
        self.generate_button.configure(text='Generate')
        self.generate_button.pack(side="top")
        self.generate_button.configure(command=self.on_gererate_button_clicked)
        self.buttons.pack(side="top")

        # Main widget
        self.mainwindow = toplevel1

    def run(self):
        self.mainwindow.mainloop()

    def on_units(self, option):
        pass

    def on_flank(self, option):
        pass

    def on_threadClass(self, option):
        pass

    def on_gererate_button_clicked(self):
        generate_code()


if __name__ == "__main__":
    app = TkthreadApp()
    app.run()

