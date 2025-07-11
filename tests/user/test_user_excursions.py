from http import HTTPStatus


def test_get_excursions_list(client):
    r = client.get("/api/user/excursions")
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert "excursions" in data
    assert isinstance(data["excursions"], list)

    r = client.get("/api/user/excursions?title=несуществующее_название")
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert "excursions" in data
    assert data["excursions"] == []

    r = client.get("/api/user/excursions?category=Экскурсия&format_type=Групповая")
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert "excursions" in data
    assert isinstance(data["excursions"], list)

    r = client.get("/api/user/excursions?sort=-price")
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert "excursions" in data
