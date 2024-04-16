# data-challenge-journaux-bf
webscraping


## Introduction

Ceci est une brève description du programme d’information automatique d’information dans le cadre de la compétition “Data Scraping Challenge” organisée par Open Burkina.

## Note

Le système a été développé en langage Python 3.10 sous une distribution Linux. Bien que n’ayant pas été testé sur d’autres systèmes tels que Mac ou Windows, il devrait quand même fonctionner dans un environnement virtuel après installation des prérequis (fichier `requirements.txt`).

## Approche

Le système se compose de deux programmes (ou tâches) principaux indépendants implémentés en packages : `scraper`, en charge de la collection et la compilation des journaux ; et `extractor`, nommé `association` en charge de l’extraction des journaux collectés et leur enregistrement sous format CSV.

### Scraper

Le package `scraper` utilise le package Selenium pour accomplir sa tâche de collecte et compilation des textes dans les journaux. L'opération est effectuée de la façon suivante :

1. **Collecte des liens des journaux :** Le programme commence par collecter les liens de l’ensemble des publications des journaux.
2. **Assemblage des pages :** Pour chaque publication ou journal, collecter et rassembler toutes les pages du journal en un seul fichier.
3. **Enregistrement des fichiers :** Chaque fichier contenant les pages d’une même publication (ou journal) est ensuite enregistré sous format texte (.txt).

### Association (extractor)

Le package `association` contient la classe `extractor` qui est chargée de l’extraction des informations se trouvant dans les fichiers collectés par la tâche de collecte effectuée par le package `scraper`. Le processus se déroule comme suit :

1. **Identification des fichiers :** Le programme commence par identifier l’ensemble des fichiers textes contenant les publications existant sur le disque.
2. **Identification des sections clés :** Pour chaque journal, une méthode parcourt le contenu à l'aide d’une expression régulière pour extraire les sections faisant mention d’une déclaration d’association.
3. **Extraction d’informations :** Pour chaque section identifiée, le programme extrait deux types d’informations qui sont les détails des associations et la liste de leurs membres et leurs rôles dans l’association. Toutes les extractions d’informations sont effectuées en utilisant uniquement des expressions régulières.
4. **Enregistrement des informations d’associations et membres :** Pour chaque publication, une fois que les associations et leurs membres extraits du journal, ils sont enregistrés sous format JSON dans deux dossiers temporaires l’un pour les associations et l’autres pour les membres.
5. **Création de fichier CSV :** Le programme s'achève par la création de deux fichiers CSV. L’ensemble des fichiers JSON se trouvant dans les dossiers temporaires `association` et `membres` sont collectés séparément, transformés en DataFrame Pandas puis exportés en deux fichiers CSV.

## Le temps

Il est important de noter que faire dérouler le programme sur l’ensemble des journaux du site web prendra plusieurs heures, voire jours, suivant la performance de l’ordinateur et de la connexion internet utilisés. Le programme se termine par un résultat similaire à celui dans l’image ci


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
## Licence

Ce projet est sous licence MIT. Pour plus d'informations, consultez le fichier [LICENSE](LICENSE).

## Contact

Pour toute question ou suggestion, n'hésitez pas à me contacter à [amosb.dev@gmail.com](mailto:amosb.dev@gmail.com).

