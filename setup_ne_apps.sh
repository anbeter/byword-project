#!/bin/bash

set -e

BASE_DIR="backend/apps"

echo "📁 Criando estrutura de apps..."

APPS=("accounts" "academic" "finance" "core")

for app in "${APPS[@]}"; do
    APP_PATH="$BASE_DIR/$app"

    mkdir -p "$APP_PATH/migrations"
    mkdir -p "$APP_PATH/services"
    mkdir -p "$APP_PATH/templates"

    touch "$APP_PATH/__init__.py"
    touch "$APP_PATH/models.py"
    touch "$APP_PATH/admin.py"
    touch "$APP_PATH/apps.py"
    touch "$APP_PATH/services/__init__.py"
    touch "$APP_PATH/migrations/__init__.py"
done

echo "📄 Criando arquivos adicionais úteis..."

# accounts
touch $BASE_DIR/accounts/signals.py
touch $BASE_DIR/accounts/managers.py

# academic
touch $BASE_DIR/academic/selectors.py
touch $BASE_DIR/academic/services/enrollment.py

# finance
touch $BASE_DIR/finance/services/payment.py
touch $BASE_DIR/finance/selectors.py

# core
touch $BASE_DIR/core/models_base.py
touch $BASE_DIR/core/choices.py

echo "⚙️ Criando apps.py básicos..."

# função helper
create_app_config () {
cat <<EOF > $1
from django.apps import AppConfig

class ${2}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.${3}'
EOF
}

create_app_config "$BASE_DIR/accounts/apps.py" "Accounts" "accounts"
create_app_config "$BASE_DIR/academic/apps.py" "Academic" "academic"
create_app_config "$BASE_DIR/finance/apps.py" "Finance" "finance"
create_app_config "$BASE_DIR/core/apps.py" "Core" "core"

echo "🧩 Criando modelos base (core)..."

cat <<EOF > $BASE_DIR/core/models_base.py
from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DateRangeModel(models.Model):
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True
EOF

echo "📌 Criando placeholders de models..."

for app in "${APPS[@]}"; do
cat <<EOF > "$BASE_DIR/$app/models.py"
from django.db import models

# TODO: implement models
EOF
done

echo "🛠️ Criando admin básico..."

for app in "${APPS[@]}"; do
cat <<EOF > "$BASE_DIR/$app/admin.py"
from django.contrib import admin

# Register your models here.
EOF
done

echo "📦 Estrutura criada com sucesso!"
