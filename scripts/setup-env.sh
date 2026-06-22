#!/bin/sh
# ============================================================================
# Cria o arquivo .env para a STACK COMPLETA (Caminho B) a partir do
# .env.example, gerando automaticamente um SECRET_KEY forte e uma senha de
# banco aleatória. Idempotente: não sobrescreve um .env existente.
#
#   ./scripts/setup-env.sh
# ============================================================================
set -e
cd "$(dirname "$0")/.."

if [ -f .env ]; then
  echo "[setup-env] .env já existe — nada a fazer (apague-o para regerar)."
  exit 0
fi

rand() {
  if command -v openssl >/dev/null 2>&1; then openssl rand -hex "$1"
  else head -c "$1" /dev/urandom | od -An -tx1 | tr -d ' \n'; fi
}

SECRET="$(rand 32)"
DBPASS="$(rand 18)"

cp .env.example .env
# Substitui os placeholders pelos segredos gerados (sed portátil).
sed -i.bak \
  -e "s|^SECRET_KEY=.*|SECRET_KEY=${SECRET}|" \
  -e "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${DBPASS}|" \
  .env && rm -f .env.bak

echo "[setup-env] .env criado com SECRET_KEY e POSTGRES_PASSWORD aleatórios."
echo "[setup-env] ATENÇÃO: ADMIN_PASSWORD ainda é 'admin' — troque no .env"
echo "[setup-env] e depois de subir, altere a senha do admin pela tela de Usuários."
