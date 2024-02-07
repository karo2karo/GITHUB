#!/usr/bin/env python3

from pyzabbix import ZabbixAPI
import csv
import math

def main():
    zapi = connect_to_zabbix()
    global rows
    rows = []

    hostai = zapi.host.get(
                monitored=True,
                groupids=5,
                with_items=True,
                output=["hostid", "host"],
            )

    items = zapi.item.get(
                monitored=True,
                groupids=5,
                output=["itemid", "key_", 'lastvalue', 'hostid'],
                search={
                    'key_': 'vfs.fs.size'
                }
            )
    
    for host in hostai:
        item_list = []
        for item in items:
            if host['hostid'] == item['hostid'] and 'C:' in item['key_']:
                item_list.append(item)
            elif host['hostid'] == item['hostid'] and 'vfs.fs.size[/,total]' in item['key_']:
                item_list.append(item)
            elif host['hostid'] == item['hostid'] and 'vfs.fs.size[/,used]' in item['key_']:
                item_list.append(item)
            elif host['hostid'] == item['hostid'] and 'vfs.fs.size[/,free]' in item['key_']:
                item_list.append(item)
        rows.append({host['host']: item_list})

    write_csv_file()


def connect_to_zabbix():
    global zapi
    zapi = ZabbixAPI("https://izabbix.telia.lt/")
    zapi.login(
        api_token='ca2b3c52d0397a304247aab26c2577659fdd5aa068ae028579e6274c471406cb')
    print("Connected to Zabbix API Version %s" % zapi.api_version())
    return zapi


def bytes_to_gigabytes(bytes):
    p = math.pow(1024, 3)
    s = round(bytes / p, 2)
    return s


def write_csv_file():
    csv_file = "fspace.csv"
    csv_headers = ["hostname", "total_space_GB", "used_space_GB", "free_space_GB"]
    with open(csv_file, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
        writer.writeheader()
        
        for row in rows:
            for hostname, items in row.items():
                total_space = ""
                used_space = ""
                free_space = ""
                for item in items:
                    if 'total' in item['key_']:
                        total_space = bytes_to_gigabytes(float(item['lastvalue']))
                    elif 'used' in item['key_']:
                        used_space = bytes_to_gigabytes(float(item['lastvalue']))
                    elif 'free' in item['key_']:
                        free_space = bytes_to_gigabytes(float(item['lastvalue']))
                    

                writer.writerow({
                    "hostname": hostname,
                    "total_space_GB": total_space,
                    "used_space_GB": used_space,
                    "free_space_GB": free_space
                })

                
if __name__ == "__main__":
    main()