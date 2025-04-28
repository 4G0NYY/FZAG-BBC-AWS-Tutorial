# FZAG-BBC-AWS-Tutorial
Die Aufträge, welche ich mit den Bbc-Menschen durchführen werde. In diesen werden wir: Einen Linux-Server in AWS (Localstack) mithilfe eines cloud-init.yml erstellen (EC2), auf dieser Instanz Docker installieren, innerhalb von Docker Portainer einrichten sowie ein Python-Skript schreiben, welches wir dann mit Docker-Compose ausführen (Portainer)

# Localstack aufsetzen

Als erstes müssen wir logischerweise mal eine "eigene" AWS-Cloud aufsetzen. Das können wir mithilfe von [Localstack](https://github.com/localstack/localstack).

## To-Do

- VM mit [Ubuntu Server 22.04.2 LTS](https://ubuntu.com/download/server/thank-you?version=24.04.2&architecture=amd64&lts=true) aufsetzen.
- In dieser VM [Docker installieren](https://docs.docker.com/engine/install/ubuntu/)
- [Localstack installieren](https://docs.localstack.cloud/getting-started/installation/#docker) Hier wichtig: Wir installieren die Community-Version. Diese unterstützt alles was wir heute brauchen (EC2)

## VM mit Ubuntu Server aufsetzen

Erstellt eine VM mit 8GB RAM und 4 vCPU-Cores. Öffnet dann das VMWare Remote Tool, startet die VM und fügt das Ubuntu-ISO hinzu. Nun startet ihr die VM neu und installiert Ubuntu Server. Hier ist folgendes wichtig:
 - Das richtige Tastaturlayout nehmen
 - Benutzernamen und Passwort merken
 - Keine Zusatzpakete installieren
 - Die IP eurer VM merken (Am besten eine statische IP!)

## Docker installieren

Mithilfe der VMWare Remote Tools installiert ihr Docker. Dies könnt ihr mit folgenden Befehlen machen: (Ja, ihr könnt Copy-Pasten, ich erkläre aber trotzdem was jeder dieser Befehle macht :3)


```
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
```
Hiermit entfernen wir alle APT-Pakete, welche einen Konflikt auslösen könnten. (Werden keine sein, da wir frische Installationen haben.)

```
sudo apt update
```
Nun updaten wir die APT-Datenbanken

```
sudo apt install ca-certificates curl
```
Dies sind die benötigten Pakete, um das Docker-APT Repository hinzuzufügen.

```
sudo install -m 0755 -d /etc/apt/keyrings
```
Hier installieren wir die Keyrings. Jedes Repository hat Keys, um die "Authentität" und die "Sicherheit" zu garantieren.

```
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
```
Hier hinterlegen wir den Key für das Docker-Repository.

```
sudo chmod a+r /etc/apt/keyrings/docker.asc
```
Nun setzen wir noch die korrekten File-Berechtigungen.

```
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
Nun fügen wir das Docker-APT Repository hinzu und "sagen" APT welche Keys zu diesem Repository gehören.

```
sudo apt update
```
Nun aktualisieren wir die APT-Datenbank nochmals, dass die Docker-Pakete auch in der lokalen Datenbank von APT auftauchen.

```
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
Und hiermit installieren wir nun Docker und die wichtigsten Plugins.

Nun haben wir Docker auf unserem neuen Server installiert. Wenn ihr jedoch einen docker-Befehl ohne sudo ausführen wollt, fehlen euch die Rechte. Theoretisch könnten wir einfach alles mit sudo machen, das ist jedoch unschön.

### Docker-Berechtigungen
Um nicht alles mit sudo ausführen zu müssen (Least-Privilege) fügen wir euren Benutzer noch in die docker-Gruppe. Das machen wir wie folgt:
```
sudo groupadd docker
```
Falls es die docker-Gruppe aus irgendwelchen Gründen nicht bei der Installation erstellt hat, machen wir das manuell. Kaputt machen können wir mit diesem Befehl nicht viel.

```
sudo usermod -aG docker $USER
```
Und nun fügen wir den momentanen Benutzer (in der ENV-Variable $USER) in die Docker-Gruppe. Durch diese Variable könnt ihr auch diesen Befehl Copy-Pasten.

## Localstack installieren
Localstack können wir mit einem einzigen Befehl installieren: [Zumindest wenn wir Localstack in Docker nutzen würden.]

### Bare-Metal: (Unser Weg)

```
curl --output localstack-cli-4.3.0-linux-amd64-onefile.tar.gz --location https://github.com/localstack/localstack-cli/releases/download/v4.3.0/localstack-cli-4.3.0-linux-amd64-onefile.tar.gz
```
Hier holen wir die schon Kompilierten Binaries von Localstack und speichern diese lokal als .tar.gz

```
sudo tar xvzf localstack-cli-4.3.0-linux-*-onefile.tar.gz -C /usr/local/bin
```
Nun extrahieren wir diese Datei in's /bin-Verzeichnis.

Um das ganze zu testen, können wir folgenden Befehl verwenden:
```
localstack --version
```

Wenn wir hier einen Output erhalten, war die Installation erfolgreich. Danach geht's weiter mit dem Aufsetzen einer EC2-Instanz.

### In Docker: (machen wir nicht)
```
docker run --rm -it -p 4566:4566 -p 4510-4559:4510-4559 -v /var/run/docker.sock:/var/run/docker.sock localstack/localstack
```

Was genau macht dieser Befehl?

```
docker run
```
Hiermit erstellen & starten wir einen neuen Docker Container

```
--rm
```
Dieser Teil löscht den Befehl automatisch sobald er gestoppt wird, sodass keine unnötigen Container "liegen" bleiben. (Den Container welchen wir händisch starten startet die "echten" Container)

```
-it
```
Sind zwei eigene "Optionen", -i ist für den interaktiven Modus (Dass wir auf die Konsole des Containers zugreifen können) und mit -t weisen wir ein Terminal zu (Für die Benutzerfreundlichkeit)

```
-p 4566:4566 -p 4510-4559:4510-4559
```
Hiermit leiten wir die Host-Ports (von unserem Server) an die Ports unseres Docker-Containers weiter. In diesem Fall den Host-Port 4566 auf den Container-Port 4566 und dasselbe mit der Port-Range 4510-4559.

```
-v /var/run/docker.sock:/var/run/docker.sock
```
Hiermit binden wir den Host-Docker Sock (ist eine Datei) an unseren Container an. Somit kann unser Container mit Docker auf unserem Server kommunizieren.

```
localstack/localstack
```
Hier definieren wir, welches Docker Image unser Container nutzen wird.


# EC2-Instanz innerhalb von Localstack aufsetzen.

## To-Do
 - Localstack starten
 - Ein EC2-Keypair erstellen
 - Firewall-Rules erstellen
 - Die EC2-Instanz erstellen
 - Bei der EC2-Instanz einloggen

## Localstack starten

Localstack können wir mit einem einzigen Befehl starten:
```

```

## EC2-Keypair erstellen
