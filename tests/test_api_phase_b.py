"""Phase B：元数据、地理位置解析、日志 SSE 契约。"""

from fastapi.testclient import TestClient

from backend.main import app
from data import GEOGRAPHICAL_DATA

client = TestClient(app)


def test_meta_geography_keys():
    r = client.get("/api/meta/geography")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert len(data) > 0


def test_meta_industries():
    r = client.get("/api/meta/industries")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert len(data) > 0


def test_resolve_location_select_ok():
    continent = None
    country = None
    city = None
    district_label = None
    for cont, countries in GEOGRAPHICAL_DATA.items():
        for cname, node in countries.items():
            if not isinstance(node, dict) or "cities" not in node:
                continue
            cities = node["cities"]
            for cty, districts in cities.items():
                if not districts:
                    continue
                d0 = districts[0]
                continent = cont
                country = cname
                city = cty
                district_label = f'{d0["en"]} ({d0["zh"]})'
                break
        if continent:
            break
    assert continent and country and city and district_label

    r = client.post(
        "/api/meta/resolve-location",
        json={
            "mode": "select",
            "continent": continent,
            "country": country,
            "city": city,
            "district": district_label,
        },
    )
    assert r.status_code == 200
    loc = r.json()
    node = GEOGRAPHICAL_DATA[continent][country]
    assert loc["country"] == node["en"]
    assert loc["city"]
    assert loc["district"]


def test_resolve_location_select_bad():
    r = client.post(
        "/api/meta/resolve-location",
        json={"mode": "select", "continent": "", "country": "", "city": ""},
    )
    assert r.status_code == 400


def test_logs_stream_opens():
    with client.stream("GET", "/api/logs/stream") as r:
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("text/event-stream")
        chunk = next(r.iter_bytes(chunk_size=512))
        assert b"connected" in chunk
