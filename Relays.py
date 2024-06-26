import requests

def Relay1(unitName):
    result = requests.get(f"http://81.179.155.109:78/{unitName}/R1.php")

def Relay2(unitName):
    result = requests.get(f"http://81.179.155.109:78/{unitName}/R2.php")


def Relay3(unitName):
    result = requests.get(f"http://81.179.155.109:78/{unitName}/R3.php")


def Relay4(unitName):
    result = requests.get(f"http://81.179.155.109:78/{unitName}/R4.php")
