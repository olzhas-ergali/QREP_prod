# Ветка test: как залить исправления и сравнить с продом

**Цель:** все исправления держать в ветке `test`, прод (main) не трогать. Деплой теста → сравнение с продом.

---

## Шаг 1. Убедиться, что все нужные правки в рабочей копии

Сейчас изменены (если что-то ещё правили — добавьте в коммит):

- `service/API/presentation/rest/client.py` — баланс бонусов, totalSpent/totalRefunded, дописывание бонусов по чеку
- `service/API/presentation/rest/whats_app.py` — баланс бонусов (bonus / future_bonus)

Остальные правки из сессии (если есть в других файлах):

- `service/API/infrastructure/utils/smpt.py` — SMTP STARTTLS, .env
- `service/API/infrastructure/database/commands/client.py` — refresh после commit, дописывание бонусов
- `service/API/infrastructure/database/loyalty.py` — get_by_client_purchase_id
- `service/API/config/__init__.py` — MAIL_TLS_INSECURE, MAIL_ENCRYPTION

Проверка:

```bash
cd /Users/onyoka/Desktop/qr_services/QREP_prod
git status
git diff --name-only
```

---

## Шаг 2. Создать ветку test и переключиться на неё

Если ветка `test` уже есть на origin — взять её и обновить. Если нет — создать от текущего main.

**Вариант A: ветка test уже есть на GitHub**

```bash
git fetch origin
git checkout test
git pull origin test
```

**Вариант B: создать новую ветку test от main**

```bash
git fetch origin
git checkout -b test origin/main
```

Либо от текущего локального main (со всеми незакоммиченными правками):

```bash
git checkout -b test
```

---

## Шаг 3. Закоммитить все исправления в ветку test

```bash
git add service/API/presentation/rest/client.py
git add service/API/presentation/rest/whats_app.py
# если правили ещё файлы:
# git add service/API/infrastructure/utils/smpt.py
# git add service/API/infrastructure/database/commands/client.py
# git add service/API/infrastructure/database/loyalty.py
# git add service/API/config/__init__.py

git status   # проверить, что в индексе только нужное
git commit -m "fix: баланс бонусов (total_earned - total_spent), totalSpent/totalRefunded, доп. бонусы по чеку"
```

---

## Шаг 4. Запушить ветку test на GitHub

```bash
git push -u origin test
```

Если `origin/test` уже существует и история разъехалась:

```bash
git push origin test --force-with-lease
```

(использовать только если вы уверены, что перезаписываете именно свою тестовую ветку.)

---

## Шаг 5. Сравнить test с продом (main)

- На GitHub: сравнить ветки `test` и `main`:  
  `https://github.com/olzhas-ergali/QREP_prod/compare/main...test`
- Локально:

```bash
git fetch origin
git log origin/main..origin/test --oneline
git diff origin/main origin/test --stat
```

Так вы увидите коммиты и файлы, которые есть в test, но нет в main (прод).

---

## Шаг 6. Деплой теста и сравнение с продом

- На тестовом сервере/стенде деплой с ветки `test` (например `git pull origin test` и перезапуск сервисов).
- Прогон сценариев: чеки, бонусы, баланс, почта (если правили smpt).
- Сравнение поведения и ответов API с продом (main).

---

## Кратко: не трогать main

- Всё коммитить и пушить только в ветку **test**.
- В **main** не мерджить, пока тест не пройдёт и не будет решения выкатывать в прод.
- Когда будете готовы выкатить в прод: отдельный мердж `test` → `main` (через PR или вручную).

---

## Репозиторий QREP_qa (тесты)

Ссылка на QA-репозиторий: https://github.com/olzhas-ergali/QREP_qa  

Если автотесты живут в QREP_qa:

1. В QREP_prod — ветка `test` с исправлениями (как выше).
2. В QREP_qa — поднять/запустить тесты против **тестового окружения**, задеплоенного с ветки `test` из QREP_prod.
3. Сравнить результаты тестов и поведения с продом (деплой с main).

Так вы «заливаете все исправления в ветку test и сравниваете с продом», не трогая main.
