# AIDOS Home v0.7.0

App Home Assistant separata da Oikos. Aggiornamento dalla v0.5/0.6 tramite GitHub Desktop: sostituisci i file nel repository `AIDOS-Home`, crea un commit, fai **Push origin** e poi aggiorna il catalogo Apps nel Supervisor.

## Funzioni

- UI originale AIDOS ispirata al layout Oikos fornito: tema chiaro con accenti oro, navigazione inferiore, header, catalogo a due colonne, selezione e anteprima di schede, configurazione per card.
- 25 template derivati dai manifest del backup Oikos, visualizzazioni dedicate per luci, clima, sensori, UPS, coperture, telecamere (placeholder), media e robot. **Non tutte le card hanno le funzionalità avanzate originali di Oikos.**
- Entità ottenute da Home Assistant al momento della configurazione, senza file JSON di importazione.
- Impostazioni private persistenti in `/data/settings.json`, protette dagli aggiornamenti. Nuove installazioni: zero card.
- Notifiche configurabili nelle Impostazioni e per card, via polling 15s.
- Assistente AI con integrazione Conversation di Home Assistant (agente configurabile).
- Conferma per comandi sensibili, come serrature e tapparelle.

## Limiti

L'interfaccia è una ricostruzione e non una copia binaria del runtime Oikos. Funzioni specializzate quali streaming video, grafici storici avanzati, preview live del catalogo, editor drag-and-drop e card multidispositivo non sono ancora equivalenti. Nessuna credenziale, licenza Oikos o impostazione della casa fa parte del repository. Licenze di terze parti vanno rispettate, anche nell'uso personale.

## Test

`python -m unittest discover -s tests -v` e `node --check aidos/app/static/app.js`.
