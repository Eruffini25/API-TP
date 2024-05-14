# Documentation API

## I. Initialisation du projet

### Créer un dossier de projet

```shell
mkdir api_syslog
cd api_syslog
```

### Installer prerequis

```shell
sudo apt install python3.11-venv git docker.io apt-transport-https ca-certificates curl software-properties-common
```

### Installation et configuration Docker

```shell
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```

```shell
apt-cache policy docker-ce
sudo apt install docker-ce
```

#### Vérifier l'installation docker

```shell
sudo systemctl status docker
```

```shell
sudo systemctl start docker
sudo systemctl enable docker
```

#### Installer Docker Compose

```shell
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

```shell
sudo chmod +x /usr/local/bin/docker-compose
```

```shell
docker-compose --version
```

#### Ajouter l'utilisateur au groupe Docker

```shell
sudo usermod -aG docker $USER
```

```shell
newgrp docker
```

### Créer et activer un environnement virtuel

```shell
python3 -m venv venv
source venv/bin/activate
```

### Installer les dépendances nécessaires

```shell
pip install fastapi uvicorn sqlalchemy databases passlib
```

### Lancer Docker Compose

```shell
docker-compose up --build
```