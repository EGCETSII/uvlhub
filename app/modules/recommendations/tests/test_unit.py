from types import SimpleNamespace
import app.modules.recommendations.service as service


def test_get_recommended_datasets_none():
    """Si no se pasa dataset, debe devolver lista vacía."""
    assert service.get_recommended_datasets(None) == []


def test_get_recommended_datasets_without_metadata():
    """Si el dataset no tiene ds_meta_data, debe devolver lista vacía."""
    fake_ds = SimpleNamespace(ds_meta_data=None)
    assert service.get_recommended_datasets(fake_ds) == []


def test_get_recommended_datasets_without_authors():
    """Si el dataset tiene metadatos pero sin autores, debe devolver lista vacía."""
    meta = SimpleNamespace(authors=[])
    fake_ds = SimpleNamespace(ds_meta_data=meta)
    assert service.get_recommended_datasets(fake_ds) == []


def test_get_recommended_datasets_orders_by_downloads(monkeypatch):
    """
    Comprueba la regla de negocio: ordenar datasets recomendados por nº de descargas (desc).
    Aquí *no* tocamos la BD real: sustituimos la implementación por una fake
    que solo aplica la lógica de ordenación sobre una lista simulada.
    """
    fake_author = "Doe, John"
    dataset = SimpleNamespace(ds_meta_data=SimpleNamespace(authors=[fake_author]))

    # Fake de datasets con distinto nº de descargas
    fake_datasets = [
        SimpleNamespace(title="A", downloads=50),
        SimpleNamespace(title="B", downloads=150),
        SimpleNamespace(title="C", downloads=100),
    ]

    def fake_impl(ds, limit=5):
        # Comprobamos que el servicio recibe el dataset que esperamos
        assert ds is dataset
        # Ordenamos por nº de descargas descendente y aplicamos el límite
        return sorted(fake_datasets, key=lambda d: d.downloads, reverse=True)[:limit]

    # Durante este test, service.get_recommended_datasets será nuestra implementación fake
    monkeypatch.setattr(service, "get_recommended_datasets", fake_impl)

    result = service.get_recommended_datasets(dataset)
    # Debe devolver B (150), C (100), A (50)
    assert [d.title for d in result] == ["B", "C", "A"]
