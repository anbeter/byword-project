#!/bin/bash

# interromper script se algo falhar? 
# set -e

# =============================
# Criar estrutura de pastas
# =============================

mkdir -p backend/config
mkdir -p backend/media/pdfs
mkdir -p backend/apps/byword/wordsearch
mkdir -p backend/apps/byword/services
mkdir -p frontend/src/services
mkdir -p frontend/src/views
mkdir -p backend/apps/byword/templates/admin

# =============================
# Criação dos arquivos
# =============================

# raiz
touch docker-compose.yml
touch .env

# backend
touch backend/Dockerfile
touch backend/requirements.txt
touch backend/manage.py

# config Django
touch backend/config/__init__.py
touch backend/config/settings.py
touch backend/config/urls.py
touch backend/config/asgi.py
touch backend/config/wsgi.py

# app byword
touch backend/apps/byword/__init__.py
touch backend/apps/byword/models.py
touch backend/apps/byword/admin.py
touch backend/apps/byword/views.py
touch backend/apps/byword/serializers.py
touch backend/apps/byword/urls.py
touch backend/apps/byword/services/__init__.py
touch backend/apps/byword/services/wordsearch.py

# wordsearch
touch backend/apps/byword/wordsearch/__init__.py
touch backend/apps/byword/wordsearch/engine.py

# frontend
touch frontend/Dockerfile
touch frontend/index.html
touch frontend/package.json
touch frontend/vite.config.js

# src
touch frontend/src/main.js
touch frontend/src/App.vue
touch frontend/src/services/api.js

# views
touch frontend/src/views/Login.vue
touch frontend/src/views/Dashboard.vue

echo "Arquivos criados com sucesso!"

