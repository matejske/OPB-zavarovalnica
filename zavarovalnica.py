#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py (bottle je knjiznica funkcij)
from bottle import *
import hashlib # računanje MD5 kriptografski hash za gesla
import inflect

# uvozimo ustrezne podatke za povezavo
import auth_matej as auth

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

# Skrivnost za kodiranje cookijev
secret = "fa1094107c907cw982982c42"

#########################################################################################


def rtemplate(*largs, **kwargs):
    """
    Izpis predloge s podajanjem spremenljivke ROOT z osnovnim URL-jem.
    """
    return template(ROOT=ROOT, *largs, **kwargs)

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

# Pomozne funkcije ======================================================================
def password_md5(s):
    """Vrni MD5 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    if not s:
        # Nočemo imeti praznih nizov za gesla!
        return
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()


# Glavna stran ==========================================================================
@get('/')
def glavna_stran():
    return rtemplate('glavna_stran.html')

@post('/')
def glavna_stran():
    return rtemplate('glavna_stran.html')

# Vse za agente =========================================================================
def get_agent(auto_login=True):
    # Cilj: Na strani za agente moras biti prijavljen, sicer te redirecta na prijavo za agente
    """Poglej cookie in ugotovi, kdo je prijavljeni agent,
       vrni njegov emso, ime in priimek. Če ni prijavljen, presumeri
       na stran za prijavo agenta ali vrni None.
    """
    # Dobimo emso iz piškotka
    agent_emso = request.get_cookie('emso', secret=secret)
    # Preverimo, ali ta agent obstaja
    if agent_emso is not None:
        cur.execute("""
            SELECT emso, ime, priimek FROM osebe WHERE emso=%s
            """, (agent_emso,))
        agent = cur.fetchone()

        if agent is not None:
            # agent obstaja, vrnemo njegove podatke
            return agent
    # Če pridemo do sem, agent ni prijavljen, naredimo redirect
    redirect("{}prijava_agent".format(ROOT))
    """
    if auto_login:
        print('redirectam')
        redirect("{}prijava_agent".format(ROOT))
    else:
        return None
    """

@get("/agent")
def stran_za_agente():
    # Glavna stran za agente.
    # Iz cookieja dobimo emso (ali ga preusmerimo na login, če
    # nima cookija)
    (emso, ime, priimek) = get_agent()
    #print(emso, ime, priimek)

    # Vrnemo predlogo za stran za agente

    return rtemplate("agent.html", napaka=None,
                            emso=emso,
                            ime=ime,
                            priimek=priimek) #,
                            # sporocilo=sporocilo)

@get("/prijava_agent")
def login_agent_get():
    """Serviraj formo za prijavo."""
    return rtemplate("prijava_agent.html",
                           napaka=None,
                           geslo='',
                           emso='')

@post("/prijava_agent")
def login_agent_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    # emso, ki ga je agent vpisal v formo
    emso = request.forms.emso
    # Izračunamo MD5 hash gesla, ki ga bomo spravili
    hash_gesla = password_md5(request.forms.geslo)
    # Preverimo, ali se je uporabnik pravilno prijavil
    cur.execute("SELECT 1 FROM osebe WHERE emso=%s AND geslo=%s", (emso, hash_gesla))

    # # Zaradi probavanja!!!
    # cur.execute("SELECT 1 FROM uporabnik WHERE uporabnisko_ime=%s",
    #           [uporabnik])

    if cur.fetchone() is None:
        # emso in hash_gesla se ne ujemata. Ali pa ta emso sploh ne obstaja.
        return rtemplate("prijava_agent.html",
                            napaka="Nepravilna prijava.",
                            geslo='',
                            emso=emso)

    # Torej emso obstaja. Geslo in emso se ujemata
    # Pogledamo se ali je res zaposlen
    cur.execute("""
            SELECT zaposleni FROM osebe WHERE emso=%s
            """, (emso,))
    zaposlen = cur.fetchone()
    # print(zaposlen, bool(zaposlen)) 'vrne': [True], True, ce je res zaposlen in
    # [False], True, tudi ce sploh ni zaposlen -> moramo dobiti element iz seznama
    # print(zaposlen, zaposlen[0])

    if not zaposlen[0]:
        # emso sploh ni emso agenta
        return rtemplate("prijava_agent.html",
                            napaka="Vstop samo za zaposlene. Izberite prijavo za zavarovance",
                            geslo='',
                            emso=emso)
    else:
        # Vse je v redu, nastavimo cookie, ki potece cez 2 minuti in preusmerimo na stran za agente
        cookie_expires = time.mktime((datetime.now() + timedelta(minutes=2)).timetuple())
        response.set_cookie('emso', emso, path='/', secret=secret, expires=cookie_expires)
        redirect('{0}agent'.format(ROOT))

@get("/odjava_agenta")
def logout():
    """Pobriši cookie in preusmeri na prijavo."""
    response.delete_cookie('emso', path='/')
    redirect('{0}prijava_agent'.format(ROOT))


# zaposlen agent:
# print(password_md5('geslo'))
# password_md5('geslo') = 'ae404a1ecbcdc8e96ae4457790025f50' ..... to je v bazi. Njegovo geslo je 'geslo'
# Smo dali rocno v bazo
# INSERT INTO osebe (emso, ime, priimek, naslov, email, rojstvo, telefon, zaposleni, geslo) VALUES ('000000', 'zaposlen', 'agent', 'ETM1', 'zaposlen.agent@etm.si', '1998-01-01', '000000', TRUE, 'ae404a1ecbcdc8e96ae4457790025f50')
# Obstaja pa tudi nezaposlen z geslom: Super Garfield. EMSO: 0000000, Geslo: lazanja


# Registracija zavarovanca (Agenta je potrebno registrirati rocno v bazi. Ne mores kar na spletni strani??)
@get("/registracija")
def register_get():
    """Prikaži formo za registracijo."""
    return rtemplate('registracija.html', 
                        emso='', 
                        ime='', 
                        priimek='', 
                        naslov='', 
                        email='', 
                        rojstvo='', 
                        telefon='', 
                        zaposleni='FALSE', 
                        napaka=None)


@post("/registracija")
def register_post():
    """Registriraj novega uporabnika."""
    emso = request.forms.emso #ta emso se nanasa na name="emso" v znački input
    ime = request.forms.ime
    priimek = request.forms.priimek
    naslov = request.forms.naslov
    email = request.forms.email
    rojstvo = request.forms.rojstvo
    telefon = request.forms.telefon

    geslo1 = request.forms.geslo1
    geslo2 = request.forms.geslo2


    # Ali uporabnik že obstaja?
    cur.execute("SELECT 1 FROM osebe WHERE emso=%s", (emso,))
    if cur.fetchone():
        # Uporabnik že obstaja
        return rtemplate("registracija.html",
                        emso=emso, 
                        ime=ime, 
                        priimek=priimek, 
                        naslov=naslov, 
                        email=email, 
                        rojstvo=rojstvo, 
                        telefon=telefon, 
                        zaposleni='FALSE',
                        napaka='Oseba s tem EMŠOM je že registrirana.')
    elif not geslo1 == geslo2:
        # Gesli se ne ujemata
        return rtemplate("registracija.html",
                        emso=emso, 
                        ime=ime, 
                        priimek=priimek, 
                        naslov=naslov, 
                        email=email, 
                        rojstvo=rojstvo, 
                        telefon=telefon, 
                        zaposleni='FALSE',
                        napaka='Gesli se ne ujemata.')
    else:
        # Vse je v redu, vstavi novega uporabnika v bazo
        hash_gesla = password_md5(geslo1)
        cur.execute("""
            INSERT INTO osebe (emso, ime, priimek, naslov, email, rojstvo, telefon, zaposleni, geslo) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE, %s)
            """, (emso, ime, priimek, naslov, email, rojstvo, telefon, hash_gesla))
        # Daj uporabniku cookie
        conn.commit()
        response.set_cookie('emso', emso, path='/', secret=secret)
        redirect("{}prijava_zavarovanec".format(ROOT))



















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

"""
Glej pod registracijo 

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
"""

# Sklenitev zavarovanja =============================================================================

# @get('/sklenitev_zavarovanja')
# def sklenitev_zavarovanja():
#     return rtemplate('sklenitev_zavarovanja.html')

# @post('/sklenitev_zavarovanja')
# def sklenitev_zavarovanja():
#     return rtemplate('sklenitev_zavarovanja.html')

# Sklenitev avtomobilskih zavarovanj ============================================================
# S tem get zahtevkom napišemo naj bo že vnešeno v polju (spremenljivka pa je value pri znački input)
@get('/sklenitev_kaskoplus')
def sklenitev_kaskoplus():
    return rtemplate('sklenitev_kaskoplus.html', 
                    registrska='', 
                    znamka='', 
                    model='', 
                    vrednost='', 
                    vrsta_avto='',  
                    napaka=None)


# Pridobimo podatke iz vnosnih polj
@post('/sklenitev_kaskoplus')
def sklenitev_kaskoplus():
    # doda ga v bazo a ne redirecta na koncu
    registrska = request.forms.registrska
    znamka = request.forms.znamka
    model = request.forms.model
    vrednost = request.forms.vrednost
    try:
        cur.execute("""
            INSERT INTO avtomobili (registrska, znamka, model, vrednost) 
            VALUES (%s, %s, %s, %s)
        """, (registrska, znamka, model, vrednost)) 
        cur.execute("""
            INSERT INTO zavarovanja (komitent_id, datum_police, premija, tip_zavarovanja)
            VALUES (%s, %s, %s, %s)
            RETURNING stevilka_police
        """, ('875-23-989', date.today(), float(vrednost) * 0.05, 2))
        stevilka_police, = cur.fetchone()
        #cur.execute("SELECT stevilka_police FROM zavarovanja ORDER BY stevilka_police DESC LIMIT 1")
        #stevilka_police = cur.fetchone()[0]
        cur.execute("""
            INSERT INTO avtomobilska (polica_id, vrsta, avto_id) 
            VALUES (%s, %s, %s)
            """, (stevilka_police, 'kasko +', registrska))
        conn.commit() 

    except Exception as ex:
        conn.rollback()
        return rtemplate('sklenitev_kaskoplus.html', 
                        registrska=registrska, 
                        znamka=znamka, 
                        model=model, 
                        vrednost=vrednost, 
                        napaka='Zgodila se je napaka: {}'.format(ex)) 
    redirect('{}avtomobilska'.format(ROOT))

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