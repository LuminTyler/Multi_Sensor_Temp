def check_vaild_ip(ip):
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
