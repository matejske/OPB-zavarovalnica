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

def vrednost_nepremicnine(naslov_nepr):
    """ Vrne vrednost nepremicnine na danem naslovu """
    cur.execute("""
            SELECT vrednost FROM nepremicnine WHERE naslov_nepr=%s
            """, (naslov_nepr,))
    vrednost = cur.fetchone()
    return(vrednost[0]) # da vrne prvi element seznama

def vrednost_avtomobila(registrska):
    """ Vrne vrednost avtomobila z dano registrsko"""
    cur.execute("""
            SELECT vrednost FROM avtomobili WHERE registrska=%s
            """, (registrska,))
    vrednost = cur.fetchone()
    return(vrednost[0]) # da vrne prvi element seznama

def starost_osebe(emso):
    """Vrne starost zavarovanca z danim EMŠOm"""
    cur.execute("SELECT rojstvo FROM osebe WHERE emso=%s", (emso,))
    datum_rojstva = cur.fetchone()[0]
    razlika = date.today() - datum_rojstva
    return(razlika.days)


def doloci_premijo_avtomobilskega(vrsta, vrednost_vozila):
    # vrsta je 'kasko', 'kasko +' ali 'avtomobilska asistenca'
    # za 'kasko' damo 5% vrednosti vozila,
    # za 'kasko +' 8%,
    # za 'avtomobilsko asistenco' pa 100€.
    if vrsta == 'kasko':
        return(0.05 * float(vrednost_vozila))
    elif vrsta == 'kasko +':
        return(0.08 * float(vrednost_vozila))
    elif vrsta == 'avtomobilska asistenca':
        return(100)

def doloci_premijo_nepremicninskega(vrsta, vrednost_nepremicnine):
    if vrsta == 'pozar':
        return(0.01 * float(vrednost_nepremicnine))
    elif vrsta == 'potres':
        return(0.0005 * float(vrednost_nepremicnine))
    elif vrsta == 'poplava':
        return(0.001 * float(vrednost_nepremicnine))

def doloci_premijo_zivljenjskega(vrsta, starost_osebe):
    if vrsta == 'pokojninsko':
        return(0.01 * int(starost_osebe))
    elif vrsta == 'invalidsko':
        return(0.005 * int(starost_osebe))
    elif vrsta == 'za primer brezposelnosti':
        return(0.008 * int(starost_osebe))
    elif vrsta == 'za primer smrti':
        return(0.02 * int(starost_osebe))

# Glavna stran ==========================================================================
@get('/')
def glavna_stran():
    """Pobriši cookie."""
    response.delete_cookie('emso', path='/')

    return rtemplate('glavna_stran.html')

@post('/')
def glavna_stran():
    return rtemplate('glavna_stran.html')

# Stran za testiranje ==========================================================================
@get('/testi')
def testi():
    return rtemplate('testi.html')

@post('/testi')
def testi():
    return rtemplate('testi.html')

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

# Stran o zaposlenih ==========================================================================
@get('/zaposleni')
def zaposleni():
    return rtemplate('zaposleni.html')

@post('/zaposleni')
def zaposleni():
    return rtemplate('zaposleni.html')

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#####################################################   Agenti  #######################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################



# Ustanovitelji:
# Tomas: Emso: 0000, Geslo: tomas
# INSERT INTO osebe (emso, ime, priimek, naslov, email, rojstvo, telefon, zaposleni, geslo) VALUES ('0000', 'Tomas', 'Rode', 'Komenda', 'tomas.rode@etm.si', '1998-05-07', '1111', TRUE, '4b506c2968184be185f6282f5dcac238')
# Enej: Emso: 1111, Geslo: enej
# INSERT INTO osebe (emso, ime, priimek, naslov, email, rojstvo, telefon, zaposleni, geslo) VALUES ('1111', 'Enej', 'Kovač', 'Bovec', 'enej.kovac@etm.si', '1998-04-02', '1111', TRUE, '05505631a907be702377d263926cab20')
# Matej: Emso: 2222, Geslo: matej
# INSERT INTO osebe (emso, ime, priimek, naslov, email, rojstvo, telefon, zaposleni, geslo) VALUES ('2222', 'Matej', 'Škerlep', 'Črnuče', 'matej.skerlpe@etm.si', '1998-01-01', '1111', TRUE, '485c859f2df22f1147ba3798b4485d48')


################################ Prijava, odjava in še kaj o agentih ##################################################


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
        # print(agent, agent[0]) vrne ['1111', 'Enej', 'Kovač'] 1111
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
        # Vse je v redu, nastavimo cookie, ki potece cez 15 minut in preusmerimo na stran za agente
        cookie_expires = time.mktime((datetime.now() + timedelta(minutes=15)).timetuple())
        response.set_cookie('emso', emso, path='/', secret=secret, expires=cookie_expires)
        redirect('{0}agent/{1}'.format(ROOT, emso))

@get("/odjava_agent/<emso_agenta>")
def odjava(emso_agenta):
    """Pobriši cookie in preusmeri na prijavo."""
    response.delete_cookie('emso', path='/')
    redirect('{0}prijava_agent'.format(ROOT))


# zaposlen agent:
# print(password_md5('geslo'))
# password_md5('geslo') = 'ae404a1ecbcdc8e96ae4457790025f50' ..... to je v bazi. Njegovo geslo je 'geslo'
# Smo dali rocno v bazo
# INSERT INTO osebe (emso, ime, priimek, naslov, email, rojstvo, telefon, zaposleni, geslo) VALUES ('000000', 'zaposlen', 'agent', 'ETM1', 'zaposlen.agent@etm.si', '1998-01-01', '000000', TRUE, 'ae404a1ecbcdc8e96ae4457790025f50')
# Obstaja pa tudi nezaposlen z geslom. Ime in priimek: Super Garfield. EMSO: 0000000, Geslo: lazanja

############################## Osebni podatki - agent ###############################################
@get('/agent/<emso_agenta>/osebni_podatki')
def osebni_podatki_agent(emso_agenta):
    (emso_ag, ime_ag, priimek_ag) = get_agent()

    cur.execute("""
    SELECT ime, priimek, naslov, email, rojstvo, telefon
    FROM osebe 
    WHERE emso=%s
    """, (emso_agenta,))
    (ime, priimek, naslov, email, rojstvo, telefon) = cur.fetchone()

    return rtemplate('agent_osebni_podatki.html',
                    ime=ime,
                    priimek=priimek,
                    naslov=naslov,
                    email=email,
                    rojstvo=rojstvo,
                    telefon=telefon,
                    emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                    ime_agenta=ime_ag,
                    priimek_agenta=priimek_ag, 
                    napaka=None)

######## Dodajanje oseb, nepremičnin in avtomobilov v podatkovno bazo na strani za agente #############################


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
        (emso_ag, ime_ag, priimek_ag) = get_agent()
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
                        emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                        ime_agenta=ime_ag,
                        priimek_agenta=priimek_ag,
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

# Dodajanje nove nepremičnine na strani za agente =====================================================================
@get("/agent/<emso_agenta>/dodaj_nepremicnino")
def dodaj_nepremicnino_get(emso_agenta):
    """Prikaži formo za dodajanje nove nepremičnine."""
    (emso_ag, ime_ag, priimek_ag) = get_agent()
    return rtemplate('dodaj_nepremicnino.html', 
                        naslov='', 
                        vrednost='',
                        emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                        ime_agenta=ime_ag,
                        priimek_agenta=priimek_ag,
                        napaka=None)


@post("/agent/<emso_agenta>/dodaj_nepremicnino")
def dodaj_nepremicnino_post(emso_agenta):
    """Dodaj novo nepremičnino."""
    naslov = request.forms.naslov 
    vrednost = request.forms.vrednost

    # Ali komitent že obstaja?
    cur.execute("SELECT 1 FROM nepremicnine WHERE naslov_nepr=%s", (naslov,))
    if cur.fetchone():
        (emso_ag, ime_ag, priimek_ag) = get_agent()
        # nepremicnina na tem naslovu že obstaja
        return rtemplate("dodaj_nepremicnino.html",
                        naslov=naslov, 
                        vrednost=vrednost,
                        emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                        ime_agenta=ime_ag,
                        priimek_agenta=priimek_ag, 
                        napaka='Nepremičnina na tem naslovu je že v bazi.')
    else:
        # Vse je v redu, vstavi novo nepremicnino v bazo
        cur.execute("""
            INSERT INTO nepremicnine (naslov_nepr, vrednost) 
            VALUES (%s, %s)
            """, (naslov, vrednost))

        # Dodaj v tabelo in preusmeri na domačo stran agenta
        conn.commit()
        redirect("{0}agent/{1}/nepremicnine".format(ROOT, emso_agenta))


# Dodajanje novega avtomobila na strani za agente =====================================================================
@get("/agent/<emso_agenta>/dodaj_avtomobil")
def dodaj_avtomobil_get(emso_agenta):
    """Prikaži formo za dodajanje novega avtomobila."""
    (emso_ag, ime_ag, priimek_ag) = get_agent()
    return rtemplate('dodaj_avtomobil.html', 
                        registrska='', 
                        znamka='',
                        model='',
                        vrednost='',
                        emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                        ime_agenta=ime_ag,
                        priimek_agenta=priimek_ag,
                        napaka=None)


@post("/agent/<emso_agenta>/dodaj_avtomobil")
def dodaj_avtomobil_post(emso_agenta):
    """Dodaj nov avtomobil."""
    registrska = request.forms.registrska 
    znamka = request.forms.znamka
    model = request.forms.model 
    vrednost = request.forms.vrednost

    # Ali komitent že obstaja?
    cur.execute("SELECT 1 FROM avtomobili WHERE registrska=%s", (registrska,))
    if cur.fetchone():
        (emso_ag, ime_ag, priimek_ag) = get_agent()
        # nepremicnina na tem naslovu že obstaja
        return rtemplate("dodaj_avtomobil.html",
                        registrska=registrska, 
                        znamka=znamka,
                        model=model,
                        vrednost=vrednost,
                        emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                        ime_agenta=ime_ag,
                        priimek_agenta=priimek_ag, 
                        napaka='Avtomobil s to registrsko je že v bazi.')
    else:
        # Vse je v redu, vstavi novo nepremicnino v bazo
        cur.execute("""
            INSERT INTO avtomobili (registrska, znamka, model, vrednost) 
            VALUES (%s, %s, %s, %s)
            """, (registrska, znamka, model, vrednost))

        # Dodaj v tabelo in preusmeri na domačo stran agenta
        conn.commit()
        redirect("{0}agent/{1}/avtomobili".format(ROOT, emso_agenta))


################################# Sklenitev novih zavarovanj na strani za agente ######################################


# Sklenitev avtomobilskih zavarovanj preko agenta =============================================================================
@get('/agent/<emso_agenta>/skleni_avtomobilsko')
def agent_skleni_avtomobilsko_get(emso_agenta):
    """ Prikaži formo za dodajanje novega avtomobilskega zavarovanja """
    (emso_ag, ime_ag, priimek_ag) = get_agent()
    return rtemplate('agent_skleni_avtomobilsko.html', 
                        emso_komitenta='',
                        vrsta_avtomobilskega='',
                        registrska='',
                        znamka='',
                        model='',
                        vrednost='',
                        premija='', 
                        emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                        ime_agenta=ime_ag,
                        priimek_agenta=priimek_ag, 
                        napaka=None)


@post('/agent/<emso_agenta>/skleni_avtomobilsko')
def agent_skleni_avtomobilsko_post(emso_agenta):
    emso_komitenta = request.forms.emso_komitenta
    vrsta_avtomobilskega = request.forms.vrsta_avtomobilskega
    registrska = request.forms.registrska
    znamka = request.forms.znamka
    model = request.forms.model
    vrednost = request.forms.vrednost
    premija = request.forms.premija

    # Dobimo podatke agenta, ki sklepa zavarovanje
    (emso_ag, ime_ag, priimek_ag) = get_agent()

    # Ali je komitent s tem emsom sploh v bazi?
    cur.execute("SELECT 1 FROM osebe WHERE emso=%s", (emso_komitenta,))
    if cur.fetchone() is None:
        # Ni ga še v bazi.
        
        return rtemplate("agent_skleni_avtomobilsko.html",
                        emso_komitenta='',
                        vrsta_avtomobilskega=vrsta_avtomobilskega,
                        registrska=registrska,
                        znamka=znamka,
                        model=model,
                        vrednost=vrednost,
                        premija=premija, 
                        emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                        ime_agenta=ime_ag,
                        priimek_agenta=priimek_ag, 
                        napaka='Oseba s tem Emšom še ni v bazi.')

    # Ali je registrska že v bazi?
    cur.execute("SELECT 1 FROM avtomobili WHERE registrska=%s", (registrska,))
    if cur.fetchone() is not None:
        # Avto je že v bazi. Vstavimo le zavarovalno polico in ne avtomobila
        try:
            # Odstraniti je bilo treba UNIQE constraint v tabeli avtomobilska na stolpcu avto_id,
            # da ima lahko isti avto več zavarovanj
            cur.execute("""
                INSERT INTO zavarovanja (komitent_id, datum_police, premija, tip_zavarovanja)
                VALUES (%s, %s, %s, %s)
                RETURNING stevilka_police
            """, (emso_komitenta, date.today(), premija, 2)) # 2 je za avtomobilsko
            stevilka_police, = cur.fetchone()
            #cur.execute("SELECT stevilka_police FROM zavarovanja ORDER BY stevilka_police DESC LIMIT 1")
            #stevilka_police = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO avtomobilska (polica_id, vrsta, avto_id) 
                VALUES (%s, %s, %s)
                """, (stevilka_police, vrsta_avtomobilskega, registrska))
            conn.commit() 

        except Exception as ex:
            conn.rollback()
            return rtemplate('agent_skleni_avtomobilsko.html', 
                            emso_komitenta=emso_komitenta,
                            vrsta_avtomobilskega=vrsta_avtomobilskega,
                            registrska=registrska, 
                            znamka=znamka, 
                            model=model, 
                            vrednost=vrednost, 
                            premija=premija, 
                            emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                            ime_agenta=ime_ag,
                            priimek_agenta=priimek_ag, 
                            napaka='Zgodila se je napaka: {}'.format(ex)) 

        redirect('{0}agent/{1}/avtomobilska'.format(ROOT, emso_agenta))

    # Sicer pa vstavimo v bazo novo polico in še avtomobil
    try:
        cur.execute("""
            INSERT INTO avtomobili (registrska, znamka, model, vrednost) 
            VALUES (%s, %s, %s, %s)
        """, (registrska, znamka, model, vrednost)) 
        cur.execute("""
            INSERT INTO zavarovanja (komitent_id, datum_police, premija, tip_zavarovanja)
            VALUES (%s, %s, %s, %s)
            RETURNING stevilka_police
        """, (emso_komitenta, date.today(), premija, 2)) # 2 je za avtomobilsko
        stevilka_police, = cur.fetchone()
        #cur.execute("SELECT stevilka_police FROM zavarovanja ORDER BY stevilka_police DESC LIMIT 1")
        #stevilka_police = cur.fetchone()[0]
        cur.execute("""
            INSERT INTO avtomobilska (polica_id, vrsta, avto_id) 
            VALUES (%s, %s, %s)
            """, (stevilka_police, vrsta_avtomobilskega, registrska))
        conn.commit() 

    except Exception as ex:
        conn.rollback()
        return rtemplate('agent_skleni_avtomobilsko.html', 
                        emso_komitenta=emso_komitenta,
                        vrsta_avtomobilskega=vrsta_avtomobilskega,
                        registrska=registrska, 
                        znamka=znamka, 
                        model=model, 
                        vrednost=vrednost, 
                        premija=premija, 
                        emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                        ime_agenta=ime_ag,
                        priimek_agenta=priimek_ag, 
                        napaka='Zgodila se je napaka: {0}'.format(ex)) 

    redirect('{0}agent/{1}/avtomobilska'.format(ROOT, emso_agenta))
    
# Sklenitev nepremicninskih zavarovanj preko agenta ===================================================================
@get('/agent/<emso_agenta>/skleni_nepremicninsko')
def agent_skleni_nepremicninsko_get(emso_agenta):
    """ Prikaži formo za dodajanje novega nepremicninskega zavarovanja """
    (emso_ag, ime_ag, priimek_ag) = get_agent()
    return rtemplate('agent_skleni_nepremicninsko.html', 
                        emso_komitenta='',
                        vrsta_nepremicninskega='',
                        naslov_nepr='',
                        vrednost='',
                        premija='', 
                        emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                        ime_agenta=ime_ag,
                        priimek_agenta=priimek_ag, 
                        napaka=None)


@post('/agent/<emso_agenta>/skleni_nepremicninsko')
def agent_skleni_nepremicninsko_post(emso_agenta):
    emso_komitenta = request.forms.emso_komitenta
    vrsta_nepremicninskega = request.forms.vrsta_nepremicninskega
    naslov_nepr = request.forms.naslov_nepr
    vrednost = request.forms.vrednost
    premija = request.forms.premija

    # Dobimo podatke agenta, ki sklepa zavarovanje
    (emso_ag, ime_ag, priimek_ag) = get_agent()

    # Ali je komitent s tem emsom sploh v bazi?
    cur.execute("SELECT 1 FROM osebe WHERE emso=%s", (emso_komitenta,))
    if cur.fetchone() is None:
        # Ni ga še v bazi.
        
        return rtemplate("agent_skleni_avtomobilsko.html",
                        emso_komitenta='',
                        vrsta_nepremicninskega=vrsta_nepremicninskega,
                        naslov_nepr=naslov_nepr,
                        vrednost=vrednost,
                        premija=premija, 
                        emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                        ime_agenta=ime_ag,
                        priimek_agenta=priimek_ag, 
                        napaka='Oseba s tem Emšom še ni v bazi.')

    # Ali je naslov nepremičnine že že v bazi?
    cur.execute("SELECT 1 FROM nepremicnine WHERE naslov_nepr=%s", (naslov_nepr,))
    if cur.fetchone() is not None:
        # Nepremičnina je že v bazi. Vstavimo le zavarovalno polico in ne naslova
        try:
            # Odstraniti je bilo treba UNIQE constraint v tabeli nepremicnine na stolpcu nepr_id,
            # da ima lahko ista nepremičnina več zavarovanj
            cur.execute("""
                INSERT INTO zavarovanja (komitent_id, datum_police, premija, tip_zavarovanja)
                VALUES (%s, %s, %s, %s)
                RETURNING stevilka_police
            """, (emso_komitenta, date.today(), premija, 3)) # 3 je za nepremičninsko
            stevilka_police, = cur.fetchone()
            #cur.execute("SELECT stevilka_police FROM zavarovanja ORDER BY stevilka_police DESC LIMIT 1")
            #stevilka_police = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO nepremicninska (polica_id, nepr_id, vrsta_n) 
                VALUES (%s, %s, %s)
                """, (stevilka_police, naslov_nepr, vrsta_nepremicninskega))
            conn.commit() 

        except Exception as ex:
            conn.rollback()
            return rtemplate('agent_skleni_nepremicninsko.html', 
                            emso_komitenta=emso_komitenta,
                            vrsta_nepremicninskega=vrsta_nepremicninskega,
                            naslov_nepr=naslov_nepr, 
                            vrednost=vrednost, 
                            premija=premija, 
                            emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                            ime_agenta=ime_ag,
                            priimek_agenta=priimek_ag, 
                            napaka='Zgodila se je napaka: {}'.format(ex)) 

        redirect('{0}agent/{1}/nepremicninska'.format(ROOT, emso_agenta))

    # Sicer pa vstavimo v bazo novo polico in še nepremičnino
    try:
        cur.execute("""
            INSERT INTO nepremicnine (naslov_nepr, vrednost) 
            VALUES (%s, %s)
        """, (naslov_nepr, vrednost)) 
        cur.execute("""
                INSERT INTO zavarovanja (komitent_id, datum_police, premija, tip_zavarovanja)
                VALUES (%s, %s, %s, %s)
                RETURNING stevilka_police
            """, (emso_komitenta, date.today(), premija, 3)) # 3 je za nepremičninsko
        stevilka_police, = cur.fetchone()
        #cur.execute("SELECT stevilka_police FROM zavarovanja ORDER BY stevilka_police DESC LIMIT 1")
        #stevilka_police = cur.fetchone()[0]
        cur.execute("""
            INSERT INTO nepremicninska (polica_id, nepr_id, vrsta_n) 
            VALUES (%s, %s, %s)
            """, (stevilka_police, naslov_nepr, vrsta_nepremicninskega))
        conn.commit() 

    except Exception as ex:
        conn.rollback()
        return rtemplate('agent_skleni_nepremicninsko.html', 
                        emso_komitenta=emso_komitenta,
                        vrsta_nepremicninskega=vrsta_nepremicninskega,
                        naslov_nepr=naslov_nepr, 
                        vrednost=vrednost, 
                        premija=premija, 
                        emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                        ime_agenta=ime_ag,
                        priimek_agenta=priimek_ag, 
                        napaka='Zgodila se je napaka: {0}'.format(ex)) 

    redirect('{0}agent/{1}/nepremicninska'.format(ROOT, emso_agenta))

# Sklenitev zivljenskih zavarovanj preko agenta =======================================================================
@get('/agent/<emso_agenta>/skleni_zivljenjsko')
def agent_skleni_zivljenjsko_get(emso_agenta):
    """ Prikaži formo za dodajanje novega življenjskega zavarovanja """
    (emso_ag, ime_ag, priimek_ag) = get_agent()
    return rtemplate('agent_skleni_zivljenjsko.html', 
                        emso_komitenta='',
                        vrsta_zivljenjskega='',
                        premija='', 
                        emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                        ime_agenta=ime_ag,
                        priimek_agenta=priimek_ag, 
                        napaka=None)


@post('/agent/<emso_agenta>/skleni_zivljenjsko')
def agent_skleni_zivljenjsko_post(emso_agenta):
    emso_komitenta = request.forms.emso_komitenta
    vrsta_zivljenjskega = request.forms.vrsta_zivljenjskega
    premija = request.forms.premija

    # Dobimo podatke agenta, ki sklepa zavarovanje
    (emso_ag, ime_ag, priimek_ag) = get_agent()

    # Ali je komitent s tem emsom sploh v bazi?
    cur.execute("SELECT 1 FROM osebe WHERE emso=%s", (emso_komitenta,))
    if cur.fetchone() is None:
        # Ni ga še v bazi.
        
        return rtemplate("agent_skleni_zivljenjsko.html",
                        emso_komitenta='',
                        vrsta_zivljenjskega=vrsta_zivljenjskega,
                        premija=premija, 
                        emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                        ime_agenta=ime_ag,
                        priimek_agenta=priimek_ag, 
                        napaka='Oseba s tem Emšom še ni v bazi.')

    # Vstavimo v bazo novo polico 
    try:
        cur.execute("""
            INSERT INTO zavarovanja (komitent_id, datum_police, premija, tip_zavarovanja)
            VALUES (%s, %s, %s, %s)
            RETURNING stevilka_police
        """, (emso_komitenta, date.today(), premija, 1)) # 1 je za življenjsko
        stevilka_police, = cur.fetchone()
        #cur.execute("SELECT stevilka_police FROM zavarovanja ORDER BY stevilka_police DESC LIMIT 1")
        #stevilka_police = cur.fetchone()[0]
        # tabela zivljenska ... slovnicno je zivljenjska
        cur.execute("""
            INSERT INTO zivljenska (polica_id, vrsta_zivlj) 
            VALUES (%s, %s)
            """, (stevilka_police, vrsta_zivljenjskega))
        conn.commit() 

    except Exception as ex:
        conn.rollback()
        return rtemplate('agent_skleni_zivljenjsko.html', 
                        emso_komitenta=emso_komitenta,
                        vrsta_zivljenjskega=vrsta_zivljenjskega, 
                        premija=premija, 
                        emso=emso_ag, # emso od agenta, ker rabimo v agent_osnova, da se izpiše kdo je prijavljen
                        ime_agenta=ime_ag,
                        priimek_agenta=priimek_ag, 
                        napaka='Zgodila se je napaka: {0}'.format(ex)) 

    redirect('{0}agent/{1}/zivljenjska'.format(ROOT, emso_agenta))


#########################################    Podatkovna baza za agente    #############################################


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


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
################################################   Zavarovanci    #####################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


# Registracija zavarovanca (Agenta je potrebno registrirati rocno v bazi.)

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
        redirect("{0}prijava_zavarovanec".format(ROOT))

# Primeri zavarovancev:
# Tomas: Emso: 000, Geslo: tomas
# INSERT INTO osebe (emso, ime, priimek, naslov, email, rojstvo, telefon, zaposleni, geslo) VALUES ('000', 'Tomas', 'Rode', 'Komenda', 'tomas.rode@etm.si', '1998-05-07', '1111', FALSE, '4b506c2968184be185f6282f5dcac238')
# Enej: Emso: 111, Geslo: enej
# INSERT INTO osebe (emso, ime, priimek, naslov, email, rojstvo, telefon, zaposleni, geslo) VALUES ('111', 'Enej', 'Kovač', 'Bovec', 'enej.kovac@etm.si', '1998-04-02', '1111', FALSE, '05505631a907be702377d263926cab20')
# Matej: Emso: 222, Geslo: matej
# INSERT INTO osebe (emso, ime, priimek, naslov, email, rojstvo, telefon, zaposleni, geslo) VALUES ('222', 'Matej', 'Škerlep', 'Črnuče', 'matej.skerlpe@etm.si', '1998-01-01', '1111', FALSE, '485c859f2df22f1147ba3798b4485d48')


################################ Prijava, odjava in še kaj o zavarovancih ##################################################


# =======================================================================================
def get_zavarovanec(auto_login=True):
    # Cilj: Na strani za zavarovance moras biti prijavljen, sicer te redirecta na prijavo za zavarovance
    """Poglej cookie in ugotovi, kdo je prijavljeni zavarovanec,
       vrni njegov emso, ime in priimek. Če ni prijavljen, presumeri
       na stran za prijavo zavarovanca ali vrni None.
    """
    # Dobimo emso iz piškotka
    emso = request.get_cookie('emso', secret=secret)
    # Preverimo, ali ta zavarovanec obstaja
    if emso is not None:
        cur.execute("""
            SELECT emso, ime, priimek FROM osebe WHERE emso=%s
            """, (emso,))
        zavarovanec = cur.fetchone()
        # print(zavarovanec, zavarovanec[0]) vrne ['111', 'Enej', 'Kovač'] 111
        if zavarovanec is not None:
            # zavarovanec obstaja, vrnemo njegove podatke
            return zavarovanec
    # Če pridemo do sem, zavarovanec ni prijavljen, naredimo redirect
    redirect("{0}prijava_zavarovanec".format(ROOT))
    """
    if auto_login:
        print('redirectam')
        redirect("{}prijava_zavarovanec".format(ROOT))
    else:
        return None
    """
#def podatki_avta(registrska):

@get("/zavarovanec/<emso_zavarovanca>")
def stran_zavarovanca(emso_zavarovanca):
    # Glavna stran za zavarovance.
    # Iz cookieja dobimo emso (ali ga preusmerimo na login, če
    # nima cookija)
    (emso, ime, priimek) = get_zavarovanec()
    #print(emso, ime, priimek)

    # Vrnemo predlogo za stran za zavarovance

    return rtemplate("zavarovanec.html", napaka=None,
                            emso=emso,
                            ime_zavarovanca=ime,
                            priimek_zavarovanca=priimek) #,
                            # sporocilo=sporocilo)

@get("/prijava_zavarovanec")
def login_zavarovanec_get():
    """Serviraj formo za prijavo."""
    return rtemplate("prijava_zavarovanec.html",
                           napaka=None,
                           geslo='',
                           emso='')

@post("/prijava_zavarovanec")
def login_zavarovanec_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    # emso, ki ga je zavarovanec vpisal v formo
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
        return rtemplate("prijava_zavarovanec.html",
                            napaka="Nepravilna prijava.",
                            geslo='',
                            emso=emso)

    # Emso obstaja. Geslo in emso se ujemata.
    else:
        # Vse je v redu, nastavimo cookie, ki potece cez ... časa in preusmerimo na stran za zavarovance
        cookie_expires = time.mktime((datetime.now() + timedelta(minutes=10)).timetuple())
        response.set_cookie('emso', emso, path='/', secret=secret, expires=cookie_expires)
        redirect('{0}zavarovanec/{1}'.format(ROOT, emso))

@get("/odjava_zavarovanec/<emso_zavarovanca>")
def odjava_zavarovanec(emso_zavarovanca):
    """Pobriši cookie in preusmeri na prijavo."""
    response.delete_cookie('emso', path='/')
    redirect('{0}prijava_zavarovanec'.format(ROOT))

############################## Osebni podatki - zavarovanec ###############################################
@get('/zavarovanec/<emso_zavarovanca>/osebni_podatki')
def osebni_podatki_zavarovanec(emso_zavarovanca):
    (emso_zav, ime_zav, priimek_zav) = get_zavarovanec()

    cur.execute("""
    SELECT ime, priimek, naslov, email, rojstvo, telefon
    FROM osebe 
    WHERE emso=%s
    """, (emso_zavarovanca,))
    (ime, priimek, naslov, email, rojstvo, telefon) = cur.fetchone()

    return rtemplate('zavarovanec_osebni_podatki.html',
                    ime=ime,
                    priimek=priimek,
                    naslov=naslov,
                    email=email,
                    rojstvo=rojstvo,
                    telefon=telefon,
                    emso=emso_zav, # emso od zavarovanca, ker rabimo v zavarovanec_osnova, da se izpiše kdo je prijavljen
                    ime_zavarovanca=ime_zav,
                    priimek_zavarovanca=priimek_zav, 
                    napaka=None)

############### Zavarovanja komitenta #####################################################################
@get('/zavarovanec/<emso_zavarovanca>/moja_zivljenjska')
def moja_zivljenjska(emso_zavarovanca):
    (emso, ime, priimek) = get_zavarovanec()
    cur.execute("""
    SELECT stevilka_police, datum_police, vrsta_zivlj, premija 
    FROM zivljenska 
    LEFT JOIN zavarovanja 
    ON (zivljenska.polica_id = zavarovanja.stevilka_police) 
    WHERE komitent_id=%s
    """, (emso,))
    return rtemplate('moja_zivljenjska.html', napaka=None,
                        moja_zivljenjska=cur,
                        emso=emso,
                        ime_zavarovanca=ime,
                        priimek_zavarovanca=priimek)

@get('/zavarovanec/<emso_zavarovanca>/moja_nepremicninska')
def moja_nepremicninska(emso_zavarovanca):
    (emso, ime, priimek) = get_zavarovanec()
    cur.execute("""
    SELECT stevilka_police, datum_police, vrsta_n, nepr_id, premija 
    FROM nepremicninska 
    LEFT JOIN zavarovanja 
    ON (nepremicninska.polica_id = zavarovanja.stevilka_police) 
    WHERE komitent_id=%s
    """, (emso,))
    return rtemplate('moja_nepremicninska.html', napaka=None,
                        moja_nepremicninska=cur,
                        emso=emso,
                        ime_zavarovanca=ime,
                        priimek_zavarovanca=priimek)

@get('/zavarovanec/<emso_zavarovanca>/moja_avtomobilska')
def moja_avtomobilska(emso_zavarovanca):
    (emso, ime, priimek) = get_zavarovanec()
    cur.execute("""
    SELECT stevilka_police, datum_police, vrsta, avto_id, premija 
    FROM avtomobilska 
    LEFT JOIN zavarovanja 
    ON (avtomobilska.polica_id = zavarovanja.stevilka_police) 
    WHERE komitent_id=%s
    """, (emso,))
    return rtemplate('moja_avtomobilska.html', napaka=None,
                        moja_avtomobilska=cur,
                        emso=emso,
                        ime_zavarovanca=ime,
                        priimek_zavarovanca=priimek)

################### Sklenitev zavarovanja - komitent #################################################
@get('/zavarovanec/<emso_zavarovanca>/skleni_zavarovanje')
def skleni_zavarovanje(emso_zavarovanca):
    (emso, ime, priimek) = get_zavarovanec()
    return rtemplate('skleni_zavarovanje.html',
                        emso=emso,
                        ime_zavarovanca=ime,
                        priimek_zavarovanca=priimek)

# Sklenitev zivljenskih zavarovanj  =======================================================================
@get('/zavarovanec/<emso_zavarovanca>/skleni_zivljenjsko')
def zavarovanec_skleni_zivljenjsko_get(emso_zavarovanca):
    """ Prikaži formo za dodajanje novega življenjskega zavarovanja """
    (emso_zav, ime_zav, priimek_zav) = get_zavarovanec()
    return rtemplate('zavarovanec_skleni_zivljenjsko.html',
                        vrsta_zivljenjskega='',
                        emso=emso_zav, # emso od agenta, ker rabimo v zavarovanec_osnova, da se izpiše kdo je prijavljen
                        ime_zavarovanca=ime_zav,
                        priimek_zavarovanca=priimek_zav, 
                        napaka=None)


@post('/zavarovanec/<emso_zavarovanca>/skleni_zivljenjsko')
def zavarovanec_skleni_zivljenjsko_post(emso_zavarovanca):
    vrsta_zivljenjskega = request.forms.vrsta_zivljenjskega
    # Dobimo podatke zavarovanca, ki sklepa zavarovanje
    (emso_zav, ime_zav, priimek_zav) = get_zavarovanec()

    # Ali je komitent s tem emsom sploh v bazi?
    # Mora biti v bazi, saj je prijavljen, torej se je registriral

    # Vstavimo v bazo novo polico 
    try:
        premija = doloci_premijo_zivljenjskega(vrsta_zivljenjskega, starost_osebe(emso_zav))
        cur.execute("""
            INSERT INTO zavarovanja (komitent_id, datum_police, premija, tip_zavarovanja)
            VALUES (%s, %s, %s, %s)
            RETURNING stevilka_police
        """, (emso_zav, date.today(), premija, 1)) # 1 je za življenjsko
        stevilka_police, = cur.fetchone()
        #cur.execute("SELECT stevilka_police FROM zavarovanja ORDER BY stevilka_police DESC LIMIT 1")
        #stevilka_police = cur.fetchone()[0]
        # tabela zivljenska ... slovnicno je zivljenjska
        cur.execute("""
            INSERT INTO zivljenska (polica_id, vrsta_zivlj) 
            VALUES (%s, %s)
            """, (stevilka_police, vrsta_zivljenjskega))
        conn.commit() 

    except Exception as ex:
        conn.rollback()
        return rtemplate('zavarovanec_skleni_zivljenjsko.html',
                        vrsta_zivljenjskega=vrsta_zivljenjskega,  
                        emso=emso_zav, # emso od zavarovanca, ker rabimo v zavarovanec_osnova, da se izpiše kdo je prijavljen
                        ime_zavarovanca=ime_zav,
                        priimek_zavarovanca=priimek_zav, 
                        napaka='Zgodila se je napaka: {0}'.format(ex)) 

    redirect('{0}zavarovanec/{1}/moja_zivljenjska'.format(ROOT, emso_zavarovanca))

# Sklenitev nepremicninskih zavarovanj ===================================================================
@get('/zavarovanec/<emso_zavarovanca>/skleni_nepremicninsko')
def zavarovanec_skleni_nepremicninsko_get(emso_zavarovanca):
    """ Prikaži formo za dodajanje novega nepremicninskega zavarovanja """
    (emso_zav, ime_zav, priimek_zav) = get_zavarovanec()
    return rtemplate('zavarovanec_skleni_nepremicninsko.html',
                        naslov_nepr='',
                        vrsta_nepremicninskega='',
                        premija='', 
                        emso=emso_zav, # emso od zavarovanca, ker rabimo v zavarovanec_osnova, da se izpiše kdo je prijavljen
                        ime_zavarovanca=ime_zav,
                        priimek_zavarovanca=priimek_zav, 
                        napaka=None)


@post('/zavarovanec/<emso_zavarovanca>/skleni_nepremicninsko')
def zavarovanec_skleni_nepremicninsko_post(emso_zavarovanca):
    naslov_nepr = request.forms.naslov_nepr
    vrsta_nepremicninskega = request.forms.vrsta_nepremicninskega

    # KER NEPREMIČNINA NIMA LASTNIKA; SE LAHKO ZGODI, DA ZAVAROVANJE SKLENEŠ NEKOMU DRUGEMU???
    # Verjetno ne boš, saj moraš plačati premijo.

    # Dobimo podatke zavarovanca, ki sklepa zavarovanje
    (emso_zav, ime_zav, priimek_zav) = get_zavarovanec()

    # Ali je naslov nepremičnine že že v bazi?
    cur.execute("SELECT 1 FROM nepremicnine WHERE naslov_nepr=%s", (naslov_nepr,))
    if cur.fetchone() is None:
        # Nepremičnine še ni v bazi
        return rtemplate('zavarovanec_skleni_nepremicninsko.html',
                            naslov_nepr='',
                            vrsta_nepremicninskega=vrsta_nepremicninskega, 
                            premija=premija, 
                            emso=emso_zav, # emso od zavarovanca, ker rabimo v zavarovanec_osnova, da se izpiše kdo je prijavljen
                            ime_zavarovanca=ime_zav,
                            priimek_zavarovanca=priimek_zav, 
                            napaka='Nepremičnina še ni v bazi') 
    else:                       
        # Nepremičnina je že v bazi. Vstavimo  zavarovalno polico in ne naslova
        premija = doloci_premijo_nepremicninskega(vrsta_nepremicninskega, vrednost_nepremicnine(naslov_nepr)) # ZA RAČUNAT PREMIJO
        try:
            # Odstraniti je bilo treba UNIQE constraint v tabeli nepremicnine na stolpcu nepr_id,
            # da ima lahko ista nepremičnina več zavarovanj
            cur.execute("""
                INSERT INTO zavarovanja (komitent_id, datum_police, premija, tip_zavarovanja)
                VALUES (%s, %s, %s, %s)
                RETURNING stevilka_police
            """, (emso_zavarovanca, date.today(), premija, 3)) # 3 je za nepremičninsko
            stevilka_police, = cur.fetchone()
            #cur.execute("SELECT stevilka_police FROM zavarovanja ORDER BY stevilka_police DESC LIMIT 1")
            #stevilka_police = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO nepremicninska (polica_id, nepr_id, vrsta_n) 
                VALUES (%s, %s, %s)
                """, (stevilka_police, naslov_nepr, vrsta_nepremicninskega))
            conn.commit() 

        except Exception as ex:
            conn.rollback()
            return rtemplate('zavarovanec_skleni_nepremicninsko.html',
                            naslov_nepr=naslov_nepr,
                            vrsta_nepremicninskega=vrsta_nepremicninskega, 
                            premija=premija, 
                            emso=emso_zav, # emso od zavarovanca, ker rabimo v zavarovanec_osnova, da se izpiše kdo je prijavljen
                            ime_zavarovanca=ime_zav,
                            priimek_zavarovanca=priimek_zav, 
                            napaka='Zgodila se je napaka: {}'.format(ex)) 

        redirect('{0}zavarovanec/{1}/moja_nepremicninska'.format(ROOT, emso_zavarovanca))

# Sklenitev avtomobilskih zavarovanj =============================================================================
@get('/zavarovanec/<emso_zavarovanca>/skleni_avtomobilsko')
def zavarovanec_skleni_avtomobilsko_get(emso_zavarovanca):
    """ Prikaži formo za dodajanje novega avtomobilskega zavarovanja """
    (emso_zav, ime_zav, priimek_zav) = get_zavarovanec()
    return rtemplate('zavarovanec_skleni_avtomobilsko.html', 
                        registrska='',
                        vrsta_avtomobilskega='', 
                        emso=emso_zav, # emso od zavarovanca, ker rabimo v zavarovanec_osnova, da se izpiše kdo je prijavljen
                        ime_zavarovanca=ime_zav,
                        priimek_zavarovanca=priimek_zav, 
                        napaka=None)


@post('/zavarovanec/<emso_zavarovanca>/skleni_avtomobilsko')
def zavarovanec_skleni_avtomobilsko_post(emso_zavarovanca):
    registrska = request.forms.registrska
    vrsta_avtomobilskega = request.forms.vrsta_avtomobilskega

    # Dobimo podatke zavarovanca, ki sklepa zavarovanje
    (emso_zav, ime_zav, priimek_zav) = get_zavarovanec()
    # Ali je registrska že v bazi?
    cur.execute("SELECT 1 FROM avtomobili WHERE registrska=%s", (registrska,))
    if cur.fetchone() is None:
        # Avta še ni v bazi.
        return rtemplate('zavarovanec_skleni_avtomobilsko.html', 
                            registrska='', 
                            vrsta_avtomobilskega=vrsta_avtomobilskega,
                            emso=emso_zav, # emso od zavarovanca, ker rabimo v zavarovanec_osnova, da se izpiše kdo je prijavljen
                            ime_zavarovanca=ime_zav,
                            priimek_zavarovanca=priimek_zav, 
                            napaka='Avtomobila še ni v bazi.') 

    else:
        # Avto je že v bazi. Vstavimo zavarovalno polico 
        premija = doloci_premijo_avtomobilskega(vrsta_avtomobilskega, vrednost_avtomobila(registrska))
        try:
            # Odstraniti je bilo treba UNIQE constraint v tabeli avtomobilska na stolpcu avto_id,
            # da ima lahko isti avto več zavarovanj
            cur.execute("""
                INSERT INTO zavarovanja (komitent_id, datum_police, premija, tip_zavarovanja)
                VALUES (%s, %s, %s, %s)
                RETURNING stevilka_police
            """, (emso_zavarovanca, date.today(), premija, 2)) # 2 je za avtomobilsko
            stevilka_police, = cur.fetchone()
            #cur.execute("SELECT stevilka_police FROM zavarovanja ORDER BY stevilka_police DESC LIMIT 1")
            #stevilka_police = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO avtomobilska (polica_id, vrsta, avto_id) 
                VALUES (%s, %s, %s)
                """, (stevilka_police, vrsta_avtomobilskega, registrska))
            conn.commit() 

        except Exception as ex:
            conn.rollback()
            return rtemplate('zavarovanec_skleni_avtomobilsko.html', 
                            registrska=registrska, 
                            vrsta_avtomobilskega=vrsta_avtomobilskega, 
                            emso=emso_zav, # emso od zavarovanca, ker rabimo v zavarovanec_osnova, da se izpiše kdo je prijavljen
                            ime_zavarovanca=ime_zav,
                            priimek_zavarovanca=priimek_zav, 
                            napaka='Zgodila se je napaka: {}'.format(ex)) 

        redirect('{0}zavarovanec/{1}/moja_avtomobilska'.format(ROOT, emso_zavarovanca))



###########################################################################################################
###########################################################################################################
###########################################################################################################
###########################################################################################################
###########################################################################################################
###########################################################################################################
###########################################################################################################
###########################################################################################################



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
    redirect('{0}avtomobilska'.format(ROOT))

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