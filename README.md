# OPB-zavarovalnica

Projekt pri predmetu Osnove podatkovnih baz v letu 2020.

Avtorji: Enej Kovač, Tomas Rode, Matej Škerlep

Zagon aplikacije z orodjem Binder: [![bottle.py](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/matejske/OPB-zavarovalnica/master?urlpath=proxy/8080/)

# Opis

Po zagonu aplikacije se nam odpre domača stran Zavarovanice ETM, kjer lahko dobimo osnovne informacije kot so naprimer kontakt, podatki o zaposlenih in možne zavarovalne police. Če hočemo skleniti zavarovanje se moramo prijaviti v spletno poslovalnico za zavarovance oziroma se najprej registrirati, če uporabniškega računa še nimamo. V spletni poslovalnici lahko sklenemo nova zavarovanja, vidimo že sklenjene police ter svoje osebne podatke. Poleg spletne poslovalnice za zavarovance obstaja tudi spletna poslovalnica za agente, kamor se lahko prijavijo zaposleni na Zavarovalnici ETM. Poslovalnica agentom omogoča hiter pregled nad osnovnimi statističnimi podatki zavarovalnice, dostop do baze podatkov ter sklepanje zavarovanj za svoje komitente.

Obstaja že račun agenta (in tudi zavarovanca) z naslednjimi potrebnimi podatki za prijavo:
Emšo: 1111
geslo: enej

# ER diagram

<img src="./ER diagram/ER_diagram_zavarovalnica.png" alt="ER diagram"/>


## Aplikacija

Aplikacijo zaženemo tako, da poženemo program [`zavarovalnica.py`](zavarovalnica.py), npr.
```bash
python zavarovalnica.py
```
Za delovanje je potrebno še sledeče:
* [`auth_public.py`](auth_public.py) - podatki za prijavo na bazo
* [`bottle.py`](bottle.py) - knjižnica za spletni strežnik
* [`static/`](static/) - mapa s statičnimi datotekami
* [`views/`](views/) - mapa s predlogami


## Binder

Aplikacijo je mogoče poganjati tudi na spletu z orodjem [Binder](https://mybinder.org/). V ta namen so v mapi [`binder/`](binder/) še sledeče datoteke:
* [`requirements.txt`](binder/requirements.txt) - seznam potrebnih Pythonovih paketov za namestitev s [`pip`](https://pypi.org/project/pip/)
* [`postBuild`](binder/postBuild) - skripta, ki se požene po namestitvi paketov in poskrbi za nastavitev posrednika za spletni strežnik
* [`start`](binder/start) - skripta za zagon aplikacije (spremenljivka `BOTTLE_RUNTIME` poda ime glavnega programa)

Zaradi omejitev javne storitve [Binder](https://mybinder.org/) se povezava z bazo vzpostavi na vratih 443 (namesto običajnih 5432), za kar je bila potrebna posebna nastavitev strežnika.

Zgornje skripte je možno prilagoditi tudi za druga ogrodja, kot npr. [Flask](https://palletsprojects.com/p/flask/) ali [Django](https://www.djangoproject.com/).

