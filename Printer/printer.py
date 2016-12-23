# -*- coding:utf-8 -*-

import escpos
EscposIO = escpos.EscposIO
Network = escpos.Network

#####################################################
content = 'ABCDE'
key = '192.168.11.12'


with EscposIO(Network(key, port=9100), autocut=False, autoclose=True) as p:
    print p.printer.receipt( content )




