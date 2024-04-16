# data-challenge-journaux-bf

Ceci est une brève description du programme d'extraction automatique d’information dans le cadre de la compétition “Data Scraping Challenge” organisée par Open Burkina.

Le programme collecte des journaux officiels numérisés sur le site accessible par ce [lien](https://www.loc.gov/search/?fa=partof:burkina+faso+legal+gazettes). 
Ces journaux sont ensuite analysés à la recherche de declarations d'existence d'associations. Une fois ces declarations 
identifiées, les informations sur l'association et ses membres sont extraites puis enregistrées dans deux fichiers CSV : 
`associations.csv` et `membres.csv`.

**Note**: Le programme a été développé en langage Python (version 3.10) sous une distribution Linux. Bien que n’ayant pas été testé sur d’autres systèmes tels que Mac ou Windows, il devrait quand même fonctionner dans un environnement virtuel après installation des prérequis (fichier `requirements.txt`).

## Comment ça marche
Pour toute information sur le fonctionnement interne du programme vous pouvez ouvrir le fichier descriptif (PDF) du 
dossier `doc`: [Description](https://github.com/bationoA/data-challenge-journaux-bf/blob/main/doc/Description%20-%20DATA%20SCRAPING%20CHALLENGE.pdf).

## Le temps

Il est important de noter que faire dérouler le programme sur l’ensemble des journaux du site web prendra plusieurs heures, voire jours, suivant la performance de l’ordinateur et de la connexion internet utilisés.

## Comment lancer le programme
Suivez les étapes suivantes pour lancer le programme :

1. **Étape 1 (pas obligatoire mais recommandée) :** Créez un environnement virtuel pour isoler les dépendances du projet.
   
2. **Étape 2 :** Clonez ce repository à l'aide de la commande suivante:
```commandline
git clone git@github.com:bationoA/data-challenge-journaux-bf.git
```
3. **Étape 3 :** Installez les packages requis se trouvant dans le fichier `requirements.txt` en exécutant la commande suivante :
```commandline
pip install -r requirements.txt
```
4. **Étape 4 :** À présent, vous êtes prêt à lancer le programme en utilisant le format suivant :
```commandline
python main.py <parametre 1> <valeur 1> <parametre 2> <valeur 2> ...
```

Les différents paramètres et leurs valeurs sont listés dans le tableau suivant :

| Paramètre | Description                                            | Options                                             |
|-----------|--------------------------------------------------------|-----------------------------------------------------|
| -t        | Task                                                   | s: Scraping. Collecte uniquement les journaux en ligne. S'arrête une fois cette tâche accomplie. <br> e: Extract. Extracte uniquement les informations des journaux collectés. Ignore la phase de téléchargement. <br> b: Both. Exécute les deux tâches dans l’ordre collecte puis extraction. |
| -st       | Scraping threads                                       | Nombre maximal de téléchargement simultanés. Dépend du processeur. Doit être supérieur à 0 et inférieur ou égal au nombre maximal de threads du processeur. Défaut = 1 |
| -et       | Extraction threads                                     | Nombre maximal de fichiers journal à traiter simultanément. Doit être supérieur à 0 et inférieur ou égal au nombre maximal de threads du processeur. Défaut = 1 |

### Exemples de commandes

- La commande suivante lance uniquement le téléchargement des journaux. Tout au long de l'exécution de la tâche, le programme téléchargera 3 journaux maximum de façon simultanée :
```commandline
python main.py -t s -st 3
```
- La commande suivante lance uniquement l’extraction des détails des associations et leurs membres se trouvant dans les journaux. Tout au long de l'exécution de la tâche, le programme examinera 5 journaux maximum de façon simultanée :
```commandline
python main.py -t e -et 5
```
- La commande suivante lance le téléchargement des journaux puis l’extraction des détails des associations et leurs membres se trouvant dans les journaux. Tout au long de l'exécution de la tâche, le programme téléchargera 2 journaux maximum de façon simultanée puis examinera 4 journaux maximum de façon simultanée.
```commandline
python main.py -t b -st 2 -et 4
```

## Contact

Pour toute question ou suggestion, n'hésitez pas à me contacter à [amosb.dev@gmail.com](mailto:amosb.dev@gmail.com).

