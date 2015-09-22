#
#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
####################################################################################
######################################################################################

#  Copyright 2014 Version-1    Dominik Lott        dominik.lott@tresch-automation.de
#
#  Copyright 2015 Version-2   Frank Weber                          simatic-man@web.de
#
####################################################################################
#
#  This Plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  smartopenHMI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################
#
#   VERSION - 2
#
####################################################################################
# 
# s7_dpt
#
# This attribute is mandatory. If you don't provide one the item will be ignored.
# The DPT has to match the type of the item!
#
# The following datapoint types are supported:
#
#+--------+---------+------+----------------------------------+
#| DPT    | Data    | Type | Values                           |
#+========+=========+======+==================================+
#| 1      | 1 bit   | bool | False | True   0 | 1             |
#+--------+---------+------+----------------------------------+
#| 5      | 2 byte  | num  | 0 - 255                          |
#+--------+---------+------+----------------------------------+
#| 6      | 4 byte  | num  | 4-Octet Float Value IEEE 754     |
#+--------+---------+------+----------------------------------+
#
#
#
#
# s7_send
# You could specify one or more group addresses to send updates to. Item update will only be sent if the item is not changed via KNX.
#
#
# s7_read
# You could specify one or more group addresses to monitor for changes.
#
# s7_init
# If you set this attribute, SmartHome.py sends a read request to specified group address at startup and set the value of the item to the response.
# It implies 'knx_listen'.
#
#
# Example
#
#[living_room]
#
#
#### bit/bool  = DB42.dbx1.1
#
#
#    [[light]]
#        type = bool
#        visu_acl = rw
#        s7_dpt = 1
#        s7_send = 42/1/1
#        s7_read_f = 42/1/1
#
#
#
#
####  Dezimalzahl = int   = DB42.dbw4
#
#
#    [[temperature_act]]
#        type = num
#        visu_acl = rw
#   	 sqlite = yes
#        s7_dpt = 5
#        s7_send = 42/4
#        s7_read_s = 42/4       / slow read cirlce
#
#
#
#
####  Gleitpunktzahl = real  = DB42.dbd6
#
#
#    [[temperature_set]]
#        type = num
#        visu_acl = rw
#   	 sqlite = yes
#        s7_dpt = 6
#        s7_send = 42/6
#        s7_read_f = 42/6      / fast read cirlce
#
#
#
#
#
#
###################################################################################################



import logging
import threading
import struct
import binascii
import re


import snap7
from snap7.snap7exceptions import Snap7Exception
from snap7.snap7types import S7AreaDB, S7WLBit, S7WLByte, S7WLWord, S7WLDWord, S7WLReal, S7DataItem
from snap7.util import *


import lib.connection


tcpport = 102
rack = 0
slot = 2


logger = logging.getLogger('')





class S7(lib.connection.Client):

    def __init__(self, smarthome, time_ga=None, date_ga=None, read_cyl_fast=1, read_cyl_slow=10, busmonitor=False, host='127.0.0.1', port=102):
        self.client = snap7.client.Client()
        self.client.connect(host, rack, slot, tcpport)


        lib.connection.Client.__init__(self, host, port, monitor=False)
        self._sh = smarthome
        self.gal = {}
        self.gar = {}
        self._init_ga = []
        self._cache_ga = []
        self.time_ga = time_ga
        self.date_ga = date_ga
        self._lock = threading.Lock()



        if read_cyl_fast:
            self._sh.scheduler.add('S7 read cycle fast', self._read_fast, prio=5, cycle=int(read_cyl_fast))



        if read_cyl_slow:
            self._sh.scheduler.add('S7 read cycle slow', self._read_slow, prio=5, cycle=int(read_cyl_slow))



    def _send(self, data):

        if len(data) < 2 or len(data) > 0xffff:                                          # 0xffff = 65535
            logger.debug('S7: Illegal data size: {}'.format(repr(data)))
            return False

        # prepend data length
        send = bytearray(len(data).to_bytes(2, byteorder='big'))
        send.extend(data)
        self.send(send)




    # ------------------------
    # Daten schreiben
    # ------------------------

    def groupwrite(self, ga, payload, dpt, flag='write'):
        print("groupwrite")
        print("ga: " +  ga)
        print("payload: " +  str(payload))
        print("dpt: " +  dpt)
        print("flag: " +  flag)
        ret_s7_num = re.findall(r'\d+', ga)




        if dpt == '1':
            #Schreibe Bool
            print("Schreibe Bool")

            ret_val = self.client.db_read(int(ret_s7_num[0]), int(ret_s7_num[1]), 1)      #Lese    DB / Ab / Byte

            writevalue = payload
            snap7.util.set_bool(ret_val, 0, int(ret_s7_num[2]), writevalue)               #Schreibe    Value aus Byte / Adresse 
            self.client.db_write(int(ret_s7_num[0]), int(ret_s7_num[1]), ret_val)         #Schreibe    DB / Ab / Byte




        elif dpt == '5':
            # Schreibe Dezimalzahl#
            print("Schreibe Dezimalzahl")

            write_value_5 = payload
            write_bytes_5 = bytearray(struct.pack('>h', write_value_5))			   
            self.client.db_write(int(ret_s7_num[0]), int(ret_s7_num[1]), write_bytes_5)          #Schreibe    DB / Ab / Byte



        elif dpt == '6':
            # Schreibe Gleitzahl
            print("Schreibe Gleitzahl")

            write_value_6 = payload
            write_bytes_6 = bytearray(struct.pack('>f', write_value_6))              
            self.client.db_write(int(ret_s7_num[0]), int(ret_s7_num[1]), write_bytes_6)         #Schreibe    DB / Ab / Byte







    # ------------------------
    # Daten Lesen
    # ------------------------



    def groupread(self, ga, dpt):
        print("groupread")
        print("ga: " +  ga)
        print("dpt: " +  dpt)
        ret_s7_num = re.findall(r'\d+', ga)
        val = 0 				#Item-Value
        src = ga				#Source-Item      (Quell-Adresse)
        dst = ga 				#Destination-Item (Ziel-Adresse)



        if dpt == '1':
            #Lese Bool
            print("Lese Bool")

            ret_val = self.client.db_read(int(ret_s7_num[0]), int(ret_s7_num[1]), 1)      #Lese    DB / Ab / Byte
            val = snap7.util.get_bool(ret_val, 0, int(ret_s7_num[2]))                     #Lese    Value aus Byte / Adresse 




        elif dpt == '5':
            # Lese Dezimalzahl#
            print("Lese Dezimalzahl")

            result = self.client.db_read(int(ret_s7_num[0]), int(ret_s7_num[1]), 2)       #Lese    DB / Ab / Byte    
            bytes = ''.join([chr(x) for x in result]).encode('utf-8')
            int_num = struct.unpack('>h', bytes)
            int_num2 = re.findall(r'\d+', str(int_num))
            val = int_num2[0]




        elif dpt == '6':
            # Lese Gleitzahl
            print("Lese Gleitzahl")

            result = self.client.db_read(int(ret_s7_num[0]), int(ret_s7_num[1]), 4)       #Lese    DB / Ab / Byte    
            int_num = struct.unpack('>f', result)[0]
            val = int_num




        item(val, 'S7', src, ga)
        print(str(val) + ":" + str(val) + ":" + str(src) + ":" + str(ga))







    # --------------------------
    # Daten lesen Zyklus schnell
    # --------------------------





    def _read_fast(self):

        for ga in self._init_ga:
            print("Daten lesen Zyklus schnell")
            print("ga: " +  ga)
            val = 0 			#Item-Value
            src = ga			#Source-Item      (Quell-Adresse)
            dst = ga 			#Destination-Item (Ziel-Adresse)


            for item in self.gal[dst]['items']:

                ret_s7_num = re.findall(r'\d+', dst)
                var_typ = len(ret_s7_num)
                dpt = item.conf['s7_dpt']
                print("dpt: " +  dpt)




                if dpt == '1':
            	    #Initialisiere Bool
                    #print("Initialisiere Bool")

                    ret_val = self.client.db_read(int(ret_s7_num[0]), int(ret_s7_num[1]), 1)      #Lese    DB / Ab / Byte
                    val = snap7.util.get_bool(ret_val, 0, int(ret_s7_num[2]))                     #Lese    Value aus Byte / Adresse 




                elif dpt == '5':
            	    #Initialisiere Dezimalzahl
                    #print("Initialisiere Dezimalzahl")

                    result = self.client.db_read(int(ret_s7_num[0]), int(ret_s7_num[1]), 2)       #Lese    DB / Ab / Byte    
                    bytes = ''.join([chr(x) for x in result]).encode('utf-8')
                    int_num = struct.unpack('>h', bytes)
                    int_num2 = re.findall(r'\d+', str(int_num))
                    val = int_num2[0]




                elif dpt == '6':
            	    #Initialisiere Gleitzahl
                    #print("Initialisiere Gleitzahl")

                    result = self.client.db_read(int(ret_s7_num[0]), int(ret_s7_num[1]), 4)       #Lese    DB / Ab / Byte    
                    int_num = struct.unpack('>f', result)[0]
                    val = int_num




                item(val, 'S7', src, ga)
                print(str(val) + ":" + str(val) + ":" + str(src) + ":" + str(ga))






    # --------------------------
    # Daten lesen Zyklus langsam
    # --------------------------





    def _read_slow(self):

        for ga in self._init_ga:
            print("Daten lesen Zyklus langsam")
            print("ga: " +  ga)
            val = 0 			#Item-Value
            src = ga			#Source-Item      (Quell-Adresse)
            dst = ga 			#Destination-Item (Ziel-Adresse)


            for item in self.gal[dst]['items']:

                ret_s7_num = re.findall(r'\d+', dst)
                var_typ = len(ret_s7_num)
                dpt = item.conf['s7_dpt']
                print("dpt: " +  dpt)




                if dpt == '1':
            	    #Initialisiere Bool
                    #print("Initialisiere Bool")

                    ret_val = self.client.db_read(int(ret_s7_num[0]), int(ret_s7_num[1]), 1)      #Lese    DB / Ab / Byte
                    val = snap7.util.get_bool(ret_val, 0, int(ret_s7_num[2]))                     #Lese    Value aus Byte / Adresse 




                elif dpt == '5':
            	    #Initialisiere Dezimalzahl
                    #print("Initialisiere Dezimalzahl")

                    result = self.client.db_read(int(ret_s7_num[0]), int(ret_s7_num[1]), 2)       #Lese    DB / Ab / Byte    
                    bytes = ''.join([chr(x) for x in result]).encode('utf-8')
                    int_num = struct.unpack('>h', bytes)
                    int_num2 = re.findall(r'\d+', str(int_num))
                    val = int_num2[0]




                elif dpt == '6':
            	    #Initialisiere Gleitzahl
                    #print("Initialisiere Gleitzahl")

                    result = self.client.db_read(int(ret_s7_num[0]), int(ret_s7_num[1]), 4)       #Lese    DB / Ab / Byte    
                    int_num = struct.unpack('>f', result)[0]
                    val = int_num




                item(val, 'S7', src, ga)
                print(str(val) + ":" + str(val) + ":" + str(src) + ":" + str(ga))








#    def _read_cyl_slow(self):
#        now = self._sh.now()

#        if self.time_ga:
#            self.groupwrite(self.time_ga, now, '10')

#        if self.date_ga:
#            self.groupwrite(self.date_ga, now.date(), '11')





#    def read_cyl_slow(self, time_ga=None, date_ga=None):
#        now = self._sh.now()

#        if time_ga:
#            self.groupwrite(time_ga, now.time(), '10')

#        if date_ga:
#            self.groupwrite(date_ga, now.date(), '11') 





#    def _read_cyl_fast(self):
#        now = self._sh.now()

#        if self.time_ga:
#            self.groupwrite(self.time_ga, now, '10')

#        if self.date_ga:
#            self.groupwrite(self.date_ga, now.date(), '11')





#    def read_cyl_fast(self, time_ga=None, date_ga=None):
#        now = self._sh.now()

#        if time_ga:
#            self.groupwrite(time_ga, now.time(), '10')

#        if date_ga:
#            self.groupwrite(date_ga, now.date(), '11') 






#    def handle_connect(self):
#        print("handle_connect")
#        self.discard_buffers()
#        enable_cache = bytearray([0, 112])
#        self._send(enable_cache)

#        init = bytearray([0, 38, 0, 0, 0])
#        self._send(init)
#        self.terminator = 2


#        if self._init_ga != []:
#            if self.connected:
#                logger.debug('S7: init read')
#                for ga in self._init_ga:
#                    self.groupread(ga)
#                self._init_ga = []





    def run(self):
        self.alive = True





    def stop(self):
        self.alive = False
        self.handle_close()





    def parse_item(self, item):




        if 's7_dtp' in item.conf:
            logger.warning("S7: Ignoring {0}: please change s7_dtp to s7_dpt.".format(item))
            return None

        if 's7_dpt' in item.conf:
            dpt = item.conf['s7_dpt']
        else:
            return None






        if 's7_read_s' in item.conf:
            ga = item.conf['s7_read_s']
            logger.debug("S7: {0} listen on and init with {1}".format(item, ga))

            if not ga in self.gal:
                self.gal[ga] = {'dpt': dpt, 'items': [item], 'logics': []}

            else:
                if not item in self.gal[ga]['items']:
                    self.gal[ga]['items'].append(item)
            self._init_ga.append(ga)





        if 's7_read_f' in item.conf:
            ga = item.conf['s7_read_f']
            logger.debug("S7: {0} listen on and init with {1}".format(item, ga))

            if not ga in self.gal:
                self.gal[ga] = {'dpt': dpt, 'items': [item], 'logics': []}

            else:
                if not item in self.gal[ga]['items']:
                    self.gal[ga]['items'].append(item)
            self._init_ga.append(ga)





        if 's7_send' in item.conf:
            if isinstance(item.conf['s7_send'], str):
                item.conf['s7_send'] = [item.conf['s7_send'], ]




#        if 's7_read' in item.conf:
#            if isinstance(item.conf['s7_read'], str):
#                item.conf['s7_read'] = [item.conf['s7_read'], ]










        if's7_send' in item.conf:
            return self.update_item_send

        return None




        if 's7_read' in item.conf:
            return self.update_item_read

        return None








        if 's7_listen' in item.conf:
            s7_listen = item.conf['s7_listen']
            if isinstance(s7_listen, str):
                s7_listen = [s7_listen, ]
            for ga in s7_listen:
                logger.debug("S7: {0} listen on {1}".format(item, ga))

                if not ga in self.gal:
                    self.gal[ga] = {'dpt': dpt, 'items': [item], 'logics': []}

                else:
                    if not item in self.gal[ga]['items']:
                        self.gal[ga]['items'].append(item)











    def update_item_send(self, item, caller=None, source=None, dest=None):


        if 's7_send' in item.conf:
            if caller != 's7':
                for ga in item.conf['s7_send']:
                    self.groupwrite(ga, item(), item.conf['s7_dpt'], flag='write')





    def update_item_read(self, item, caller=None, source=None, dest=None):



        if 's7_status' in item.conf:
            for ga in item.conf['s7_status']:  # send status update
                if ga != dest:
                    self.groupread(ga, item.conf['s7_dpt'])




