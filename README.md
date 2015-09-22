# S7-Plugin
S7-Plugin für Smarthome / Smartvisu



#
#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
####################################################################################
######################################################################################

#  Copyright 2014 Version-1    Dominik Lott        dominik.lott@tresch-automation.de
#
#  Copyright 2015 Version-2     Frank Weber                       simatic-man@web.de
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
# You could specify one or more group addresses to send updates to. Item update will only be sent if the item is not changed.
#
#
# s7_read_s
# You could specify one or more group addresses to monitor for changes. cirle slow
#
#
# s7_read_f
# You could specify one or more group addresses to monitor for changes. cirle fast
#
#
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
