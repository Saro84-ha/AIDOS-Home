# AIDOS Home — Smart Home Control

**Versione 0.3.0 (sviluppo)** — Dashboard professionale, autonoma e modulare per Home Assistant, ispirata all'organizzazione funzionale di Oikos. Tutto il codice è una nuova implementazione: **non** include file di Oikos, configurazioni, licenze o token ricavati dagli archivi forniti.

## Funzioni incluse

- Menu laterale con Dashboard, Illuminazione, Riscaldamento, Sicurezza, Multimedia, Energia, Stato sistema e pagine personalizzate.
- Editor card: creazione, modifica, eliminazione; card standard o a doppia larghezza.
- 25 template (luci, termostati, porte, tapparelle, serrature, sensori, Zigbee, allarme, energia, UPS, robot, media, persone, calendario, meteo, scene, ventole e altri).
- Lettura periodica degli stati da Home Assistant; comandi per i domini supportati.
- **Menu → Impostazioni → Notifiche**: attivazione globale, servizio `persistent_notification.create` o `notify.*`, cooldown e opzione unavailable. **Ogni card ha la propria attivazione notifiche**. Monitoraggio lato server anche a dashboard chiusa, a intervalli di 15 secondi, senza notificare lo stato iniziale dopo l'avvio.
- Assistente conversazionale tramite `conversation/process` di Home Assistant, con agente configurabile. AI generativa solo se installata e configurata in Home Assistant.
- Backup/importazione JSON della configurazione, temi chiaro/scuro, funzionamento responsive, interfaccia in italiano.
- Dati personali su volume persistente `/data`, non in GitHub. Nessun token esposto nel browser. Ingress gestisce l'autenticazione.

## Installazione via GitHub su Home Assistant OS / Supervised

1. Crea un repository GitHub (es. `AIDOS-Home`) e carica **il contenuto di questa cartella** nella root. Non caricare file Oikos o archivi privati.
2. In `repository.yaml`, sostituisci `YOUR_USERNAME` con il tuo account GitHub.
3. Home Assistant → Impostazioni → Apps → Store → menu ⋮ → Repository → aggiungi `https://github.com/TUO_UTENTE/AIDOS-Home`.
4. Aggiorna l'elenco, apri **AIDOS Home**, installa e avvia. Attiva "Mostra nella barra laterale".
5. Apri **AIDOS**, vai su una pagina e aggiungi le prime card selezionando le tue entità.
6. In **Impostazioni → Notifiche** configura un servizio reale di notifica, attiva la funzione globale e attivala solo nelle card interessate.
7. In **Impostazioni → Assistente AI** lascia vuoto l'agente per usare il Conversation predefinito, oppure specifica un `agent_id` configurato in HA.

### Aggiornamenti

Esegui commit dei nuovi sorgenti e incrementa **`aidos/config.yaml` → `version`**. Dopo l'aggiornamento dell'indice Apps, Home Assistant può proporre la nuova versione. AIDOS salva la configurazione nel volume `/data` anche tra gli aggiornamenti. L'installazione di app da sorgente GitHub richiede un'istanza HA con Supervisor. **Home Assistant Container puro non supporta Apps**: in quel caso serve deployment Docker separato (non incluso in questa prima release).

## Sicurezza e limiti della versione

- Non pubblicare mai `oikos.tar.gz`, `Oikos_Full_Backup.zip`, `oikos-config.json`, token, chiavi o indirizzi privati.
- Le card camera, allarme, calendario, Zigbee e apertura rilevano lo stato, ma non hanno ancora player video, arm/disarm, storico eventi avanzato o gestione firmware Zigbee.
- Notifiche: cambiamento di stato, non un motore di regole complesse; polling a 15 secondi, eventi transitori potrebbero non essere visti. Necessaria scelta di `notify.mobile_app_*` per notifiche push reali.
- L'assistente delega a Home Assistant Conversation: può rispondere a comandi di controllo solo se l'agente ha accesso alle entità e alle funzioni abilitate in HA.
- **Comandi su serrature, tapparelle, script e automazioni chiedono conferma.** Non esporre indiscriminatamente entità critiche all'AI.
- Test automatizzati backend inclusi, ma **non testato sul server reale né su un'istanza Supervisor**: prima installazione di prova e backup Home Assistant consigliati.
- Per autorizzazioni e aggiornamenti il codice dovrebbe essere valutato prima dell'esposizione pubblica del repository. Ingress evita una porta esterna, ma il backend ha accesso privilegiato all'API HA.

## Sviluppo locale

```bash
cd aidos/app
AIDOS_DATA_DIR=/tmp/aidos-test AIDOS_PORT=8099 python3 server.py
```

La UI si apre su `http://localhost:8099` ma senza il token Supervisor la connessione HA non funzionerà. Per test con HA separato si possono impostare `AIDOS_HA_URL` e `AIDOS_HA_TOKEN` nell'ambiente locale (**mai committarli**).

```bash
python3 -m unittest discover -s tests -v
```

## Struttura

```
repository.yaml
README.md
aidos/
  config.yaml
  Dockerfile
  app/
    server.py
    static/{index.html,style.css,app.js}
tests/
  test_server.py
```
