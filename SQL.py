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
def addUnits(Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType):

    if victronID == "":
        cursor.execute(f"INSERT INTO dbo.Units (Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType) VALUES ('{str(Name)}', '{str(IP)}', NULL, '{str(Location)}', {int(NoCCTV)}, '{str(Company)}', {float(Lat)}, {float(Lon)}, '{str(UnitType)}')")
    else:
        cursor.execute(f"INSERT INTO dbo.Units (Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType) VALUES ('{str(Name)}', '{str(IP)}', {int(victronID)}, '{str(Location)}', {int(NoCCTV)}, '{str(Company)}', {float(Lat)}, {float(Lon)}, '{str(UnitType)}')")
    cnxn.commit()

def deleteUnits(Name):

    cursor.execute(f"DELETE FROM dbo.Units WHERE Name = {str(Name)}")

    cnxn.commit()

def addUsers(Username, Password, Company):

    cursor.execute(f"INSERT INTO dbo.Users (Username, Password, Company, Rights) VALUES ('{str(Username)}', '{str(Password)}', '{str(Company)}', 'USER')")

    cnxn.commit()

def deleteUsers(Username):

    cursor.execute(f"DELETE FROM dbo.Users WHERE Username = {str(Username)}")

    cnxn.commit()
