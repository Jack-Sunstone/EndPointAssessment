import requests

def Relay1():
    result = requests.get("http://81.179.155.109:79/testing/R1.php")
    if (result.status_code == 200): print("Relay set")
def Relay2():
    result = requests.get("http://81.179.155.109:79/testing/R2.php")
    if (result.status_code == 200): print("Relay set")

def Relay3():
    result = requests.get("http://81.179.155.109:79/testing/R3.php")
    if (result.status_code == 200): print("Relay set")

def Relay4():
    result = requests.get("http://81.179.155.109:79/testing/R4.php")
    if (result.status_code == 200): print("Relay set")