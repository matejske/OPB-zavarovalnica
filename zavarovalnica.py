#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py (bottle je knjiznica funkcij)
from bottle import *

# uvozimo ustrezne podatke za povezavo
import auth_enej as auth

# uvozimo psycopg2 (to je za server)
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os 

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080) #na tem portu zaženemo
RELOADER = os.environ.get('BOTTLE_RELOADER', True) #se bo avtomatsko posabljalo, rabimo le relodat spletno stran v brskalniku
ROOT = os.environ.get('BOTTLE_ROOT', '/')
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

# odkomentiraj, če želiš sporočila o napakah
debug(True)


#########################################################################################


def rtemplate(*largs, **kwargs):
    """
    Izpis predloge s podajanjem spremenljivke ROOT z osnovnim URL-jem.
    """
    return template(ROOT=ROOT, *largs, **kwargs)

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

# Zacetna stran ==========================================================================
@get('/')
def zacetna_stran():
    return rtemplate('zacetna_stran.html')

@post('/')
def zacetna_stran():
    return rtemplate('zacetna_stran.html')


# Podstrani za vsako tabelo iz baze =======================================================
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
    cur.execute("SELECT * FROM Mozne_vrste_zivlj_tb") #s SELECT naredimo sistemsko poizvedbo
    return rtemplate('vrste_zivlj.html', Mozne_vrste_zivlj_tb=cur)


# Prijava za agenta =============================================================================
@get('/prijava_agent')
def prijava_agent():
    return rtemplate('prijava_agent.html', emso='', geslo='', napaka=None)

@post('/prijava_agent')
def prijava_agent():
    #emso = request.forms.emso
    #geslo = request.forms.geslo ###Tu nevem čisto kako bomo s tem geslom zaenkrat, da bi nam začasno delovalo brez cookijev
    return rtemplate('prijava_agent.html', napaka=None)


# Prijava za že registriranega zavarovanca =======================================================
@get('/prijava_zavarovanec')
def prijava_zavarovanec():
    return rtemplate('prijava_zavarovanec.html', emso='', geslo='', napaka=None)

@post('/prijava_zavarovanec')
def prijava_zavarovanec():
    #emso = request.forms.emso
    #geslo = request.forms.geslo ###Tu nevem čisto kako bomo s tem geslom zaenkrat, da bi nam začasno delovalo brez cookijev
    return rtemplate('prijava_zavarovanec.html', napaka=None)

# Dodajanje novega komitenta ============================================================
# S tem get zahtevkom napišemo naj bo že vnešeno v polju (spremenljivka pa je value pri znački input)
@get('/dodaj_osebo')
def dodaj_osebo():
    return rtemplate('dodaj_osebo.html', emso='', ime='', priimek='', naslov='', email='', 
                    rojstvo='', telefon='', zaposleni='FALSE',  napaka=None)


# Pridobimo podatke iz vnosnih polj
@post('/dodaj_osebo')
def dodaj_osebo():
    emso = request.forms.emso #ta emso se nanasa na name="emso" v znački input
    ime = request.forms.ime
    priimek = request.forms.priimek
    naslov = request.forms.naslov
    email = request.forms.email
    rojstvo = request.forms.rojstvo
    telefon = request.forms.telefon
    #zaposleni = request.forms.zaposleni
    try:
        cur.execute("INSERT INTO osebe (emso,ime,priimek,naslov,email,rojstvo,telefon,zaposleni) VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)", 
                    (emso,ime,priimek,naslov,email,rojstvo,telefon))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        return rtemplate('dodaj_osebo.html', emso=emso, ime=ime, priimek=priimek, naslov=naslov, email=email, 
                        rojstvo=rojstvo, telefon=telefon, napaka='Zgodila se je napaka: %s' % ex)
    redirect("%sosebe" %ROOT) 

# Sklenitev zavarovanja =============================================================================
@get('/sklenitev_zavarovanja')
def sklenitev_zavarovanja():
    return rtemplate('sklenitev_zavarovanja.html')

@post('/sklenitev_zavarovanja')
def sklenitev_zavarovanja():
    return rtemplate('sklenitev_zavarovanja.html')


##########################################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
#conn = psycopg2.connect(na katero bazo se priklopimo (auth je una datoteka, z .db pa v njej klicemo na katero bazo gremo), 
# host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)


#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) #na cur nastavimo objekt kurzorja (obnaša se podobno kot odzivnik v ukazni vrstici)
    #cur.execute(sql stavek) nam bo potem izvedel nekaj na bazi
    #cur je globalna spremenljivka

# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
#run(localhost, da zaženemo na svojem PC, dolocimo na katerem portfu zaženemo)
 

#Izpis sql stavkov v terminal (za debugiranje)
# conn.set_trace_callback(print) <<<<<<<<<<<<<<<<<<<<<<<<<<< Nevem ali ni to samo za sqlite