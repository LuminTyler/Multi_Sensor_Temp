import sys , os , time , datetime , signal, atexit
from threading import Thread , Timer

from IsFileCheck import *
from CheckIPVaild import *
import TCP_Connect as tcp

import Multi_Sensor_Temp_GUI as GUI_MODE

g_tcp_file_list = []

# TODO: Add comments...

def attempt_connect(IP):
        connected = 0
        print("Attempting to connect to {}".format(IP) )

        new_link = start_connect(IP)

        time.sleep(1)

        connected = new_link.check_connection()

        new_link.join()

        if connected:
            print("Was able to connect to {}".format(IP))

            command = "board printsensordata 2"
            new_link.send_command("")
            new_link.send_command(command)
        else:
            pass

        if connected:
            return True , new_link
        else: 
            return False , None

def start_connect(IP):
    t = tcp.TCP_Connect(IP)
    t.start()
    return t

def start_save(link_dict):
    # IP : {LINK}
    if not(any(link_dict)):
        print("No active links found: nothing to save")
        return None
    else:
        cur_time = datetime.datetime.today().strftime("%m_%d_%Y %H_%M_%S")
        os.mkdir(cur_time)
        os.chdir(cur_time)
        file_list = []
        for IP in link_dict:
            print("IP: " + str(IP))
            IP = str(IP).replace("." , "_")
            fn = (IP + ' ' + cur_time)
            f = open(fn + '.csv' , ('w'))
            f.write("Time (s) , Board Temp (C) , Laser Case Temp (C) , FPGA (C)\n")
            print("Saveing {} to {}".format(IP , fn))
            file_list.append(f)
        return file_list

def run_update(tcp_link_list , tcp_file_list, q_mode=False):
    Timer(1 , update_temp, (tcp_link_list , tcp_file_list, q_mode)).start()

def update_temp(tcp_link_list , tcp_file_list, q_mode= False):
    if not q_mode:
        print("Updating temp")
        print("IP:                  "
              "Time (s)             "
              "Board Temp (C)       "
              "Laser Case Temp (C)  "
              "FPGA Temp (C)        ")
    for IP , file in zip(tcp_link_list , tcp_file_list):
        get_read_back(tcp_link_list[IP], file, IP, q_mode)
    run_update(tcp_link_list , tcp_file_list, q_mode)

def get_read_back(link , file, IP, q_mode=False):
    message = link.read_back_quite()

    if len(message):
        time_val , brd_tmp_val , l_temp_val , fpga_temp_val = line_parser(message)

        save_message = (str(time_val)      + " , " + 
                        str(brd_tmp_val)   + " , " + 
                        str(l_temp_val)    + " , " + 
                        str(fpga_temp_val) + "\n"
                        )
        file.write(save_message)

    if not q_mode:
        print(str(IP) + " :         " + save_message.replace("," , "             "))

def line_parser(line):
    line_elements = line.split()
    return line_elements[0] , line_elements[3] , line_elements[4] , line_elements[9]

## Console Mode

def Console_Mode(sys_arg_ip , settings):

    print("Running Console Mode")

    tcp_ip_list = []
    tcp_link_list = {}
    global g_tcp_file_list

    if sys_arg_ip:
        for IP in sys_arg_ip:
            if check_vaild_ip(IP):
                if sys_arg_ip.count(IP) > 1:
                    print("More than one instance of an IP was found: {}".format(IP))
                    break
                else:
                    tcp_ip_list.append(IP)

    print(tcp_ip_list)

    for num in range(0,len(tcp_ip_list)):
        #print(num , tcp_ip_list[num])
        link_ip = tcp_ip_list[num]
        connected , link = attempt_connect(link_ip)

        if connected:
            tcp_link_list[link_ip] = link

    if tcp_link_list:
        print("active systems")
        tcp_file_list = start_save(tcp_link_list)
        g_tcp_file_list = tcp_file_list
        if len(tcp_link_list) == len(tcp_file_list):
            run_update(tcp_link_list , tcp_file_list, settings['-q'])
        else:
            print("Error: mismatch in save file lenght")
    else:
        print("Error: Was not able to connect to any systems")

## GUI_Mode

def GUI_Mode():
    print("Running in GUI Mode")

## Handlers For Console Exit

# At exit not working as intented
# Closing console will still fail to save CSV
@atexit.register
def exit_handler():
    g_file_handler()

def keyboardInterruptHandler(signal, frame):
    print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(signal))
    g_file_handler()
    sys.exit(-1)

signal.signal(signal.SIGINT, keyboardInterruptHandler)

def g_file_handler():
    if g_tcp_file_list:
        print("Closing all open files...")
        for file in g_tcp_file_list:
            file.close()

## Main

def par_sys_argv():
    IP_list = []
    sys_arg_settings = {}
    sys.argv.pop(0)

    if sys.argv:

        # Help mode
        if "-h" in sys.argv:
            print(
                  "Commands:                                                            \n"
                  " -ip  n.n.n.n  n.n.n.n ...                                           \n"
                  "  IP mode will try to connect to up to 4 sensors                     \n"
                  " -q                                                                  \n"
                  "  Runs in quite mode, will not display temp readouts in console      \n"
                  " -gui                                                                \n"
                  "  Runs the GUI for temp readout                                      \n"
                  "  Note: Running -gui will ignore other commands and only run GUI mode\n"
                  )
            sys.exit(1)

        # Console mode, displays console
        if '-gui' in sys.argv:
            #sys.argv.remove('-gui')
            print("Running GUI Mode..")
            sys_arg_settings['-gui'] = True
            return None , sys_arg_settings
        else:
            sys_arg_settings['-gui'] = False

        # Quite mode, will not print out data
        if "-q" in sys.argv:
            #sys.argv.remove("-q")
            print("Quite Mode")
            sys_arg_settings['-q'] = True
        else:
            sys_arg_settings['-q'] = False

        # Reads in IP's
        if "-ip" in sys.argv:
            start_index = sys.argv.index("-ip")
            if len(sys.argv[start_index:]) > 1:
                for IP in sys.argv[start_index+1:]:
                    if "-" in IP.strip():
                        break
                    else:
                        IP_list.append(IP)
            else:
                print("Error: No IP's were found")
                
    else:
        print("Running GUI mode")
        sys_arg_settings['-gui'] = True
        return None , sys_arg_settings

    return IP_list , sys_arg_settings

if __name__ == "__main__":
    sys_arg_ip , settings = par_sys_argv()

    if settings['-gui'] == True:
        GUI_MODE.Multi_Sensor()
    else:
        Console_Mode(sys_arg_ip , settings)