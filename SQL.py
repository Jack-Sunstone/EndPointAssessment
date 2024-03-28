import pyodbc

cnxn = pyodbc.connect(driver="{ODBC Driver 17 for SQL Server}",
            server="81.179.155.109,1433",
            database="ARCDashboard",
            uid="Monitoring",pwd='12Sunstone34')

cursor = cnxn.cursor()

#cursor.execute("INSERT INTO dbo.Units (Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType) VALUES (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL")

def fetchUnits():

    cursor.execute("SELECT Name FROM dbo.Units")

    for row in cursor.fetchall():
        yield row[0]

def fetchUnitDetails(unitName):

    cursor.execute(f"SELECT Location, Company, NoCCTV FROM dbo.Units WHERE Name = '{unitName}'")

    for row in cursor.fetchall():
        yield row

def updateunit(unitName, Location, Company, CCTV):

    cursor.execute(f"UPDATE dbo.Units SET Location = '{Location}', Company = '{Company}', NoCCTV = {CCTV} WHERE Name = '{unitName}'")

    cnxn.commit()

def fetchCompanies():

    cursor.execute("SELECT Company FROM dbo.Units")

    for row in cursor.fetchall():
        yield row[0]

    cnxn.commit()

def fetchUsers():

    cursor.execute("SELECT Username FROM dbo.Users")

    for row in cursor.fetchall():
        yield row[0]

    cnxn.commit()

def fetchPassword(Username):

    cursor.execute(f"SELECT Password FROM dbo.Users WHERE Username = '{Username}'")

    for row in cursor.fetchall():
        return row[0]

def checkUsername(Username):
    cursor.execute(f"SELECT Username FROM dbo.Users WHERE Username = '{Username}'")

    for row in cursor.fetchall():
        return row[0]


def addUnits(Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType):

    if victronID == "":
        cursor.execute(f"INSERT INTO dbo.Units (Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType) VALUES ('{Name}', '{IP}', NULL, '{Location}', {NoCCTV}, '{Company}', {Lat}, {Lon}, '{UnitType}')")
    else:
        cursor.execute(f"INSERT INTO dbo.Units (Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType) VALUES ('{Name}', '{IP}', {victronID}, '{Location}', {NoCCTV}, '{Company}', {Lat}, {Lon}, '{UnitType}')")
    cnxn.commit()

def deleteUnits(Name):

    cursor.execute(f"DELETE FROM dbo.Units WHERE Name = '{Name}'")

    cnxn.commit()

def addUsers(Username, Password, Company):

    cursor.execute(f"INSERT INTO dbo.Users (Username, Password, Company, Rights) VALUES ('{Username}', '{Password}', '{Company}', 'USER')")

    cnxn.commit()

def updateUser(Password, Username):

    cursor.execute(f"UPDATE dbo.Users SET Password = '{Password}' WHERE Username = '{Username}' ")

    cnxn.commit()

def deleteUsers(Username):

    cursor.execute(f"DELETE FROM dbo.Users WHERE Username = '{Username}'")

    cnxn.commit()
