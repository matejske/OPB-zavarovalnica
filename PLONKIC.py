#PLONKIČ:

from IPython.core.display import HTML

@route("/povezava") # to iz spodnje funkcije pridela neko novo strežniško funkcijo (kao če gremo na to povezavo=routo se bo klicala ta funkcija)
def ime_funkcije():
  blabla bpa
  return...


@route("/hello/<parameter>") #kar tu napišemo bo spodnje funkcija vzela za parameter
def hello(parameter):
    return "hello {0}".format(parameter)


@get("link")   #<-------- relativna povezava od strežnika dalje 
def ime_funkcije():
    return  <a href="link"> besedilo za prikaz</a>       #<------- HTML link

@get('/zavarovanja')
def zavarovanja():
     cur.execute("SELECT * FROM zavarovanja") #<----- cur rata iterabilen objekt
     return rtemplate('zavarovanja.html', zavarovanja=cur) #<--- v template ....html damo 
# objekt cur (to je tisto, kar smo zgoraj dobili iz poizvedbe) pod imenom zavarovanja, 
# objekt zavarovanja pa b potem uporabila html predloga
 


#####################################################################


V VIEWS PIŠEMO TEMPLATE:
 - mešanica html in pythona
 - python kodo začnemo s %
 - vsaka zanka (%for, %if,...) mora imeti %end na koncu
 - dobeseden izpis spremenljvke v html tako, da damo v {{.....}}





HTML PLINKIC ZA V VIEWS:
<html>
    <head>
        <title> naslov v tabu </title>
    </head>
</html>



###############
za post in get moraš gledat kot uporabnik spletne strani,
s post nekaj napišem v polja in postnem to na strežnik,
z get pa kao nekaj dobim iz strežnika