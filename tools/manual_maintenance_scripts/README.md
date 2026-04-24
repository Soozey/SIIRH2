# Scripts de maintenance manuelle

Ce dossier regroupe les scripts Python qui ne relevent pas du runtime normal de l'application.

## Pourquoi ils ont ete deplaces

- ils encombraient la racine du depot ;
- ils ressemblent a des scripts ponctuels de migration, rollback, diagnostic cible ou preparation de donnees ;
- leur presence a la racine augmentait le risque d'erreur humaine.

## Regle d'usage

Ces scripts ne doivent pas etre executes automatiquement au demarrage, ni etre consideres comme partie prenante du flux applicatif standard.

Toute execution doit etre precedee de :

1. lecture du script ;
2. verification de son perimetre exact ;
3. verification de la base cible ;
4. sauvegarde si le script modifie des donnees.

## Nature des scripts archives ici

- migrations manuelles ;
- rollbacks ;
- diagnostics ponctuels ;
- generation ou correction de jeux de donnees ;
- verifications ad hoc post-incident.

