# Database Palestra
## AA24/25 - Progetto del corso **Basi di Dati** [SCP4065533]
Il seguente progetto è un lavoro realizzato a coppie per il conseguimento del 25% della valutazione al corso sopracitato.

La traccia accademica prevedeva:
1. modellazione di una realtà di riferimento a scelta, comprensiva di relazione strutturata;
2. implementazione del database (con implementazione di query e indici di ottimizzazione);
3. codice in linguaggio C per l'interazione con la base di dati.

**NB:** Per questo lavoro è stato fatto uso di RDBMS *PostgreSQL*.
## Contenuto del repository
Il lavoro è completo dei seguenti elementi:
* documentazione di progetto:
  * modellazione della realtà di riferimento (gestione di una palestra);
  * progettazione concettuale: diagramma E-R completo di glossario;
  * progettazione logica:
    * analisi per ridondanza di attributi;
    * eliminazione di generalizzazione da diagramma E-R;
    * schema relazionale.
  * considerazioni circa l'utilizzo di indici per l'ottimizzazione delle query.
* file [palestra.sql](palestra.sql) contenente le seguenti istruzioni:
  * implementazione delle relazioni;
  * implementazione delle query ideate con indici di ottimizzazione;
  * popolamento completo e logicamente corretto della base di dati.
* file [palestra.c](palestra.c) per il collegamento e l'interrogazione della base di dati in linguaggio C;
* file [popolamento.py](popolamento.py) per la generazione di dati fittizzi in linguaggio Python.
