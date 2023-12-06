#!/usr/bin/env python3

from pyzabbix import ZabbixAPI


def main():
    connect_to_zabbix()
    global items
    items = zapi.item.get(monitored=True,
                        output=["name", "itemid", "key_", "state"],
                        filter={
                            "key_": "net.if.in[Microsoft Kernel Debug Network Adapter,ifname]",
                            "state": 1
                            })
    print(("Item total= "), len(items))
    for item in items:
        zapi.item.update(itemid=item["itemid"], status=1)

def connect_to_zabbix():
    global zapi
    zapi = ZabbixAPI("https://izabbix.telia.lt/")
    zapi.login(
        api_token='dcdce0335f620f3d255ad54679863e06900297b6c0b4414c0d65a237dbbc92fc')
    print("Connected to Zabbix API Version %s" % zapi.api_version())


if __name__ == "__main__":
    main()
    print("Finished")