# Viaconnect SOC Maturity — Health Check

Aplicação **web** interna para avaliação de maturidade de SOC, baseada
**fielmente** nos instrumentos *Viaconnect Health Check* e *SOC-CMM 2.4.2*
(planilhas em `frameworks/`).

Arquitetura de **3 contêineres** (sobe com um `docker compose up`):

| Serviço | O que é | Exposto |
|---|---|---|
| **web** | Nginx servindo a SPA (interface) + proxy reverso de `/api` | porta `8080` |
| **api** | FastAPI/Uvicorn — guarda o estado da aplicação | interno |
| **db**  | PostgreSQL 16 — persistência (volume `pgdata`) | interno |

Os dados (organizações, ciclos, respostas, roadmap, entregáveis, usuários) ficam
no **PostgreSQL**, compartilhados entre máquinas/usuários. **Login: `admin` / `admin`.**

---

## 🚀 Rodar no servidor Linux (clone + compose)

**Pré-requisito:** Docker Engine + plugin Compose (`docker --version`, `docker compose version`).

```bash
git clone https://github.com/CarlosHenchen/claude-soc.git
cd claude-soc
docker compose up -d --build
# abra http://SEU_SERVIDOR:8080     (login: admin / admin)
```

Não precisa de `.env` — sobe com defaults. Para customizar:
```bash
PORT=9090 POSTGRES_PASSWORD=umaSenhaForte docker compose up -d --build
```

Comandos úteis:
```bash
docker compose logs -f          # logs de todos os serviços
docker compose ps               # status
docker compose down             # parar (mantém o banco)
docker compose down -v          # parar e APAGAR o banco (volume pgdata)
```

Atualizar para a última versão no servidor:
```bash
git pull
docker compose up -d --build
```

---

## O que a aplicação faz

- **3 tipos de avaliação** com os itens reais extraídos das planilhas:
  - **Domínios (Viaconnect Health Check)** — 9 domínios, 45 aspectos, 166 itens.
  - **SOC-CMM 2.4.2 — Basic** — 5 domínios, 27 aspectos (Maturity + Capability).
  - **SOC-CMM 2.4.2 — Advanced** — idem, com importância editável.
- **Organizações** com **ciclos de execução** e **evolução de postura** ao longo do tempo.
- Abas por organização: **Assessment · Evolução · Recomendações · Roadmap · Entregáveis Viaconnect**.
- **Recomendações** fundamentadas nos frameworks (CTI-CMM, HMM, SIM3, MITRE Engage…) e nos
  entregáveis Viaconnect, com botão **"✨ Gerar com Claude"** (IA) — ver abaixo.
- **Roadmap** priorizável por horizonte (3/6/12 meses).
- **Dashboards** com gauge, radar e ranking (ECharts, escala 0–5).
- **Configurações**: organizações, usuários internos e integração com o Claude.

---

## Integração com o Claude (IA)

Em **Configurações → Integração com Claude**, informe a **chave da API** e o **modelo**
(padrão `claude-opus-4-8`). A chamada vai **direto do navegador** para `api.anthropic.com`.

> ⚠️ A chave fica no navegador (`localStorage`), por opção: modelo "cada usuário usa a
> própria chave". Em ambiente exposto, sirva por **HTTPS** (ver Produção).

---

## Produção (HTTPS)

Para expor à internet, ponha um proxy reverso com TLS automático na frente. Exemplo
com **Caddy** (crie `Caddyfile`, troque o domínio):

```caddy
soc.seudominio.com {
    reverse_proxy web:80
}
```
Aponte o DNS para o servidor **antes** de subir; adicione um serviço `caddy` ao
`docker-compose.yml` publicando `80:443`, e remova o `ports:` do serviço `web`
(só o Caddy fica exposto). Troque também `POSTGRES_PASSWORD` via `.env`.

---

## Desenvolvimento — regenerar o frontend

A SPA em `web/` (`index.html`, `app.js`, `data.js`, `echarts.min.js`) já vem **gerada e
versionada** — o build Docker não precisa de Node. Só é preciso regenerar se você
mudar a lógica em `gen_preview.py` ou as planilhas em `frameworks/`. Requer Python 3 + `openpyxl`:

```bash
pip install openpyxl
python extract_frameworks.py   # frameworks/ (.xlsx) -> assets/frameworks.json
python gen_preview.py          # assets/ -> web/{index.html,app.js,data.js,echarts.min.js}
```

Para visualizar só o frontend localmente (sem backend; cai no fallback localStorage):
`python -m http.server 4173 --directory web` e abra `http://localhost:4173`.

---

## Estrutura do repositório

```
web/                      # FRONTEND (SPA) — servido por Nginx
  index.html  app.js  data.js  echarts.min.js   # gerados por gen_preview.py
  nginx.conf  Dockerfile
api/                      # BACKEND FastAPI
  main.py  requirements.txt  Dockerfile
docker-compose.yml        # db + api + web  ->  docker compose up
gen_preview.py            # gera o frontend (web/) a partir de assets/
extract_frameworks.py     # gera assets/frameworks.json a partir de frameworks/
assets/                   # frameworks.json (dados) + echarts.min.js
ingest/                   # parser das planilhas (usado por extract_frameworks.py)
frameworks/               # planilhas-fonte (.xlsx)
```

### Persistência

O frontend lê/grava o estado em `GET/PUT /api/state` (documento JSONB no PostgreSQL),
com `localStorage` como cache e fallback (se o backend não estiver disponível, a app
ainda funciona localmente no navegador).
