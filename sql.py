# Embedded file name: sql.py
import requests
import json
import time
import xmlrpclib
import logging
import socket
import config
_logger = logging.getLogger(__name__)
xmlrpc_uid = 0
pre_ops = xmlrpclib.ServerProxy(config.xmlrpc_host + '/xmlrpc/2/common')
xmlrpc_uid = pre_ops.authenticate(config.xmlrpc_db, config.xmlrpc_uname, config.xmlrpc_pwd, {})
models = xmlrpclib.ServerProxy(config.xmlrpc_host + '/xmlrpc/2/object')
while True:
    try:
        ret_dicts = models.execute_kw(config.xmlrpc_db, xmlrpc_uid, config.xmlrpc_pwd, 'qdodoo.print.list', 'search_read', [[['is_print', '=', False]]], {'fields': ['id', 'ip_addr', 'name'],
         'limit': 50})
        for one_print_dict in ret_dicts:
            _logger.info('1111111111111111:%s', one_print_dict.get('id'))
            print_id = one_print_dict.get('id')
            print_content = one_print_dict.get('name')
            ip_addr = one_print_dict.get('ip_addr')
            payload = {'method': 'call',
             'params': {'receipt': print_content},
             'jsonrpc': '2.0',
             'id': 0}
            if ip_addr:
                #lable_printer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #lable_printer.connect((ip_addr, 9100))
                #lable_printer.send(print_content.encode('gb2312'))
                #lable_printer.close()
                response_json = requests.post('http://127.0.0.1:8069/hw_proxy/print_xml_receipt',
                                              data=json.dumps(payload), headers={'content-type': 'application/json'})
            else:
                response_json = requests.post('http://127.0.0.1:8069/hw_proxy/print_xml_receipt', data=json.dumps(payload), headers={'content-type': 'application/json'})
            models.execute_kw(config.xmlrpc_db, xmlrpc_uid, config.xmlrpc_pwd, 'qdodoo.print.list', 'write', [[print_id], {'is_print': True}])

        time.sleep(5)
    except Exception as e:
        _logger.info('1111111111111111:%s', e)
        time.sleep(5)