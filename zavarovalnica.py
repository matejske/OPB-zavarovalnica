#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py (bottle je knjiznica funkcij)
from bottle import *

# uvozimo ustrezne podatke za povezavo
import auth_enej as auth

#uvozimo paket za delo z datumi
from datetime import date

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

# Glavna stran ==========================================================================
@get('/')
def glavna_stran():
    return rtemplate('glavna_stran.html')

@post('/')
def glavna_stran():
    return rtemplate('glavna_stran.html')

# Stran o zaposlenih ==========================================================================
@get('/zaposleni')
def zaposleni():
    return rtemplate('zaposleni.html')

@post('/zaposleni')
def zaposleni():
    return rtemplate('zaposleni.html')

# Kontaktna stran ==========================================================================
@get('/kontakt')
def kontakt():
    return rtemplate('kontakt.html')

@post('/kontakt')
def kontakt():
    return rtemplate('kontakt.html')

# Predstavitev zavarovanj ==========================================================================
@get('/predstavitev_zavarovanj')
def predstavitev_zavarovanj():
    return rtemplate('predstavitev_zavarovanj.html')

@post('/predstavitev_zavarovanj')
def predstavitev_zavarovanj():
    return rtemplate('predstavitev_zavarovanj.html')



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

# Stran za prijavljenega zavarovanca =======================================================
@get('/zavarovanec')
def zavarovanec():
    return rtemplate('zavarovanec.html', napaka=None)

@get('/zavarovanec/<komitent_id>')
def posameznikova_zavarovanja(komitent_id):
    cur.execute("SELECT * FROM zavarovanja WHERE komitent_id LIKE '%s' ORDER BY datum_police DESC" %komitent_id)
    return rtemplate('zavarovanja_posameznik.html', komitent_id=komitent_id, zavarovanja_posameznik=cur)

# Dodajanje novega komitenta ============================================================
# S tem get zahtevkom napišemo naj bo že vnešeno v polju (spremenljivka pa je value pri znački input)
@get('/dodaj_osebo')
def dodaj_osebo():
    return rtemplate('dodaj_osebo.html', emso='', ime='', priimek='', naslov='', email='', rojstvo='', telefon='', zaposleni='FALSE',  napaka=None)


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

# Sklenitev avtomobilskih zavarovanj ============================================================
# S tem get zahtevkom napišemo naj bo že vnešeno v polju (spremenljivka pa je value pri znački input)
@get('/sklenitev_avtomobilsko')
def sklenitev_avtomobilsko():
    return rtemplate('sklenitev_avtomobilsko.html', stevilka_police='', emso='', registrska='', znamka='', model='', vrednost='', vrsta_avto='',  napaka=None)


# Pridobimo podatke iz vnosnih polj
@post('/sklenitev_avtomobilsko')
def sklenitev_avtomobilsko():
    stevilka_police = request.forms.stevilka_police #IDEALNO BI BLO, DA SE TEGA NEKAKO ZNEBIMO IN DA SAMO GENERIRA
    emso = request.forms.emso
    registrska = request.forms.registrska
    znamka = request.forms.znamka
    model = request.forms.model
    vrednost = request.forms.vrednost
    vrsta_avto = request.forms.vrsta_avto
    try:
        cur.execute("INSERT INTO avtomobili (registrska,znamka,model,vrednost) VALUES (%d, %s, %s, %d); INSERT INTO zavarovanja (stevilka_police, komitent_id, datum_police, premija, tip_zavarovanja) VALUES (%d, %s, %s, %d, %d); INSERT INTO avtomobilska (polica_id, vrsta, avto_id) VALUES (%d,%s,%d);",  (registrska, znamka, model, vrednost, stevilka_police, emso, date.today(), vrednost * 0.05, 2, stevilka_police, vrsta_avto, registrska)) #avtomobilska zavarovanja majo tip 2
        conn.commit()
    except Exception as ex:
        conn.rollback()
        return rtemplate('sklenitev_avtomobilsko.html', stevilka_police=stevilka_police, emso=emso, registrska=registrska, znamka=znamka, model=model, vrednost=vrednost, vrsta_avto=vrsta_avto, napaka='Zgodila se je napaka: %s' % ex)
    redirect("%savtomobilska" %ROOT) 



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