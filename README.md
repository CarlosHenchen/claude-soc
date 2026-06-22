# Viaconnect SOC Maturity — Health Check

Aplicação web **interna** e **on-premise** para avaliação de maturidade de SOC,
baseada **fielmente** no instrumento *Viaconnect Health Check* (planilha
`Viaconnect_HealthCheck_Dominios_SOC_COMPLETOv2.xlsx`).

Totalmente containerizada com Docker Compose: **PostgreSQL 16 + FastAPI + React/Vite**,
servida por Nginx que também faz proxy reverso de `/api`.

---

## 🚀 Rodar no Linux (clonar e executar)

**Pré-requisito:** Docker Engine + plugin Compose (`docker --version` e `docker compose version`).
Existem **dois caminhos** — escolha um:

### Caminho A — App de arquivo único (mais simples, sem banco)

Single-usuário, dados no navegador (`localStorage`). Ideal para demonstração/validação.

```bash
git clone https://github.com/CarlosHenchen/claude-soc.git
cd claude-soc
docker compose -f docker-compose.preview.yml up -d --build
# abra http://SEU_SERVIDOR:8080   (login: admin / admin)
```

> Sem Docker? Basta abrir o arquivo `preview.html` num navegador, ou servir a pasta:
> `python3 -m http.server 8080` e acessar `http://SEU_SERVIDOR:8080/preview.html`.

### Caminho B — Stack completa (multiusuário, PostgreSQL)

Multiusuário, dados no banco, autenticação JWT.

```bash
git clone https://github.com/CarlosHenchen/claude-soc.git
cd claude-soc
./scripts/setup-env.sh          # cria .env com SECRET_KEY e senha de banco fortes
docker compose up -d --build    # sobe db + api + web (migração e seed automáticos)
# abra http://SEU_SERVIDOR:8080   (login: admin / admin — TROQUE a senha em Usuários)
```

Comandos úteis: `docker compose logs -f` (logs), `docker compose down` (parar),
`docker compose down -v` (parar **e apagar o banco**).

> **Antes de expor à internet (produção):** sirva por **HTTPS** (proxy reverso
> Caddy/Traefik), troque `ADMIN_PASSWORD`, restrinja o CORS (`api/app/main.py`)
> e mova a chave do Claude para o backend. Veja **`DEPLOY.md`** para o checklist completo.

---

## ⚡ App de arquivo único — `preview.html` (rodável sem instalar nada)

Como a máquina-alvo não tem Docker/Node, há uma versão **completa e funcional em um
único arquivo**: basta **dar duplo-clique em `preview.html`** (sem servidor, sem
internet). Persiste os dados no `localStorage` do navegador. **Login padrão: `admin` / `admin`.**

Inclui **3 tipos de avaliação** com os itens reais extraídos das planilhas:

| Tipo | Domínios | Aspectos | Itens | Fonte |
|------|----------|----------|-------|-------|
| Domínios (Viaconnect Health Check) | 9 | 45 | 166 | `Viaconnect_HealthCheck...xlsx` |
| SOC-CMM 2.4.2 — Basic | 5 | 27 | 667 (350 Maturity + 317 Capability) | `62-soc-cmm-242-basic.xlsx` |
| SOC-CMM 2.4.2 — Advanced | 5 | 27 | 667 + importância editável | `63-soc-cmm-242-advanced.xlsx` |

### Fidelidade ao SOC-CMM (fórmulas transcritas da planilha)
* Estrutura macro→sub idêntica ao radar oficial: **5 domínios → 27 aspectos**, com
  **Maturity** (todos) e **Capability** (apenas Technology e Services).
* Scoring transcrito célula a célula: `factor(importância)={none:0,low:.5,normal:1,high:2,critical:4}`,
  `I=resposta×factor`, `H=Σfactor`, `J=5×factor`, **% do aspecto** `K=max(0,100×(ΣI−ΣH)/(ΣJ−ΣH))`;
  **Maturity = 5×K/100**, **Capability = 3×K/100**; domínio = média dos aspectos.
* **Dashboard com o radar igual ao print**: 27 eixos agrupados por domínio, série Maturity (0–5)
  e Capability (0–3 na mesma escala).
* **Formulário no estilo planilha**: navegação por **dropdowns** (domínio macro → aspecto),
  resposta com o significado de cada nível, **importância** (Advanced), **remarks** inline e
  **guidance** completa no botão de ajuda.

Funcionalidades:
* **Organizações** (cadastro/exclusão) e escolha de qual avaliação fazer para cada uma;
* **Ciclos de execução** por organização+framework → **gráfico de evolução** da maturidade;
* **Botão de ajuda (?)** em cada item: explica o que avaliar (remarks da planilha) e o
  **significado de cada nível 0–5** (guidance oficial do SOC-CMM), destacando o nível escolhido;
* **Dashboard** com gauge geral, radar por domínio e **detalhe por domínio colapsável**
  (clique para mostrar/ocultar os subdomínios);
* **Exportar PDF** do dashboard (via impressão do navegador → "Salvar como PDF");
* **Registro de quem preencheu** cada avaliação;
* **Configurações (admin)**: criar/excluir organizações, criar/excluir usuários e **alterar senhas**.

Para regenerar o arquivo após mudanças: `python extract_frameworks.py && python gen_preview.py`.

### Camada de relatórios e visualização (ECharts)

Os dashboards foram refatorados com **Apache ECharts** (no single-file embutido offline;
na app React via `echarts-for-react`), escolhido por lidar muito melhor que Recharts com
**radar de muitos eixos, rótulos longos, responsividade e densidade**.

* **Hierarquia de cards:** score geral em destaque (gauge 0–5) → KPIs → **ranking de
  domínios** (barras horizontais ordenadas, comparação primária) + **radar de "shape"** →
  **cards de score por domínio** (nível 0–5 segmentado) → evolução por ciclo.
* **Rótulos longos:** nomes completos no ranking (quebra de linha, sem truncar); no radar,
  `axisName` com quebra inteligente. Nada de texto cortado no meio da palavra.
* **Dados faltantes explícitos:** domínio sem respostas aparece como **"não avaliado"**
  (cinza/tracejado em barras e cards, excluído da forma do radar) com selo de cobertura —
  sem polígono quebrado.
* **Escala de cor acessível 0–5** (vermelho→âmbar→verde por faixa), consistente em
  gauge/barras/cards, sempre acompanhada do número e do nível (não depende só de cor).
* **Loading/empty** tratados (skeleton e estado vazio com CTA).
* Charts em **SVG** (`renderer:'svg'`) → vetor nítido para impressão/PDF.

### Export PDF (vetorial, fiel à tela)

* **App React (Docker):** endpoint `GET /api/assessments/{id}/report.pdf` renderiza o
  relatório (capa com cliente/responsável/data, sumário executivo e detalhamento por
  domínio) via **Playwright/headless Chromium** → PDF com os gráficos **SVG vetoriais**
  (não screenshot). O Chromium é instalado na imagem da API (ver `api/Dockerfile`).
* **Single-file:** o botão "Exportar PDF" usa **print-to-PDF** do navegador — como os
  gráficos ECharts são SVG, o PDF também sai vetorial.

### Jornada por organização (abas)

Cada organização tem abas que compõem a jornada de maturidade do SOC:
* **Assessment** — os três tipos de avaliação (Domínios, SOC-CMM Basic, Advanced) com ciclos.
* **Evolução de postura** — evolução da avaliação de *Domínios* por ciclos (linha geral + Δ por domínio).
* **Recomendações** — resumo executivo automático: compara cada domínio ao seu framework, identifica a
  lacuna e lista as ações Viaconnect com **checkbox para o usuário escolher** quais entram no Roadmap.
* **Entregáveis Viaconnect** — matriz de entregáveis das propostas **SOC Standard / SOC Advanced** (Health
  Check, Sala de Crise, Threat Hunting, EASM, etc.). O usuário escolhe o **plano contratado** e só são
  listados os entregáveis que fazem sentido nele; cada um recebe uma **nota de 1 a 5** (com média).
* **Roadmap** — ações em horizontes de **3 / 6 / 12 meses**, priorizáveis por domínio (Alta/Média/Baixa),
  com **seleção de domínios** a incluir/excluir e respeitando as recomendações marcadas. As ações são os entregáveis reais Viaconnect
  (Sophos XDR/Central/Firewall; Standard = fundação, Advanced = evolução proativa), ancorados nos frameworks
  NIST CSF/800-61, MITRE ATT&CK, SANS PICERL e TaHiTI/PEAK — base de conhecimento em `KB` (gen_preview.py),
  derivada da proposta e da apresentação comercial da Viaconnect.

> Limitação: por usar `localStorage`, os dados ficam **no navegador local** (não são
> compartilhados entre máquinas). Para uso multiusuário/persistente compartilhado, use a
> stack Docker abaixo (que hoje serve o framework Viaconnect; trazer SOC-CMM Basic/Advanced
> e os módulos de organização/ciclos/config para a API+React é o próximo passo de paridade).

---

## Arquitetura

```
                    ┌──────────────────────── host ────────────────────────┐
                    │                                                       │
   navegador  ──►  :8080 ──►  web (Nginx)  ──/api──►  api (FastAPI/Uvicorn) │
                    │            estáticos React          │                 │
                    │                                     ▼                 │
                    │                                db (PostgreSQL 16)      │
                    │            rede interna do Compose (não publicada)     │
                    └───────────────────────────────────────────────────────┘
```

* **db** — PostgreSQL 16 oficial, volume nomeado `pgdata`, variáveis via `.env`.
* **api** — FastAPI (Python 3.12), Dockerfile multi-stage slim, Uvicorn,
  SQLAlchemy 2.x + Alembic. Migrations e seed rodam no `entrypoint`.
* **web** — React + Vite + TypeScript, Dockerfile multi-stage (Node builda →
  Nginx serve). Nginx faz proxy de `/api` para o container `api`.

Apenas o **web** publica porta no host (`${WEB_PORT}`, padrão `8080`). Postgres e
API ficam **somente na rede interna** do Compose, inacessíveis de fora do host.

---

## Modelo de dados (fiel à planilha)

A planilha é **um instrumento** ("Viaconnect Health Check SOC") com **9 domínios**
(as 9 abas), cada um com **escala de maturidade própria**.

| Entidade | Origem na planilha | Qtde |
|----------|--------------------|------|
| `Framework` | o instrumento inteiro | 1 |
| `Domain` | cada aba (CTI, Threat Hunting, Detection Eng, DFIR, CSIRT, PSIRT, Deception, Vuln Mgmt, Automação) | 9 |
| `Control` | os subdomínios dentro de cada aba (PROGRAM, ASSET, PREPARE…) | 45 |
| `Question` | cada item de avaliação (CTI-01 … AU-09), com `weight` | 166 |
| `Scale` / `ScaleOption` | dropdown de maturidade de cada domínio (0–3, 0–4, 1–5, 0–5) | 6 escalas |
| `Assessment` | uma execução (cliente / data / responsável) | — |
| `Response` | resposta a uma pergunta (atual + meta + evidências) | — |
| `Score` | snapshot consolidado por controle / domínio / geral | — |
| `User` | usuários internos (login + CRUD admin) | — |

### Scoring (igual à aba `Dash`)
* maturidade do **controle** = média ponderada (`weight`) dos itens respondidos;
* maturidade do **domínio** = média ponderada de todos os itens do domínio;
* **geral** = média das maturidades **normalizadas** dos domínios.

Como cada domínio usa uma escala diferente, os resultados também são
**normalizados em %** (`nível ÷ máximo_da_escala`) para o radar dos 9 domínios e o
gauge consolidado. Meta e gap são calculados da mesma forma.

---

## Como subir

Pré-requisitos: **Docker** e **Docker Compose**.

```bash
# 1. Configurar variáveis
cp .env.example .env
#   edite .env: troque POSTGRES_PASSWORD, SECRET_KEY e ADMIN_PASSWORD

# 2. Subir os 3 containers (build + migrations + seed automáticos)
docker compose up -d --build

# 3. Acessar
#    http://localhost:8080   (login: ADMIN_USERNAME / ADMIN_PASSWORD do .env)
```

No primeiro boot o `entrypoint` do container `api`:
1. roda `alembic upgrade head` (cria o schema);
2. lê a planilha em `/frameworks` e popula o catálogo (seed);
3. cria o usuário admin a partir do `.env`;
4. inicia o Uvicorn.

### Logs / estado
```bash
docker compose logs -f api
docker compose ps
```

---

## Planilhas-fonte (bind volume read-only)

As planilhas **não** vão na imagem. Ficam no diretório `./frameworks` do host,
montado **read-only** no container:

```yaml
volumes:
  - ./frameworks:/frameworks:ro
```

Para atualizar o conteúdo **sem rebuild**: substitua/edite o `.xlsx` em
`./frameworks` e rode o **re-seed** (idempotente — faz *upsert*, não duplica):

* pela UI: aba **Framework → "Re-seed da planilha"** (somente admin); ou
* pela API:
  ```bash
  curl -X POST http://localhost:8080/api/admin/reseed \
       -H "Authorization: Bearer <token>"
  ```

O nome do arquivo lido é definido por `SEED_WORKBOOK` no `.env`.

---

## Parser modular

A ingestão usa **openpyxl** e é modular (`api/app/ingest/`):

* `base.py` — estruturas intermediárias e a interface `WorkbookParser`;
* `viaconnect_parser.py` — parser **exato** desta planilha (abas, linha de
  cabeçalho na linha 4, itens via regex `^[A-Z]{2,4}-\d+`, escala lida da
  *data validation* de cada aba, metadados da aba `Framework`);
* `seeder.py` — grava o `ParsedFramework` no banco com *upsert* idempotente.

Se o layout mudar (novas abas/colunas/escala), basta ajustar as constantes no
topo de `viaconnect_parser.py` — o restante (seeder, scoring, API, UI) é
desacoplado. Para um workbook totalmente diferente, implemente outro
`WorkbookParser` e use-o no `seeder`.

---

## Endpoints principais (`/api`)

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/auth/login` | login (OAuth2 password form) → JWT |
| `GET`  | `/auth/me` | usuário atual |
| `GET/POST/PATCH/DELETE` | `/users` | CRUD de usuários (admin) |
| `GET`  | `/frameworks`, `/frameworks/{id}` | catálogo (domínios/controles/perguntas/escala) |
| `GET/POST/PATCH/DELETE` | `/assessments` | CRUD de avaliações |
| `GET/PUT` | `/assessments/{id}/responses` | ler / salvar respostas (bulk upsert) |
| `GET`  | `/assessments/{id}/dashboard` | scores consolidados (live) |
| `POST` | `/assessments/{id}/recompute` | recalcula e persiste snapshot |
| `GET`  | `/admin/frameworks-dir` | lista `.xlsx` montados |
| `POST` | `/admin/reseed` | re-seed da planilha |

Docs interativas (apenas via rede interna/dev): `:8000/docs`.

---

## Telas

* **Avaliações** — lista + criação de avaliações.
* **Execução** — perguntas agrupadas por domínio/controle, com dropdowns de
  *avaliação atual* e *meta* (escala oficial de cada domínio) + evidências.
* **Dashboard** — gauge de maturidade geral, radar dos 9 domínios e **um gráfico
  próprio por domínio** com seus subdomínios, mais tabela de gaps.
* **Framework** — visão do catálogo e re-seed (admin).
* **Usuários** — CRUD de acesso interno (admin).

---

## Estrutura do projeto

```
soc-maturity/
├── docker-compose.yml
├── .env.example
├── frameworks/                     # planilhas (bind read-only)
├── api/
│   ├── Dockerfile · entrypoint.sh · requirements.txt · alembic.ini
│   ├── migrations/                 # Alembic (0001_initial)
│   └── app/
│       ├── main.py · config.py · database.py · security.py · cli.py
│       ├── models/ · schemas/ · routers/ · services/ · ingest/
└── web/
    ├── Dockerfile · nginx.conf · package.json · vite/tailwind/ts configs
    └── src/
        ├── components/ui · components/charts · components/layout
        ├── pages/ (Login, Assessments, AssessmentRun, Dashboard, Frameworks, Users)
        └── lib/ (api, auth, types, utils)
```

---

## Desenvolvimento local (opcional, sem Docker)

```bash
# API
cd api && python -m venv .venv && . .venv/Scripts/activate   # (Windows)
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://soc:soc@localhost:5432/soc_maturity
alembic upgrade head && python -m app.cli seed
uvicorn app.main:app --reload

# Web (proxy /api -> :8000 já configurado no vite.config.ts)
cd web && npm install && npm run dev
```

---

> Instrumento autoral Viaconnect que segue a **estrutura e a nomenclatura
> pública** de cada framework de referência (SIM3, CREST, CTI-CMM, PSIRT
> Services Framework, MITRE Engage, PEAK/HMM, SANS VMMM, SOC-CMM). Para avaliação
> oficial/certificável, use a ferramenta original do mantenedor.
