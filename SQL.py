import pyodbc
cnxn = ""
def connection():
    global cnxn
    cnxn = pyodbc.connect(driver="{ODBC Driver 17 for SQL Server}",
                server="81.179.155.109,1433",
                database="ARCDashboard",
                uid="Monitoring",pwd='12Sunstone34')


#cursor.execute("INSERT INTO dbo.Units (Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType) VALUES (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL")

def fetchUnits():
    connection()
    cursor = cnxn.cursor()
    cursor.execute("SELECT Name FROM dbo.Units ORDER BY Name")

    for row in cursor.fetchall():
        yield row[0]

def fetchUnitDetails(unitName):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT IP, victronID, Location, Company, NoCCTV, CameraType, efoyID FROM dbo.Units WHERE Name = '{unitName}'")

    for row in cursor.fetchall():
        yield row

def fetchLocations():
    connection()
    cursor = cnxn.cursor()

    cursor.execute("SELECT Name, Lat, Lon FROM dbo.Units")

    for row in cursor.fetchall():
        yield row

def updateunit(unitName, Location, Company, CCTV):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"UPDATE dbo.Units SET Location = '{Location}', Company = '{Company}', NoCCTV = {CCTV} WHERE Name = '{unitName}'")

    cnxn.commit()

def fetchCompanies():
    connection()
    cursor = cnxn.cursor()

    cursor.execute("SELECT Company FROM dbo.Units")

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

    cursor.execute("SELECT Username FROM dbo.Users")

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

def checkUsername(Username):

    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT Username FROM dbo.Users WHERE Username = '{Username}'")

    for row in cursor.fetchall():
        return row[0]

def checkUnit(Name):
    connection()
    cursor = cnxn.cursor()

    cursor.execute(f"SELECT Username FROM dbo.Units WHERE Name = '{Name}'")

    for row in cursor.fetchall():
        return row[0]

def addUnits(Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType, CameraType, EfoyID):
    connection()
    cursor = cnxn.cursor()

    if victronID == "":
        cursor.execute(f"INSERT INTO dbo.Units (Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType, CameraType, efoyID) VALUES ('{Name}', '{IP}', NULL, '{Location}', {NoCCTV}, '{Company}', {Lat}, {Lon}, '{UnitType}', '{CameraType}', NULL)")
    else:
        cursor.execute(f"INSERT INTO dbo.Units (Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType, CameraType, efoyID) VALUES ('{Name}', '{IP}', {victronID}, '{Location}', {NoCCTV}, '{Company}', {Lat}, {Lon}, '{UnitType}', '{CameraType}', '{EfoyID}')")
    cnxn.commit()

def deleteUnits(Name):
    connection()
    cursor = cnxn.cursor()
    cursor.execute(f"DELETE FROM dbo.Units WHERE Name = '{Name}'")

    cnxn.commit()

def addUsers(Username, Password, Company):
    connection()
    cursor = cnxn.cursor()
    cursor.execute(f"INSERT INTO dbo.Users (Username, Password, Company, Rights) VALUES ('{Username}', '{Password}', '{Company}', 'USER')")

    cnxn.commit()

def updateUser(Password, Username):
    connection()
    cursor = cnxn.cursor()
    cursor.execute(f"UPDATE dbo.Users SET Password = '{Password}' WHERE Username = '{Username}' ")

    cnxn.commit()

def deleteUsers(Username):
    connection()
    cursor = cnxn.cursor()
    cursor.execute(f"DELETE FROM dbo.Users WHERE Username = '{Username}'")

    cnxn.commit()
