# Documentation API

## I. Initialisation du projet


### Installer prerequis

```shell
sudo apt update
sudo apt install python3.11-venv git docker.io apt-transport-https ca-certificates curl software-properties-common
```

### Créer un dossier de projet et clone du repo

```shell
mkdir api_syslog
cd api_syslog
git clone https://github.com/Eruffini25/API-TP.git
cd API-TP
```

### Installation et configuration Docker

```shell
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
```

```shell
sudo apt update
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
#sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo mv docker-compose-linux-x86_64 /usr/local/bin/docker-compose
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
pip install -r requirements.txt
```

### Lancer Docker Compose

```shell
docker-compose up --build
```

#### Si il y a des proxy faire ceci

##### sudo mkdir -p /etc/systemd/system/docker.service.d
##### sudo nano /etc/systemd/system/docker.service.d/http-proxy.conf

```shell
[Service]
Environment="HTTP_PROXY=http://proxy.example.com:8080"
Environment="HTTPS_PROXY=http://proxy.example.com:8080"
```

##### sudo systemctl daemon-reload
##### sudo systemctl restart docker
