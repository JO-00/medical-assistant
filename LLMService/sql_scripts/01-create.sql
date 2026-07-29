-- Table medecin
CREATE TABLE medecin (
    id_medecin SERIAL PRIMARY KEY,
    nom VARCHAR(255),
    prenom VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255),
    specialite VARCHAR(255),
    phone_number VARCHAR(50),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table patient
CREATE TABLE patient (
    id_patient SERIAL PRIMARY KEY,
    nom VARCHAR(255),
    prenom VARCHAR(255),
    date_naissance DATE,
    genre VARCHAR(1),
    email VARCHAR(255),
    id_medecin INTEGER REFERENCES medecin(id_medecin),
    date_premiere_visite TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    numero_dossier VARCHAR(255)
);

-- Table acte_medecin
CREATE TABLE acte_medecin (
    id SERIAL PRIMARY KEY,
    acte VARCHAR(255),
    duree INTEGER,
    prix NUMERIC(19,2),
    id_medecin INTEGER REFERENCES medecin(id_medecin),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    flag_actif BOOLEAN DEFAULT TRUE
);

-- Table rdv (rendez-vous)
CREATE TABLE rdv (
    id_rdv SERIAL PRIMARY KEY,
    date_rdv TIMESTAMP,
    duree INTEGER,
    motif VARCHAR(255),
    etat INTEGER DEFAULT 0,
    prix_acte NUMERIC(19,2),
    id_patient INTEGER NOT NULL REFERENCES patient(id_patient),
    id_medecin INTEGER NOT NULL REFERENCES medecin(id_medecin),
    id_acte INTEGER REFERENCES acte_medecin(id),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_last_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table note_patient
CREATE TABLE note_patient (
    id SERIAL PRIMARY KEY,
    note_medecin VARCHAR(1000),
    id_patient INTEGER REFERENCES patient(id_patient),
    id_medecin INTEGER REFERENCES medecin(id_medecin),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les recherches fréquentes
CREATE INDEX idx_patient_medecin ON patient(id_medecin);
CREATE INDEX idx_rdv_medecin ON rdv(id_medecin);
CREATE INDEX idx_rdv_patient ON rdv(id_patient);
CREATE INDEX idx_rdv_date ON rdv(date_rdv);
CREATE INDEX idx_note_patient_patient ON note_patient(id_patient);
CREATE INDEX idx_note_patient_medecin ON note_patient(id_medecin);

