import requests
import json
import pyodbc
import time

cnxn = ""

victronIDS = []

# Defining login details to access Sites
login_url = 'https://vrmapi.victronenergy.com/v2/auth/login'
login_string = '{"username":"support@sunstone-systems.com","password":"12Security34!"}'
# Stores and loads Json request to the login URL
response = requests.post(login_url, login_string)
token = json.loads(response.text).get("token")
headers = {"X-Authorization": 'Bearer ' + token}

def connection():
    global cnxn
    cnxn = pyodbc.connect(driver="{ODBC Driver 17 for SQL Server}",
                          server="81.179.155.109,1433",
                          database="ARCDashboard",
                          uid="Victron",pwd="12Victron34")

def pushVictronData(Solar, Volatage, Load, victronID):

    connection()

    cursor = cnxn.cursor()
    cursor.execute(f"UPDATE dbo.VictronData SET Solar = {Solar}, Voltage = {Volatage}, UnitLoad = {Load} WHERE victronID = {victronID}")

    cnxn.commit()
def getVictronData():

    global unitSolar
    global unitVoltage
    global unitLoad
    global formattedLoad
    global formattedSolar
    global response
    global headers

    for i in victronIDS:

        diags_url = "https://vrmapi.victronenergy.com/v2/installations/{}/diagnostics?count=1000".format(
            i)
        response = requests.get(diags_url, headers=headers)
        data = response.json().get("records")

        unitSolar = str([element['rawValue'] for element in data if element['code'] == "PVP"][0])

        unitVoltage = str([element['rawValue'] for element in data if element['code'] == "bv"][0])

        unitLoad = str([element['rawValue'] for element in data if element['code'] == "dc"][0])

        pushVictronData(unitSolar, unitVoltage, unitLoad, i)

def getIDS():

    connection()

    cursor = cnxn.cursor()
    cursor.execute(f"SELECT victronID FROM dbo.VictronData")

    for row in cursor.fetchall():
        victronIDS.append(row[0])

    getVictronData()

while True:
    getIDS()
    print("Data Updated Successfully")
    time.sleep(45)

