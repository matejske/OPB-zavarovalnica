# Primer spletne aplikacije z `bottle.py`

* [![bottle.py](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jaanos/OPB-bottle/master?urlpath=proxy/8080/) Aplikacija `bottle.py`
* [![Jupyter](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jaanos/OPB-bottle/master) Jupyter


Ta repozitorij vsebuje minimalen primer spletne aplikacije z ogrodjem [`bottle.py`](https://bottlepy.org/docs/dev/) in povezavo na podatkovno bazo [PostgreSQL](https://www.postgresql.org/) za potrebe predmeta [Osnove podatkovnih baz](https://github.com/jaanos/OPB).


## Aplikacija

Aplikacijo zaženemo tako, da poženemo program [`primer.py`](primer.py), npr.
```bash
python primer.py
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
