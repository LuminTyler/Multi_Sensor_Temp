import sys , os , time , datetime , signal, atexit
from threading import Thread , Timer

from IsFileCheck import *
from CheckIPVaild import *
import TCP_Connect as tcp

g_tcp_file_list = []

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
            print("Was not able to connect")

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

def run_update(tcp_link_list , tcp_file_list):
    Timer(1 , update_temp, (tcp_link_list , tcp_file_list)).start()

def update_temp(tcp_link_list , tcp_file_list):
    print("Updating temp")
    print("IP:                  "
          "Time (s)             "
          "Board Temp (C)       "
          "Laser Case Temp (C)  "
          "FPGA Temp (C)        ")
    for IP , file in zip(tcp_link_list , tcp_file_list):
        #print(tcp_link_list[IP] , file)
        get_read_back(tcp_link_list[IP], file, IP)
    run_update(tcp_link_list , tcp_file_list)

def get_read_back(link , file, IP):
    message = link.read_back_quite()
            
    #print("Link: {} File: {}".format(link, file))

    if len(message):
        time_val , brd_tmp_val , l_temp_val , fpga_temp_val = line_parser(message)

        save_message = (str(time_val)      + " , " + 
                        str(brd_tmp_val)   + " , " + 
                        str(l_temp_val)    + " , " + 
                        str(fpga_temp_val) + "\n"
                        )
        file.write(save_message)

    #print("Link: {}".format(link))
    print(str(IP) + " :         " + save_message.replace("," , "             "))

def line_parser(line):
    line_elements = line.split()
    return line_elements[0] , line_elements[3] , line_elements[4] , line_elements[9]

def main():
    tcp_ip_list = []
    tcp_link_list = {}
    global g_tcp_file_list

    if 1 < len(sys.argv) < 6:
        for num , ip in enumerate(sys.argv[1:]):
            if check_vaild_ip(ip):
                if ip in sys.argv[num+2:]:
                    print("Dup IP found " + str(ip))
                    break
                else:
                    tcp_ip_list.append(ip)
                    print("Num {} IP {}".format(num , ip))
    else:
        print("Arg Error")

    for num in range(0,len(tcp_ip_list)):
        #print(num , tcp_ip_list[num])
        link_ip = tcp_ip_list[num]
        connected , link = attempt_connect(link_ip)
        print(connected , link)

        if connected:
            tcp_link_list[link_ip] = link

    #tcp_link_list["10.42.0.10"] = "Link"
    #tcp_link_list["10.42.0.12"] = "Link"
    #tcp_link_list["10.42.0.14"] = "Link"

    if tcp_link_list:
        print("active systems")
        tcp_file_list = start_save(tcp_link_list)
        #print(tcp_file_list , g_tcp_file_list)
        g_tcp_file_list = tcp_file_list
        #print(tcp_file_list , g_tcp_file_list)
        if len(tcp_link_list) == len(tcp_file_list):
            run_update(tcp_link_list , tcp_file_list)
        else:
            print("Error: mismatch in save file lenght")
    else:
        print("Error: Was not able to connect to any systems")

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

if __name__ == "__main__":
    main()