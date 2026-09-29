def create_high_value_transaction(client, headers):
    return client.post(
        "/api/transactions",
        json={
            "transaction_reference": "TXN-ALERT-001",
            "card_reference": "CARD-ALERT-001",
            "amount": 150000,
            "transaction_type": "Online Purchase",
            "location": "Abuja",
            "transaction_date": "2026-09-10T12:00:00Z",
        },
        headers=headers,
    )


def test_list_and_update_fraud_alert(client, auth_headers):
    transaction_response = create_high_value_transaction(client, auth_headers)

    assert transaction_response.status_code == 201
    alert_id = transaction_response.json()["alert_ids"][0]

    list_response = client.get("/api/alerts", headers=auth_headers)

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1
    assert list_response.json()["items"][0]["id"] == alert_id
    assert list_response.json()["items"][0]["alert_status"] == "new"

    update_response = client.put(
        f"/api/alerts/{alert_id}",
        json={"alert_status": "reviewed"},
        headers=auth_headers,
    )

    assert update_response.status_code == 200

    updated_alert = update_response.json()
    assert updated_alert["alert_status"] == "reviewed"
    assert updated_alert["reviewed_at"] is not None
    assert updated_alert["transaction"]["transaction_reference"] == "TXN-ALERT-001"