import datetime
import requests

instance_url = "http://localhost:5000"
apartment_id = None
reservation_id = None
apartment_name = "test_apartment"
valid_date = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=1), "%Y%m%d")


def test_is_up():
    assert requests.get(f"{instance_url}/up").status_code == 200


def test_missing_parameter():
    assert requests.get("http://apartments:5000/add").status_code == 400


def test_add_apartment():
    result = requests.get(f"http://apartments:5000/add?name={apartment_name}&size=1").json()
    list = requests.get("http://apartments:5000/apartments").json()

    global apartment_id
    apartment_id = result["id"]

    assert result["name"] == apartment_name and any(
           app["name"] == apartment_name for app in list["apartments"])


def test_add_reservation():
    result = requests.get(f"http://reservations:5000/add?app_id={apartment_id}&start={valid_date}&duration=1").json()
    list = requests.get("http://reservations:5000/reservations").json()

    global reservation_id
    reservation_id = result["id"]

    assert result["app_id"] == apartment_id and any(
           res["id"] == reservation_id for res in list["reservations"])


def test_search_booked():
    result = requests.get(f"http://search:5000/search?start={valid_date}&duration=1").json()

    assert all(res["id"] != apartment_id for res in result["apartments"])


def test_remove_reservation():
    assert requests.get(f"http://reservations:5000/delete?id={reservation_id}").status_code == 200


def test_remove_apartment():
    assert requests.get(f"http://apartments:5000/delete?name={apartment_name}").status_code == 200
