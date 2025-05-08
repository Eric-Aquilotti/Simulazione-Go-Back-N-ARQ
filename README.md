# Elaborato di Programmazione di Reti  
## Simulazione Go-Back-N ARQ  

**Autore:** Eric Aquilotti  

## 📌 Introduzione

Questo progetto implementa una simulazione del protocollo **Go-Back-N ARQ** per l'invio affidabile di pacchetti tramite UDP.

## 🖥️ Struttura del `server.py`

Il server mantiene un contatore globale `expected` che rappresenta il numero del prossimo pacchetto atteso. Alla ricezione di un pacchetto:

- Il pacchetto viene decodificato e confrontato con il valore atteso.
- Se corrisponde, viene inviato un ACK al client e `expected` viene incrementato.
- Il server simula inoltre:
  - Ritardi casuali (5% dei casi), tramite `time.sleep(2)`.
  - Errori di trasmissione (5% dei casi), in cui il pacchetto viene ignorato.
- Il numero di pacchetti "persi" viene mantenuto.
- Alla fine della comunicazione, il server si aspetta un pacchetto **EOF**, che segna la fine della trasmissione.
- Successivamente, il server invia al client il numero di pacchetti effettivamente persi.

## 🧑‍💻 Struttura del `client.py`

Il client implementa il protocollo **Go-Back-N**:

- Invia i pacchetti in base a una **finestra scorrevole** di dimensione `window_size` specificata dall'utente.
- Tiene traccia di:
  - `base`: il primo pacchetto non confermato
  - `current`: il prossimo pacchetto da inviare
- Se scade il timeout prima della ricezione di un ACK, tutti i pacchetti non confermati nella finestra vengono ritrasmessi.
- L'uso di `select.select` permette di gestire la ricezione asincrona degli ACK con timeout.
- Un ACK è accettato solo se corrisponde al `base`. In caso contrario, viene ignorato.

## 📊 Statistiche

Il client mostra:

- Il numero di pacchetti inviati correttamente.
- Il numero di ritrasmissioni dell'intera finestra.
- Il numero di pacchetti effettivamente persi (comunicato dal server).

> ⚠️ Nota: Puo’ succedere che il numero di ritrasmissioni sia maggiore del numero di pacchetti persi a causa di eventuali ritardi nella risposta da parte del server.

## ▶️ Esecuzione

```bash
# Avvio del server
python server.py

# In un altro terminale, avvio del client
python client.py