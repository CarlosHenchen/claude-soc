# Deploy & Produção — Viaconnect SOC Maturity

Este guia complementa o **README** (que cobre o *clone-and-run* básico). Aqui está
o que é preciso para rodar com segurança em um servidor exposto à internet.

> Legenda: 🔴 **bloqueador de segurança** · 🟡 importante · ⚪ recomendável

---

## 1. Antes de expor à internet — bloqueadores 🔴

- [ ] **Segredos fortes.** Rode `./scripts/setup-env.sh` (gera `SECRET_KEY` e
  `POSTGRES_PASSWORD` aleatórios) **e** troque `ADMIN_PASSWORD` no `.env`.
  Os defaults (`admin/admin`, `dev-insecure-secret-change-me`) estão em
  `api/app/config.py` e o app emite **aviso no boot** se eles forem usados.
- [ ] **HTTPS obrigatório.** Sirva atrás de um proxy com TLS automático
  (Caddy — ver §3). A aba *Recomendações* do `preview.html` chama
  `api.anthropic.com` direto do navegador; em HTTP plano a chave trafega exposta.
- [ ] **CORS restrito.** `api/app/main.py` usa `allow_origins=["*"]`. Troque pela
  origem real (ex.: `https://soc.seudominio.com`).
- [ ] **Não publique a porta do `web`/`api`/`db`.** Só o proxy (Caddy) deve
  escutar 80/443. No `docker-compose.prod.yml` abaixo o `web` não tem `ports:`.
- [ ] **Chave do Claude (stack completa).** Não porte o padrão "chave no navegador"
  para o SPA React. Crie uma rota proxy autenticada `POST /api/recommendations`
  no FastAPI guardando `ANTHROPIC_API_KEY` como segredo do servidor. *(Hoje a
  feature de IA só existe no `preview.html`, não no SPA.)*

## 2. Produção — itens importantes 🟡

- [ ] Múltiplos workers: `UVICORN_WORKERS=2..4` no `.env` (o PDF via Playwright é
  síncrono e bloqueia 1 worker).
- [ ] Rate limiting em `/api/auth/login` (brute force do admin).
- [ ] Backups do Postgres (ver §4).
- [ ] `systemctl enable docker` no host (containers voltam no reboot; todos os
  serviços já usam `restart: unless-stopped`).
- [ ] Registro DNS `A/AAAA` do domínio → IP do servidor **antes** do 1º `up`
  (o Caddy precisa para emitir o certificado Let's Encrypt).

## 3. HTTPS com Caddy (recomendado)

Crie `deploy/Caddyfile` (troque o domínio):

```caddy
soc.seudominio.com {
    reverse_proxy web:80
}
```

Crie `deploy/docker-compose.prod.yml` (sobe db + api + web **sem porta exposta** +
Caddy publicando 80/443; build local, sem precisar de registry):

```yaml
services:
  db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 10
    networks: [internal]

  api:
    build: { context: ../api }
    restart: unless-stopped
    env_file: ../.env
    environment:
      DATABASE_URL: postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
    volumes:
      - ../frameworks:/frameworks:ro
    depends_on:
      db: { condition: service_healthy }
    healthcheck:
      test: ["CMD-SHELL", "python -c 'import urllib.request;urllib.request.urlopen(\"http://localhost:8000/api/health\")' || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 6
    deploy:
      resources:
        limits: { memory: 1g }   # Chromium/PDF é memory-spiky
    networks: [internal]

  web:
    build: { context: ../web }
    restart: unless-stopped
    depends_on:
      api: { condition: service_healthy }
    networks: [internal]
    # SEM ports: — só o Caddy fica exposto

  caddy:
    image: caddy:2-alpine
    restart: unless-stopped
    ports: ["80:80", "443:443"]
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
    depends_on: [web]
    networks: [internal]

networks:
  internal: { driver: bridge }

volumes:
  pgdata: { name: soc_maturity_pgdata }
  caddy_data:
  caddy_config:
```

Subir:

```bash
./scripts/setup-env.sh
docker compose -f deploy/docker-compose.prod.yml up -d --build
```

## 4. Backups do Postgres 🟡

```bash
# backup diário (cron no host); copie para fora do servidor depois
docker exec soc_maturity_db_1 pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" \
  | gzip > "/backups/soc_$(date +%F).sql.gz"

# restore
gunzip -c /backups/soc_AAAA-MM-DD.sql.gz \
  | docker exec -i soc_maturity_db_1 psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

> O volume `soc_maturity_pgdata` sobrevive a `up`/`down`, **mas `docker compose
> down -v` apaga tudo.**

## 5. CI/CD (opcional) — publicar imagens no GHCR ⚪

Para deploy a partir de imagens (em vez de build no servidor), adicione um
workflow `.github/workflows/release.yml` que faz `docker/build-push-action` das
imagens `api` e `web` para `ghcr.io/<owner>/claude-soc-{api,web}` (o `GITHUB_TOKEN`
embutido já basta para push no GHCR do próprio repositório) e troque os `build:`
do compose de produção por `image: ghcr.io/...:<tag>`. Nenhum segredo de banco/JWT
vai para o CI — eles vivem só no `.env` do servidor.

## 6. Robustez ⚪

- Pinar imagens base por digest (`postgres:16`, `python:3.12-slim`, `node:20-alpine`, `nginx:1.27-alpine`).
- `web/package-lock.json` + trocar `npm install` por `npm ci` no `web/Dockerfile` (builds reprodutíveis).
- Headers de segurança/cache no `web/nginx.conf`; desabilitar `/docs` e `/redoc` em produção.
