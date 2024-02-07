#!/usr/bin/env python3

from pyzabbix import ZabbixAPI
import csv


def main():
    connect_to_zabbix()
    global items
    items = zapi.item.get(monitored=True,
                        output=["name", "itemid", "key_", 
                                "status", "error"],
                        filter={"state": 1}, 
                        sortorder="hostid")
    print("Collecting item data...")
    write_csv_file()
    print("total unsupported items = ", len(items))
def connect_to_zabbix():
    global zapi
    zapi = ZabbixAPI("https://izabbix.telia.lt/")
    zapi.login(
        api_token='dcdce0335f620f3d255ad54679863e06900297b6c0b4414c0d65a237dbbc92fc')
    print("Connected to Zabbix API Version %s" % zapi.api_version())

def write_csv_file():
    
    csv_file = "notsupported.csv"
    csv_headers = ["name", "itemid", "key_", 
                   "status", "error"]
    with open(csv_file, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
        writer.writeheader()
        for item in items:
            writer.writerow(item)
    print("Writing data to CSV file...")

if __name__ == "__main__":
    main()
    print("Finished")