#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "C:/Program Files/PostgreSQL/17/include/libpq-fe.h"

#define MAX_COLS 20     // Colonne max. stampate a video
#define MAX_WIDTH 50        // Larghezza max. di un campo della tabella

// Funzione di pulizia console
void clean_console() {
#ifdef _WIN32
    system("cls");
#else
    system("clear");
#endif
}

void Query(PGconn *conn, const char *query) {
    int len;
    char *val;
    PGresult *ris = PQexec(conn, query);

    // Errore nella restituzione del risultato (query errata)
    if (PQresultStatus(ris) != PGRES_TUPLES_OK) {
        fprintf(stderr, "Non e' possibile restituire il risultato: %s", PQerrorMessage(conn));
        PQclear(ris);
        return;
    }

    int rows = PQntuples(ris);
    int cols = PQnfields(ris);
    int widths[MAX_COLS];       // Vettore di lunghezze per le colonne

    // Condizione di query vuota
    if (rows == 0) {
        printf("La query non restituisce alcun risultato.\n");
        return;
    }

    // Larghezza max. per ciascuna colonna
    for (int i = 0; i < cols; i++) {
        widths[i] = strlen(PQfname(ris, i));        // Nome della colonna

        for (int j = 0; j < rows; j++) {
            len = strlen(PQgetvalue(ris, j, i));
            if (len > widths[i]) widths[i] = len;       // Se il dato successivo (stessa colonna) occupa più spazio in larghezza
        }

        if (widths[i] > MAX_WIDTH) widths[i] = MAX_WIDTH;       // Troncamento del campo se troppo lungo
    }

    // Riga superiore di contorno alla tabella
    printf("\n");
    for (int i = 0; i < cols; i++) {
        printf("+");
        for (int j = 0; j < widths[i] + 2; j++) printf("-");
    }
    printf("+\n");

    // Stampa delle intestazioni della tabella
    for (int i = 0; i < cols; i++) printf("| %-*s ", widths[i], PQfname(ris, i));
    printf("|\n");

    // Riga inferiore di contorno alle intestazioni
    for (int i = 0; i < cols; i++) {
        printf("+");
        for (int j = 0; j < widths[i] + 2; j++) printf("-");
    }
    printf("+\n");

    // Righe dei dati nel risultato della query
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            val = PQgetvalue(ris, i, j);

            printf("| %-*.*s ", widths[j], widths[j], val);
            /*
             * % = Allineamento testo a sx
             * (1) * = Larghezza minima della "cella"
             * (2) * = Larghezza massima della "cella"
             * s = Dato da inserire nella cella
             */
        }
        printf("|\n");
    }

    // Riga inferiore di contorno alla tabella
    for (int i = 0; i < cols; i++) {
        printf("+");
        for (int j = 0; j < widths[i] + 2; j++) printf("-");
    }
    printf("+\n");

    PQclear(ris);       // Pulizia del risultato di query
}

int main() {
    int scelta;
    int inUtente;     // Dato input per query parametrica
    char query[2048];

    PGconn *conn = PQconnectdb("dbname=palestra");

    // Errore nella connessione al database (parametri errati)
    if (PQstatus(conn) != CONNECTION_OK) {
        fprintf(stderr, "Errore di connessione: %s", PQerrorMessage(conn));
        PQfinish(conn);
        exit(1);
    }

    clean_console();
    do {
        printf("\n<><> MENU QUERY <><>\n"
               "0) ESCI\n"
               "1) Clienti con almeno n%% di debito per iscrizione attiva\n"
               "2) Clienti con minimo num. di assenze ai corsi\n"
               "3) Classifica degli abbonamenti con numero di sottoscrizioni\n"
               "4) Istruttori con piu' partecipanti presenti\n"
               "5) Manutenzioni attive per ciascuna sala\n"
               "Scelta utente:");
        scanf("%d", &scelta);
        clean_console();

        switch (scelta) {
            case 0:
                printf("...Uscita\n");
                break;

            case 1:
                /*
                 * Q1 Stampare tutti i clienti che devono ancora pagare alla struttura almeno il 50%
                 * del prezzo della propria quota di iscrizione attiva. Ordinare i clienti per “debito”
                 * più cospicuo.
                 */

                do {
                    printf("Inserire percentuale di soglia minima:");
                    scanf("%d", &inUtente);
                } while (inUtente < 0);

                sprintf(query, "SELECT c.CF, c.Nome, c.Cognome, i.DataInizio, i.DataFine, "
                               "SUM(p.Importo) AS TotalePagato, "
                               "ROUND(a.Prezzo * (1 - i.Sconto / 100.0), 2) AS PrezzoIscrizione, "
                               "(ROUND(a.Prezzo * (1 - i.Sconto / 100.0), 2) - SUM(p.Importo)) AS SaldoResiduo "
                               "FROM Cliente c "
                               "JOIN Iscrizione i ON c.CF = i.Cliente "
                               "JOIN Abbonamento a ON i.Abbonamento = a.Codice "
                               "JOIN Pagamento p ON i.Cliente = p.Cliente AND i.DataInizio = p.Iscrizione "
                               "WHERE i.DataFine >= CURRENT_DATE "
                               "GROUP BY c.CF, c.Nome, c.Cognome, i.DataInizio, i.DataFine, a.Prezzo, i.Sconto "
                               "HAVING ((a.Prezzo * (1 - i.Sconto / 100.0)) * (%.1f / 100.0)) <= (ROUND(a.Prezzo * (1 - i.Sconto / 100.0), 2) - SUM(p.Importo)) "
                               "ORDER BY SaldoResiduo DESC", (double)inUtente);

                Query(conn, query);
                break;

            case 2:
                /*
                 * Q2 Stampare i clienti con un numero minimo di assenze ai corsi ai quali si sono
                 * prenotati (num. min. assenze = dato input).
                 */

                do {
                    printf("Inserire minimo num. di assenze:");
                    scanf("%d", &inUtente);
                } while (inUtente <= 0);

                sprintf(query, "SELECT c.CF, c.Nome, c.Cognome, COUNT(*) AS Assenze "
                               "FROM Cliente c "
                               "JOIN Prenotazione p ON c.CF = p.Cliente "
                               "WHERE Presenza = FALSE "
                               "GROUP BY c.CF, c.Nome, c.Cognome "
                               "HAVING COUNT(*) >= %d", inUtente);
                Query(conn, query);
                break;

            case 3:
                /*
                 * Q3 Stampare per ciascun abbonamento, offerto dalla palestra, il numero di clienti
                 * che lo hanno sottoscritto. Ordinare i risultati in ordine decrescente.
                 */

                Query(conn, "SELECT a.*, COUNT(DISTINCT i.Cliente) AS Clienti "
                            "FROM Abbonamento a "
                            "LEFT JOIN Iscrizione i ON a.Codice = i.Abbonamento "
                            "GROUP BY a.Codice "
                            "ORDER BY Clienti DESC");
                break;

            case 4:
                /*
                 * Q4 Trovare l’istruttore (o gli istruttori) che hanno tenuto la lezione con
                 * il maggior numero di presenze effettive.
                 */

                Query(conn, "SELECT DISTINCT CF, Nome, Cognome, Num_prenotazioni "
                            "FROM ( "
                                    "SELECT I.CF, I.Nome, I.Cognome, COUNT(*) AS Num_prenotazioni "
                                    "FROM Istruttore I "
                                    "JOIN Lezione L ON I.CF = L.Istruttore "
                                    "JOIN Prenotazione P ON P.Lezione = L.DataOra AND P.Corso = L.Corso "
                                    "WHERE P.Presenza = TRUE "
                                    "GROUP BY I.CF, I.Nome, I.Cognome, L.Corso, L.DataOra "
                                    "HAVING COUNT(*) = ( "
                                            "SELECT MAX(Num_prenotazioni) FROM ( "
                                                    "SELECT COUNT(*) AS Num_prenotazioni "
                                                    "FROM Lezione L "
                                                    "JOIN Prenotazione P ON P.Lezione = L.DataOra AND P.Corso = L.Corso "
                                                    "WHERE P.Presenza = TRUE "
                                                    "GROUP BY L.Corso, L.Dataora "
                                            ") AS Prenotazioni "
                                    ") "
                            ")As IstruttoriTop");
                break;

            case 5:
                /*
                 * Q5 Calcolare il numero di manutenzioni attive per ciascuna sala, ordinandole dalla più
                 * “problematica” alla meno.
                 */

                Query(conn, "SELECT S.Nome, COUNT (*) AS Manutenzioni_Attive "
                            "FROM Sala S "
                            "JOIN Attrezzatura A ON A.Sala = S.Nome "
                            "JOIN Manutenzione M ON M.Attrezzatura = A.CodiceAttrezzatura "
                            "WHERE M.DataFine IS NULL "
                            "GROUP BY S.Nome "
                            "ORDER BY Manutenzioni_Attive DESC");
                break;

            default:
                printf("Scelta non valida!\n");
        }
    } while (scelta != 0);

    PQfinish(conn);     // Chiusura della connessione con database
    return 0;
}