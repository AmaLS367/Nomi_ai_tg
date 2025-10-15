class AppError(Exception):
    """Базовая ошибка приложения."""

class ConfigError(AppError):
    """Ошибка конфигурации."""

class NomiApiError(AppError):
    """Ошибка ответа Nomi API."""

class RateLimitExceeded(AppError):
    """Локальный лимит исчерпан."""

class DbError(AppError):
    """Ошибка БД."""
