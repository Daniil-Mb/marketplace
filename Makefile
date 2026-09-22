# ===============================
# Настройки проекта
# ===============================

# Каталоги с кодом
PY_SRCS = src

# Порог для Radon
RADON_MIN_MI = 65

# ===============================
# Служебные цели
# ===============================

.PHONY: help install lint format type security cc mi hal raw check clean

help:
	@echo "Доступные цели:"
	@echo "  install   - Установка зависимостей"
	@echo "  lint      - Ruff check (с автофиксом)"
	@echo "  format    - Ruff format"
	@echo "  type      - Mypy (проверка типов)"
	@echo "  security  - Bandit (скан безопасности)"
	@echo "  cc        - Radon CC (цикломатическая сложность) + quality gate"
	@echo "  mi        - Radon MI (индекс поддерживаемости) + quality gate"
	@echo "  hal       - Radon Hal (метрика халстеда)"
	@echo "  raw       - Radon Raw (SLOC, LLOC, комментарии)"
	@echo "  check     - Быстрый локальный quality gate (все проверки)"
	@echo "  test      - Pytest (запуск тестов)"
	@echo "  clean     - Очистка кэша и временных файлов"


# ===============================
# Установка зависимостей
# ===============================

install:
	poetry install

# ===============================
# Ruff: линт и форматирование
# ===============================

lint:
	poetry run ruff check $(PY_SRCS) --fix

format:
	poetry run ruff format $(PY_SRCS)

# ===============================
# Mypy: проверка типов
# ===============================

type:
	poetry run mypy $(PY_SRCS)

# ===============================
# Bandit: анализ безопасности
# ===============================

security:
	poetry run bandit -r $(PY_SRCS) -lll -x .venv,venv,build,dist,migrations

# ===============================
# Radon: метрики качества
# ===============================

# Цикломатическая сложность
cc:
	@poetry run radon cc -s -a $(PY_SRCS)
	@echo "\n=== Quality Gate: Проверка сложности ==="
	@if poetry run radon cc -s $(PY_SRCS) | grep -E ' - [EF] '; then \
		echo "Radon CC: Обнаружены функции со сложностью E или F"; \
		exit 1; \
	else \
		echo "Radon CC: Нет функций со сложностью E/F"; \
	fi

# Индекс поддерживаемости
mi:
	@poetry run radon mi $(PY_SRCS)
	@echo "\n=== Quality Gate: Проверка поддерживаемости ==="
	@MI_BAD=$$(poetry run radon mi -n $(PY_SRCS) | grep -E '\([0-9.]+\)' | awk -F'[()]' '{print $$(NF-1)}' | awk '$$1+0<$(RADON_MIN_MI) {print}'); \
	if [ -n "$$MI_BAD" ]; then \
		echo "Radon MI: Найден MI < $(RADON_MIN_MI)"; \
		exit 1; \
	else \
		echo "Radon MI: Все файлы с MI >= $(RADON_MIN_MI)"; \
	fi

# Метрика Халстеда
hal:
	poetry run radon hal $(PY_SRCS)

# Raw метрики
raw:
	poetry run radon raw $(PY_SRCS)

# ===============================
# Комплексные цели
# ===============================

# Локальный быстрый прогон с автофиксом
check: lint format type security cc mi hal raw

# ===============================
# Очистка
# ===============================

clean:
	@echo "Очистка кэша Python..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Очистка завершена"

# ===============================
# Pytest: тесты
# ===============================

test:
	poetry run pytest
