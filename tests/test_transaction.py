def create_transaction(client, headers, **overrides):
    payload = {
        "transaction_reference": "TXN-TEST-001",
        "card_reference": "CARD-TEST-001",
        "amount": 5000,
        "transaction_type": "POS Payment",
        "location": "Lagos",
        "transaction_date": "2026-09-10T10:00:00Z",
    }
    payload.update(overrides)

    return client.post(
        "/api/transactions",
        json=payload,
        headers=headers,
    )


def test_normal_transaction_is_recorded_without_alert(client, auth_headers):
    response = create_transaction(client, auth_headers)

    assert response.status_code == 201

    data = response.json()
    assert data["transaction"]["fraud_status"] == "normal"
    assert data["alert_generated"] is False
    assert data["alert_ids"] == []
    assert data["triggered_rules"] == []


def test_high_value_transaction_creates_fraud_alert(client, auth_headers):
    response = create_transaction(
        client,
        auth_headers,
        transaction_reference="TXN-TEST-002",
        amount=150000,
    )

    assert response.status_code == 201

    data = response.json()
    assert data["transaction"]["fraud_status"] == "suspicious"
    assert data["alert_generated"] is True
    assert len(data["alert_ids"]) == 1
    assert data["triggered_rules"] == ["High Transaction Amount"]


def test_transaction_history_returns_created_transactions(client, auth_headers):
    create_transaction(
        client,
        auth_headers,
        transaction_reference="TXN-TEST-003",
    )
    create_transaction(
        client,
        auth_headers,
        transaction_reference="TXN-TEST-004",
        amount=150000,
    )

    response = client.get(
        "/api/transactions?fraud_status=suspicious",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["transaction_reference"] == "TXN-TEST-004"
    assert data["items"][0]["fraud_status"] == "suspicious"