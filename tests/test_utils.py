import pytest

from utils import formatear_duracion, generar_slug, validar_año, validar_correo


def test_validar_correo():
    assert validar_correo("usuario@example.com")
    assert not validar_correo("correo_invalido")


def test_formatear_duracion():
    assert formatear_duracion(355) == "5:55"


def test_formatear_duracion_negativa():
    with pytest.raises(ValueError):
        formatear_duracion(-1)


def test_generar_slug():
    assert generar_slug("  Canción Nueva!!  ") == "cancin-nueva"


def test_validar_año():
    assert validar_año(2020)
    assert not validar_año(1800)
