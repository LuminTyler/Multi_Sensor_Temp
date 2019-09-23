import telnetlib , socket, time
from threading import Thread

class TCP_Connect(Thread):
    """Connects to Model H via TCP connection"""

    #def __init__(self, *args, **kwargs):
    #    self.connected = 2
        
    #    self.get_ip_address()
    #    self.Connect()

    #    if self.connected:
    #        pass

    # Modded Version

    #def __init__(self):
    #    super(TCP_Connect, self).__init__(self)
    #    self.connected = 2
        
    #    #ip = args[0]
    #    ip = "10.42.0.3"
    #    print("IP passed: " + ip)
    #    if self.check_vaild_ip(ip):
    #        self.dest_ip = ip
    #        #self.connect()
    #        if self.connected:
    #            print("Was able to connect")
    #        else:
    #            print("Was not able to connect")
    #    else:
    #        return False

    def __init__(self, ip):
        
        Thread.__init__(self)
        self.dest_ip = ip
        self.connected = 0

    def run(self):
        print("IP passed: " + self.dest_ip)
        if self.check_vaild_ip(self.dest_ip):
            self.connect()
            if self.connected:
                print("Was able to connect")
            else:
                print("Was not able to connect")
        else:
            print("Ip was not vaild")

    def check_connection(self):
        ''' Checks to see if connection is good
        ''' 
        return self.connected

    def check_vaild_ip(self , ip):
        a = ip.split('.')
        if (len(a) != 4):
            return False
        for num in a:
            if not num.isdigit():
                return False
            i = int(num)
            if(i < 0 or i > 255):
                return False
        return True

    def get_ip_address(self):
        self.dest_ip = ""

        while(1):
            # Runs until good IP is given
            self.dest_ip = input("Destination IP address: ")
            if self.check_vaild_ip(self.dest_ip):
                break
            else:
                print("Not a vaild IP address")
                time.sleep(0.1)

        while(not(self.check_vaild_ip(self.dest_ip))):
            # Runs until good IP is given
            self.dest_ip = input("Destination IP address: ")

        print("Looking for IP ", self.dest_ip)

    def connect(self):
        try:
            self.tn = telnetlib.Telnet(self.dest_ip, timeout=10)
            #self.connected = True
        except (EOFError, socket.gaierror, TimeoutError, socket.timeout) as e:
            if(e == TimeoutError or socket.timeout):    
                print("Error could not connect")
            elif(e == EOFError):
                print("End of file error")
            elif(e == socket.gaierror):
                print("Socket error")
            else:
                print("Unexpected error")
            self.connected = 0
        else:
            print("Was able to connect to ", self.dest_ip)
            self.connected = 1

    def send_command(self, command):
        print("Command being sent: " + command)
        self.tn.write(command.encode('ascii') + b'\r\n')
        # Added slight buffer time so system doesn't become inundated with commands
        time.sleep(0.1)

        self.last_responce = self.read_back()

        self.bypass_encryption()

    def read_back(self):
        ''' Reads until you get a blank return
            Returns responce
        '''
        response = ""
        while(1): # Read until you get a blank return
            rd = self.tn.read_until(b"\r\n", timeout=0.5)
            rd_d = rd.decode('ascii')
            if(rd_d == ''): break
            else:
                print(rd_d, end='')
                response = response + rd_d
        return response

    def read_back_empty(self):
        ''' Reads until you get a blank return
            Does not return responce
        '''
        response = ""
        while(1): # Read until you get a blank return
            rd = self.tn.read_until(b"\r\n", timeout=0.5)
            rd_d = rd.decode('ascii')
            if(rd_d == ''): break
            else:
                print(rd_d, end='')

    def read_back_quite(self):
        ''' Reads until you get a blank return
            Returns responce
            No print
        '''
        response = ""
        while(1): # Read until you get a blank return
            rd = self.tn.read_until(b"\r\n", timeout=0.01)
            rd_d = rd.decode('ascii')
            if(rd_d == ''): 
                break
            else:
                response = response + rd_d
        return response

    def bypass_encryption(self):
        
        responce_string = self.last_responce.split()
        for pos , word in enumerate(responce_string):
            #print("Checking: " + word)
            if(word == 'Challenge'):
                print("Challenge was found, FIGHT")
                challange = responce_string[pos+2]

                responce = self.decrypt(challange)

                self.send_command(responce)

                if "SUCCESS" in self.last_responce.split():
                    print("Bypass encryption")
                else:
                    self.bypass_encryption()
                self.send_command("")
        # Send test commnad

        # rather read last line gotten

        # Test to see if last line had the Challange string in it

        # if it did find the challange string

        # decode challnage string

        # send responce to system

        # check to make sure that challange string was able to defeate the encryption

        #
    def decrypt(self , challange):
        decrypt_table = []
        decrypt_dic = {
            "1" : "157FC3CD",
            "2" : "0134B163",
            "3" : "11998E4F",
            "4" : "00804EBD",
            "5" : "1590D80E",
            "6" : "17A9786D",
            "7" : "0E833F5C",
            "8" : "1469A357",
            "9" : "04698844",
            "0" : "0EC8636F",
            "q" : "10F93824",
            "w" : "117AF4FF",
            "e" : "180C480E",
            "r" : "0234AD15",
            "t" : "029104F8",
            "y" : "04C2E5BB",
            "u" : "1141350D",
            "i" : "11727FF9",
            "o" : "113BC818",
            "p" : "0937CEB0",
            "a" : "068AB594",
            "s" : "0EE4170E",
            "d" : "143F61AD",
            "f" : "0E9F903B",
            "g" : "0FCAFAC3",
            "h" : "11DDDE9F",
            "j" : "104C14FB",
            "k" : "0000EE83",
            "l" : "056AF033",
            "z" : "0B045F60",
            "x" : "068A5178",
            "c" : "0FAF9CEB",
            "v" : "038B036C",
            "b" : "1556B7C7",
            "n" : "0FEC7A8E",
            "m" : "0D6D34D2",
            "Q" : "15251917",
            "W" : "0BDCD8F0",
            "E" : "0FDE2660",
            "R" : "088A853B",
            "T" : "054FDD9A",
            "Y" : "10484921",
            "U" : "19FFFC40",
            "I" : "11AEE2BC",
            "O" : "182D7F2F",
            "P" : "044618EA",
            "A" : "02D77C1D",
            "S" : "17B85C86",
            "D" : "010C7FE3",
            "F" : "0E47969F",
            "G" : "04FAA912",
            "H" : "0430B36B",
            "J" : "0BD5A6A3",
            "K" : "19B5C039",
            "L" : "11FB1063",
            "Z" : "15EA90A2",
            "X" : "1201FF09",
            "C" : "1001B123",
            "V" : "1756AC31",
            "B" : "0F93292C",
            "N" : "0E635F00",
            "M" : "1A142EA0",
            "-" : "0FF47F0B",
            "=" : "1AD2209B",
            "_" : "09BAC4ED",
            "+" : "1AEB7A7F"
        }
        responce = ''
        for char in list(challange):
            responce += (' ' + decrypt_dic[char])

        return responce



