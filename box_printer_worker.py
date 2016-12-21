# Embedded file name: sql.py
import oerplib
import sys
from  ConfigParser import RawConfigParser
import requests
import json
import time
import xmlrpclib
import logging
import socket

_logger = logging.getLogger(__name__)
config = RawConfigParser(allow_no_value=True)

def check_conf():
    try:
        conf_file = sys.argv[1]
        config.read(conf_file)
        host = config.get('box_options', 'printer_host')
        port = config.get('box_options', 'printer_port') or '8069'
        user = config.get('box_options', 'printer_user')
        pw = config.get('box_options', 'printer_passwd')
        db = config.get('box_options', 'printer_db')
        local_printer_id = config.get('box_options', 'printer_local_ip')
        printer_log = config.get('box_options', 'printer_log')
        printer_time_gap = config.getfloat('box_options', 'printer_time_gap')
        printer_pos_url = config.get('box_options', 'printer_pos_url')
        printer_pos_timeout = config.getint('box_options', 'printer_pos_timeout')
        printer_step_count = config.getint('box_options', 'printer_step_count')
        print 'check conf ok'
        return  {
            'host':host,
            'port':port or 8069,
            'user':user,
            'pw':pw,
            'db':db,
            'local_printer_id':local_printer_id,
            'printer_log':printer_log,
            'printer_time_gap': printer_time_gap or 10,
            'printer_pos_url': printer_pos_url or 'http://127.0.0.1:8069/hw_proxy/print_xml_receipt',
            'printer_pos_timeout': printer_pos_timeout or 30,
            'printer_step_count': printer_step_count or 5,
        }
    except Exception as e:
        print e
        return False

def run(conf):
    post_headers = {'content-type': 'application/json'}
    oerp = oerplib.OERP(conf['host'], protocol='xmlrpc', port=conf['port'])
    oerp.login(conf['user'],conf['pw'], conf['db'])
    print_obj = oerp.get('qdodoo.print.list')
    printer_list = print_obj.search_read([('is_print', '=', False)], ['id', 'ip_addr', 'name'], limit=conf['printer_step_count']) #oerp.execute('qdodoo.print.list', 'search_read', [('is_print', '=', False)], ['id', 'ip_addr', 'name'], limit=50)
    for pp in printer_list:
        pp_id, content, ip_addr = pp.get('id'), pp.get('name'), pp.get('ip_addr')
        if ip_addr:
            lable_printer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            lable_printer.connect((ip_addr, 9100))
            lable_printer.send(content.encode('gb2312'))
            lable_printer.close()
        else:
            data = {
                'method': 'call',
                'params': {'receipt': content},
                'jsonrpc': '2.0',
                'id': 0
            }
            response = requests.post(conf['printer_pos_url'], data=json.dumps(data), headers=post_headers, timeout=conf['printer_pos_timeout'])
            print response
            ##todo  check response
            #print_obj.write(pp_id, {'is_print': True})

    print len(printer_list)




def main():
    conf = check_conf()
    while conf:
        try:
            run(conf)
        except Exception as e:
            time.sleep(conf['printer_time_gap'])
            print e
########
main()








# _logger = logging.getLogger(__name__)
# xmlrpc_uid = 0
# pre_ops = xmlrpclib.ServerProxy(config.xmlrpc_host + '/xmlrpc/2/common')
# xmlrpc_uid = pre_ops.authenticate(config.xmlrpc_db, config.xmlrpc_uname, config.xmlrpc_pwd, {})
# models = xmlrpclib.ServerProxy(config.xmlrpc_host + '/xmlrpc/2/object')
# while True:
#     try:
#         ret_dicts = models.execute_kw(config.xmlrpc_db, xmlrpc_uid, config.xmlrpc_pwd, 'qdodoo.print.list', 'search_read', [[['is_print', '=', False]]], {'fields': ['id', 'ip_addr', 'name'],
#          'limit': 50})
#         for one_print_dict in ret_dicts:
#             print_id = one_print_dict.get('id')
#             print_content = one_print_dict.get('name')
#             ip_addr = one_print_dict.get('ip_addr')
#             payload = {'method': 'call',
#              'params': {'receipt': print_content},
#              'jsonrpc': '2.0',
#              'id': 0}
#             if ip_addr:
#                 lable_printer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                 lable_printer.connect((ip_addr, 9100))
#                 lable_printer.send(print_content.encode('gb2312'))
#                 lable_printer.close()
#             else:
#                 response_json = requests.post('http://127.0.0.1:8069/hw_proxy/print_xml_receipt', data=json.dumps(payload), headers={'content-type': 'application/json'})
#             models.execute_kw(config.xmlrpc_db, xmlrpc_uid, config.xmlrpc_pwd, 'qdodoo.print.list', 'write', [[print_id], {'is_print': True}])
#
#         time.sleep(5)
#     except Exception as e:
#         _logger.info('1111111111111111:%s', e)
#         time.sleep(5)