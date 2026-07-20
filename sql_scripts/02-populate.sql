-- ============================================================
-- 1. MEDECIN INSERTIONS (10 doctors)
-- ============================================================
-- Populate medecin table with doctors and their hashed passwords
-- Passwords: 
-- sophie.martin@cabinet.fr -> password123
-- jean.bernard@cabinet.fr -> sussy_boi
-- marie.dubois@cabinet.fr -> secret456
-- pierre.petit@cabinet.fr -> kingdom789
-- claire.lefevre@cabinet.fr -> confidential
-- thomas.moreau@cabinet.fr -> dont_show
-- isabelle.roux@cabinet.fr -> secret123
-- antoine.garcia@cabinet.fr -> hidden
-- catherine.david@cabinet.fr -> hide_me
-- nicolas.bertrand@cabinet.fr -> suspicious

INSERT INTO public.medecin (
    id_medecin, 
    nom, 
    prenom, 
    genre, 
    email, 
    password,
    date_debut_convention, 
    etat,
    date_creation,
    date_last_maj,
    flag_inscri_portail
) VALUES
(1, 'Martin', 'Sophie', 'F', 'sophie.martin@cabinet.fr', '$2b$12$FuLJp7T6R1ncgQkyegk2SeYxr6YSNT/EcAD4hZP6WuA8O8.64Cc82', '2020-01-01 00:00:00', 1, NOW(), NOW(), true),
(2, 'Bernard', 'Jean', 'M', 'jean.bernard@cabinet.fr', '$2b$12$3ObVeM0PmC3WoPjf6lzCzO0OYKjBj5OxCtHl1bk70cnbOMPbmTRJW', '2020-01-01 00:00:00', 1, NOW(), NOW(), true),
(3, 'Dubois', 'Marie', 'F', 'marie.dubois@cabinet.fr', '$2b$12$lZjJwnFAMYNqGA4wkRrIRu/iH2YtGbY3Q3MW.7h1m7vOrJr4.TkMm', '2020-01-01 00:00:00', 1, NOW(), NOW(), true),
(4, 'Petit', 'Pierre', 'M', 'pierre.petit@cabinet.fr', '$2b$12$Jb.bGdVc8ywyKmvQm6mKQeNnIFLmSBqe1ft3mYPHH5ZgZFybCsDia', '2020-01-01 00:00:00', 1, NOW(), NOW(), true),
(5, 'Lefevre', 'Claire', 'F', 'claire.lefevre@cabinet.fr', '$2b$12$lB92h3hOps8aqoM.r2oSK.lfE7btCaB36523RtrS0kihlKFNP/zFS', '2020-01-01 00:00:00', 1, NOW(), NOW(), true),
(6, 'Moreau', 'Thomas', 'M', 'thomas.moreau@cabinet.fr', '$2b$12$upb9sgmoidZxDkqyGxvO6OV8wF4Q79vIPn3tg.aQ8iSw4DKCob4ui', '2020-01-01 00:00:00', 1, NOW(), NOW(), true),
(7, 'Roux', 'Isabelle', 'F', 'isabelle.roux@cabinet.fr', '$2b$12$DKrrIotofYRbvlH4RMCUwOi30UihEq2nTEl35plz3KwcTP75UYzO.', '2020-01-01 00:00:00', 1, NOW(), NOW(), true),
(8, 'Garcia', 'Antoine', 'M', 'antoine.garcia@cabinet.fr', '$2b$12$p2LJ9awQ8HbB4gWMJvFxLuttEjLDHt2WliWVWahtpQxV0uawf6E86', '2020-01-01 00:00:00', 1, NOW(), NOW(), true),
(9, 'David', 'Catherine', 'F', 'catherine.david@cabinet.fr', '$2b$12$mxPoOFmfkZb1PSgkJjgEFOI0jLImx6i1XzitHtue7jYuEYLvTKzI6', '2020-01-01 00:00:00', 1, NOW(), NOW(), true),
(10, 'Bertrand', 'Nicolas', 'M', 'nicolas.bertrand@cabinet.fr', '$2b$12$y95702KHyq5y3d5R4p0N7.FqykYawFWtD1r78pXG5PFRGlW9lktGS', '2020-01-01 00:00:00', 1, NOW(), NOW(), true);

-- Reset the sequence to continue from the next ID
SELECT setval('medecin_id_medecin_seq', 10, true);

-- ============================================================
-- 2. PATIENT INSERTIONS (50 patients)
-- ============================================================
INSERT INTO public.patient (id_patient, nom, prenom, date_naissance, genre, email, id_medecin) VALUES
(1, 'Dupont', 'Lucas', '1990-05-15', 'M', 'lucas.dupont@gmail.com', 1),
(2, 'Lambert', 'Emma', '1985-08-22', 'F', 'emma.lambert@gmail.com', 1),
(3, 'Durand', 'Hugo', '2000-11-30', 'M', 'hugo.durand@gmail.com', 2),
(4, 'Morel', 'Lea', '1995-03-10', 'F', 'lea.morel@gmail.com', 2),
(5, 'Fournier', 'Maxime', '1988-07-19', 'M', 'maxime.fournier@gmail.com', 3),
(6, 'Girard', 'Chloe', '1992-09-25', 'F', 'chloe.girard@gmail.com', 3),
(7, 'Leroy', 'Nathan', '2001-12-05', 'M', 'nathan.leroy@gmail.com', 4),
(8, 'Rousseau', 'Julie', '1993-04-18', 'F', 'julie.rousseau@gmail.com', 4),
(9, 'Robin', 'Arthur', '1986-06-28', 'M', 'arthur.robin@gmail.com', 5),
(10, 'Mercier', 'Sarah', '1998-10-14', 'F', 'sarah.mercier@gmail.com', 5),
(11, 'Blanc', 'Louis', '1991-02-08', 'M', 'louis.blanc@gmail.com', 6),
(12, 'Chevalier', 'Alice', '1983-11-20', 'F', 'alice.chevalier@gmail.com', 6),
(13, 'Francois', 'Ethan', '2002-07-03', 'M', 'ethan.francois@gmail.com', 7),
(14, 'Boyer', 'Camille', '1996-05-12', 'F', 'camille.boyer@gmail.com', 7),
(15, 'Dumas', 'Raphael', '1989-09-17', 'M', 'raphael.dumas@gmail.com', 8),
(16, 'Leclerc', 'Manon', '1994-12-24', 'F', 'manon.leclerc@gmail.com', 8),
(17, 'Gautier', 'Jules', '2000-03-15', 'M', 'jules.gautier@gmail.com', 9),
(18, 'Muller', 'Lina', '1987-08-30', 'F', 'lina.muller@gmail.com', 9),
(19, 'Fontaine', 'Leo', '1997-06-09', 'M', 'leo.fontaine@gmail.com', 10),
(20, 'Marchand', 'Zoe', '1990-01-25', 'F', 'zoe.marchand@gmail.com', 10),
(21, 'Colin', 'Gabin', '1984-10-11', 'M', 'gabin.colin@gmail.com', 1),
(22, 'Renaud', 'Eva', '1999-05-08', 'F', 'eva.renaud@gmail.com', 2),
(23, 'Lemaire', 'Mael', '1992-02-14', 'M', 'mael.lemaire@gmail.com', 3),
(24, 'Noel', 'Iris', '1986-09-22', 'F', 'iris.noel@gmail.com', 4),
(25, 'Meyer', 'Liam', '2001-07-19', 'M', 'liam.meyer@gmail.com', 5),
(26, 'Schmitt', 'Mila', '1995-12-03', 'F', 'mila.schmitt@gmail.com', 6),
(27, 'Weber', 'Sacha', '1988-04-27', 'M', 'sacha.weber@gmail.com', 7),
(28, 'Klein', 'Elena', '1993-08-16', 'F', 'elena.klein@gmail.com', 8),
(29, 'Wagner', 'Valentin', '2000-11-11', 'M', 'valentin.wagner@gmail.com', 9),
(30, 'Fischer', 'Louise', '1985-01-20', 'F', 'louise.fischer@gmail.com', 10),
(31, 'Bauer', 'Eliott', '1997-06-30', 'M', 'eliott.bauer@gmail.com', 1),
(32, 'Adam', 'Rose', '1991-10-05', 'F', 'rose.adam@gmail.com', 2),
(33, 'Henry', 'Marius', '1989-03-18', 'M', 'marius.henry@gmail.com', 3),
(34, 'Vincent', 'Nina', '1998-09-12', 'F', 'nina.vincent@gmail.com', 4),
(35, 'Rolland', 'Oscar', '1994-07-07', 'M', 'oscar.rolland@gmail.com', 5),
(36, 'Gauthier', 'Lila', '1987-02-28', 'F', 'lila.gauthier@gmail.com', 6),
(37, 'Poulain', 'Leon', '2002-05-16', 'M', 'leon.poulain@gmail.com', 7),
(38, 'Delahaye', 'Alma', '1996-11-19', 'F', 'alma.delahaye@gmail.com', 8),
(39, 'Lucas', 'Malo', '1990-08-24', 'M', 'malo.lucas@gmail.com', 9),
(40, 'Benoit', 'Adele', '1984-03-13', 'F', 'adele.benoit@gmail.com', 10),
(41, 'Clement', 'Tristan', '1993-12-08', 'M', 'tristan.clement@gmail.com', 1),
(42, 'Morvan', 'Luna', '1999-07-01', 'F', 'luna.morvan@gmail.com', 2),
(43, 'Garnier', 'Enzo', '1995-04-04', 'M', 'enzo.garnier@gmail.com', 3),
(44, 'Faure', 'Elise', '1988-09-26', 'F', 'elise.faure@gmail.com', 4),
(45, 'Delmas', 'Gaspard', '2001-01-17', 'M', 'gaspard.delmas@gmail.com', 5),
(46, 'Martel', 'Ines', '1992-06-21', 'F', 'ines.martel@gmail.com', 6),
(47, 'Langlois', 'Noe', '1986-10-09', 'M', 'noe.langlois@gmail.com', 7),
(48, 'Leblanc', 'Alice', '1997-03-02', 'F', 'alice.leblanc@gmail.com', 8),
(49, 'Perrin', 'Romain', '1991-11-30', 'M', 'romain.perrin@gmail.com', 9),
(50, 'Guillon', 'Clara', '1998-08-14', 'F', 'clara.guillon@gmail.com', 10);

-- ============================================================
-- 3. ACTE_MEDECIN INSERTIONS (3 acts per doctor)
-- ============================================================
INSERT INTO public.acte_medecin (id, acte, duree, prix, id_medecin, date_creation, date_last_maj) VALUES
-- Doctor 1 (Sophie Martin)
(1, 'Consultation générale', 30, 45.00, 1, NOW(), NOW()),
(2, 'Électrocardiogramme', 45, 80.00, 1, NOW(), NOW()),
(3, 'Vaccination', 15, 25.00, 1, NOW(), NOW()),
-- Doctor 2 (Jean Bernard)
(4, 'Consultation cardiologie', 40, 60.00, 2, NOW(), NOW()),
(5, 'Échocardiographie', 60, 120.00, 2, NOW(), NOW()),
(6, 'Test d''effort', 50, 90.00, 2, NOW(), NOW()),
-- Doctor 3 (Marie Dubois)
(7, 'Consultation dermatologie', 30, 50.00, 3, NOW(), NOW()),
(8, 'Examen de la peau', 45, 75.00, 3, NOW(), NOW()),
(9, 'Cryothérapie', 20, 100.00, 3, NOW(), NOW()),
-- Doctor 4 (Pierre Petit)
(10, 'Consultation pédiatrie', 35, 50.00, 4, NOW(), NOW()),
(11, 'Suivi de croissance', 30, 40.00, 4, NOW(), NOW()),
(12, 'Vaccin enfant', 15, 25.00, 4, NOW(), NOW()),
-- Doctor 5 (Claire Lefevre)
(13, 'Consultation gynécologie', 45, 55.00, 5, NOW(), NOW()),
(14, 'Examen pelvien', 30, 65.00, 5, NOW(), NOW()),
(15, 'Échographie mammaire', 60, 110.00, 5, NOW(), NOW()),
-- Doctor 6 (Thomas Moreau)
(16, 'Consultation orthopédie', 40, 55.00, 6, NOW(), NOW()),
(17, 'Infiltration', 30, 85.00, 6, NOW(), NOW()),
(18, 'Rééducation', 45, 70.00, 6, NOW(), NOW()),
-- Doctor 7 (Isabelle Roux)
(19, 'Consultation ophtalmologie', 30, 50.00, 7, NOW(), NOW()),
(20, 'Examen visuel', 45, 75.00, 7, NOW(), NOW()),
(21, 'Fond d''œil', 25, 95.00, 7, NOW(), NOW()),
-- Doctor 8 (Antoine Garcia)
(22, 'Consultation ORL', 30, 50.00, 8, NOW(), NOW()),
(23, 'Audiométrie', 40, 70.00, 8, NOW(), NOW()),
(24, 'Examen du nez', 20, 45.00, 8, NOW(), NOW()),
-- Doctor 9 (Catherine David)
(25, 'Consultation rhumatologie', 45, 55.00, 9, NOW(), NOW()),
(26, 'Examen articulaire', 35, 65.00, 9, NOW(), NOW()),
(27, 'Échographie des tendons', 50, 100.00, 9, NOW(), NOW()),
-- Doctor 10 (Nicolas Bertrand)
(28, 'Consultation généraliste', 30, 45.00, 10, NOW(), NOW()),
(29, 'Prise de sang', 20, 30.00, 10, NOW(), NOW()),
(30, 'ECG', 40, 70.00, 10, NOW(), NOW());


-- Re-insert with id_acte included
INSERT INTO public.rdv (id_rdv, date_rdv, duree, motif, etat, id_patient, id_medecin, id_acte, date_creation, date_last_maj) VALUES
-- Doctor 1 (Sophie Martin)
(1, '2026-07-20 09:00:00', 30, 'Consultation annuelle', 2, 1, 1, 1, NOW(), NOW()),
(2, '2026-07-20 09:30:00', 30, 'Suivi traitement', 2, 2, 1, 1, NOW(), NOW()),
(3, '2026-07-20 10:30:00', 45, 'ECG de contrôle', 1, 21, 1, 2, NOW(), NOW()),
(4, '2026-07-21 08:30:00', 30, 'Consultation', 2, 31, 1, 1, NOW(), NOW()),
(5, '2026-07-21 09:30:00', 15, 'Vaccination', 3, 41, 1, 3, NOW(), NOW()),
(6, '2026-07-21 10:30:00', 30, 'Renouvellement ordonnance', 2, 1, 1, 1, NOW(), NOW()),
(7, '2026-07-22 09:00:00', 30, 'Consultation', 1, 2, 1, 1, NOW(), NOW()),
(8, '2026-07-22 10:00:00', 45, 'Bilan cardiologique', 2, 21, 1, 2, NOW(), NOW()),
(9, '2026-07-23 08:30:00', 30, 'Suivi', 3, 31, 1, 3, NOW(), NOW()),
(10, '2026-07-23 09:30:00', 30, 'Consultation', 2, 41, 1, 1, NOW(), NOW()),
-- Doctor 2 (Jean Bernard)
(11, '2026-07-20 09:00:00', 40, 'Consultation cardiologie', 2, 3, 2, 4, NOW(), NOW()),
(12, '2026-07-20 10:00:00', 60, 'Échographie cardiaque', 1, 4, 2, 5, NOW(), NOW()),
(13, '2026-07-20 14:00:00', 50, 'Test d''effort', 2, 22, 2, 6, NOW(), NOW()),
(14, '2026-07-21 09:00:00', 40, 'Suivi post-opératoire', 3, 32, 2, 4, NOW(), NOW()),
(15, '2026-07-21 10:00:00', 40, 'Consultation', 2, 42, 2, 4, NOW(), NOW()),
(16, '2026-07-21 11:00:00', 60, 'Échocardiographie', 1, 3, 2, 5, NOW(), NOW()),
(17, '2026-07-22 09:30:00', 40, 'Consultation', 2, 4, 2, 4, NOW(), NOW()),
(18, '2026-07-22 10:30:00', 50, 'Test d''effort', 3, 22, 2, 6, NOW(), NOW()),
(19, '2026-07-23 09:00:00', 40, 'Consultation', 2, 32, 2, 4, NOW(), NOW()),
(20, '2026-07-23 10:00:00', 40, 'Suivi', 2, 42, 2, 4, NOW(), NOW()),
-- Doctor 3 (Marie Dubois)
(21, '2026-07-20 09:00:00', 30, 'Consultation dermatologie', 2, 5, 3, 7, NOW(), NOW()),
(22, '2026-07-20 09:30:00', 45, 'Examen de la peau', 1, 6, 3, 8, NOW(), NOW()),
(23, '2026-07-20 14:00:00', 20, 'Cryothérapie', 2, 23, 3, 9, NOW(), NOW()),
(24, '2026-07-21 09:00:00', 30, 'Consultation', 3, 33, 3, 7, NOW(), NOW()),
(25, '2026-07-21 09:30:00', 45, 'Examen complet', 2, 43, 3, 7, NOW(), NOW()),
(26, '2026-07-21 14:00:00', 20, 'Cryothérapie', 1, 5, 3, 9, NOW(), NOW()),
(27, '2026-07-22 09:00:00', 30, 'Consultation', 2, 6, 3, 7, NOW(), NOW()),
(28, '2026-07-22 09:30:00', 45, 'Examen', 2, 23, 3, 8, NOW(), NOW()),
(29, '2026-07-23 09:00:00', 30, 'Suivi', 3, 33, 3, 7, NOW(), NOW()),
(30, '2026-07-23 09:30:00', 30, 'Consultation', 2, 43, 3, 7, NOW(), NOW()),
-- Doctor 4 (Pierre Petit)
(31, '2026-07-20 09:00:00', 35, 'Consultation pédiatrique', 2, 7, 4, 10, NOW(), NOW()),
(32, '2026-07-20 09:35:00', 30, 'Suivi de croissance', 1, 8, 4, 11, NOW(), NOW()),
(33, '2026-07-20 14:00:00', 15, 'Vaccination', 2, 24, 4, 12, NOW(), NOW()),
(34, '2026-07-21 09:00:00', 35, 'Consultation', 3, 34, 4, 10, NOW(), NOW()),
(35, '2026-07-21 09:35:00', 30, 'Suivi', 2, 44, 4, 10, NOW(), NOW()),
(36, '2026-07-21 14:00:00', 15, 'Vaccin', 1, 7, 4, 12, NOW(), NOW()),
(37, '2026-07-22 09:00:00', 35, 'Consultation', 2, 8, 4, 10, NOW(), NOW()),
(38, '2026-07-22 09:35:00', 30, 'Suivi', 2, 24, 4, 11, NOW(), NOW()),
(39, '2026-07-23 09:00:00', 35, 'Consultation', 3, 34, 4, 10, NOW(), NOW()),
(40, '2026-07-23 09:35:00', 30, 'Suivi', 2, 44, 4, 10, NOW(), NOW()),
-- Doctor 5 (Claire Lefevre)
(41, '2026-07-20 09:00:00', 45, 'Consultation gynécologie', 2, 9, 5, 13, NOW(), NOW()),
(42, '2026-07-20 10:00:00', 30, 'Examen pelvien', 1, 10, 5, 14, NOW(), NOW()),
(43, '2026-07-20 14:00:00', 60, 'Échographie mammaire', 2, 25, 5, 15, NOW(), NOW()),
(44, '2026-07-21 09:00:00', 45, 'Consultation', 3, 35, 5, 13, NOW(), NOW()),
(45, '2026-07-21 10:00:00', 30, 'Examen', 2, 45, 5, 13, NOW(), NOW()),
(46, '2026-07-21 14:00:00', 60, 'Échographie', 1, 9, 5, 15, NOW(), NOW()),
(47, '2026-07-22 09:00:00', 45, 'Consultation', 2, 10, 5, 13, NOW(), NOW()),
(48, '2026-07-22 10:00:00', 30, 'Examen', 2, 25, 5, 14, NOW(), NOW()),
(49, '2026-07-23 09:00:00', 45, 'Suivi', 3, 35, 5, 13, NOW(), NOW()),
(50, '2026-07-23 10:00:00', 30, 'Consultation', 2, 45, 5, 13, NOW(), NOW()),
-- Doctor 6 (Thomas Moreau)
(51, '2026-07-20 09:00:00', 40, 'Consultation orthopédie', 2, 11, 6, 16, NOW(), NOW()),
(52, '2026-07-20 10:00:00', 30, 'Infiltration', 1, 12, 6, 17, NOW(), NOW()),
(53, '2026-07-20 14:00:00', 45, 'Rééducation', 2, 26, 6, 18, NOW(), NOW()),
(54, '2026-07-21 09:00:00', 40, 'Consultation', 3, 36, 6, 16, NOW(), NOW()),
(55, '2026-07-21 10:00:00', 30, 'Infiltration', 2, 46, 6, 16, NOW(), NOW()),
(56, '2026-07-21 14:00:00', 45, 'Rééducation', 1, 11, 6, 18, NOW(), NOW()),
(57, '2026-07-22 09:00:00', 40, 'Consultation', 2, 12, 6, 16, NOW(), NOW()),
(58, '2026-07-22 10:00:00', 30, 'Infiltration', 2, 26, 6, 17, NOW(), NOW()),
(59, '2026-07-23 09:00:00', 40, 'Consultation', 3, 36, 6, 16, NOW(), NOW()),
(60, '2026-07-23 10:00:00', 40, 'Suivi', 2, 46, 6, 16, NOW(), NOW()),
-- Doctor 7 (Isabelle Roux)
(61, '2026-07-20 09:00:00', 30, 'Consultation ophtalmologie', 2, 13, 7, 19, NOW(), NOW()),
(62, '2026-07-20 09:30:00', 45, 'Examen visuel', 1, 14, 7, 20, NOW(), NOW()),
(63, '2026-07-20 14:00:00', 25, 'Fond d''œil', 2, 27, 7, 21, NOW(), NOW()),
(64, '2026-07-21 09:00:00', 30, 'Consultation', 3, 37, 7, 19, NOW(), NOW()),
(65, '2026-07-21 09:30:00', 45, 'Examen', 2, 47, 7, 19, NOW(), NOW()),
(66, '2026-07-21 14:00:00', 25, 'Fond d''œil', 1, 13, 7, 21, NOW(), NOW()),
(67, '2026-07-22 09:00:00', 30, 'Consultation', 2, 14, 7, 19, NOW(), NOW()),
(68, '2026-07-22 09:30:00', 45, 'Examen', 2, 27, 7, 20, NOW(), NOW()),
(69, '2026-07-23 09:00:00', 30, 'Suivi', 3, 37, 7, 19, NOW(), NOW()),
(70, '2026-07-23 09:30:00', 30, 'Consultation', 2, 47, 7, 19, NOW(), NOW()),
-- Doctor 8 (Antoine Garcia)
(71, '2026-07-20 09:00:00', 30, 'Consultation ORL', 2, 15, 8, 22, NOW(), NOW()),
(72, '2026-07-20 09:30:00', 40, 'Audiométrie', 1, 16, 8, 23, NOW(), NOW()),
(73, '2026-07-20 14:00:00', 20, 'Examen du nez', 2, 28, 8, 24, NOW(), NOW()),
(74, '2026-07-21 09:00:00', 30, 'Consultation', 3, 38, 8, 22, NOW(), NOW()),
(75, '2026-07-21 09:30:00', 40, 'Audiométrie', 2, 48, 8, 22, NOW(), NOW()),
(76, '2026-07-21 14:00:00', 20, 'Examen', 1, 15, 8, 24, NOW(), NOW()),
(77, '2026-07-22 09:00:00', 30, 'Consultation', 2, 16, 8, 22, NOW(), NOW()),
(78, '2026-07-22 09:30:00', 40, 'Audiométrie', 2, 28, 8, 23, NOW(), NOW()),
(79, '2026-07-23 09:00:00', 30, 'Suivi', 3, 38, 8, 22, NOW(), NOW()),
(80, '2026-07-23 09:30:00', 30, 'Consultation', 2, 48, 8, 22, NOW(), NOW()),
-- Doctor 9 (Catherine David)
(81, '2026-07-20 09:00:00', 45, 'Consultation rhumatologie', 2, 17, 9, 25, NOW(), NOW()),
(82, '2026-07-20 09:45:00', 35, 'Examen articulaire', 1, 18, 9, 26, NOW(), NOW()),
(83, '2026-07-20 14:00:00', 50, 'Échographie des tendons', 2, 29, 9, 27, NOW(), NOW()),
(84, '2026-07-21 09:00:00', 45, 'Consultation', 3, 39, 9, 25, NOW(), NOW()),
(85, '2026-07-21 09:45:00', 35, 'Examen', 2, 49, 9, 25, NOW(), NOW()),
(86, '2026-07-21 14:00:00', 50, 'Échographie', 1, 17, 9, 27, NOW(), NOW()),
(87, '2026-07-22 09:00:00', 45, 'Consultation', 2, 18, 9, 25, NOW(), NOW()),
(88, '2026-07-22 09:45:00', 35, 'Examen', 2, 29, 9, 26, NOW(), NOW()),
(89, '2026-07-23 09:00:00', 45, 'Suivi', 3, 39, 9, 25, NOW(), NOW()),
(90, '2026-07-23 09:45:00', 45, 'Consultation', 2, 49, 9, 25, NOW(), NOW()),
-- Doctor 10 (Nicolas Bertrand)
(91, '2026-07-20 09:00:00', 30, 'Consultation généraliste', 2, 19, 10, 28, NOW(), NOW()),
(92, '2026-07-20 09:30:00', 20, 'Prise de sang', 1, 20, 10, 29, NOW(), NOW()),
(93, '2026-07-20 14:00:00', 40, 'ECG de contrôle', 2, 30, 10, 30, NOW(), NOW()),
(94, '2026-07-21 09:00:00', 30, 'Consultation', 3, 40, 10, 28, NOW(), NOW()),
(95, '2026-07-21 09:30:00', 20, 'Prise de sang', 2, 50, 10, 28, NOW(), NOW()),
(96, '2026-07-21 14:00:00', 40, 'ECG', 1, 19, 10, 30, NOW(), NOW()),
(97, '2026-07-22 09:00:00', 30, 'Consultation', 2, 20, 10, 28, NOW(), NOW()),
(98, '2026-07-22 09:30:00', 20, 'Prise de sang', 2, 30, 10, 29, NOW(), NOW()),
(99, '2026-07-23 09:00:00', 30, 'Suivi', 3, 40, 10, 28, NOW(), NOW()),
(100, '2026-07-23 09:30:00', 30, 'Consultation', 2, 50, 10, 28, NOW(), NOW());







-- ============================================================
-- 5. NOTE_PATIENT INSERTIONS (30 patient notes)
-- ============================================================
INSERT INTO public.note_patient (id, note_medecin, id_patient, id_medecin, date_creation) VALUES
(1, 'Patient en bonne santé générale. Poursuivre le traitement habituel.', 1, 1, NOW()),
(2, 'Amélioration notable des symptômes. Réduire la posologie.', 2, 1, NOW()),
(3, 'Patient anxieux. Prévoir un suivi dans 2 mois.', 3, 2, NOW()),
(4, 'Bonne évolution. Continuer les exercices prescrits.', 4, 2, NOW()),
(5, 'Examen cutané satisfaisant. Prochaine visite dans 3 mois.', 5, 3, NOW()),
(6, 'Lésion suspecte à surveiller. Proposer biopsie.', 6, 3, NOW()),
(7, 'Croissance conforme aux courbes. Rendez-vous dans 6 mois.', 7, 4, NOW()),
(8, 'Patient allergique à la pénicilline à noter dans dossier.', 8, 4, NOW()),
(9, 'Examen pelvien normal. Poursuivre le suivi annuel.', 9, 5, NOW()),
(10, 'Présence de fibromes bénins. Surveillance recommandée.', 10, 5, NOW()),
(11, 'Entorse du genou droit. Repos et kiné pendant 3 semaines.', 11, 6, NOW()),
(12, 'Ostéoporose débutante. Traitement par bisphosphonates.', 12, 6, NOW()),
(13, 'Myopie stable. Nouvelle correction optique nécessaire.', 13, 7, NOW()),
(14, 'Augmentation de la pression intraoculaire. Bilan complémentaire.', 14, 7, NOW()),
(15, 'Hypertrophie des cornets. Traitement corticoïde nasal.', 15, 8, NOW()),
(16, 'Perte auditive légère. Appareillage à discuter.', 16, 8, NOW()),
(17, 'Polyarthrite rhumatoïde en phase active. Ajustement du traitement.', 17, 9, NOW()),
(18, 'Tendinite de la coiffe des rotateurs. Infiltration à prévoir.', 18, 9, NOW()),
(19, 'Suivi diabétique satisfaisant. Hémoglobine glyquée dans normes.', 19, 10, NOW()),
(20, 'Hypertension stable sous traitement. Maintenir les efforts.', 20, 10, NOW()),
(21, 'Patient nécessite bilan sanguin complet. Prévoir prise de sang.', 21, 1, NOW()),
(22, 'Prise de poids excessive. Recommandations nutritionnelles.', 22, 2, NOW()),
(23, 'Acné persistante. Traitement local renforcé.', 23, 3, NOW()),
(24, 'Retard staturo-pondéral. Bilan endocrinien demandé.', 24, 4, NOW()),
(25, 'Suspicion d''endométriose. IRM pelvienne prescrite.', 25, 5, NOW()),
(26, 'Lombalgie chronique. Repos et séances de kiné.', 26, 6, NOW()),
(27, 'Astigmatisme hypermétropique. Correction optique.', 27, 7, NOW()),
(28, 'Rhinite allergique. Antihistaminiques à renouveler.', 28, 8, NOW()),
(29, 'Gonflement articulaire. Prise d''anti-inflammatoire.', 29, 9, NOW()),
(30, 'Hypercholestérolémie. Alimentation à adapter.', 30, 10, NOW());

-- ============================================================
-- Reset sequences (optional - if you want to continue from these IDs)
-- ============================================================
SELECT setval('public.rdv_id_rdv_seq', 100);
SELECT setval('public.acte_medecin_id_seq', 30);
SELECT setval('public.note_patient_id_seq', 30);
SELECT setval('public.patient_id_patient_seq', 50);
SELECT setval('public.medecin_id_medecin_seq', 10);