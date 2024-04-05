import socket
import SQL
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

#print(checkURL('000.000.000.000',0000,1))

names = []

lat = []

lon = []

data = SQL.fetchLocations()

for row in data:
    altered = list(row)
    names.append(altered[0])
    lat.append(altered[1])
    lon.append(altered[2])

print(names)
print(lat)
print(lon)
