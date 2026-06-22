# Viaconnect SOC Maturity — Health Check

Aplicação web **interna** para avaliação de maturidade de SOC, baseada
**fielmente** nos instrumentos *Viaconnect Health Check* e *SOC-CMM 2.4.2*
(planilhas em `frameworks/`).

A aplicação é um **único arquivo auto-contido — `preview.html`** (HTML + JS +
ECharts + dados embutidos). Não precisa de banco, backend nem build: os dados
ficam no `localStorage` do navegador. **Login padrão: `admin` / `admin`.**

> Esta é a **única versão** do produto. (O antigo scaffold React + FastAPI +
> Postgres foi removido do repositório — ele divergiu e não tinha as funcionalidades
> atuais. Veja o histórico do git se precisar dele.)

---

## 🚀 Rodar no Linux (clonar e executar)

**Opção 1 — Docker (recomendado para servidor):**
```bash
git clone https://github.com/CarlosHenchen/claude-soc.git
cd claude-soc
docker compose up -d --build
# abra http://SEU_SERVIDOR:8080   (login: admin / admin)
```
Porta configurável: `PORT=9090 docker compose up -d --build`.

**Opção 2 — sem Docker (qualquer máquina):**
```bash
# servir a pasta com um servidor estático qualquer:
python3 -m http.server 8080
# abra http://SEU_SERVIDOR:8080/preview.html
```

**Opção 3 — sem servidor:** basta abrir o arquivo `preview.html` num navegador
(duplo-clique). Funciona offline.

---

## O que a aplicação faz

- **3 tipos de avaliação** com os itens reais extraídos das planilhas:
  - **Domínios (Viaconnect Health Check)** — 9 domínios, 45 aspectos, 166 itens.
  - **SOC-CMM 2.4.2 — Basic** — 5 domínios, 27 aspectos (Maturity + Capability).
  - **SOC-CMM 2.4.2 — Advanced** — idem, com importância editável.
- **Organizações** com **ciclos de execução** e **evolução de postura** ao longo do tempo.
- Abas por organização: **Assessment · Evolução · Recomendações · Roadmap · Entregáveis Viaconnect**.
- **Recomendações** fundamentadas nos frameworks (CTI-CMM, HMM, SIM3, MITRE Engage, etc.)
  e nos entregáveis Viaconnect, com botão **"✨ Gerar com Claude"** (IA) — ver abaixo.
- **Roadmap** priorizável por horizonte (3/6/12 meses).
- **Dashboards** com gauge, radar e ranking (ECharts, escala 0–5) e **exportar PDF** (via impressão do navegador).
- **Configurações**: organizações, usuários internos e integração com o Claude.

---

## Integração com o Claude (IA)

A aba **Recomendações** pode gerar uma análise sob medida chamando a API do Claude.
Em **Configurações → Integração com Claude**, informe a **chave da API** e o **modelo**
(padrão `claude-opus-4-8`). A chamada vai **direto do navegador** para
`api.anthropic.com`.

> ⚠️ **Segurança:** a chave fica salva no `localStorage` do navegador e trafega do
> cliente. Use apenas em ambiente confiável e **sempre sob HTTPS** (ver Produção).
> É um modelo "cada usuário usa a própria chave".

---

## Produção (HTTPS)

Como a página chama a API do Claude pelo navegador, **sirva por HTTPS**. O jeito
mais simples é pôr um proxy reverso com TLS automático na frente. Exemplo com
**Caddy** (crie um `Caddyfile`, troque o domínio):

```caddy
soc.seudominio.com {
    reverse_proxy app:80
}
```
Aponte o DNS do domínio para o servidor **antes** de subir (para o Let's Encrypt
do Caddy emitir o certificado), adicione um serviço `caddy` ao `docker-compose.yml`
publicando `80:443` e remova o `ports:` do serviço `app` (só o Caddy fica exposto).

---

## Regenerar `preview.html` (apenas para desenvolvedores)

O `preview.html` já vem versionado e pronto. Só é preciso regenerar se as planilhas
em `frameworks/` mudarem. Requer Python 3 + `openpyxl`:

```bash
pip install openpyxl
python extract_frameworks.py   # planilhas (frameworks/) -> assets/frameworks.json
python gen_preview.py          # assets/ -> preview.html
```

---

## Estrutura do repositório

```
preview.html              # A APLICAÇÃO (auto-contida)
gen_preview.py            # gera preview.html a partir de assets/
extract_frameworks.py     # gera assets/frameworks.json a partir de frameworks/
assets/
  frameworks.json         # dados embutidos (gerado)
  echarts.min.js          # biblioteca de gráficos (Apache-2.0)
ingest/                   # parser das planilhas (usado por extract_frameworks.py)
frameworks/               # planilhas-fonte (.xlsx)
Dockerfile                # imagem Nginx que serve o preview.html
docker-compose.yml        # docker compose up -> app na porta 8080
```
