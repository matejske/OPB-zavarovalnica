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

def ime_osebe(emso):
    """ Vrne ime in priimek osebe z EMSOM: emso"""
    cur.execute("""
            SELECT ime, priimek FROM osebe WHERE emso=%s
            """, (emso,))
    oseba = cur.fetchone()
    print(oseba)
    return(oseba)


# Glavna stran ==========================================================================
@get('/')
def glavna_stran():
    return rtemplate('glavna_stran.html')

@post('/')
def glavna_stran():
    return rtemplate('glavna_stran.html')

# Vse za agente =========================================================================
# Ustanovitelji:
# Tomas: Emso: 0000, Geslo: tomas
# INSERT INTO osebe (emso, ime, priimek, naslov, email, rojstvo, telefon, zaposleni, geslo) VALUES ('0000', 'Tomas', 'Rode', 'Komenda', 'tomas.rode@etm.si', '1998-05-07', '1111', TRUE, '4b506c2968184be185f6282f5dcac238')
# Enej: Emso: 1111, Geslo: enej
# INSERT INTO osebe (emso, ime, priimek, naslov, email, rojstvo, telefon, zaposleni, geslo) VALUES ('1111', 'Enej', 'Kovač', 'Bovec', 'enej.kovac@etm.si', '1998-04-02', '1111', TRUE, '05505631a907be702377d263926cab20')
# Matej: Emso: 2222, Geslo: matej
# INSERT INTO osebe (emso, ime, priimek, naslov, email, rojstvo, telefon, zaposleni, geslo) VALUES ('2222', 'Matej', 'Škerlep', 'Črnuče', 'matej.skerlpe@etm.si', '1998-01-01', '1111', TRUE, '485c859f2df22f1147ba3798b4485d48')



# =======================================================================================
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
    redirect("{0}prijava_agent".format(ROOT))
    """
    if auto_login:
        print('redirectam')
        redirect("{}prijava_agent".format(ROOT))
    else:
        return None
    """

@get("/agent/<emso_agenta>")
def stran_agenta(emso_agenta):
    # Glavna stran za agente.
    # Iz cookieja dobimo emso (ali ga preusmerimo na login, če
    # nima cookija)
    (emso, ime, priimek) = get_agent()
    #print(emso, ime, priimek)

    # Vrnemo predlogo za stran za agente

    return rtemplate("agent.html", napaka=None,
                            emso=emso,
                            ime_agenta=ime,
                            priimek_agenta=priimek) #,
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
        cookie_expires = time.mktime((datetime.now() + timedelta(minutes=3)).timetuple())
        response.set_cookie('emso', emso, path='/', secret=secret, expires=cookie_expires)
        redirect('{0}agent/{1}'.format(ROOT, emso))

@get("/odjava_agent/<emso_agenta>")
def odajava(emso_agenta):
    """Pobriši cookie in preusmeri na prijavo."""
    response.delete_cookie('emso', path='/')
    redirect('{0}prijava_agent'.format(ROOT))


# zaposlen agent:
# print(password_md5('geslo'))
# password_md5('geslo') = 'ae404a1ecbcdc8e96ae4457790025f50' ..... to je v bazi. Njegovo geslo je 'geslo'
# Smo dali rocno v bazo
# INSERT INTO osebe (emso, ime, priimek, naslov, email, rojstvo, telefon, zaposleni, geslo) VALUES ('000000', 'zaposlen', 'agent', 'ETM1', 'zaposlen.agent@etm.si', '1998-01-01', '000000', TRUE, 'ae404a1ecbcdc8e96ae4457790025f50')
# Obstaja pa tudi nezaposlen z geslom. Ime in priimek: Super Garfield. EMSO: 0000000, Geslo: lazanja

# Dodajanje novega komitenta na strani za agente ======================================================================
# Agent ga lahko doda brez potrebe po geslu. Komitent ne rabi racuna za spletno poslovalnico.
@get("/agent/<emso_agenta>/dodaj_komitenta")
def dodaj_komitenta_get(emso_agenta):
    """Prikaži formo za dodajanje novega komitenta."""
    (emso_ag, ime_ag, priimek_ag) = get_agent()
    return rtemplate('dodaj_komitenta.html', 
                        emso_komitenta='', 
                        ime='', 
                        priimek='', 
                        naslov='', 
                        email='', 
                        rojstvo='', 
                        telefon='', 
                        zaposleni='FALSE', 
                        emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                        ime_agenta=ime_ag,
                        priimek_agenta=priimek_ag,
                        napaka=None)


@post("/agent/<emso_agenta>/dodaj_komitenta")
def dodaj_komitenta_post(emso_agenta):
    """Dodaj novega komitenta."""
    emso_komitenta = request.forms.emso_komitenta #ta emso se nanasa na name="emso" v znački input
    ime = request.forms.ime
    priimek = request.forms.priimek
    naslov = request.forms.naslov
    email = request.forms.email
    rojstvo = request.forms.rojstvo
    telefon = request.forms.telefon

    # Ali komitent že obstaja?
    cur.execute("SELECT 1 FROM osebe WHERE emso=%s", (emso_komitenta,))
    if cur.fetchone():
        # komitent že obstaja
        return rtemplate("dodaj_komitenta.html",
                        emso_komitenta=emso_komitenta, 
                        ime=ime, 
                        priimek=priimek, 
                        naslov=naslov, 
                        email=email, 
                        rojstvo=rojstvo, 
                        telefon=telefon, 
                        zaposleni='FALSE',
                        napaka='Oseba s tem EMŠOM je že registrirana.')
    else:
        # Vse je v redu, vstavi novega uporabnika v bazo
        cur.execute("""
            INSERT INTO osebe (emso, ime, priimek, naslov, email, rojstvo, telefon, zaposleni) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)
            """, (emso_komitenta, ime, priimek, naslov, email, rojstvo, telefon))

        # Dodaj v tabelo in preusmeri na domačo stran agenta
        conn.commit()
        redirect("{0}agent/{1}/osebe".format(ROOT, emso_agenta))

# Sklenitev novih zavarovanj preko agenta =============================================================================
@get('/agent/<emso_agenta>/skleni_avtomobilsko')
def skleni_avtomobilsko(emso_agenta):
    """ Prikaži formo za dodajanje novega avtomobilskega zavarovanja """
    # Podatki komitenta
    emso_komitenta = request.forms.emso_komitenta #ta emso se nanasa na name="emso" v znački input
    ime = request.forms.ime
    priimek = request.forms.priimek
    naslov = request.forms.naslov
    email = request.forms.email
    rojstvo = request.forms.rojstvo
    telefon = request.forms.telefon

    # vrsta zavarovanja in registrska
    vrsta_avtomobilskega = request.forms.vrsta_avtomobilskega
    registrska = request.forms.registrska
    premija = request.forms.premija

    (emso_ag, ime_ag, priimek_ag) = get_agent()
    return rtemplate('agent_avtomobilsko.html', 
                        emso_komitenta='', 
                        ime='', 
                        priimek='', 
                        naslov='', 
                        email='', 
                        rojstvo='', 
                        telefon='', 
                        zaposleni='FALSE', 
                        vrsta_avtomobilskega='',
                        registrska='',
                        premija=premija,
                        emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                        ime_agenta=ime_ag,
                        priimek_agenta=priimek_ag,
                        napaka=None)


@post('/agent/<emso_agenta>/skleni_avtomobilsko')

# Podstrani za vsako tabelo iz baze, ki jih lahko vidi le agent =======================================================
@get('/agent/<emso_agenta>/osebe')
def osebe(emso_agenta):
    cur.execute("SELECT * FROM Osebe")
    (emso, ime, priimek) = get_agent()
    return rtemplate('osebe.html', napaka=None,
                        osebe=cur,
                        emso=emso,
                        ime_agenta=ime,
                        priimek_agenta=priimek)

@get('/agent/<emso_agenta>/zavarovanja')
def zavarovanja(emso_agenta):
    cur.execute("SELECT * FROM zavarovanja")
    (emso, ime, priimek) = get_agent()
    return rtemplate('zavarovanja.html', napaka=None,
                        zavarovanja=cur,
                        emso=emso,
                        ime_agenta=ime,
                        priimek_agenta=priimek)

@get('/agent/<emso_agenta>/nepremicnine')
def nepremicnine(emso_agenta):
    cur.execute("SELECT * FROM nepremicnine")
    (emso, ime, priimek) = get_agent()
    return rtemplate('nepremicnine.html', napaka=None,
                        nepremicnine=cur,
                        emso=emso,
                        ime_agenta=ime,
                        priimek_agenta=priimek)

@get('/agent/<emso_agenta>/nepremicninska')
def nepremicninska(emso_agenta):
    cur.execute("SELECT * FROM nepremicninska")
    (emso, ime, priimek) = get_agent()
    return rtemplate('nepremicninska.html', napaka=None,
                        nepremicninska=cur,
                        emso=emso,
                        ime_agenta=ime,
                        priimek_agenta=priimek)

@get('/agent/<emso_agenta>/vrste_nepr')
def vrste_avto(emso_agenta):
    cur.execute("SELECT * FROM Mozne_vrste_nepr_tb")
    (emso, ime, priimek) = get_agent()
    return rtemplate('vrste_nepr.html', napaka=None,
                        Mozne_vrste_nepr_tb=cur,
                        emso=emso,
                        ime_agenta=ime,
                        priimek_agenta=priimek)

@get('/agent/<emso_agenta>/avtomobili')
def avtomobili(emso_agenta):
    cur.execute("SELECT * FROM avtomobili")
    (emso, ime, priimek) = get_agent()
    return rtemplate('avtomobili.html', napaka=None,
                        avtomobili=cur,
                        emso=emso,
                        ime_agenta=ime,
                        priimek_agenta=priimek)

@get('/agent/<emso_agenta>/avtomobilska')
def avtomobilska(emso_agenta):
    cur.execute("SELECT * FROM avtomobilska")
    (emso, ime, priimek) = get_agent()
    return rtemplate('avtomobilska.html', napaka=None,
                        avtomobilska=cur,
                        emso=emso,
                        ime_agenta=ime,
                        priimek_agenta=priimek)

@get('/agent/<emso_agenta>/vrste_avto')
def vrste_avto(emso_agenta):
    cur.execute("SELECT * FROM Mozne_vrste_avto_tb")
    (emso, ime, priimek) = get_agent()
    return rtemplate('vrste_avto.html', napaka=None,
                        Mozne_vrste_avto_tb=cur,
                        emso=emso,
                        ime_agenta=ime,
                        priimek_agenta=priimek)

@get('/agent/<emso_agenta>/zivljenjska')
def zivljenjska(emso_agenta):
    cur.execute("SELECT * FROM zivljenska")
    (emso, ime, priimek) = get_agent()
    return rtemplate('zivljenjska.html', napaka=None,
                        zivljenjska=cur,
                        emso=emso,
                        ime_agenta=ime,
                        priimek_agenta=priimek)

@get('/agent/<emso_agenta>/vrste_zivlj')
def vrste_zivlj(emso_agenta):
    cur.execute("SELECT * FROM Mozne_vrste_zivlj_tb")
    (emso, ime, priimek) = get_agent()
    return rtemplate('vrste_zivlj.html', napaka=None,
                        Mozne_vrste_zivlj_tb=cur,
                        emso=emso,
                        ime_agenta=ime,
                        priimek_agenta=priimek)


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


    # Ali je oseba s tem EMŠOM že registrirana?
    cur.execute("SELECT 1 FROM osebe WHERE emso=%s", (emso,))
    if cur.fetchone():
        # oseba je že registrirana
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