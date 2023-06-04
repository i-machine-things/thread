
#!/usr/bin/python3

import numpy as np
import pathlib
import pygubu
import os
PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "tkthread.ui"
directory = "output"
path = os.path.join(PROJECT_PATH, directory)

# #CREATE OUTPUT FOLDER
# try:
#     os.mkdir(path)
# except:
#     pass

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

    # def get_input(prompt, default=None):
    #     user_input = input(prompt).strip()
    #     return user_input if user_input else default

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
        
    # def write_wcs():
    #     get_output(f'G{workOffset}')
        
    def write_units():
        if units == "Inch":
            get_output('G20')
        elif units == "MM":
            get_output('G21')
        
    def program_reset():
        get_output(F'M30\n%')
        
    def program_start():
        get_output(f'%\nO1000 ({filename})')

    def program_note():
        get_output(f'({filename})')

    def home_x():
        get_output(f'G28 U0.0')

    def home_z():
        get_output(f'G28 W0.0')     

    units = app.units.get() #get_input('Inch (I) or MM (M)\nDefault Inch: ', 'i').lower()
    flank = app.flank.get() #get_input('Flanking infeed? Y/N\nDefault No: ', 'n').lower()
    threadClass = app.threadClass.get() #"E"  # internal (I) or external (E) hard-coded default value
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
    # if units.upper() == "I":
    #     uni = ('INCH')
    # else:
    #     uni = ('MM')
    filename = f'{majorDia} X {feed} {units} {infeedAngle*2} DEG THREAD'
    fileType = '.nc'

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(f'{directory}/{filename}{fileType}', 'w') as f:
        
        program_start()
    #    program_note()
        write_units()
        home_x()
        home_z()
        write_tool()
        start_spindle()    
        if threadClass == "External":
            xApproach = majorDia + xClearance # APPROACH DIAMETER
            if numPass == 1:
                doC = threadDepth #SINGLE PASS
            else:
                doC = (threadDepth / (numPass)) # doC FIRST PASS
            diaFirstpass = round(majorDia - (2 * doC), 4) # DIAMETER OF FIRST PASS
            zInitial = round(zInitial - (doC * z_Offset),4)
            get_output(f'G0 G{workOffset} X{xApproach} Z{threadCenter}\nX{diaFirstpass} Z{zInitial}\nG32 Z{zFinal} F{feed}\nG0 X{xApproach}\nZ{threadCenter}')
            i = 2

        if numPass >= 2:
            while i <= numPass:
                if flank == "Yes": #LH
                    if i <= numPass:
                        apx = (threadDepth / numPass) * (i)
                        xpF = round(majorDia - (2 * apx), 4)
                        zShift = (apx) * z_Offset # SHIFT ON Z
                        zF = round(zInitialFlank + zShift, 4) # Z SHIFTED FROM INITIAL Z
                        i += 1
                        get_output(f'GO X{xpF} Z{zF}\nG32 z{zFinal} F{feed}\nG0 X{xApproach}\nZ{threadCenter}')
                if i <= numPass:    
                    apx = (threadDepth / numPass) * (i)
                    xp = round(majorDia - (2 * apx), 4)
                    zShift = (apx - doC) * z_Offset # SHIFT ON Z
                    z = round(zInitial - zShift, 4) # Z SHIFTED FROM INITIAL Z
                    i += 1
                    get_output(f'G0 X{xp} Z{z}\nG32 Z{zFinal} F{feed}\nG0 X{xApproach}\nZ{threadCenter}')

                
        #EVERYTHING BELOW IS FOR ID THREADING, WILL GET TO THAT LATER
            
        #else:
        #   dh = majorDia-feed # HOLE DIAMETER
        #   xApproach = dh - xClearance # APPROACH DIAMETER
        #   xClearance = 0.54127 * feed # THREAD DEPTH
        #   doC = (xClearance / (numPass - 1) ) * (0.3 ** 0.5) # doC FIRST PASS
        #   diaFirstpass = round(dh + 2 * doC, 4) # DIAMETER OF FIRST PASS
        #   print('G0 X' + str(xApproach), 'Z' + str(zInitial))
        #   print('X' + str(diaFirstpass))
        #   print('G32 Z' + str(zFinal), 'F' + str(feed))
        #   print('G0 X' + str(xApproach))
        #   print('Z' + str(zInitial))
        #   i = 2
        #while i <= numPass:
        #    apx = (xClearance / (numPass - 1)) * ((i - 1))
        #    xp = round(dh + (2 * apx), 4)
        #     if zInitial > zFinal:
        #               zShift = (apx - doC) * z_Offset # NEGATIVE SHIFT ON Z
        #           else:
        #               zShift = (apx + doC) * z_Offset # POSITIVE SHIFT ON Z
        #    z = round(zInitial + zShift, 4) # Z SHIFTED FROM INITIAL Z
        #    i = i + 1
        #    print('G0 X' + str(xp), 'Z' + str(z))
        #    print('G32 Z' + str(zFinal), 'F' + str(feed))
        #    print('G0 X' + str(xApproach))
        #    print('Z' + str(zInitial))
        home_x()
        home_z()
        stop_spindle()
        program_reset()


class TkthreadApp:
    def __init__(self, master=None):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow = builder.get_object("toplevel1", master)

        self.units = None
        self.flank = None
        self.threadClass = None
        self.majorDia = None
        self.feed = None
        self.zFinal = None
        self.numPass = None
        self.infeedAngle = None
        self.threadDepth = None
        self.tool = None
        self.workOffset = None
        self.threadCenter = None
        self.spindleSpeed = None
        builder.import_variables(self,
                                 ['units',
                                  'flank',
                                  'threadClass',
                                  'majorDia',
                                  'feed',
                                  'zFinal',
                                  'numPass',
                                  'infeedAngle',
                                  'threadDepth',
                                  'tool',
                                  'workOffset',
                                  'threadCenter',
                                  'spindleSpeed'])

        builder.connect_callbacks(self)

    def run(self):
        self.mainwindow.mainloop()

    def on_units(self, option):
        units = option

    def on_flank(self, option):
        flank = option

    def on_threadClass(self, option):
        threadClass = option

    def on_gererate_button_clicked(self):
        generate_code()


if __name__ == "__main__":
    app = TkthreadApp()
    app.run()