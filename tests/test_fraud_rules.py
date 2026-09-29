def create_transaction(
    client,
    headers,
    transaction_reference,
    transaction_date,
    location="Lagos",
    card_reference="CARD-RULE-001",
):
    return client.post(
        "/api/transactions",
        json={
            "transaction_reference": transaction_reference,
            "card_reference": card_reference,
            "amount": 5000,
            "transaction_type": "POS Payment",
            "location": location,
            "transaction_date": transaction_date,
        },
        headers=headers,
    )


def test_high_frequency_transactions_create_alert(client, auth_headers):
    first = create_transaction(
        client,
        auth_headers,
        "TXN-FREQUENCY-001",
        "2026-09-10T10:00:00Z",
    )
    second = create_transaction(
        client,
        auth_headers,
        "TXN-FREQUENCY-002",
        "2026-09-10T10:03:00Z",
    )
    third = create_transaction(
        client,
        auth_headers,
        "TXN-FREQUENCY-003",
        "2026-09-10T10:06:00Z",
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert third.status_code == 201

    assert first.json()["transaction"]["fraud_status"] == "normal"
    assert second.json()["transaction"]["fraud_status"] == "normal"

    data = third.json()
    assert data["transaction"]["fraud_status"] == "suspicious"
    assert data["alert_generated"] is True
    assert data["triggered_rules"] == ["High Transaction Frequency"]


def test_unusual_location_creates_alert(client, auth_headers):
    for index, hour in enumerate([8, 9, 10], start=1):
        response = create_transaction(
            client,
            auth_headers,
            f"TXN-LOCATION-00{index}",
            f"2026-09-10T{hour:02d}:00:00Z",
            location="Lagos",
            card_reference="CARD-LOCATION-001",
        )
        assert response.status_code == 201
        assert response.json()["transaction"]["fraud_status"] == "normal"

    unusual_location = create_transaction(
        client,
        auth_headers,
        "TXN-LOCATION-004",
        "2026-09-10T11:00:00Z",
        location="Abuja",
        card_reference="CARD-LOCATION-001",
    )

    assert unusual_location.status_code == 201

    data = unusual_location.json()
    assert data["transaction"]["fraud_status"] == "suspicious"
    assert data["alert_generated"] is True
    assert data["triggered_rules"] == ["Unusual Location"]