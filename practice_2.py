import requests
import time

while True:
    print("What relay would you like to set? 1/2/3/4 ")
    relay = input()

    match relay:
        case "1":
            result = requests.get("http://81.179.155.109:79/testing/R1.php")

        case "2":
            result = requests.get("http://81.179.155.109:79/testing/R2.php")

        case "3":
            result = requests.get("http://81.179.155.109:79/testing/R3.php")

        case "4":
            result = requests.get("http://81.179.155.109:79/testing/R1.php")

        case _:
            print("Invalid Relay")

    time.sleep(60)
    if(result.status_code == 200): print("Relay set")

