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
        printer_log = config.get('box_options', 'printer_log')
        printer_pos_url = config.get('box_options', 'printer_pos_url')
        return  {
            'host':host,
            'port':port or 8069,
            'user':user,
            'pw':pw,
            'db':db,
            'printer_log':printer_log,
            'printer_pos_url': printer_pos_url or 'http://127.0.0.1:8069/hw_proxy/print_xml_receipt',
        }
    except Exception as e:
        print e
        return False

def run(conf):
    post_headers = {'content-type': 'application/json'}
    oerp = oerplib.OERP(conf['host'], protocol='xmlrpc', port=conf['port'])
    oerp.login(conf['user'],conf['pw'], conf['db'])
    print_obj = oerp.get('qdodoo.print.list')
    printer_list = print_obj.search_read([('is_print', '!=', True)], ['id', 'ip_addr', 'name'], limit=4) #oerp.execute('qdodoo.print.list', 'search_read', [('is_print', '=', False)], ['id', 'ip_addr', 'name'], limit=50)

    for pp in printer_list:
        pp_id, content, ip_addr = pp.get('id'), pp.get('name'), pp.get('ip_addr')
        if ip_addr:
            data = {
                'method': 'call',
                'params': {'receipt': content},
                'jsonrpc': '2.0',
                'id': 0
            }
            response = requests.post(conf['printer_pos_url'], data=json.dumps(data), headers=post_headers, timeout=10)
            print_obj.write(pp_id, {'is_print': True})


def main():
    conf = check_conf()
    while conf:
        try:
            run(conf)
        except Exception as e:
            time.sleep(5)
            print e
########
main()

