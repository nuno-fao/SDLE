import os 
import ntplib
import time
import datetime



def getNTPDateTime():
    addr = '1.pool.ntp.org'
    try:
        client = ntplib.NTPClient()
        response = client.request(addr, version=3)
        os.system('date ' + time.strftime('%m%d%H%M%Y.%S',
                                          time.localtime(response.tx_time)))
    except Exception as e:
        print(e)

def synchronize():
    while True:
        getNTPDateTime()
        time.sleep(60)