import sys, os , subprocess , time , asyncio , datetime
from threading import Thread
#import qdarkstyle

from IsFileCheck import *
from CheckIPVaild import *
import TCP_Connect as tcp
from PyQt5 import QtCore, QtGui, QtWidgets, uic , QtTest

from random import *

class Multi_Head_Window(QtWidgets.QMainWindow):

    ## Init Functions

    update_signal = QtCore.pyqtSignal()

    @QtCore.pyqtSlot()
    def trigger_update(self):
        self.update_temp()

    def __init__(self):
        super(Multi_Head_Window, self).__init__()
        uic.loadUi('Multi_Temp.ui', self)
        self.setWindowTitle('Luminar Multi-Sensor Temperature Readout')
        self.show()
        self.error_message = ""
        self.sys_ip = 0
        self.keep_alive = 1
        self.trigger_val = 0

        self.sys_active = [0 , 0, 0 , 0 ]
        self.tcp_link_list = [None , None , None , None]
        self.tcp_ip_list = [None , None , None , None]
        self.tcp_file_list = [None , None , None , None]
        self.initUI()

    #@QtCore.pyqtSignal(int)
    #def on_tigger_valueChange(self):
    #    print(self.trigger_update)

    def initUI(self):
        # Connect to system buttons
        self.Connect_1.clicked.connect(lambda : self.attempt_connect(0))
        self.Connect_2.clicked.connect(lambda : self.attempt_connect(1))
        self.Connect_3.clicked.connect(lambda : self.attempt_connect(2))
        self.Connect_4.clicked.connect(lambda : self.attempt_connect(3))

        #self.tirgger_update.valueChange.connect(self.update_val)

        self.start_save_button.clicked.connect(self.start_save)
        self.stop_save_button.clicked.connect(self.stop_save)

        # Get system file path
        self.sreach_file.clicked.connect(self.get_filepath)

        self.update_signal.connect(self.trigger_update)

        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_temp)
        self.update_timer.start(500)

        self.update_temp()

    ## Test Section

    def display_value(self):
        #print("This is a test")
        val = self.tirgger_update
        #print(val)

    def connect_tirgger_update(self):
        pass

    ## Save file Section

    def start_save(self):
        #print(self.sys_active)
        #print(any(self.sys_active))
        if not(any(self.sys_active)):
            self.console_box.append("No active links found: nothing to save")
        else:
            cur_time = datetime.datetime.today().strftime("%m_%d_%Y %H_%M_%S")
            os.mkdir(cur_time)
            os.chdir(cur_time)
            for num , active in enumerate(self.sys_active):
                #print("Active: {}\n {} is {}".format(active, num , bool(self.tcp_file_list[num])))
                if active and not(self.tcp_file_list[num]):
                    #print("{} is {}".format(self.tcp_ip_list[num] , self.tcp_file_list[num]))
                    ip = str(self.tcp_ip_list[num]).replace("." , "_")
                    fn = (ip + ' ' + cur_time)
                    f = open(fn + '.csv' , ('w'))
                    self.tcp_file_list[num] = f
                    self.console_box.append("Saveing {} to {}".format(ip , fn))

    def stop_save(self):
        for active in filter(None, self.tcp_file_list):
            self.console_box.append("Stopping " + str(active))
        self.tcp_file_list = [None , None , None , None]

    ## Connect Section

    def update_temp(self):
        #start = time.time()
        #message = "Null" 
        #for i in range(0,100):
        #while(self.keep_alive):
        #print("Checking to see if its alive")
        #print(bool(any(self.sys_active)))
        #while(any(self.sys_active)):
        #print(self.sys_active) #Check to see which systems are on

        #for link_num , link in enumerate(self.tcp_link_list):
        #    if link:
        #        print("{} link is active".format(link_num))

        ## System 1

        if self.sys_active[0]:
            #start_read = time.time()
            message = self.tcp_link_list[0].read_back_quite()
            #end_read = time.time()
            
            if len(message):
                time_1 , brd_tmp_1 , l_temp_1 , fpga_temp_1 = self.line_parser(message)
            
                self.time_1.setText(time_1)
                self.board_temp_1.setText(brd_tmp_1)
                self.laser_case_temp_1.setText(l_temp_1)
                self.fpga_temp_1.setText(fpga_temp_1)

            #print("Time to read:    {}\n" 
            #      .format(
            #          (end_read - start_read),
            #          )
            #      )

            #self.time_1.setText(str(i))
            #print("Link 1 save active: {}".format(bool(self.tcp_file_list[0])))
            if self.tcp_file_list[0]:
                save_message = (str(time_1)      + " , " + 
                                str(brd_tmp_1)   + " , " + 
                                str(l_temp_1)    + " , " + 
                                str(fpga_temp_1) + "\n"
                                )
                self.tcp_file_list[0].write(save_message)
 
                #save_message = str(i) + " , " + "\n"
                #print("Saving message {} to {}".format(save_message , self.tcp_file_list[0]))
                #self.tcp_file_list[0].write(save_message)

        ## System 2
                
        if self.sys_active[1]:
            message = self.tcp_link_list[1].read_back_quite()
            
            if len(message):
                time_2 , brd_tmp_2 , l_temp_2 , fpga_temp_2 = self.line_parser(message)
                self.time_2.setText(time_2)
                self.board_temp_2.setText(brd_tmp_2)
                self.laser_case_temp_2.setText(l_temp_2)
                self.fpga_temp_2.setText(fpga_temp_2)

            if self.tcp_file_list[1]:
                save_message = (str(time_2)      + " , " + 
                                str(brd_tmp_2)   + " , " + 
                                str(l_temp_2)    + " , " + 
                                str(fpga_temp_2) + "\n"
                                )
                self.tcp_file_list[1].write(save_message)

        ## System 3

        if self.sys_active[2]:
            message = self.tcp_link_list[2].read_back_quite()

            if len(message):
                time_3 , brd_tmp_3 , l_temp_3 , fpga_temp_3 = self.line_parser(message)
                self.time_3.setText(time_3)
                self.board_temp_3.setText(brd_tmp_3)
                self.laser_case_temp_3.setText(l_temp_3)
                self.fpga_temp_3.setText(fpga_temp_3)

            if self.tcp_file_list[2]:
                save_message = (str(time_3)      + " , " + 
                                str(brd_tmp_3)   + " , " + 
                                str(l_temp_3)    + " , " + 
                                str(fpga_temp_3) + "\n"
                                )
                self.tcp_file_list[2].write(save_message)

        ## System 4

        if self.sys_active[3]:
            message = self.tcp_link_list[3].read_back_quite()

            if len(message):
                time_4 , brd_tmp_4 , l_temp_4 , fpga_temp_4 = self.line_parser(message)
                self.time_4.setText(time_4)
                self.board_temp_4.setText(brd_tmp_4)
                self.laser_case_temp_4.setText(l_temp_4)
                self.fpga_temp_4.setText(fpga_temp_4)

            if self.tcp_file_list[3]:
                save_message = (str(time_4)      + " , " + 
                                str(brd_tmp_4)   + " , " + 
                                str(l_temp_4)    + " , " + 
                                str(fpga_temp_4) + "\n"
                                )
                self.tcp_file_list[3].write(save_message)

        # End Keep Alive While
        #end = time.time()

        #print("Time to run if: {}".format(end-start))

    def get_connect_input(self , num):
        if num == 0:
            sys_ip = self.system_ip_box_1.text()
        if num == 1:
            sys_ip = self.system_ip_box_2.text()
        if num == 2:
            sys_ip = self.system_ip_box_3.text()
        if num == 3:
            sys_ip = self.system_ip_box_4.text()

        if check_vaild_ip(sys_ip):
            self.sys_ip = sys_ip
            return True
        else:
            self.console_box.append("Not a vaild IP address")
            return False
    
    def attempt_connect(self, num):
        connected = 0
        if self.sys_active[num]:
            self.console_box.append("Link already active...")
        else:
            if self.get_connect_input(num):
                #self.console_box.append("Attempting to connect to {}".format(num , self.sys_ip) )
                self.console_box.append("Using Button {}\nAttempting to connect to {}".format(num , self.sys_ip) )

                #new_t = self.start_connect(self.sys_ip)
                new_link = self.start_connect(self.sys_ip)
                #self.start_connect()
                #new_t.join()

                time.sleep(1)

                connected = new_link.check_connection()

                if connected:
                    self.console_box.append("Was able to connect to {}".format(self.sys_ip))

                    command = "board printsensordata 2"
                    #print("Sending Command: " + command)
                    new_link.send_command("")
                    new_link.send_command(command)
                else:
                    self.console_box.append("Was not able to connect")


                #connected = 1

                #new_link.send_command(command)
                #self.line_parser(new_link.last_responce)

                # start new thread . safe thread
                # test if connection:
                # if bad report back as bad
                # if good add number to list as active
                # also disable button so it can't be spamed as its trying to work
                # got to figure that one out as well, can't be to hard
                # i would think.... 
                if connected:
                    self.tcp_link_list[num] = new_link
                    self.tcp_ip_list[num] = self.sys_ip
                    self.sys_active[num] = 1

        # emits a signal to start the update
        #self.update_signal.emit()

                # TODO:
    # Yet to add, have each button try to connect to the sensor
    # then have that break off into a new thread
    # read from that thread and report out each temp in it's box

    def line_parser(self , line):
        #line = "         473             -49.030              -49.284           38.708                23.450         1826         9200         1831         9196          42.359"
        #print("Line Elements are: ")
        line_elements = line.split()
        #for ele in line_elements:
            #print(ele , end='')
        return line_elements[0] , line_elements[3] , line_elements[4] , line_elements[9]
    #   "Time (s)"  "Left HV Bias (V)"  "Right HV Bias (V)"  "Board tmp (C)"  "Laser Case tmp (C)"  "L NW (mV)"  "L tmp raw"  "R NW (mV)"  "R tmp raw"  "FPGA tmp (C)"
    #       0           1                       2                   3                   4                  5            6           7           8               9

    ## Threading stuff ##

    def start_connect(self, ip):
        t = tcp.TCP_Connect(ip)
        t.start()
        return t

    def start_loop(self , loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def start_connect_old(self):
        new_loop = asyncio.new_event_loop()
        t = Thread(target= self.start_loop , args=(new_loop , ))
        t.start()
        new_loop.call_soon_threadsafe(self.count_down)

    def count_down(self):
        message = ("Count down: ")
        self.console_box.append(message)
        for i in range(0,10):
            self.console_box.moveCursor(QtGui.QTextCursor.End)
            self.console_box.insertPlainText(".")
            #self.console_box.insertPlainText((str(i) + " "))
            #time.sleep(1)
            QtTest.QTest.qWait(1000)

    ## browse files / save data section

    def browse_file(self):
        # Looks for a existing Directory <Duh, read the name>
        #QtWidgets.QFileDialog.FileMode(QFileDialog.Directory)
        #return QtWidgets.QFileDialog.getOpenFileName()[0]
        return QtWidgets.QFileDialog.getExistingDirectory()

    def get_filepath(self):
        # Looks for folder then checks to make sure it's real
        self.filepath = self.browse_file()
        self.filename_box.clear()
        if is_pathname_valid(self.filepath):
            #self.filename = str(self.filepath.split('/')[-1])
            self.filename_box.setText(self.filepath)
        else:
            self.error_message = "Not a Vaild Filepath"
            #print("Not a Vaild Filepath")
            self.console_box.append(self.error_message)



 ## Main Section 

def Multi_Sensor():
    app = QtWidgets.QApplication(sys.argv)
    window = Multi_Head_Window()

    # Set Sytle and Icon
    #app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    #app.setWindowIcon(QtGui.QIcon('Luminar_Icon.JPG'))

    #window = Multi_Head_Window()
    app.exec_()

if __name__ == '__main__':
    Multi_Sensor()
