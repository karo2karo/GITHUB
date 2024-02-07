#!/usr/bin/env python3

from pyzabbix import ZabbixAPI
import datetime

def connect_to_zabbix():
    try:
        z = ZabbixAPI("http://10.75.20.171/zabbix/")
        z.login(api_token='11ca2eb4c82e4a33fc79c39fff59572081e9f87df0486560ae98579a988b6de5')
        return z
    except Exception as e:
        return None

def jei_none():
    now = datetime.datetime.now()
    nhour = now.hour
    nminute = now.minute
    return now.hour * now.minute

def send_highest_number():
    from pyzabbix import ZabbixSender, ZabbixMetric
    metrics = []
    m = ZabbixMetric('Agent1', 'highest.number', max(max_value))
    metrics.append(m)
    zbx = ZabbixSender('10.75.20.171')
    zbx.send(metrics)

def main():
    zabbix_api = connect_to_zabbix()
    if zabbix_api:
        try:
            x_input = input()
            if not x_input:
                x = jei_none()
            else:
                x = int(x_input)

            n = time_variable()
            count = 1
            global max_value
            max_value = []
            while x != 1:
                if x % 2 == 0:
                    x = x // 2
                else:
                    x = 3 * x + 1
                count += 1
                max_value.append(x)
            send_highest_number()

        except ValueError:
            print("Invalid input.")
        except EOFError:
            x = jei_none()
            count = 1
            while x != 1:
                if x % 2 == 0:
                    x = x // 2
                else:
                    x = 3 * x + 1
                count += 1
            print(count)

        # Logout from the Zabbix API
        try:
            zabbix_api.user.logout()
        except Exception:
            pass  # Ignore logout errors

if __name__ == "__main__":
    main()
