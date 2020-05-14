#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import *

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
ROOT = os.environ.get('BOTTLE_ROOT', '/')
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

# odkomentiraj, če želiš sporočila o napakah
debug(True)
######################################################################

def rtemplate(*largs, **kwargs):
    """
    Izpis predloge s podajanjem spremenljivke ROOT z osnovnim URL-jem.
    """
    return template(ROOT=ROOT, *largs, **kwargs)

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

@get('/')
def index():
    return("Dobrodošli v Naši zavarovalnici")

@get('/osebe')
def osebe():
    cur.execute("SELECT * FROM Osebe")
    return rtemplate('osebe.html', osebe=cur)

@get('/zavarovanja')
def zavarovanja():
    cur.execute("SELECT * FROM zavarovanja")
    return rtemplate('zavarovanja.html', zavarovanja=cur)

@get('/nepremicnine')
def nepremicnine():
    cur.execute("SELECT * FROM nepremicnine")
    return rtemplate('nepremicnine.html', nepremicnine=cur)

@get('/nepremicninska')
def nepremicninska():
    cur.execute("SELECT * FROM nepremicninska")
    return rtemplate('nepremicninska.html', nepremicninska=cur)

@get('/vrste_nepr')
def vrste_avto():
    cur.execute("SELECT * FROM Mozne_vrste_nepr_tb")
    return rtemplate('vrste_nepr.html', Mozne_vrste_nepr_tb=cur)

@get('/avtomobili')
def avtomobili():
    cur.execute("SELECT * FROM avtomobili")
    return rtemplate('avtomobili.html', avtomobili=cur)

@get('/avtomobilska')
def avtomobilska():
    cur.execute("SELECT * FROM avtomobilska")
    return rtemplate('avtomobilska.html', avtomobilska=cur)

@get('/vrste_avto')
def vrste_avto():
    cur.execute("SELECT * FROM Mozne_vrste_avto_tb")
    return rtemplate('vrste_avto.html', Mozne_vrste_avto_tb=cur)

@get('/zivljenjska')
def zivljenjska():
    cur.execute("SELECT * FROM zivljenska")
    return rtemplate('zivljenjska.html', zivljenska=cur)

@get('/vrste_zivlj')
def vrste_zivlj():
    cur.execute("SELECT * FROM Mozne_vrste_zivlj_tb")
    return rtemplate('vrste_zivlj.html', Mozne_vrste_zivlj_tb=cur)


######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
