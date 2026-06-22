# Frontend (SPA modular) servido por Nginx, que também faz proxy de /api -> api.
# Os arquivos já vêm gerados no repositório (gen_preview.py) — sem build Node.
FROM nginx:1.27-alpine

RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/app.conf
COPY index.html app.js data.js echarts.min.js /usr/share/nginx/html/

EXPOSE 80
