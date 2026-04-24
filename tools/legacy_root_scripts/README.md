## Legacy Root Scripts

Ce dossier contient des scripts déplacés depuis la racine du dépôt lors de l'audit de stabilisation.

Principes:
- aucun script n'a été supprimé;
- ils ont été isolés pour assainir la racine du projet;
- ils ne font pas partie du runtime normal backend/frontend;
- plusieurs scripts sont des outils d'investigation, de migration manuelle, de debug ou de validation ponctuelle.

Catégories déplacées:
- `analyze_*`, `check_*`, `debug_*`, `diagnostic_*`, `verify_*`, `test_*`
- scripts de correction ponctuelle comme `fix_*`, `cleanup_*`, `restore_*`
- scripts de migration/exécution manuelle comme `create_*`, `run_*`, `task_*`

Règle d'usage:
- ne pas exécuter ces scripts en production sans revue préalable;
- si un script doit être conservé comme outil officiel, il doit être relocalisé ensuite dans un dossier dédié (`tools/`, `scripts/`, `maintenance/`) avec documentation et prérequis.
