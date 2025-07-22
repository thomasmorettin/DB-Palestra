import random
from datetime import datetime, timedelta, date
from faker import Faker

fake = Faker('it_IT')
#fake.seed_instance(0)
#random.seed(0)

def escape(value):
    if value is None:
        return 'NULL'
    if isinstance(value, str):
        return f"'{value.replace("'", "''")}'"
    elif isinstance(value, datetime):
        return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
    elif isinstance(value, date):
        return f"'{value.strftime('%Y-%m-%d')}'"
    elif isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    return str(value)

def insert_sql(table, rows):
    if not rows:
        return ""
    sql_lines = []
    for row in rows:
        non_null_items = {k: v for k, v in row.items() if v is not None}
        columns = ", ".join(non_null_items.keys())
        values = ", ".join(escape(v) for v in non_null_items.values())
        sql_lines.append(f"INSERT INTO {table} ({columns}) VALUES ({values});")
    return "\n".join(sql_lines) + "\n"

def generate_clients(n):
    clients = []
    for i in range(1, n + 1):
        clients.append({
            'CF': ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16)),
            'Nome': fake.first_name(),
            'Cognome': fake.last_name(),
            'DataNascita': fake.date_of_birth(minimum_age=18, maximum_age=70),
            'Telefono': fake.msisdn()[:10],
            'Email': fake.email(),
            'DataIscrizione': fake.date_between(start_date='-2y', end_date='today'),
            'NumIngressi': random.randint(1, 5)
        })
    return clients

def generate_checkins(clients):
    checkins = []
    for client in clients:
        for _ in range(client['NumIngressi']):
            checkins.append({
                'Cliente': client['CF'],
                'DataOraIngresso': fake.date_time_between(start_date='-30d', end_date='now')
            })
    return checkins

def generate_instructors(n):
    instructors = []
    for i in range(1, n + 1):
        instructors.append({
            'CF': ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16)),
            'Nome': fake.first_name(),
            'Cognome': fake.last_name(),
            'DataNascita': fake.date_of_birth(minimum_age=25, maximum_age=65),
            'Telefono': fake.msisdn()[:10],
            'Email': fake.email(),
            'Stipendio': round(random.uniform(1300.0, 3000.0), 2)
        })
    return instructors

def generate_abbonamenti():
    return [
        {'Codice': 1, 'Prezzo': 10.00, 'Durata': 1, 'AccessoLibero': True, 'AccessoCorsi': False},
        {'Codice': 2, 'Prezzo': 15.00, 'Durata': 1, 'AccessoLibero': False, 'AccessoCorsi': True},
        {'Codice': 3, 'Prezzo': 60.00, 'Durata': 1, 'AccessoLibero': True, 'AccessoCorsi': False},
        {'Codice': 4, 'Prezzo': 100.00, 'Durata': 1, 'AccessoLibero': False, 'AccessoCorsi': True},
        {'Codice': 5, 'Prezzo': 250.00, 'Durata': 6, 'AccessoLibero': True, 'AccessoCorsi': False},
        {'Codice': 6, 'Prezzo': 350.00, 'Durata': 6, 'AccessoLibero': False, 'AccessoCorsi': True},
        {'Codice': 7, 'Prezzo': 400.00, 'Durata': 12, 'AccessoLibero': True, 'AccessoCorsi': False},
        {'Codice': 8, 'Prezzo': 450.00, 'Durata': 12, 'AccessoLibero': False, 'AccessoCorsi': True},
    ]

def generate_certificati_medici(clients):
    certificati = []
    for c in clients:
        rilascio = fake.date_between(start_date='-1y', end_date='-1d')
        certificati.append({
            'Cliente': c['CF'],
            'DataRilascio': rilascio,
            'Scadenza': rilascio + timedelta(days=365),
            'Dottore': 'Dr. ' + fake.name()
        })
    return certificati

def generate_iscrizioni(clienti, abbonamenti):
    iscrizioni = []
    for c in clienti:
        ab1 = random.choice(abbonamenti[:6])
        ab2 = random.choice(abbonamenti[5:])
        inizio1 = fake.date_between(start_date='-2y', end_date='-18M')
        inizio2 = fake.date_between(start_date='-17M', end_date='now')

        if (ab1['Codice'] == 1 or ab1['Codice'] == 2): durata = inizio1 + timedelta(days=ab1['Durata'])
        else: durata = inizio1 + timedelta(days=ab1['Durata'] * 30)
        
        iscrizioni.append({
            'Cliente': c['CF'], 'DataInizio': inizio1, 'Sconto': random.choice([0, 10, 15]),
            'DataFine': durata, 'Abbonamento': ab1['Codice']
        })
        iscrizioni.append({
            'Cliente': c['CF'], 'DataInizio': inizio2, 'Sconto': random.choice([0, 5, 20]),
            'DataFine': inizio2 + timedelta(days=ab2['Durata'] * 30), 'Abbonamento': ab2['Codice']
        })
    return iscrizioni

def generate_pagamenti(iscrizioni, abbonamenti):
    pagamenti = []
    for i in iscrizioni:
        prezzo = next(a['Prezzo'] for a in abbonamenti if a['Codice'] == i['Abbonamento'])
        sconto = i['Sconto']
        totale_scontato = prezzo * (1 - sconto / 100)
        if (totale_scontato % 4) == 0:
            rata = round(totale_scontato / 4, 2)
            for r in range(random.randint(1, 4)):
                pagamenti.append({
                    'Cliente': i['Cliente'],
                    'Iscrizione': i['DataInizio'],
                    'NumRata': r,
                    'Metodo': random.choice(['Contanti', 'Elettronico']),
                    'Data': i['DataInizio'] + timedelta(days=10 * r),
                    'Importo': rata
                })
        else:
            rata = round(totale_scontato / 2, 2)
            for r in range(random.randint(1, 2)):
                pagamenti.append({
                    'Cliente': i['Cliente'],
                    'Iscrizione': i['DataInizio'],
                    'NumRata': r,
                    'Metodo': random.choice(['Contanti', 'Elettronico']),
                    'Data': i['DataInizio'] + timedelta(days=10 * r),
                    'Importo': rata
                })
    return pagamenti

def generate_schede(iscrizioni, abbonamenti, clienti):
    schede = []
    codice = 1
    clienti_con_iscrizione_libera = {i['Cliente'] for i in iscrizioni if next(ab for ab in abbonamenti if ab['Codice'] == i['Abbonamento'])['AccessoLibero']}
    for cliente in clienti:
        if cliente['CF'] in clienti_con_iscrizione_libera:
            schede.append({
                'Codice': codice,
                'Tipologia': random.choice(['Massa', 'Tonificazione']),
                'DataCreazione': fake.date_between(start_date=[i for i in iscrizioni if i['Cliente'] == cliente['CF']][-1]['DataInizio'], end_date=[i for i in iscrizioni if i['Cliente'] == cliente['CF']][-1]['DataFine']),
                'Cliente': cliente['CF']
            })
            codice += 1
    return schede

def generate_sale():
    return [
        {'Nome': 'Sala A', 'Tipo': 'Sala corsi', 'Capienza': 30},
        {'Nome': 'Sala B', 'Tipo': 'Sala attrezzi', 'Capienza': 25},
        {'Nome': 'Sala C', 'Tipo': 'Sala corsi', 'Capienza': 20},
        {'Nome': 'Sala D', 'Tipo': 'Sala corsi', 'Capienza': 50},
        {'Nome': 'Sala E', 'Tipo': 'Sala attrezzi', 'Capienza': 50},
    ]

def generate_attrezzature(sale):
    tipi = ['A carico', 'Isotonico', 'Cardio', 'Funzionale']
    attrezzature = []
    codice = 1
    for sala in sale:
        for _ in range(30):
            attrezzature.append({
                'CodiceAttrezzatura': codice,
                'Nome': f'Attrezzo {codice}',
                'Tipo': random.choice(tipi),
                'Sala': sala['Nome']
            })
            codice += 1
    return attrezzature

def generate_manutenzioni(attrezzature):
    manutenzioni = []
    for att in attrezzature:
        for i in range(2):
            start = fake.date_between(start_date='-6M', end_date='today')
            if (datetime.now().date() - start).days < 30:
                if random.random() < 0.7:  # 70% delle manutenzioni recenti sono ancora aperte
                    data_fine = None
                else:
                    data_fine = fake.date_between(start_date=start + timedelta(days=1), end_date=datetime.today().date())
            else:
                if start + timedelta(days=1) >= datetime.today().date():
                    data_fine = None
                else:
                    data_fine = fake.date_between(start_date=start + timedelta(days=1), end_date=datetime.today().date())
            manutenzioni.append({
                'Attrezzatura': att['CodiceAttrezzatura'],
                'DataInizio': start,
                'Descrizione': f'Manutenzione {i}',
                'DataFine': data_fine
            })
    return manutenzioni

def generate_corsi(sale):
    livelli = ['Base', 'Intermedio', 'Avanzato']
    corsi = []
    for i in range(1, 11):
        corsi.append({
            'Nome': f'Corso {i}',
            'DurataLezione': random.choice([45, 60, 90]),
            'Descrizione': fake.sentence(nb_words=6),
            'Livello': random.choice(livelli),
            'Sala': random.choice([s['Nome'] for s in sale if s['Tipo'] == 'Sala corsi'])
        })
    return corsi

def generate_lezioni(corsi, istruttori, certificazioni):
    lezioni = []
    # Seleziona solo gli istruttori con qualifica idonea
    istruttori_specializzati = [i['CF'] for i in istruttori if any(q in ['Istruttore cardio', 'Istruttore mobilità'] for q in [cert['Specializzazione'] for cert in certificazioni if cert['Istruttore'] == i['CF']])]
    for corso in corsi:
        num_lezioni = random.randint(1, 10)
        for _ in range(num_lezioni):
            lezioni.append({
                'Corso': corso['Nome'],
                'DataOra': fake.date_time_between(start_date='-6M', end_date='-1d'),
                'Istruttore': random.choice(istruttori_specializzati)
            })
    return lezioni

def generate_prenotazioni(lezioni, clienti, iscrizioni, abbonamenti):
    prenotazioni = []
    clienti_abilitati = []
    for c in clienti:
        iscrizioni_cliente = [i for i in iscrizioni if i['Cliente'] == c['CF']]
        if iscrizioni_cliente:
            seconda = iscrizioni_cliente[-1]
            abbonamento = next((a for a in abbonamenti if a['Codice'] == seconda['Abbonamento']), None)
            if abbonamento and abbonamento['AccessoCorsi']:
                clienti_abilitati.append(c['CF'])

    for cf in clienti_abilitati:
        lezioni_scelte = random.sample(lezioni, k=random.randint(1, min(len(lezioni), 7)))
        for lezione in lezioni_scelte:
            prenotazioni.append({
                'Corso': lezione['Corso'],
                'Lezione': lezione['DataOra'],
                'Cliente': cf,
                'Presenza': random.choice([True, False])
            })

    return prenotazioni

def generate_certificazioni_sportive(istruttori):
    specializzazioni = ['Personal trainer', 'Istruttore cardio', 'Istruttore mobilità']
    certificazioni = []
    for istr in istruttori:
        num_cert = random.randint(1, 2)
        chosen_specs = random.sample(specializzazioni, num_cert)
        for spec in chosen_specs:
            data_rilascio = fake.date_between(start_date='-3y', end_date='-1y')
            certificazioni.append({
                'Istruttore': istr['CF'],
                'DataRilascio': data_rilascio,
                'Specializzazione': spec,
                'EnteCertificatore': fake.company(),
                'Scadenza': data_rilascio + timedelta(days=3*365)
            })
    return certificazioni

def generate_esercizi(n):
    esercizi = []

    steps = ''
    for i in range(random.randint(1, 4)): steps += f'Step {i}: ...'
    for i in range(1, n + 1):
        esercizi.append({
            'Nome': f'Esercizio {i}',
            'StepsSvolgimento': steps
        })
    return esercizi

def generate_comporre(schede, esercizi):
    comporre = []
    for scheda in schede:
        esercizi_scheda = random.sample(esercizi, 10)
        for es in esercizi_scheda:
            comporre.append({
                'Scheda': scheda['Codice'],
                'Esercizio': es['Nome'],
                'Note': fake.sentence(nb_words=6),
                'SerieRipetizioni': f"{random.randint(3, 5)}x{random.randint(8, 15)}",
                'Recupero': random.choice([30, 60, 90])
            })
    return comporre

def main():
    clienti = generate_clients(300)
    checkin = generate_checkins(clienti)
    istruttori = generate_instructors(30)
    abbonamenti = generate_abbonamenti()
    certificati = generate_certificati_medici(clienti)
    iscrizioni = generate_iscrizioni(clienti, abbonamenti)
    pagamenti = generate_pagamenti(iscrizioni, abbonamenti)
    schede = generate_schede(iscrizioni, abbonamenti, clienti)
    sale = generate_sale()
    attrezzature = generate_attrezzature(sale)
    manutenzioni = generate_manutenzioni(attrezzature)
    corsi = generate_corsi(sale)
    certificazioni = generate_certificazioni_sportive(istruttori)
    lezioni = generate_lezioni(corsi, istruttori, certificazioni)
    prenotazioni = generate_prenotazioni(lezioni, clienti, iscrizioni, abbonamenti)
    esercizi = generate_esercizi(50)
    comporre = generate_comporre(schede, esercizi)

    sql_output = ""
    sql_output += insert_sql("Cliente", clienti)
    sql_output += insert_sql("CheckIn", checkin)
    sql_output += insert_sql("Istruttore", istruttori)
    sql_output += insert_sql("Abbonamento", abbonamenti)
    sql_output += insert_sql("CertificatoMedico", certificati)
    sql_output += insert_sql("Iscrizione", iscrizioni)
    sql_output += insert_sql("Pagamento", pagamenti)
    sql_output += insert_sql("Scheda", schede)
    sql_output += insert_sql("Sala", sale)
    sql_output += insert_sql("Attrezzatura", attrezzature)
    sql_output += insert_sql("Manutenzione", manutenzioni)
    sql_output += insert_sql("Corso", corsi)
    sql_output += insert_sql("Lezione", lezioni)
    sql_output += insert_sql("Prenotazione", prenotazioni)
    sql_output += insert_sql("CertificazioneSportiva", certificazioni)
    sql_output += insert_sql("Esercizio", esercizi)
    sql_output += insert_sql("Comporre", comporre)

    with open("popolamento_palestra.sql", "w", encoding="utf-8") as f:
        f.write(sql_output)

    print("Script di popolamento generato con successo.")

if __name__ == "__main__":
    main()
