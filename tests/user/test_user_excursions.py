from http import HTTPStatus

import pytest

from backend.core.messages import AuthMessages
from backend.core.models.event_models import EventSession
from tests.conftest import TestUserData


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


def test_get_reservations(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    r = client.get("/api/user/reservations", headers=headers)
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert "reservations" in data
    assert isinstance(data["reservations"], list)


class TestUserReservations:

    @pytest.fixture
    def headers(self, access_token):
        return {"Authorization": f"Bearer {access_token}"}

    def test_create_reservation(self, client, app, headers, existing_event_id):
        with app.app_context():
            session_obj = EventSession.query.filter_by(event_id=existing_event_id).first()
            assert session_obj is not None, "Сеанс экскурсии не найден"

            payload = {
                "session_id": session_obj.session_id,
                "full_name": TestUserData.FULL_NAME,
                "phone_number": TestUserData.PHONE,
                "email": TestUserData.EMAIL,
                "participants_count": 1
            }
            response = client.post("/api/user/v2/reservations", json=payload, headers=headers)
            assert response.status_code == HTTPStatus.CREATED, response.get_data(as_text=True)
            resp_data = response.get_json()
            assert "message" in resp_data
            assert "успешно" in resp_data["message"].lower()
            assert "reservation_id" in resp_data

            reservation_id = resp_data["reservation_id"]

            self._check_reservation_in_list(client, headers, reservation_id, cancelled_expected=False)

            self._cancel_reservation(client, headers, reservation_id)

            self._check_reservation_in_list(client, headers, reservation_id, cancelled_expected=True)

    def _check_reservation_in_list(self, client, headers, reservation_id, cancelled_expected):
        response = client.get("/api/user/reservations", headers=headers)
        assert response.status_code == HTTPStatus.OK
        resp_data = response.get_json()

        assert "reservations" in resp_data
        res_list = resp_data["reservations"]
        assert isinstance(res_list, list)
        assert len(res_list) > 0, "Список броней пуст"

        found = False
        for res in res_list:
            if res["reservation_id"] == reservation_id:
                found = True
                assert isinstance(res["is_cancelled"], bool)
                assert res["is_cancelled"] is cancelled_expected
            assert isinstance(res["reservation_id"], int)
            assert isinstance(res["session_id"], int)
            assert isinstance(res["user_id"], int)
            assert isinstance(res["booked_at"], str)
            assert isinstance(res["full_name"], str)
            assert isinstance(res["phone_number"], str)
            assert isinstance(res["email"], str)
            assert isinstance(res["participants_count"], int)
            assert isinstance(res["is_cancelled"], bool)
            assert isinstance(res["is_paid"], bool)
            assert isinstance(res["excursion_title"], str)
            assert isinstance(res["session_start_datetime"], str)
            assert isinstance(res["place"], str)
            assert isinstance(res["total_cost"], (float, int))
            assert isinstance(res["payment_status"], str)
        assert found, f"Бронь с id {reservation_id} не найдена в списке"

    def _cancel_reservation(self, client, headers, reservation_id):
        cancel_payload = {"reservation_id": reservation_id}
        cancel_response = client.delete("/api/user/v2/reservations", json=cancel_payload, headers=headers)
        assert cancel_response.status_code == HTTPStatus.OK, cancel_response.get_data(as_text=True)
        cancel_data = cancel_response.get_json()
        assert "message" in cancel_data
        assert "отменено" in cancel_data["message"].lower()


def test_delete_profile(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    r = client.delete("/api/user/profile", headers=headers)
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert AuthMessages.USER_DELETED_SELF in data.get("message", "")
