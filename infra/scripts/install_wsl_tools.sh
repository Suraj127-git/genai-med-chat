#!/usr/bin/env bash
set -euo pipefail

# ---------- helper ----------
log() { printf "\n\e[1;34m%s\e[0m\n" "$1"; }

# ---------- start ----------
log "🔧 Updating system and installing prerequisites..."
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg apt-transport-https lsb-release software-properties-common

# ensure keyrings dir exists (apt >= Ubuntu 22.04 pattern)
sudo install -m 0755 -d /etc/apt/keyrings
sudo install -m 0755 -d /usr/share/keyrings

# ---------- Kubernetes repo key ----------
log "📦 Installing Kubernetes apt repo key..."
# remove old key if present to avoid interactive prompts
sudo rm -f /usr/share/keyrings/k8s-apt-keyring.gpg
curl --retry 5 --retry-delay 2 --fail --silent --show-error --location \
  https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key \
  | sudo gpg --dearmor -o /usr/share/keyrings/k8s-apt-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/k8s-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /" \
  | sudo tee /etc/apt/sources.list.d/kubernetes.list >/dev/null

# ---------- Helm (try apt repo key, fallback to binary installer) ----------
log "⚓ Attempting to add Helm apt repo key (baltocdn.com)..."
# remove old helm key to avoid overwrite prompt
sudo rm -f /usr/share/keyrings/helm.gpg

set +e
curl --retry 5 --retry-delay 2 --fail --silent --show-error --location \
  https://baltocdn.com/helm/signing.asc \
  | sudo gpg --dearmor -o /usr/share/keyrings/helm.gpg
rc=$?
set -e

HELM_REPO_ADDED=0
if [ $rc -eq 0 ]; then
  log "✔ Helm repo key added successfully."
  echo "deb [signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" \
    | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list >/dev/null
  HELM_REPO_ADDED=1
else
  log "⚠️ Could not reach baltocdn.com. Will fall back to official Helm installer (binary)."
  # fallback: official get-helm-3 script (installs helm binary to /usr/local/bin)
  curl --retry 5 --retry-delay 2 --fail --silent --show-error --location \
    https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \
    | bash
fi

# ---------- Docker repo ----------
log "🐳 Setting up Docker repository (key + apt source)..."
sudo rm -f /etc/apt/keyrings/docker.gpg
curl --retry 5 --retry-delay 2 --fail --silent --show-error --location \
  https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release; echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

# ---------- update and install ----------
log "🔄 Updating package lists..."
sudo apt-get update -y

log "📥 Installing kubectl and Docker packages..."
# Do not assume helm apt package exists if repo not added
sudo apt-get install -y kubectl docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin || true

if [ $HELM_REPO_ADDED -eq 1 ]; then
  log "📥 Trying to install helm from apt repo..."
  sudo apt-get install -y helm || true
else
  log "ℹ️ Skipping apt helm install (repo not added). Helm binary already installed via fallback."
fi

# ---------- enable/start docker if systemd ----------
log "⚙️ Enabling Docker service if systemd available..."
if command -v systemctl >/dev/null 2>&1; then
  sudo systemctl enable docker || true
  sudo systemctl start docker || true
fi

log "👤 Adding current user to docker group (no-op for root)."
sudo usermod -aG docker "${USER:-$(whoami)}" || true

# ---------- kind ----------
log "📦 Installing k3s (lightweight Kubernetes) if missing..."
if ! command -v k3s >/dev/null 2>&1; then
  curl --retry 5 --retry-delay 2 --fail --silent --show-error --location \
    https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
fi

# ---------- summary ----------
echo
log "🎉 Installation Summary:"

# kubectl version: robust printing (some kubectl packaged builds error on --short)
if command -v kubectl >/dev/null 2>&1; then
  if kubectl version --client --short >/dev/null 2>&1; then
    printf "🟢 kubectl: %s\n" "$(kubectl version --client --short | tr -d '\n')"
  else
    # fallback: print first line of default output
    printf "🟢 kubectl: %s\n" "$(kubectl version --client 2>&1 | sed -n '1p' | tr -d '\n')"
  fi
else
  echo "🔴 kubectl: not installed"
fi

if command -v helm >/dev/null 2>&1; then
  printf "🟢 helm: %s\n" "$(helm version --short 2>/dev/null || helm version 2>/dev/null | sed -n '1p')"
else
  echo "🔴 helm: not installed"
fi

if command -v docker >/dev/null 2>&1; then
  printf "🟢 docker: %s\n" "$(docker --version | tr -d '\n')"
else
  echo "🔴 docker: not installed"
fi

if command -v k3s >/dev/null 2>&1; then
  printf "🟢 k3s: %s\n" "$(k3s -v | tr -d '\n')"
else
  echo "🔴 k3s: not installed"
fi

echo
log "✅ Done."
echo "👉 If you just added your user to the docker group, log out and back in or run: newgrp docker"
echo "👉 If Docker in WSL fails: enable systemd in WSL or use Docker Desktop integration."
