#!/usr/bin/env python3

from pyzabbix import ZabbixAPI
import csv

def main():
    connect_to_zabbix()

    hosts = zapi.host.get(monitored=True,
                        proxyids=10339,
                        output=["hostid", "host", "status"],
                        selectGroups=["groupid", "name"],
                        selectParentTemplates=["templateid", "name"])

    items = zapi.item.get(monitored=True,
                        hostids=[host["hostid"] for host in hosts],
                        output=["hostid", "key_", "lastvalue", "type"],
                        filter={"key_": "agent.version"})
    
    filtered_items = []
    for item in items:
        if item['type'] == '7' and item['key_'] == "agent.version":
            filtered_items.append(item)
    global filtered_hosts
    filtered_hosts = []
    for host in hosts:
        for item in filtered_items:
            if host["hostid"] == item["hostid"]:
                host["agent_version"] = item["lastvalue"]
                filtered_hosts.append(host)

    
    hosts = filtered_hosts
    print(filtered_hosts[1])

    write_csv_file()

def connect_to_zabbix():
    global zapi
    zapi = ZabbixAPI("https://zabbix.telia.lt/")
    zapi.login(user="zut970", password="2023Zuikis2023+++")
    print("Connected to Zabbix API Version %s" % zapi.api_version())

def write_csv_file():
    
    csv_file = "RIMI_proxy_data3.csv"
    csv_headers = ["hostid", "host", "groups",
                    "parentTemplates", "status",
                    "agent_version"]
    with open(csv_file, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
        writer.writeheader()
        for host in filtered_hosts:
            host['groups'] = [hostgroup['name'] 
                                for hostgroup in host['groups']]
            host['parentTemplates'] = [template['name'] 
                                for template in host['parentTemplates']]
            writer.writerow(host)
    print("Writing data to CSV file...")

if __name__ == "__main__":
    main()