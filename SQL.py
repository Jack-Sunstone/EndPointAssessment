import pyodbc
cnxn = ""
def connection():
    global cnxn
    cnxn = pyodbc.connect(driver="{ODBC Driver 17 for SQL Server}",
                server="81.179.155.109,1433",
                database="ARCDashboard",
                uid="Monitoring",pwd='12Sunstone34')


#cursor.execute("INSERT INTO dbo.Units (Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType) VALUES (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL")

def fetchUnitsSunstone():
    connection()
    cursor = cnxn.cursor()
    cursor.execute("SELECT Name FROM dbo.Units ORDER BY Name")

    for row in cursor.fetchall():
        yield row[0]

def fetchUnits(Company):
    connection()
    cursor = cnxn.cursor()
    cursor.execute(f"SELECT Name FROM dbo.Units WHERE Company = '{Company}' ORDER BY Name")

    for row in cursor.fetchall():
        yield row[0]

def fetchGeneratorSunstone():
    connection()
    cursor = cnxn.cursor()
    cursor.execute("SELECT Name FROM dbo.Generators ORDER BY Name")

    for row in cursor.fetchall():
        yield row[0]

def fetchGenerators(Company):
    connection()
    cursor = cnxn.cursor()
    cursor.execute(f"SELECT Name FROM dbo.Generators WHERE Company = '{Company}' ORDER BY Name")

    for row in cursor.fetchall():
        yield row[0]

def fetchUnitDetails(unitName):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT IP, victronID, Location, Company, NoCCTV, CameraType, efoyID, Lat, Lon FROM dbo.Units WHERE Name = '{unitName}'")

    for row in cursor.fetchall():
        yield row

def fetchGenDetails(genName):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT victronID, Location, Company, efoy1ID, efoy2ID, Lat, Lon FROM dbo.Units WHERE Name = '{genName}'")

    for row in cursor.fetchall():
        yield row

def fetchLocationsSunstone():
    connection()
    cursor = cnxn.cursor()

    cursor.execute("SELECT Name, Lat, Lon FROM dbo.Units")

    for row in cursor.fetchall():
        yield row

def fetchLocations(Company):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT Name, Lat, Lon FROM dbo.Units WHERE Company = '{Company}'")

    for row in cursor.fetchall():
        yield row


def updateUnit(unitName, Location, Company, CCTV):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"UPDATE dbo.Units SET Location = '{Location}', Company = '{Company}', NoCCTV = {CCTV} WHERE Name = '{unitName}'")

    cnxn.commit()

def updateUnitSuper(unitName, Location, Company, CCTV, Type, IP, Victron, Efoy, Lat, Lon):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"UPDATE dbo.Units SET Location = '{Location.strip()}', Company = '{Company.strip()}', NoCCTV = {CCTV.strip()}, CameraType = '{Type.strip()}', IP = '{IP.strip()}', victronID = {Victron.strip()}, efoyID = '{Efoy.strip()}', Lat = {Lat.strip()}, Lon = {Lon.strip()} WHERE Name = '{unitName}'")
    cursor.execute(f"UPDATE dbo.VictronData SET victronID = {Victron.strip()}', Company = '{Company.strip()}' WHERE Name = '{unitName}'")

    cnxn.commit()
def fetchCompanies():
    connection()
    cursor = cnxn.cursor()

    cursor.execute("SELECT Company FROM dbo.Units")

    for row in cursor.fetchall():
        yield row[0]

    cnxn.commit()

def fetchSitesSunstone():
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT Location FROM dbo.Units ORDER BY Name")

    for row in cursor.fetchall():
        yield row[0]

    cnxn.commit()

def fetchSites(Company):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT Location FROM dbo.Units WHERE Company = '{Company}' ORDER BY Name")

    for row in cursor.fetchall():
        yield row[0]

    cnxn.commit()

def fetchUnitType(unitName):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT UnitType FROM dbo.Units WHERE Name = '{unitName}'")

    for row in cursor.fetchall():
        return row[0]

    cnxn.commit()

def fetchUsers():
    connection()
    cursor = cnxn.cursor()

    cursor.execute("SELECT Username FROM dbo.Users WHERE Rights = 'USER' OR Rights = 'ADMIN'")

    for row in cursor.fetchall():
        yield row[0]

    cnxn.commit()

def fetchPassword(Username):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT Password FROM dbo.Users WHERE Username = '{Username}'")

    for row in cursor.fetchall():
        return row[0]


def fetchRights(Username):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT Rights FROM dbo.Users WHERE Username = '{Username}'")

    for row in cursor.fetchall():
        return row[0]

def fetchCompany(Username):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT Company FROM dbo.Users WHERE Username = '{Username}'")

    for row in cursor.fetchall():
        return row[0]

def checkUsername(Username):

    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT Username FROM dbo.Users WHERE Username = '{Username}'")

    for row in cursor.fetchall():
        return row[0]

def checkUnit(Name):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT Name FROM dbo.Units WHERE Name = '{Name}'")

    for row in cursor.fetchall():
        return row[0]

def checkGen(Name):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT Name FROM dbo.Generators WHERE Name = '{Name}'")

    for row in cursor.fetchall():
        return row[0]

def addUnits(Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType, CameraType, EfoyID):
    connection()
    cursor = cnxn.cursor()

    if victronID == "":
        cursor.execute(f"INSERT INTO dbo.Units (Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType, CameraType, efoyID) VALUES ('{Name.strip()}', '{IP.strip()}', NULL, '{Location.strip()}', {NoCCTV.strip()}, '{Company.strip()}', {Lat.strip()}, {Lon.strip()}, '{UnitType.strip()}', '{CameraType.strip()}', NULL)")
    else:
        cursor.execute(f"INSERT INTO dbo.Units (Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType, CameraType, efoyID) VALUES ('{Name.strip()}', '{IP.strip()}', {victronID.strip()}, '{Location.strip()}', {NoCCTV.strip()}, '{Company.strip()}', {Lat.strip()}, {Lon.strip()}, '{UnitType.strip()}', '{CameraType.strip()}', '{EfoyID.strip()}')")

        cursor.execute(f"INSERT INTO dbo.VictronData (Name, Solar, Voltage, Load, victronID, Company) VALUES ('{Name.strip()}', NULL, NULL, NULL, {victronID.strip()}, '{Company.strip()}')")
    cnxn.commit()

def addGenerator(Name, victronID, Location, Company, Lat, Lon, efoy1ID, efoy2ID):

    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"INSERT INTO dbo.Generators (Name, victronID, Location, Company, Lat, Lon, efoy1ID, efoy2ID) VALUES ('{Name.strip()}', '{victronID.strip()}', '{Location.strip()}', '{Company.strip()}', {Lat.strip()}, {Lon.strip()}, '{efoy1ID.strip()}', '{efoy2ID.strip()}')")
    cursor.execute(f"INSERT INTO dbo.VictronData (Name, Solar, Voltage, Load, victronID, Company) VALUES ('{Name.strip()}', NULL, NULL, NULL, {victronID.strip()}, '{Company.strip()}')")

    cnxn.commit()

def deleteUnits(Name):
    connection()
    cursor = cnxn.cursor()
    cursor.execute(f"DELETE FROM dbo.Units WHERE Name = '{Name}'")
    cursor.execute(f"DELETE FROM dbo.VictronData WHERE Name = '{Name}'")

    cnxn.commit()

def addUsers(Username, Password, Company, Rights):
    connection()
    cursor = cnxn.cursor()
    cursor.execute(f"INSERT INTO dbo.Users (Username, Password, Company, Rights) VALUES ('{Username.strip()}', '{Password.strip()}', '{Company.strip()}', '{(Rights.strip()).upper()}')")

    cnxn.commit()

def updateUser(Username, Password, Rights):
    connection()
    cursor = cnxn.cursor()
    cursor.execute(f"UPDATE dbo.Users SET Password = '{Password}', Rights = '{Rights}' WHERE Username = '{Username}'")

def deleteUsers(Username):
    connection()
    cursor = cnxn.cursor()
    cursor.execute(f"DELETE FROM dbo.Users WHERE Username = '{Username}'")

    cnxn.commit()


def fetchVictronData(unitName):

    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SElECT Solar, Voltage, Load FROM dbo.VictronData WHERE Name = '{unitName}'")

    for row in cursor.fetchall():
        yield row

def fetchVictronAllDataSunstone():

    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT Name, Voltage, Solar, Load FROM dbo.VictronData ORDER BY Name")

    for row in cursor.fetchall():
        yield row

def fetchVictronAllData(Company):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT Name, Voltage, Solar, Load FROM dbo.VictronData WHERE Company = '{Company}' ORDER BY Name")

    for row in cursor.fetchall():
        yield row


def fetchFilteredVictronSunstone(Filter):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(
        f"SELECT Name, Voltage, Solar, Load FROM dbo.VictronData ORDER By {Filter} DESC")

    for row in cursor.fetchall():
        yield row

def fetchFilteredVictron(Company, Filter):

    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT Name, Voltage, Solar, Load FROM dbo.VictronData WHERE Company = '{Company}' ORDER By {Filter} DESC")

    for row in cursor.fetchall():
        yield row