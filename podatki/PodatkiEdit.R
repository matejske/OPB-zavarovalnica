library(readr)
library(dplyr)

`%nin%` = Negate(`%in%`)

## OSEBE - zaposlenim damo TRUE ali FALSE
Osebe <- read_csv("F:/Faks/OPB-zavarovalnica/podatki/Osebe_uvoz.csv")
Osebe$zaposleni[is.na(Osebe$zaposleni)] <- TRUE
write.csv(Osebe,"F:/Faks/OPB-zavarovalnica/podatki/Osebe.csv", fileEncoding='UTF-8', row.names = FALSE)

##ZAVAROVANJA - Odstranimo agente iz zavarovanj
Zavarovanja <- read_csv("F:/Faks/OPB-zavarovalnica/podatki/Zavarovanja_uvoz.csv")
Zaposleni <- Osebe %>% filter(zaposleni == TRUE) 
Zavarovanja <- Zavarovanja %>% filter(komitent_id %nin% Zaposleni$emso)

#Tabela <- full_join(Osebe, Zavarovanja, by = c("emso" = "komitent_id")) %>% filter(zaposleni == TRUE) %>% filter(is.na(stevilka_police) == FALSE)

write.csv(Zavarovanja,"F:/Faks/OPB-zavarovalnica/podatki/Zavarovanja.csv", fileEncoding='UTF-8', row.names = FALSE)

##ŽIVLJENJSKA - Odstranimo ostala
Zivljenjska <- read_csv("F:/Faks/OPB-zavarovalnica/podatki/Zivljenjska_uvoz.csv")
Zivljenjske_police <- Zavarovanja %>% filter(tip_zavarovanja == 1)
Zivljenjska <- Zivljenjska %>% filter(polica_id %in% Zivljenjske_police$stevilka_police)
Zivljenjska <- Zivljenjska[1:299,]

write.csv(Zivljenjska,"F:/Faks/OPB-zavarovalnica/podatki/Zivljenjska.csv", fileEncoding='UTF-8', row.names = FALSE)

#AVTOMOBILSKA - odstranimo ostala
Avtomobilska <- read_csv("F:/Faks/OPB-zavarovalnica/podatki/Avtomobilska_uvoz.csv")
Avtomobilska_police <- Zavarovanja %>% filter(tip_zavarovanja == 2)
Avtomobilska <- Avtomobilska %>% filter(polica_id %in% Avtomobilska_police$stevilka_police)
Avtomobilska <- Avtomobilska[1:327,]

write.csv(Avtomobilska,"F:/Faks/OPB-zavarovalnica/podatki/Avtomobilska.csv", fileEncoding='UTF-8', row.names = FALSE)

#NEPREMICNINSKA - odstranimo ostala
Nepremicninska <- read_csv("F:/Faks/OPB-zavarovalnica/podatki/Nepremicninska_uvoz.csv")
Nepremicninska_police <- Zavarovanja %>% filter(tip_zavarovanja == 3)
Nepremicninska <- Nepremicninska %>% filter(polica_id %in% Nepremicninska_police$stevilka_police)
Nepremicninska <- Nepremicninska[1:318,]

write.csv(Nepremicninska,"F:/Faks/OPB-zavarovalnica/podatki/Nepremicninska.csv", fileEncoding='UTF-8', row.names = FALSE)
