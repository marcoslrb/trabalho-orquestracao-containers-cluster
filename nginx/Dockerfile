FROM nginx:1.25-alpine

# Remover config padrão
RUN rm /etc/nginx/conf.d/default.conf

# Copiar configuração customizada
COPY nginx.conf /etc/nginx/nginx.conf

# Copiar arquivos do frontend
COPY html/ /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
