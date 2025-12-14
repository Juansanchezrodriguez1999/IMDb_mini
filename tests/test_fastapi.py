from app.main import app


def test_app_starts():
    """
    La app FastAPI carga correctamente
    """
    assert app is not None


def test_people_route_exists():
    """
    El endpoint /people/search está registrado
    """
    paths = [route.path for route in app.router.routes]
    assert "/people/search" in paths


def test_titles_route_exists():
    """
    El endpoint /titles/search está registrado
    """
    paths = [route.path for route in app.router.routes]
    assert "/titles/search" in paths
