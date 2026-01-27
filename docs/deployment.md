# Deployment Guide: AWS Lightsail

This guide covers deploying the LLTCG Discord Bot to an AWS Lightsail instance using Docker.

## 1. Create a Lightsail Instance
1. Login to the [AWS Lightsail Console](https://lightsail.aws.amazon.com/).
2. Click **Create instance**.
3. Select a **Region** (e.g., Ohio).
4. **Platform**: Linux/Unix.
5. **Blueprint**: OS Only -> **Ubuntu 24.04 LTS** (or 22.04).
6. **Instance Plan**: The $3.50 or $5/month plan is plenty for this bot.
7. Give it a name (e.g., `lltcg-bot-server`) and click **Create instance**.

## 2. Server Setup
Connect to your instance via SSH (either through the browser or a local terminal) and run these commands to install Docker:

```bash
# Update and install Docker
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# IMPORTANT: Run this to apply group changes without logging out
newgrp docker
```

## 3. Deployment Steps

### A. Prepare Configuration
Ensure you have your `config.json` and `card_data.json` ready.
- `config.json`: Contains your `DISCORD_TOKEN` and other settings.
- `card_data.json`: The card database file used by the bot.

### B. Transfer Files
You can use `scp` or simply clone your repository if it's hosted online. If transferring manually:
```bash
# Example using SCP from your local machine
scp -r . ubuntu@<INSTANCE_IP>:~/lltcg-discord
```

### C. Build and Run
On the server, run the automation script to build the image and start the container:
```bash
cd ~/lltcg-discord
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## 4. Updating & Redeploying
Since everything is automated, just run the script again whenever you want to update the bot with your latest code:

```bash
cd ~/lltcg-discord
./scripts/deploy.sh
```

## 5. Troubleshooting
- **Logs**: `docker logs -f lltcg-bot`
- **Restart (No Code Change)**: `docker restart lltcg-bot` (Use this if you only changed `config.json` or `card_data.json`, as they are mounted live).
- **Verify Mounts**: `docker inspect lltcg-bot`
