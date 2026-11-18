"""
Tests para la API de Música.
Pruebas unitarias y de integración usando pytest.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.models import Cancion, Favorito, Usuario
from main import app

# =============================================================================
# CONFIGURACIÓN DE FIXTURES
# =============================================================================


# Fixture para crear una base de datos en memoria para testing
@pytest.fixture(name="session")
def session_fixture():
    """
    Crea una sesión de base de datos en memoria para cada test.
    Se limpia automáticamente después de cada test.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


# Fixture para cliente de pruebas
@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Crea un cliente de pruebas de FastAPI con la sesión de test.
    """

    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(name="usuario_test")
def usuario_test_fixture(session: Session):
    """
    Crea un usuario de prueba en la base de datos.
    """

    usuario = Usuario(
        nombre="Usuario de prueba",
        correo="usuario.prueba@example.com",
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@pytest.fixture(name="cancion_test")
def cancion_test_fixture(session: Session):
    """
    Crea una cancion de prueba en la base de datos.
    """
    cancion = Cancion(
        titulo="Canción Test",
        artista="Artista Test",
        album="Álbum Test",
        duracion=180,
        año=2020,
        genero="Rock",
    )
    session.add(cancion)
    session.commit()
    session.refresh(cancion)
    return cancion


# =============================================================================
# TESTS DE USUARIOS
# =============================================================================


class TestUsuarios:
    """Tests para los endpoints de usuarios."""

    def test_listar_usuarios(self, client: TestClient):
        """Test para GET /api/usuarios"""
        response = client.get("/api/usuarios")
        assert response.status_code == 200
        assert response.json() == []

    def test_crear_usuario(self, client: TestClient):
        """Test para POST /api/usuarios"""
        response = client.post(
            "/api/usuarios",
            json={"nombre": "Ana García", "correo": "ana@example.com"},
        )
        assert response.status_code == 201
        assert response.json()["nombre"] == "Ana García"

    def test_crear_usuario_correo_duplicado(
        self, client: TestClient, usuario_test: Usuario
    ):
        """Test para verificar que no se permiten correos duplicados"""
        response = client.post(
            "/api/usuarios",
            json={
                "nombre": "Otro usuario",
                "correo": usuario_test.correo,
            },
        )
        assert response.status_code == 409

    def test_obtener_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para GET /api/usuarios/{id}"""
        response = client.get(f"/api/usuarios/{usuario_test.id}")
        assert response.status_code == 200
        assert response.json()["correo"] == usuario_test.correo

    def test_obtener_usuario_no_existe(self, client: TestClient):
        """Test para verificar error 404 con usuario inexistente"""
        response = client.get("/api/usuarios/999999")
        assert response.status_code == 404

    def test_actualizar_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para PUT /api/usuarios/{id}"""
        response = client.put(
            f"/api/usuarios/{usuario_test.id}",
            json={"nombre": "Usuario actualizado"},
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "Usuario actualizado"

    def test_eliminar_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para DELETE /api/usuarios/{id}"""
        response = client.delete(f"/api/usuarios/{usuario_test.id}")
        assert response.status_code == 204
        assert client.get(f"/api/usuarios/{usuario_test.id}").status_code == 404


# =============================================================================
# TESTS DE canciónS
# =============================================================================


class TestCancions:
    """Tests para los endpoints de cancións."""

    def test_listar_cancions(self, client: TestClient):
        """Test para GET /api/cancions"""
        response = client.get("/api/canciones")
        assert response.status_code == 200
        assert response.json() == []

    def test_crear_cancion(self, client: TestClient):
        """Test para POST /api/cancions"""
        response = client.post(
            "/api/canciones",
            json={
                "titulo": "Imagine",
                "artista": "John Lennon",
                "album": "Imagine",
                "duracion": 183,
                "año": 1971,
                "genero": "Rock",
            },
        )
        assert response.status_code == 201
        assert response.json()["titulo"] == "Imagine"

    def test_obtener_cancion(self, client: TestClient, cancion_test: Cancion):
        """Test para GET /api/cancions/{id}"""
        response = client.get(f"/api/canciones/{cancion_test.id}")
        assert response.status_code == 200
        assert response.json()["titulo"] == cancion_test.titulo

    def test_actualizar_cancion(self, client: TestClient, cancion_test: Cancion):
        """Test para PUT /api/cancions/{id}"""
        response = client.put(
            f"/api/canciones/{cancion_test.id}",
            json={"titulo": "Canción actualizada"},
        )
        assert response.status_code == 200
        assert response.json()["titulo"] == "Canción actualizada"

    def test_eliminar_cancion(self, client: TestClient, cancion_test: Cancion):
        """Test para DELETE /api/cancions/{id}"""
        response = client.delete(f"/api/canciones/{cancion_test.id}")
        assert response.status_code == 204
        assert client.get(f"/api/canciones/{cancion_test.id}").status_code == 404

    def test_buscar_canciones(self, client: TestClient, cancion_test: Cancion):
        """Test para GET /api/canciones/buscar"""
        response = client.get(
            "/api/canciones/buscar",
            params={"titulo": "Test", "artista": "Artista", "genero": "Rock"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == cancion_test.id

    def test_buscar_canciones_sin_filtros(
        self, client: TestClient, cancion_test: Cancion
    ):
        """Test para buscar canciones sin parámetros"""
        response = client.get("/api/canciones/buscar")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_buscar_cancions(self, client: TestClient, cancion_test: Cancion):
        """Test para GET /api/cancions/buscar"""
        response = client.get("/api/canciones/buscar", params={"artista": "Artista"})
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_buscar_cancions_multiples_filtros(
        self, client: TestClient, cancion_test: Cancion
    ):
        """Test para búsqueda con múltiples parámetros"""
        response = client.get(
            "/api/canciones/buscar",
            params={"titulo": "Test", "genero": "Rock", "artista": "Artista"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1


# =============================================================================
# TESTS DE FAVORITOS
# =============================================================================


class TestFavoritos:
    """Tests para los endpoints de favoritos."""

    def test_listar_favoritos(self, client: TestClient):
        """Test para GET /api/favoritos"""
        response = client.get("/api/favoritos")
        assert response.status_code == 200
        assert response.json() == []

    def test_crear_favorito(
        self, client: TestClient, usuario_test: Usuario, cancion_test: Cancion
    ):
        """Test para POST /api/favoritos"""
        response = client.post(
            "/api/favoritos",
            json={
                "id_usuario": usuario_test.id,
                "id_cancion": cancion_test.id,
            },
        )
        assert response.status_code == 201
        assert response.json()["id_usuario"] == usuario_test.id

    def test_crear_favorito_duplicado(
        self, client: TestClient, usuario_test: Usuario, cancion_test: Cancion
    ):
        """Test para verificar que no se permiten favoritos duplicados"""
        client.post(
            "/api/favoritos",
            json={
                "id_usuario": usuario_test.id,
                "id_cancion": cancion_test.id,
            },
        )
        response = client.post(
            "/api/favoritos",
            json={
                "id_usuario": usuario_test.id,
                "id_cancion": cancion_test.id,
            },
        )
        assert response.status_code == 409

    def test_eliminar_favorito(
        self,
        client: TestClient,
        session: Session,
        usuario_test: Usuario,
        cancion_test: Cancion,
    ):
        """Test para DELETE /api/favoritos/{id}"""
        favorito = client.post(
            "/api/favoritos",
            json={
                "id_usuario": usuario_test.id,
                "id_cancion": cancion_test.id,
            },
        ).json()
        response = client.delete(f"/api/favoritos/{favorito['id']}")
        assert response.status_code == 204
        assert client.get(f"/api/favoritos/{favorito['id']}").status_code == 404

    def test_obtener_favorito(
        self, client: TestClient, usuario_test: Usuario, cancion_test: Cancion
    ):
        """Test para GET /api/favoritos/{id}"""
        creado = client.post(
            "/api/favoritos",
            json={
                "id_usuario": usuario_test.id,
                "id_cancion": cancion_test.id,
            },
        )
        response = client.get(f"/api/favoritos/{creado.json()['id']}")
        assert response.status_code == 200
        assert response.json()["id_usuario"] == usuario_test.id

    def test_eliminar_favorito_usuario(
        self, client: TestClient, usuario_test: Usuario, cancion_test: Cancion
    ):
        """Test para DELETE /api/usuarios/{id}/favoritos/{id_cancion}"""
        creado = client.post(
            f"/api/usuarios/{usuario_test.id}/favoritos/{cancion_test.id}"
        )
        assert creado.status_code == 201

        eliminado = client.delete(
            f"/api/usuarios/{usuario_test.id}/favoritos/{cancion_test.id}"
        )
        assert eliminado.status_code == 204

        favoritos = client.get(f"/api/usuarios/{usuario_test.id}/favoritos")
        assert favoritos.status_code == 200
        assert favoritos.json() == []

    def test_favorito_usuario_duplicado(
        self, client: TestClient, usuario_test: Usuario, cancion_test: Cancion
    ):
        """Test para verificar duplicados desde la ruta de usuario"""
        ruta = f"/api/usuarios/{usuario_test.id}/favoritos/{cancion_test.id}"
        assert client.post(ruta).status_code == 201
        assert client.post(ruta).status_code == 409

    def test_marcar_favorito_usuario(
        self, client: TestClient, usuario_test: Usuario, cancion_test: Cancion
    ):
        """Test para POST /api/usuarios/{id}/favoritos/{id_cancion}"""
        response = client.post(
            f"/api/usuarios/{usuario_test.id}/favoritos/{cancion_test.id}"
        )
        assert response.status_code == 201

    def test_listar_favoritos_usuario(
        self,
        client: TestClient,
        session: Session,
        usuario_test: Usuario,
        cancion_test: Cancion,
    ):
        """Test para GET /api/usuarios/{id}/favoritos"""
        client.post(f"/api/usuarios/{usuario_test.id}/favoritos/{cancion_test.id}")
        response = client.get(f"/api/usuarios/{usuario_test.id}/favoritos")
        assert response.status_code == 200
        assert len(response.json()) == 1


# =============================================================================
# TESTS DE INTEGRACIÓN
# =============================================================================


class TestIntegracion:
    """Tests de integración que prueban flujos completos."""

    def test_flujo_completo(self, client: TestClient):
        """Test que verifica el flujo completo de la aplicación"""
        usuario = client.post(
            "/api/usuarios",
            json={"nombre": "Integración", "correo": "integracion@example.com"},
        )
        assert usuario.status_code == 201

        cancion = client.post(
            "/api/canciones",
            json={
                "titulo": "Integración",
                "artista": "Pruebas",
                "album": "Taller",
                "duracion": 200,
                "año": 2020,
                "genero": "Test",
            },
        )
        assert cancion.status_code == 201

        favorito = client.post(
            "/api/favoritos",
            json={
                "id_usuario": usuario.json()["id"],
                "id_cancion": cancion.json()["id"],
            },
        )
        assert favorito.status_code == 201

        favoritos = client.get(f"/api/usuarios/{usuario.json()['id']}/favoritos")
        assert favoritos.status_code == 200
        assert len(favoritos.json()) == 1


# =============================================================================
# TESTS DE VALIDACIÓN
# =============================================================================


class TestValidacion:
    """Tests para validaciones de datos."""

    def test_email_invalido(self, client: TestClient):
        """Test para verificar validación de email"""
        response = client.post(
            "/api/usuarios",
            json={"nombre": "Usuario", "correo": "correo-invalido"},
        )
        assert response.status_code == 422

    def test_año_cancion_invalido(self, client: TestClient):
        """Test para verificar validación de año"""
        response = client.post(
            "/api/canciones",
            json={
                "titulo": "Canción",
                "artista": "Artista",
                "album": "Álbum",
                "duracion": 180,
                "año": 1800,
                "genero": "Rock",
            },
        )
        assert response.status_code == 422

    def test_campos_requeridos(self, client: TestClient):
        """Test para verificar que los campos requeridos son obligatorios"""
        response = client.post("/api/usuarios", json={"nombre": ""})
        assert response.status_code == 422


class TestEndpointsGenerales:
    """Tests para los endpoints raíz y de salud."""

    def test_raiz(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["documentacion"] == "/docs"

    def test_health(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestPaginacion:
    """Tests para los parámetros de paginación."""

    def test_limitar_usuarios(self, client: TestClient, usuario_test: Usuario):
        otro = client.post(
            "/api/usuarios",
            json={"nombre": "Segundo", "correo": "segundo@example.com"},
        )
        assert otro.status_code == 201

        response = client.get("/api/usuarios", params={"skip": 0, "limit": 1})
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_limitar_canciones(self, client: TestClient, cancion_test: Cancion):
        response = client.get("/api/canciones", params={"skip": 0, "limit": 1})
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_limite_invalido(self, client: TestClient):
        response = client.get("/api/canciones", params={"limit": 0})
        assert response.status_code == 422


class TestEstadisticas:
    """Tests para estadísticas y canciones populares."""

    def test_estadisticas_generales(
        self, client: TestClient, usuario_test: Usuario, cancion_test: Cancion
    ):
        client.post(
            "/api/favoritos",
            json={
                "id_usuario": usuario_test.id,
                "id_cancion": cancion_test.id,
            },
        )
        response = client.get("/api/estadisticas/uso")
        assert response.status_code == 200
        data = response.json()
        assert data["total_usuarios"] == 1
        assert data["total_canciones"] == 1
        assert data["total_favoritos"] == 1
        assert data["canciones_mas_favoritas"][0]["titulo"] == cancion_test.titulo

    def test_canciones_populares(
        self, client: TestClient, usuario_test: Usuario, cancion_test: Cancion
    ):
        client.post(
            "/api/favoritos",
            json={
                "id_usuario": usuario_test.id,
                "id_cancion": cancion_test.id,
            },
        )
        response = client.get("/api/canciones/populares", params={"limit": 5})
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["total_favoritos"] == 1
