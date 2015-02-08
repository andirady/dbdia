#!/usr/bin/python3.4

import json
import sqlite3
import cgi
import os
import time
import sys
import mysql.connector
from urllib.parse import parse_qsl
from collections import OrderedDict
from random import choice

__chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
__con = sqlite3.connect('htbin/sessions.db')
__cursor = __con.cursor()

path = os.environ['PATH_INFO']
data = sys.stdin.read(int(os.environ.get('CONTENT_LENGTH', 0)))
form = dict(parse_qsl(data))

def list_tables(con):
    c = con.cursor()
    c.execute('show tables')
    tables = OrderedDict()
    for name, in c.fetchall():
        c.execute('desc %s' % name)
        if tables.get(name, None) == None:
            tables[name] = []
        for field in c.fetchall():
            tables[name].append(dict(zip(c.column_names, field)))
    return tables

if path == '/connect':
    cookie = ''
    if 'database' in form and 'user' in form and 'password' in form:
        sessionId = ''.join(choice(__chars) for i in range(32))
        t = time.time()
        expire = time.gmtime(t + 900) # 15 mins
        __cursor.execute('''
            INSERT INTO session VALUES (?, ?, ?)
        ''', (sessionId, int(time.time() * 1000), json.dumps(form)))
        __con.commit()
        
        try:
            con = mysql.connector.connect(connection_timeout=5, **form)     
            data = list_tables(con)
            con.close()
            print('Content-Type: application/json\n'
                  'Set-Cookie: _SESSION_ID=%s, Expires=%s\n'
                  '\n%s' % (sessionId, time.strftime('%a, %d %b %Y %H:%M:%S GMT', expire), json.dumps(data)))
        except:
            print('DbDia-Error: Failed to connect to database server')
            print()
    else:
        print('DbDia-Error: Invalid request')
        print()
    
    
__con.close()
