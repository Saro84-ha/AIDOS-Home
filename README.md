# AIDOS Home 0.4.0

Dashboard indipendente per Home Assistant Supervisor, con interfaccia originale ispirata all'organizzazione delle pagine Oikos.

## Funzionalità
- Layout a righe / colonne con importazione delle sette pagine e delle associazioni alle schede da un backup personale Oikos.
- Oltre 40 categorie di template; alcune card importate sono visualizzazioni generiche e richiedono collegamento manuale a entità HA.
- Comandi HA per luci, clima, serrature, tapparelle, media, switch e dispositivi supportati.
- Notifiche **Menu → Impostazioni → Notifiche**, disabilitate di default, e controllo per card.
- Assistente AI tramite API Conversation di Home Assistant (agente HA da configurare).
- Configurazione persistente in `/data` e import/export privato dalla dashboard.

## Aggiornamento da 0.3
1. Conservare una copia della configurazione AIDOS usando Impostazioni → Esporta.
2. Copiare i file di questa cartella nella directory locale GitHub `AIDOS-Home`, **senza copiare il backup Oikos**.
3. GitHub Desktop → Commit → Push origin.
4. In Home Assistant → Apps → AIDOS Home, aggiornare alla 0.4.0 (potrebbe occorrere ricaricare il catalogo).
5. Mantenere Oikos installato: non è coinvolto dalla procedura.

## Importazione privata delle tue dashboard Oikos
**Non aggiungere il backup `oikos.tar.gz` o il JSON esportato al repository pubblico.**

Sul tuo PC Windows, se Python è installato, apri PowerShell in una cartella **fuori dal repository** e lancia:

```powershell
py "C:\Users\rgian\Documents\GitHub\AIDOS-Home\tools\import_oikos.py" "C:\percorso\privato\oikos.tar.gz" --output "C:\percorso\privato\AIDOS-settings-PRIVATE.json"
```

Sostituisci i percorsi con quelli reali, quindi in AIDOS apri **Impostazioni → Importa configurazione** e seleziona il JSON. L'importazione sostituisce le impostazioni AIDOS correnti: effettua un'esportazione preventiva.

## Privacy e limiti
Questo repository contiene **solo codice originale AIDOS**. L'importer legge il backup locale e importa esclusivamente la disposizione delle pagine, i nomi delle card e una singola entità per scheda dove identificabile. Non importa codice Oikos, i suoi bundle commerciali, i plugin, licenze, password, URL privati, token né gli asset grafici. Gli ID delle entità possono essere informazioni private: non pubblicare l'output dell'importer.

La ricostruzione delle card avanzate di Oikos (grafici complessi, pop-up interattivi, layout speciali e CCTV live) non è completa; per queste funzioni sono necessarie ulteriori implementazioni originali e verifiche su Home Assistant reale. Non è stato eseguito un test end-to-end con l'istanza domestica.
