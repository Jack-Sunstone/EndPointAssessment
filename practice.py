import socket
def checkURL(IPAddress, Port, Timeout):
    socketOpen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketOpen.settimeout(Timeout)
    try:
        socketOpen.connect((IPAddress, Port))
    except:
        return 0
    else:
        socketOpen.close()
        return 1

print(checkURL('000.000.000.000',0000,timeout=1))
