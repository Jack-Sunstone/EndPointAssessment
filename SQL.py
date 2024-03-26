import pyodbc

cnxn = pyodbc.connect(driver="{ODBC Driver 17 for SQL Server}",
            server="81.179.155.109,1433",
            database="ARCDashboard",
            uid="Monitoring",pwd='12Sunstone34')

cursor = cnxn.cursor()

cursor.execute("INSERT INTO dbo.Units (ID, Name, IP, victronID, Location, NoCCTV, Company, Lat, Lon, UnitType) VALUES (01, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL")


cnxn.commit()