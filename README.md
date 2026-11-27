# AIDOS Home 0.8.0

App Home Assistant separata: dashboard configurate da zero, template card selezionabili nel catalogo AIDOS, collegamento alle entità esistenti di Home Assistant, notifiche per-card e assistente Conversation.

## Installazione / aggiornamento

Copia il contenuto della cartella estratta nella radice di `AIDOS-Home`, commit/push da GitHub Desktop, poi aggiorna repository e app dal catalogo Home Assistant. Mantieni Oikos installato.

## Cosa replica / cosa non replica

Riproduce il flusso di navigazione inferiore, la gestione per raccolte, il catalogo con anteprima e le impostazioni delle schede, usando codice AIDOS originale. Non contiene il server proprietario Oikos, i suoi bundle compilati, i suoi token o le sue verifiche di licenza.

Card: le funzioni semplici (luci, termostati, tapparelle, sensori, media, UPS) usano servizi di Home Assistant. Funzioni specializzate come telecamere live, UI di terze parti e template proprietari avanzati non sono equivalenti al prodotto originale.

## Sicurezza

Nessun token HA pubblicato nel repository. Impostazioni AIDOS sotto `/data/settings.json`, dopo il primo avvio. Le azioni sensibili richiedono conferma. Evita la pubblicazione degli archivi completi Oikos su GitHub.
