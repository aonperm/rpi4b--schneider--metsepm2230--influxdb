#!/usr/bin/env python

# rpi4b--schneider--metsepm2230--influxdb

import os
#import threading
import argparse, time
from influxdb import InfluxDBClient
import simplejson as json
import pyspeedtest
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import struct
import math


delay_to_send = 60.0

delay_polling_register = 0.001

delay_polling_device = 0.1

measurement = "ABC_MDB"


######################
# Get Service Status #
######################
def get_main_service():
    # 0 means running, 768 stopped
    s = os.system('systemctl is-active main.service')
    return s


###################
# Get MAC Address #
###################
def get_mac_address(interface=""):
    # Return the MAC address of the specified interface
    try:
        str = open('/sys/class/net/%s/address' %interface).read()
    except:
        str = "00:00:00:00:00:00"
    return str[0:17]
mac_address = get_mac_address("eth0")


###################
# Get Temperature #
###################
def get_temp():
    try:
        temp = float(open("/sys/class/thermal/thermal_zone0/temp").read())/1000.0
        temp = round(temp, 6) # Limiting floats decimal points
    except:
        temp = 0.0
    return temp


############
# Get Ping #
############
def get_ping(url=""):
    try:
        ping = pyspeedtest.SpeedTest().ping(url)
        ping = round(ping, 6) # Limiting floats decimal points
    except:
        ping = 0.0
    return ping


def send_master_data():
    try:
        a = [{
            "measurement": measurement,
            "tags": {
                "mac_address": mac_address,
                "slave_id": 0,
                "type": "rpi"
            },
            "fields": {
                "0_temp": get_temp(),
                "0_ping": get_ping("google.co.th")
                "0_main.service": get_main_service()
            }
        }]

        print "\r\n"+a[0]["tags"]["type"]+"["+str(a[0]["tags"]["slave_id"])+"]"
        print json.dumps(a, sort_keys=True, indent=2)
        print myInfluxDBClient.write_points(a)
        return True

    except:
        print "\r\n"+a[0]["tags"]["type"]+"["+str(a[0]["tags"]["slave_id"])+"]"
        print ValueError
        return False


############
# InfluxDB #
############
host = '192.168.1.100'
port = 8086
user = 'admin'
password = 'admin'
dbname = 'mydb'
myInfluxDBClient = InfluxDBClient(host, port, user, password, dbname)


schneider_metsepm2230 = {
    "slave_id":1,
    "type":"power_meter",
    "registers": [
        {"name":"c_Current_L1",             "address":3000, "scaling_factor":1.0, "units":"A"},
        {"name":"c_Current_L2",             "address":3002, "scaling_factor":1.0, "units":"A"},
        {"name":"c_Current_L3",             "address":3004, "scaling_factor":1.0, "units":"A"},
        {"name":"c_Current_Neutral",        "address":3006, "scaling_factor":1.0, "units":"A"},
        # {"name":"c_Current_Earth",          "address":3008, "scaling_factor":1.0, "units":"A"},
        {"name":"c_Current_Average",        "address":3010, "scaling_factor":1.0, "units":"A"},

        {"name":"v_Voltage_L1-L2",          "address":3020, "scaling_factor":1.0, "units":"V"},
        {"name":"v_Voltage_L2-L3",          "address":3022, "scaling_factor":1.0, "units":"V"},
        {"name":"v_Voltage_L3-L1",          "address":3024, "scaling_factor":1.0, "units":"V"},
        {"name":"v_Voltage_L-L_Avg",        "address":3026, "scaling_factor":1.0, "units":"V"},
        {"name":"v_Voltage_L1-N",           "address":3028, "scaling_factor":1.0, "units":"V"},
        {"name":"v_Voltage_L2-N",           "address":3030, "scaling_factor":1.0, "units":"V"},
        {"name":"v_Voltage_L3-N",           "address":3032, "scaling_factor":1.0, "units":"V"},
        {"name":"v_Voltage_L-N_Avg",        "address":3036, "scaling_factor":1.0, "units":"V"},

        {"name":"p_Active_Power_L1",        "address":3054, "scaling_factor":1000.0, "units":"kW"},
        {"name":"p_Active_Power_L2",        "address":3056, "scaling_factor":1000.0, "units":"kW"},
        {"name":"p_Active_Power_L3",        "address":3058, "scaling_factor":1000.0, "units":"kW"},
        {"name":"p_Active_Power_Total",     "address":3060, "scaling_factor":1000.0, "units":"kW"},
        {"name":"p_Reactive_Power_L1",      "address":3062, "scaling_factor":1000.0, "units":"kVAR"},
        {"name":"p_Reactive_Power_L2",      "address":3064, "scaling_factor":1000.0, "units":"kVAR"},
        {"name":"p_Reactive_Power_L3",      "address":3066, "scaling_factor":1000.0, "units":"kVAR"},
        {"name":"p_Reactive_Power_Total",   "address":3068, "scaling_factor":1000.0, "units":"kVAR"},
        {"name":"p_Apparent_Power_L1",      "address":3070, "scaling_factor":1000.0, "units":"kVA"},
        {"name":"p_Apparent_Power_L2",      "address":3072, "scaling_factor":1000.0, "units":"kVA"},
        {"name":"p_Apparent_Power_L3",      "address":3074, "scaling_factor":1000.0, "units":"kVA"},
        {"name":"p_Apparent_Power_Total",   "address":3076, "scaling_factor":1000.0, "units":"kVA"},

        {"name":"pf_Power_Factor_L1",       "address":3078, "scaling_factor":1.0, "units":"-"},
        {"name":"pf_Power_Factor_L2",       "address":3080, "scaling_factor":1.0, "units":"-"},
        {"name":"pf_Power_Factor_L3",       "address":3082, "scaling_factor":1.0, "units":"-"},
        {"name":"pf_Power_Factor_Total",    "address":3084, "scaling_factor":1.0, "units":"-"},

        {"name":"f_Frequency",              "address":3110, "scaling_factor":1.0, "units":"Hz"},

        {"name":"e_Active_Energy_Delivered_(Into_Load)",  "address":2700, "scaling_factor":1000.0, "units":"kWh"},
        {"name":"e_Active_Energy_Received_(Out_of_Load)", "address":2702, "scaling_factor":1000.0, "units":"kWh"},
        {"name":"e_Reactive_Energy_Delivered",            "address":2708, "scaling_factor":1000.0, "units":"kVARh"},
        {"name":"e_Reactive_Energy_Received",             "address":2710, "scaling_factor":1000.0, "units":"kVARh"},
        {"name":"e_Apparent_Energy_Delivered",            "address":2716, "scaling_factor":1000.0, "units":"kVAh"},
        {"name":"e_Apparent_Energy_Received",             "address":2718, "scaling_factor":1000.0, "units":"kVAh"},

        {"name":"s_Normal_Phase_Rotation",  "address":2024, "scaling_factor":1.0, "units":"-"}
    ]
}

'''
def twos(val, bits):
    if(val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val
'''

def send_modbus_to_cloud(data):
    try:
        a = [{
            "measurement": measurement,
            "tags": {
                "mac_address": mac_address,
                "slave_id": data["slave_id"],
                "type": data["type"]
            },
            "fields": {}
        }]

        myModbusClient = ModbusClient(method='rtu', port='/dev/ttyUSB0', baudrate=19200, parity='E', timeout=1)
        myModbusClient.connect()

        for i in range(len(data["registers"])):

            address_offset = 1

            name = data["registers"][i]["name"]
            address = (data["registers"][i]["address"]) - address_offset
            #bits = data["registers"][i]["bits"]
            count = 2
            slave_id = data["slave_id"]
            scaling_factor = data["registers"][i]["scaling_factor"]
            type_name = data["type"]

            #print "slave_id:", slave_id
            r = myModbusClient.read_holding_registers(address, count, unit=slave_id)

            value = 0.0

            msb = "{0:04x}".format(r.registers[0])
            lsb = "{0:04x}".format(r.registers[1])
            hex32 = msb+lsb
            #print msb, lsb, hex32
            value = struct.unpack('!f', hex32.decode('hex'))[0]

            '''
            if(name=="pf_Power_Factor_L1"or\
               name=="pf_Power_Factor_L2"or\
               name=="pf_Power_Factor_L3"or\
               name=="pf_Power_Factor_Total"):
                regVal = value
                PF_Val = 0
                # Pseudo code to decode PF Value
                if (regVal > 1):
                    PF_Val = 2 - regVal
                    print "PF is leading"
                elif (regVal < -1):
                    PF_Val = -2-regVal
                    print "PF is leading"
                elif ( abs(regVal) == 1 ):
                    PF_Val = regVal
                    print "PF is at unity"
                else:
                    PF_Val = regVal
                    print "PF is lagging"
                print PF_Val
                value = PF_Val
                print value
            else:
                value *= scaling_factor
            '''
            value *= scaling_factor

            if math.isnan(value) == True:
                value = 0.0

            # value = round(value, 6) # Limiting floats decimal points
            # print value
            a[0]["fields"][name] = value

            time.sleep(delay_polling_register)
            #end for

        ret = myInfluxDBClient.write_points(a)
        if ret==True:
            myModbusClient.close()
            print "\r\n"+a[0]["tags"]["type"]+"["+str(a[0]["tags"]["slave_id"])+"]"
            print json.dumps(a, sort_keys=True, indent=2)
            print ret
            return True
        else:
            return False

    except:
        print "\r\n"+a[0]["tags"]["type"]+"["+str(a[0]["tags"]["slave_id"])+"]"
        print ValueError
        return False


def main():
    while True:
        '''
        schneider_metsepm2230["slave_id"] = 3
        send_modbus_to_cloud(schneider_metsepm2230)
        '''


        send_master_data()
        for i in range(1, 11): # 1 to 10
            schneider_metsepm2230["slave_id"] = i
            send_modbus_to_cloud(schneider_metsepm2230)
            time.sleep(delay_polling_device)

        time.sleep(delay_to_send)

if __name__ == "__main__":
    main()
