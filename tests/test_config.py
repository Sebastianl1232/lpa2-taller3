import pytest
from pydantic import ValidationError

from musica_api.config import (
    DevelopmentSettings,
    ProductionSettings,
    Settings,
)
from musica_api.config import (
    TestingSettings as TestingSettingsModel,
)


def test_default_settings():
    settings = Settings()
    assert settings.database_url == "sqlite:///./musica.db"
    assert settings.port == 8000


def test_database_url_requires_scheme():
    with pytest.raises(ValidationError):
        Settings(database_url="musica.db")


def test_environment_settings():
    assert DevelopmentSettings().debug
    assert TestingSettingsModel().database_url == "sqlite:///./test_musica.db"
    assert not ProductionSettings().debug
