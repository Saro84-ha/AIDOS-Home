# AIDOS Home 0.5.0

Dashboard indipendente, con installazione tramite Home Assistant Apps e aggiornamenti via GitHub. Compatibile con Home Assistant Supervisor, incluso il tuo Debian 12.

## Che cosa cambia

- Nuovo design dark e card compatte, **ispirato** all'organizzazione e alle anteprime condivise di Oikos (non una copia del runtime Oikos).
- Catalogo di **25 modelli di card** con nomi e categorie derivati dai manifest del tuo backup `oikos.tar.gz`.
- Widget con rendering dedicato per luci, termostati, climatizzazione, temperatura, UPS, sicurezze, tapparelle, media e robot; gli altri modelli mostrano dati delle entità associate in stile AIDOS, non tutte le funzionalità Oikos originali.
- **Entità selezionate in tempo reale** dall'inventario Home Assistant, filtrate per dominio compatibile. Le card sono configurate in AIDOS.
- Nuove installazioni: **sette pagine senza card**. Nessun import JSON e nessun dato Oikos personale.
- Impostazioni persistenti nell'app `/data/settings.json`, gestite automaticamente. In un aggiornamento di un'installazione esistente la configurazione precedente viene conservata. Per ripartire da zero: Impostazioni → Sistema → Azzera card AIDOS.
- Notifiche: Impostazioni → Notifiche, poi switch nelle singole card. Monitoraggio periodico, non istantaneo.
- Chat Conversation di Home Assistant, con possibile agente AI configurato in Home Assistant.
- Spostamento card a sinistra/destra con frecce nella base della scheda.

## Installazione / aggiornamento

1. Estrai lo ZIP e copia **i contenuti della cartella** nella radice di `AIDOS-Home` sul tuo GitHub Desktop, sostituendo la v0.4.0.
2. Verifica `repository.yaml`: l'URL deve puntare al **tuo** repository.
3. GitHub Desktop: `Commit to main` → `Push origin`.
4. Home Assistant → Impostazioni → Apps → Store → ⋮ → Controlla aggiornamenti (o ricarica repository); aggiorna AIDOS alla **0.5.0**.
5. Avvia e controlla i log dell'app. Apri **AIDOS** dal pannello laterale.

Nessun file con credenziali o impostazioni HA del tuo ambiente va caricato su GitHub.

## Compatibilità e limiti

- Le card originarie di Oikos incluse nel backup non sono state copiate: i codici inclusi nel backup non presentano tutti una licenza riutilizzabile verificata. Per questo AIDOS implementa un proprio frontend e proprio backend.
- Le card specialistiche (es. video live, mappa robot, allarme PIN, grafici storici avanzati, shopping/TMDB, notifica push critica) **non sono ancora equivalenti** alle card Oikos. Nessuna funzione non realizzata è presentata come funzionante.
- La categoria sensori non sempre esprime la tipologia del dispositivo: verifica che il dominio dell'entità scelta sia coerente.
- AIDOS v0.5 non abilita automaticamente allarmi o notifiche critiche. Le chiamate di servizio alle entità sensibili richiedono conferma dell'utente.

## Privacy e licenze

- Nessun token, host privato, configurazione, backup delle entità Oikos o password presente nei tuoi archivi viene distribuito.
- I metadati del catalogo sono utilizzati come riferimento; **non viene incluso il codice originale di Oikos**.
- Il kit `oikos-card-starter-main(2).zip` che hai fornito include una licenza MIT (Copyright 2026 Oikos community) e descrive la separazione tra manifest, card e settings. AIDOS non incorpora il suo runtime o SDK; ove si riutilizzasse in futuro codice sostanziale da quel kit, conserveremo attribuzioni e licenza MIT.

## Sviluppo

```bash
python -m unittest discover -s tests -v
node --check aidos/app/static/app.js
```

Il server usa solo librerie standard Python. Home Assistant Core rimane il backend per stati e comandi; il Supervisor token rimane sul server e non viene trasmesso al browser.
