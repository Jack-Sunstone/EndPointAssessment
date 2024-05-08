import socket
import SQL
import what3words


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



print(checkURL('000.000.000.000',0000,1))

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

def checkConnected():
    socketOpen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketOpen.settimeout(2)
    try:
        socketOpen.connect(("google.com", 80))
    except:
        return 0
    else:
        socketOpen.close()
        return 1
print(checkConnected())

geocoder = what3words.Geocoder("RMNUBSDA")

result = geocoder.convert_to_coordinates("fight.power.spoken")

print(result['coordinates']['lat'])
print(result['coordinates']['lng'])