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

test = fetchCompanies()
for item in test:
    print(item)

def addUnits(Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType):

    cursor.execute(f"INSERT INTO dbo.Units (Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType) VALUES ({str(Name)}, {str(IP)}, {int(victronID)}, {str(Location)}, {int(NoCCTV)}, {str(Company)}, {float(Lat)}, {float(Lon)}, {str(UnitType)})")

def addUsers(Username, Password, Rights):

    cursor.execute(f"INSERT INTO dbo.Users (Username, Password, Rights) VALUES ({str(Username)}, {str(Password)}, {str(Rights)})")

cnxn.commit()