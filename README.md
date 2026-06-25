# 📦 Catálogo de Produtos e Categorias – Cluster K3s

**Grupo 2 – Tema 2 | Serviços de Redes**

API REST (FastAPI) com frontend web (NGINX) para gerenciamento de produtos e categorias, orquestrada em cluster K3s de 2 VMs com observabilidade via Grafana Loki.

---

## 📐 Topologia do Cluster

```
┌──────────────────────────────────────────────────────────────────────┐
│                        CLUSTER K3s (2 nós)                          │
│                                                                      │
│  ┌────────────────── VM2 (server/control-plane) ──────────────────┐  │
│  │  Label: layer=app                                              │  │
│  │                                                                │  │
│  │  ┌─────────────────┐        ┌─────────────────┐               │  │
│  │  │  NGINX (x2)      │        │  FastAPI (x2)    │              │  │
│  │  │  Deployment       │───────▶│  Deployment      │             │  │
│  │  │  NodePort :30080  │        │  ClusterIP :8000 │             │  │
│  │  └─────────────────┘        └────────┬─────────┘              │  │
│  └──────────────────────────────────────┼────────────────────────┘  │
│                                         │                           │
│  ┌────────────────── VM1 (agent/worker) ─┼───────────────────────┐  │
│  │  Label: layer=dados                   │                       │  │
│  │                                       ▼                       │  │
│  │  ┌──────────────────┐    ┌─────────────────┐                  │  │
│  │  │  PostgreSQL       │    │  Grafana Loki    │                 │  │
│  │  │  StatefulSet (x1) │    │  Deployment (x1) │                │  │
│  │  │  ClusterIP :5432  │    │  ClusterIP :3100 │                │  │
│  │  │  PVC 10Gi         │    │  PVC 5Gi         │                │  │
│  │  └──────────────────┘    └─────────────────┘                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Rede interna: Flannel (CNI padrão K3s)                             │
│  Acesso externo: apenas NGINX via NodePort 30080                    │
└──────────────────────────────────────────────────────────────────────┘
```

### Fluxo de rede

1. **Usuário externo** → `http://<IP_VM2>:30080` → **NGINX** (NodePort)
2. **NGINX** → `http://fastapi-service:8000` → **FastAPI** (ClusterIP)
3. **FastAPI** → `postgres-service:5432` → **PostgreSQL** (ClusterIP)
4. **FastAPI** → `loki-service:3100` → **Loki** (ClusterIP) — envio de logs

---

## 📁 Estrutura do Repositório

```
.
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py          # App FastAPI + middleware de logging
│       ├── database.py      # Conexão SQLAlchemy + PostgreSQL
│       ├── models.py        # Modelos: Categoria, Produto
│       ├── schemas.py       # Schemas Pydantic
│       ├── logger.py        # Envio de logs ao Loki via HTTP
│       └── routes/
│           ├── __init__.py
│           ├── categorias.py  # CRUD de categorias
│           └── produtos.py    # CRUD de produtos
├── nginx/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── html/
│       ├── index.html
│       ├── style.css
│       └── script.js
├── loki/
│   └── loki-config.yaml
└── k8s/
    ├── namespace.yaml
    ├── secrets.yaml
    ├── postgres-pvc.yaml
    ├── postgres-statefulset.yaml
    ├── postgres-service.yaml
    ├── loki-configmap.yaml
    ├── loki-pvc.yaml
    ├── loki-deployment.yaml
    ├── loki-service.yaml
    ├── fastapi-deployment.yaml
    ├── fastapi-service.yaml
    ├── nginx-configmap.yaml
    ├── nginx-deployment.yaml
    └── nginx-service.yaml
```

---

## 🚀 Instalação e Configuração

### Pré-requisitos

- 2 VMs com Ubuntu 22.04+ (ou similar), comunicando-se na mesma rede
- Docker instalado em ambas as VMs (para build das imagens)
- Acesso root/sudo

### 1. Instalar K3s na VM2 (server/control-plane)

```bash
# Na VM2 (será o server)
curl -sfL https://get.k3s.io | sh -

# Verificar se o K3s está rodando
sudo systemctl status k3s

# Obter o token para juntar o agent
sudo cat /var/lib/rancher/k3s/server/node-token

# Configurar kubectl para o usuário
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config
export KUBECONFIG=~/.kube/config
```

### 2. Instalar K3s na VM1 (agent/worker)

```bash
# Na VM1 – substituir <IP_VM2> e <TOKEN>
curl -sfL https://get.k3s.io | K3S_URL=https://<IP_VM2>:6443 K3S_TOKEN=<TOKEN> sh -

# Verificar se o agent está rodando
sudo systemctl status k3s-agent
```

### 3. Verificar o cluster e rotular nós

```bash
# Na VM2 (server)
kubectl get nodes

# Rotular os nós para separar camadas
kubectl label node <NOME_VM1> layer=dados
kubectl label node <NOME_VM2> layer=app

# Verificar labels
kubectl get nodes --show-labels
```

### 4. Construir e publicar imagens Docker

```bash
# Na máquina de desenvolvimento

# Backend
cd backend/
docker build -t SEU_DOCKERHUB_USER/catalogo-backend:latest .
docker push SEU_DOCKERHUB_USER/catalogo-backend:latest

# NGINX/Frontend
cd ../nginx/
docker build -t SEU_DOCKERHUB_USER/catalogo-nginx:latest .
docker push SEU_DOCKERHUB_USER/catalogo-nginx:latest
```

> **Nota:** Substitua `SEU_DOCKERHUB_USER` nos manifests `k8s/fastapi-deployment.yaml` e `k8s/nginx-deployment.yaml`.

### 5. Aplicar manifests no cluster

```bash
# Na VM2 (server), na raiz do repositório
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/loki-configmap.yaml
kubectl apply -f k8s/loki-pvc.yaml
kubectl apply -f k8s/loki-deployment.yaml
kubectl apply -f k8s/loki-service.yaml
kubectl apply -f k8s/fastapi-deployment.yaml
kubectl apply -f k8s/fastapi-service.yaml
kubectl apply -f k8s/nginx-configmap.yaml
kubectl apply -f k8s/nginx-deployment.yaml
kubectl apply -f k8s/nginx-service.yaml
```

Ou de forma simplificada:

```bash
kubectl apply -f k8s/
```

---

## ✅ Comandos de Verificação

### Status geral do cluster

```bash
# Nós do cluster
kubectl get nodes -o wide

# Todos os recursos no namespace catalogo
kubectl get all -n catalogo

# Pods com detalhes (nó onde está rodando)
kubectl get pods -n catalogo -o wide

# Services
kubectl get svc -n catalogo

# PVCs
kubectl get pvc -n catalogo
```

### Verificar separação de camadas

```bash
# Pods na VM1 (layer=dados) – deve mostrar PostgreSQL e Loki
kubectl get pods -n catalogo -o wide | grep <NOME_VM1>

# Pods na VM2 (layer=app) – deve mostrar FastAPI e NGINX
kubectl get pods -n catalogo -o wide | grep <NOME_VM2>
```

### Testar a API

```bash
# Health check
curl http://<IP_VM2>:30080/api/health

# Listar categorias
curl http://<IP_VM2>:30080/api/categorias/

# Criar categoria
curl -X POST http://<IP_VM2>:30080/api/categorias/ \
  -H "Content-Type: application/json" \
  -d '{"nome": "Eletrônicos", "descricao": "Dispositivos eletrônicos"}'

# Criar produto
curl -X POST http://<IP_VM2>:30080/api/produtos/ \
  -H "Content-Type: application/json" \
  -d '{"nome": "Notebook", "descricao": "Notebook 15 polegadas", "preco": 3500.00, "quantidade": 10, "categoria_id": 1}'

# Listar produtos
curl http://<IP_VM2>:30080/api/produtos/
```

### Verificar que portas internas NÃO estão expostas

```bash
# De uma máquina EXTERNA ao cluster, estas conexões devem FALHAR:
curl http://<IP_VM1>:5432    # PostgreSQL – deve falhar
curl http://<IP_VM1>:3100    # Loki – deve falhar
curl http://<IP_VM2>:8000    # FastAPI – deve falhar

# Apenas esta deve funcionar:
curl http://<IP_VM2>:30080   # NGINX – OK ✓
```

---

## 📊 Consulta de Logs no Loki

Os logs são enviados pelo FastAPI via HTTP para o Loki. Para consultar **de dentro do cluster**:

```bash
# Acessar um pod do FastAPI para fazer consultas internas
kubectl exec -it -n catalogo deploy/fastapi -- /bin/sh

# Ou usar port-forward para acessar o Loki localmente
kubectl port-forward -n catalogo svc/loki-service 3100:3100
```

### Consultar labels disponíveis

```bash
curl -s http://localhost:3100/loki/api/v1/labels | python3 -m json.tool
```

### Consultar logs recentes (últimos 30 minutos)

```bash
# Todos os logs do backend
curl -s "http://localhost:3100/loki/api/v1/query_range" \
  --data-urlencode 'query={job="catalogo-backend"}' \
  --data-urlencode "start=$(date -d '30 minutes ago' +%s)000000000" \
  --data-urlencode "end=$(date +%s)000000000" \
  --data-urlencode "limit=50" | python3 -m json.tool

# Apenas logs de requisições
curl -s "http://localhost:3100/loki/api/v1/query_range" \
  --data-urlencode 'query={job="catalogo-backend", event="request"}' \
  --data-urlencode "start=$(date -d '30 minutes ago' +%s)000000000" \
  --data-urlencode "end=$(date +%s)000000000" \
  --data-urlencode "limit=20" | python3 -m json.tool

# Apenas erros
curl -s "http://localhost:3100/loki/api/v1/query_range" \
  --data-urlencode 'query={job="catalogo-backend", level="error"}' \
  --data-urlencode "start=$(date -d '1 hour ago' +%s)000000000" \
  --data-urlencode "end=$(date +%s)000000000" | python3 -m json.tool

# Log de startup
curl -s "http://localhost:3100/loki/api/v1/query_range" \
  --data-urlencode 'query={job="catalogo-backend", event="startup"}' \
  --data-urlencode "start=$(date -d '1 hour ago' +%s)000000000" \
  --data-urlencode "end=$(date +%s)000000000" | python3 -m json.tool
```

### Valores de uma label

```bash
curl -s "http://localhost:3100/loki/api/v1/label/level/values" | python3 -m json.tool
```

---

## 🔧 Tecnologias Utilizadas

| Componente    | Tecnologia              | Versão       |
|---------------|-------------------------|--------------|
| Orquestrador  | K3s                     | latest       |
| Backend       | Python + FastAPI         | 3.11 / 0.111 |
| Frontend      | NGINX + HTML/CSS/JS      | 1.25         |
| Banco de Dados| PostgreSQL               | 16-alpine    |
| Observabilidade| Grafana Loki            | 2.9.6        |
| ORM           | SQLAlchemy               | 2.0          |
| HTTP Client   | httpx                   | 0.27         |

---

## 👥 Grupo 2

Trabalho de Serviços de Redes – Tema 2: Catálogo de Produtos e Categorias.
