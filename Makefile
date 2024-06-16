.PHONY: \
	lint \
	fmt 

all:
	@echo "lint TARGET=<...>          Выполнить статический анализ кода."
	@echo "fmt  TARGET=<...>          Форматировать код."
	@echo "test TARGET=<...>          Запустить тесты."
	@echo "req TARGET=<...>           Сгенерировать зависимости."

SHELL := /bin/bash
TARGET ?= src/
FILES = $(TARGET)

lint:
	@if ! black --check $(FILES); then \
		echo "Run 'make fmt' to fix"; \
		false; \
	fi
	@if ! isort --check-only $(FILES); then \
		echo "Run 'make fmt' to fix"; \
		false; \
	fi
	flake8 $(FILES)
	pydocstyle $(FILES)
	mypy $(FILES)

fmt:
	black $(FILES)
	isort $(FILES)
