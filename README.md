# Documentation API

## I. Initialisation du projet

### Créer un dossier de projet

```shell
mkdir api_syslog
cd api_syslog
```

### Créer et activer un environnement virtuel

```shell
sudo apt install python3.11-venv
python3 -m venv venv
source venv/bin/activate
```

### Installer les dépendances nécessaires

```shell
pip install fastapi uvicorn sqlalchemy databases passlib
```
