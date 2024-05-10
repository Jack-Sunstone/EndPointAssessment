import requests
import json
import pyodbc

cnxn = ""

def connection():
    global cnxn
    cnxn = pyodbc.connect(driver="{ODBC Driver 17 for SQL Server}",
                          server="81.179.155.109,1433",
                          database="ARCDashboard",
                          uid="Victron",pwd="12Victron34")

