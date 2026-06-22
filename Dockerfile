# ============================================================================
# Viaconnect SOC Maturity — app de arquivo único (preview.html)
#
# Serve o preview.html (auto-contido: HTML + JS + ECharts + dados embutidos)
# por Nginx. Sem banco, sem backend. Persistência no localStorage do navegador.
#
#   docker build -t claude-soc .
#   docker run -d -p 8080:80 claude-soc       # http://localhost:8080
# (ou simplesmente: docker compose up -d --build)
# ============================================================================
FROM nginx:1.27-alpine

# O preview.html já vem versionado no repositório (não precisa de toolchain).
COPY preview.html /usr/share/nginx/html/index.html

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost/ >/dev/null 2>&1 || exit 1

EXPOSE 80
