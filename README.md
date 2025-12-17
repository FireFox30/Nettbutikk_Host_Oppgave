# NerdParts.no - Nettbutikk

En komplett nettbutikk for PC-komponenter og gaming-utstyr, bygget med Flask og MySQL.

## 📋 Innholdsfortegnelse

- [Installasjon](#installasjon)
- [Database-oppsett](#database-oppsett)
- [Kjøre applikasjonen](#kjøre-applikasjonen)
- [Funksjoner](#funksjoner)
- [Filstruktur](#filstruktur)

##  Installasjon

### Forutsetninger

- Python 3.7 eller nyere
- MySQL Server
- pip (Python package manager)

### Steg 1: Installer avhengigheter

```bash
pip install -r requirements.txt
```

##  Database-oppsett

### Steg 1: Opprett databasen

Kjør SQL-skriptet `database.sql` i MySQL:

```bash
mysql -u root -p < database.sql
```

Eller logg inn i MySQL og kjør:

```sql
source database.sql;
```

### Hva skjer i databasen?

Skriptet oppretter:
- **Database**: `nettbutikk`
- **Tabeller**:
  - `products` - Produktkatalog med navn, beskrivelse, pris og bilde
  - `orders` - Kundeordrer med kontaktinformasjon
  - `order_items` - Produkter i hver ordre
- **Testdata**: 7 produkter (gaming PC, mus, tastatur, SSD, etc.)

## ▶️ Kjøre applikasjonen

Start Flask-serveren (dette krever en Python-fil som ikke er inkludert, vanligvis `app.py`):

```bash
python app.py
```

Åpne nettleseren på: `http://localhost:5000`

##  Funksjoner

### 1. Produktvisning (`index.html`)

**Hovedsiden** viser alle tilgjengelige produkter i et responsivt rutenett.

**Funksjonalitet:**
- Viser produktbilde, navn, beskrivelse og pris
- "Legg til"-knapp for å legge produkter i handlekurven
- Navigasjon til handlekurv i toppmeny

### 2. AI Kundeservice Chat Widget

**Plassering:** Flytende chat-knapp nederst til høyre på hovedsiden.

**Hvordan bruke:**
1. Klikk på blå AI-knappen nederst til høyre
2. Skriv din melding i tekstfeltet
3. Trykk Enter eller klikk "Send"
4. AI-assistenten svarer på spørsmål om produkter og butikken

**Funksjoner:**
- Sanntids chat med AI-assistent
- Automatisk scrolling til nye meldinger
- "Skriver..."-indikator mens AI tenker
- Responsivt design for mobil og desktop

### 3. Handlekurv (`cart.html`)

**Tilgang:** Klikk "Handlekurv" i toppen av siden.

**Funksjonalitet:**
- Viser alle produkter i handlekurven
- +/- knapper for å justere antall
- Automatisk totalsum-beregning
- "Bestill"-knapp går videre til kassen
- "Tilbake til butikken"-lenke

### 4. Kassen (`checkout.html`)

**Tilgang:** Klikk "Bestill" fra handlekurven.

**Påkrevd informasjon:**
- Navn
- E-postadresse
- Leveringsadresse

**Funksjonalitet:**
- Valideringsskjema
- "Bekreft"-knapp fullfører kjøpet
- "Tilbake til handlekurv"-lenke

### 5. Ordrebekreftelse (`order_confirmation.html`)

**Automatisk visning** etter vellykket bestilling.

**Informasjon som vises:**
- ✓ Suksessmelding
- Ordrenummer
- Bestillingsdato og tidspunkt
- Kundedetaljer (navn, e-post, adresse)
- Fullstendig produktoversikt med antall og priser
- Total sum

**Navigasjon:**
- "Tilbake til butikken"-knapp for å fortsette shopping

##  Filstruktur

```
nettbutikk/
│
├── static/
│   ├── style.css          # All styling inkludert chat widget
│   └── [produktbilder]    # Bilder av produktene
│
├── templates/
│   ├── index.html         # Hovedside med produkter og AI chat
│   ├── cart.html          # Handlekurv
│   ├── checkout.html      # Kasseside
│   └── order_confirmation.html  # Ordrebekreftelse
│
├── database.sql           # Database-skjema og testdata
├── requirements.txt       # Python-avhengigheter
└── README.md             # Denne filen

```

##  Design og styling

**Designsystem:**
- Moderne, ren estetikk med hvit bakgrunn
- Bløte skygger og avrundede hjørner
- Responsivt rutenett-layout
- Hover-effekter på produktkort og knapper
- Farger:
  - Primær (blå): `#007bff`
  - Suksess (grønn): `#28a745`
  - Bakgrunn: `#f8f9fa`

**Chat Widget Design:**
- Flytende blå knapp med AI-ikon
- Moderne chat-bobler med animasjoner
- Responsiv og mobilvennlig
- Smooth slide-in animasjoner

##  Teknologi

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI Chat**: Fetch API for asynkron kommunikasjon

##  Notater

- Produktbilder må lagres i `static/` mappen
- Chat-funksjonalitet krever backend endpoint `/chat` i Flask-appen
- Database-tilkobling må konfigureres i backend
- All tekst er på norsk

##  Support

For spørsmål om butikken, bruk AI chat-widgeten på nettsiden!