# Product Requirements Document (PRD)

**Projekt:** Restaurant Booking System  
**Version:** 0.1 – Første udkast  
**Status:** Under udarbejdelse  
**Projekttype:** Fullstack-webapplikation

---

## 1. Produktbeskrivelse

### 1.1 Formål

Formålet med projektet er at udvikle et webbaseret bookingsystem, der gør det muligt for restauranter at administrere bordreservationer og for kunder at reservere borde online.

Systemet skal automatisere centrale dele af reservationsprocessen, herunder kontrol af tilgængelige borde, oprettelse af reservationer og håndtering af eksisterende bookinger.

Applikationen skal bestå af en brugergrænseflade, et backend-API og en relationel database.

### 1.2 Problemstilling

Restauranter har behov for at håndtere reservationer og sikre, at antallet af gæster ikke overstiger restaurantens tilgængelige kapacitet.

Manuel reservationshåndtering kan medføre dobbeltbookinger, manglende overblik og administrativt arbejde.

Systemet skal tilbyde en samlet digital løsning, hvor kunder selv kan foretage reservationer - altså en client facing del.
Mens restaurantens personale kan administrere dem, en administrativ del.

### 1.3 Produktmål

- Kunder skal kunne foretage bordreservationer via en webapplikation.
- Systemet skal forhindre dobbeltbookinger.
- Restaurantens personale skal kunne administrere reservationer via en webapplikation.
- Restaurantens kapacitet og åbningstider skal kunne konfigureres.
- Systemet skal kunne testes automatisk og idriftsættes.
- Arkitekturen skal understøtte vedligeholdelse og fremtidig videreudvikling.

## 2. Målgrupper

### 2.1 Restaurantens kunder

Kunderne skal kunne reservere borde uden at kontakte restauranten direkte.

Kunden skal kunne:

- Se ledige reservationstidspunkter.
- Vælge dato, tidspunkt og antal gæster.
- Oprette en reservation.
- Modtage en bekræftelse på skærmen.

### 2.2 Restaurantens personale

Personalet skal kunne administrere restaurantens reservationer gennem en beskyttet administrationsgrænseflade.

Personalet skal kunne:

- Se eksisterende reservationer.
- Se reservationer for en bestemt dato.
- Oprette reservationer manuelt.
- Annullere reservationer.

## 3. Projektets afgrænsning

Projektet udvikles som en Minimum Viable Product (MVP).

Det primære mål er at implementere en komplet og fungerende reservationsproces fra kundeforespørgsel til registrering i databasen.

### 3.1 In scope – MVP

- Webbaseret brugergrænseflade.
- REST API til reservationshåndtering.
- Relationel database.
- Kontrol af ledige borde.
- Oprettelse og annullering af reservationer.
- Beskyttet administrationsgrænseflade.
- Konfigurerbare åbningstider og borde.
- Automatiserede tests.
- Deployment af applikationen.

### 3.2 Out of scope

Følgende funktioner indgår ikke i den første version:

- SMS- og e-mailnotifikationer.
- Kundekonti og loyalitetsprogrammer.
- Statistik og avanceret rapportering.
- Komplet SaaS-platform med flere restauranter på samme installation.
- Avanceret bordplan med drag-and-drop.
- Automatisk sammensætning af flere borde til store selskaber.

Funktionerne kan indgå i senere versioner.

## 4. Funktionelle krav

Kravene er identificeret med et unikt ID for at sikre sporbarhed mellem kravspecifikation, use cases, implementering og test.

| ID | Krav | Prioritet |
|---|---|---|
| F-01 | Kunden skal kunne vælge dato og antal gæster | Must |
| F-02 | Systemet skal vise tilgængelige reservationstidspunkter | Must |
| F-03 | Kunden skal kunne oprette en reservation | Must |
| F-04 | Systemet skal forhindre dobbeltbookinger | Must |
| F-05 | Kunden skal modtage en synlig reservationsbekræftelse | Must |
| F-06 | Personalet skal kunne logge ind | Must |
| F-07 | Personalet skal kunne se reservationer | Must |
| F-08 | Personalet skal kunne annullere reservationer | Must |
| F-09 | Systemet skal understøtte konfigurerbare borde og åbningstider | Must |
| F-10 | Personalet skal kunne oprette reservationer manuelt | Should |
| F-11 | Personalet skal kunne redigere reservationer | Could |
| F-12 | Personalet skal kunne ændre restaurantindstillinger i brugergrænsefladen | Could |

*Must = obligatorisk for MVP. Should = ønskeligt, hvis tiden tillader det. Could = mulig udvidelse.*

## 5. Centrale use cases

### UC-01: Opret reservation

**Aktør:** Kunde

**Forudsætninger:**
- Restauranten har definerede åbningstider.
- Systemet indeholder oplysninger om restaurantens borde.

**Hovedforløb:**

1. Kunden åbner bookingsiden.
2. Kunden vælger dato og antal gæster.
3. Systemet viser tilgængelige tidspunkter.
4. Kunden vælger et tidspunkt.
5. Kunden indtaster navn og kontaktoplysninger.
6. Kunden bekræfter reservationen.
7. Systemet kontrollerer igen tilgængeligheden.
8. Reservationen gemmes i databasen.
9. Kunden får vist en reservationsbekræftelse.

**Alternative forløb:**
- Hvis tidspunktet ikke længere er ledigt, afvises reservationen.
- Hvis kunden indtaster ugyldige oplysninger, vises en fejlmeddelelse.
- Hvis restaurantens kapacitet ikke tillader reservationen, tilbydes kunden andre ledige tidspunkter, hvis sådanne findes.

### UC-02: Vis reservationer

**Aktør:** Restaurantpersonale

**Forudsætning:** Personalet er autentificeret.

**Hovedforløb:**

1. Personalet åbner administrationssiden.
2. Personalet vælger en dato.
3. Systemet henter reservationerne.
4. Reservationerne vises med tidspunkt, gæsteantal og relevante kundeoplysninger.

### UC-03: Annuller reservation

**Aktør:** Restaurantpersonale

**Forudsætning:** Reservationen eksisterer, og personalet er autentificeret.

**Hovedforløb:**

1. Personalet finder reservationen.
2. Personalet vælger annullering.
3. Systemet beder om bekræftelse.
4. Reservationens status ændres til annulleret.
5. Den frigivne kapacitet indgår igen i tilgængelighedsberegningen.

## 6. Acceptkriterier

Acceptkriterierne bruges til at afgøre, om de centrale funktionelle krav er opfyldt.

### AC-01: Reservation

Relateret krav: F-03

- [ ] En kunde kan oprette en reservation med gyldige oplysninger.
- [ ] Reservationen gemmes korrekt i databasen.
- [ ] Kunden modtager en bekræftelse på skærmen.
- [ ] Ugyldige input afvises.

### AC-02: Dobbeltbooking

Relateret krav: F-04

- [ ] Systemet afviser en reservation, hvis ingen passende borde er ledige.
- [ ] Et bord må ikke have to aktive reservationer med overlappende tidsrum.
- [ ] To samtidige forespørgsler må ikke resultere i dobbeltbooking.
- [ ] En annulleret reservation optager ikke længere kapacitet.

### AC-03: Tilgængelighed

Relaterede krav: F-02 og F-09

- [ ] Systemet viser kun tidspunkter, hvor en reservation kan gennemføres.
- [ ] Systemet tager hensyn til åbningstider.
- [ ] Systemet tager hensyn til gæsteantal og bordkapacitet.
- [ ] Eksisterende reservationer indgår i tilgængelighedsberegningen.

### AC-04: Administration

Relaterede krav: F-06, F-07 og F-08

- [ ] Kun autentificerede medarbejdere kan tilgå administrationsfunktioner.
- [ ] Personalet kan hente reservationer for en valgt dato.
- [ ] Personalet kan annullere en reservation.
- [ ] Annulleringen afspejles korrekt i databasen.

## 7. Forretningsregler

Bookingsystemet skal understøtte følgende forretningsregler:

| ID | Regel |
|---|---|
| B-01 | Reservationer kan kun oprettes inden for restaurantens åbningstider. |
| B-02 | Onlinebooking tillades for 1–6 personer. Større selskaber henvises til telefonisk kontakt eller e-mail. |
| B-03 | En reservation skal tildeles et bord med tilstrækkelig kapacitet. |
| B-04 | En reservation har en fast varighed på 120 minutter. |
| B-05 | Reservationer kan oprettes i intervaller på 15 minutter med første mulige starttidspunkt kl. 17.30. |
| B-06 | Der skal være mindst 15 minutters buffer mellem to reservationer på samme bord. |
| B-07 | Et bord må ikke have overlappende aktive reservationer, inklusive den påkrævede buffer. |
| B-08 | Annullerede reservationer frigiver bordets kapacitet. |
| B-09 | Systemet skal understøtte to separate seatings pr. bord pr. aften, under hensyntagen til reservationsvarighed og buffer mellem reservationerne. |
| B-10 | Første seating kan starte mellem kl. 17.30 og 18.30, og anden seating mellem kl. 19.30 og 20.30, forudsat at reglerne om varighed og buffer overholdes. |
| B-11 | Systemet skal beregne tilgængelighed uafhængigt af, hvilken seating der reserveres først. |
| B-12 | Bookingregler skal kunne konfigureres uden ændringer i den centrale reservationslogik. |


### Foreløbige konfigurationsvalg

Følgende værdier er forslag og skal endeligt fastlægges under kravspecifikationen:

| Parameter | Foreløbig værdi |
|---|---|
| Reservationsvarighed | 120 minutter |
| Tidsintervaller | 15 minutter |
| Maksimalt gæsteantal | Afhænger af bordkapacitet |
| Bookinghorisont | 30 dage frem |
| Tidszone | Konfigurerbar; Europe/Copenhagen som udgangspunkt |
| Åbningstider | Konfigureres pr. restaurant |

## 8. Ikke-funktionelle krav

| ID | Krav | Verifikation |
|---|---|---|
| NF-01 | Systemet skal forhindre ugyldige reservationer | Automatiserede tests |
| NF-02 | Reservationsdata skal bevares konsistent ved samtidige forespørgsler | Integrationstest og samtidighedstest |
| NF-03 | Administrationsfunktioner skal være adgangsbeskyttede | Autentifikations- og adgangstests |
| NF-04 | Systemet skal validere brugerinput på backend | Tests med ugyldige input |
| NF-05 | Systemet skal kunne anvendes på mobil og desktop | Manuel test af responsive layouts |
| NF-06 | Systemet skal kunne startes og konfigureres med dokumenterede trin | Installationstest |
| NF-07 | Der skal findes automatiserede tests af centrale bookingregler | Testresultater |
| NF-08 | Systemet skal håndtere kunders personoplysninger forsvarligt | Gennemgang af datalagring, adgang og sletning |
| NF-09 | Systemet skal have en acceptabel responstid ved almindelig bookingbelastning | Målinger med dokumenteret testmiljø og belastning |

Konkrete grænseværdier for responstid og eventuelle øvrige kvalitetsmål fastlægges i teststrategien.

## 9. Overordnet datamodel

Systemet forventes som minimum at indeholde følgende centrale entiteter:

| Entitet | Formål |
|---|---|
| Restaurant | Restaurantens oplysninger og konfiguration |
| Table | Bordnummer og kapacitet |
| Reservation | Dato, start- og sluttidspunkt, gæsteantal, status og tilknyttet bord |
| Customer | Kundens navn og kontaktoplysninger |
| OpeningHours | Restaurantens åbningstider |
| StaffUser | Medarbejderoplysninger til administration |

De endelige attributter, relationer og databasebegrænsninger specificeres i systemdesignet.

Det skal blandt andet undersøges, hvordan datamodellen bedst understøtter reservationer, samtidighed og dataintegritet.

## 10. Brugergrænseflade

Brugergrænsefladen designes indledningsvis i Figma.

### 10.1 Kundevendt bookingside

Siden skal indeholde:

- Valg af dato.
- Valg af antal gæster.
- Oversigt over ledige tidspunkter.
- Formular til kundeoplysninger.
- Bekræftelse af reservation.

### 10.2 Administrationsside

Siden skal indeholde:

- Login.
- Oversigt over reservationer.
- Datofiltrering.
- Mulighed for manuel oprettelse og annullering.

Figma-designet anvendes som visuel reference under frontendimplementeringen.

## 11. Teknologier og arkitektur

Den endelige teknologistak er endnu ikke fastlagt.

Systemet forventes at bestå af følgende komponenter:

**Frontend:** Webapplikation, der kommunikerer med backend gennem HTTP.

**Backend:** REST API, der håndterer forretningslogik, validering og adgang til data.

**Database:** Relationel database til lagring af restaurantdata, borde, kunder og reservationer.

**ORM:** Værktøj til håndtering af relationen mellem applikationens datamodeller og databasen.

**Deployment:** Containerbaseret eller tilsvarende reproducerbar idriftsættelse.

Foreløbige teknologier, som overvejes:

- FastAPI eller et Rust-baseret backendframework.
- SQLAlchemy eller en ORM tilpasset den valgte backend.
- PostgreSQL.
- Svelte.
- Docker.

Valgene begrundes senere i projektets teknologianalyse.

## 12. Teststrategi

Testene skal verificere, at systemets implementering opfylder de definerede krav og acceptkriterier.

Testarbejdet omfatter:

**Unit tests:** Test af afgrænset forretningslogik, eksempelvis tidsintervalberegning og kontrol af bookingregler.

**Integrationstests:** Test af API, database og reservationshåndtering.

**Samtidighedstests:** Test af konkurrerende reservationsforespørgsler.

**End-to-end-tests:** Test af centrale brugerflows gennem frontend og backend.

**Manuel test:** Afprøvning af brugergrænseflade og fejlscenarier.

Testcases udarbejdes med udgangspunkt i acceptkriterierne og skal så vidt muligt fastlægges før implementering.

## 13. Succeskriterier for MVP

Projektets produktmål betragtes som opfyldt, når:

- [ ] Kunden kan gennemføre en reservation fra frontend.
- [ ] Reservationen registreres korrekt i databasen.
- [ ] Systemet håndterer bordtilgængelighed og forhindrer dobbeltbookinger.
- [ ] Personalet kan tilgå og administrere reservationer.
- [ ] Systemet understøtter konfiguration af restaurantens borde og åbningstider.
- [ ] De centrale automatiserede tests består.
- [ ] Applikationen kan idriftsættes og tilgås via en browser.
- [ ] Installation og konfiguration er dokumenteret.

## 14. Åbne spørgsmål

Følgende beslutninger skal afklares, før de relevante udviklingsopgaver implementeres:

1. Skal borde tildeles automatisk, eller skal kunden kunne vælge et konkret bord?
- De skal ikke kune vælge et konkret bord
2. Skal restaurantens personale kunne ændre indstillinger i administrationspanelet, eller er konfigurationsfiler tilstrækkelige for MVP?
- personalet skal kunne ændre bordreservation osv i administrationspanelet.
3. Skal kunder selv kunne annullere reservationer?
- Ja - kunden skal selv kunne annullere reservationen.
4. Skal reservationer kunne ændres efter oprettelse?
- Nej, reservationen skal ikke kunne ændres efter oprettelse. Men den kan annulleres.
5. Hvordan skal større selskaber, der kræver flere borde, håndteres?
- Hvis selvskabet er over 6 i størrelse kræver det direkte kontakt til restauranten endten på mail eller telefon.
6. Hvilken backend og ORM skal anvendes?
- Der skal bruges pythons FASTAPI til backend og SQLmodel til som ORM værktøj 
7. Hvordan skal deployment foretages?
- FastAPI hostes på Render og bruger PostgreSQL hos Neon. Nye versioner deployes automatisk ved merge til main. Databaseforbindelsen konfigureres via DATABASE_URL, som sættes i .env lokalt og i Renders miljøindstillinger ved deployment.
8. Hvilke konkrete grænseværdier skal gælde for performance og øvrige ikke-funktionelle krav?
- De udarbejdes løbende



Render er en cloudplatform, der bygger og kører din app. Du forbinder dit GitHub-repo, fortæller Render, hvordan din FastAPI-app skal startes, og vælger main som deploy-branch. Når du merger til main, bygger og deployer Render den nye version og gør API’et tilgængeligt via en HTTPS-adresse. I dit setup kører FastAPI på Render, mens PostgreSQL ligger hos Neon. Renders deploy-guide

Ja, det er et legitimt setup i professionelt regi, især til en MVP. En hostingplatform, en separat managed database og automatisk deploy fra Git er almindelige valg. Din lokale .env passer også fint ind. Hold den ude af Git, og sæt produktionsværdien for DATABASE_URL i Renders miljøindstillinger. Renders guide til miljøvariabler

Jeg ville tilføje automatiske tests før merge og en fast måde at køre databasemigreringer på, fx med Alembic. Gratisplanen er fin til en demo eller tidlig afprøvning. Hvis brugerne forventer hurtige svar hele dagen, ville jeg vælge en betalt app-instans, fordi Renders gratis instans går i dvale efter 15 minutters inaktivitet. Renders gratis hosting

