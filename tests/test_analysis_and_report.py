def create_transaction(
    client,
    headers,
    transaction_reference,
    amount,
    location,
):
    return client.post(
        "/api/transactions",
        json={
            "transaction_reference": transaction_reference,
            "card_reference": f"CARD-{transaction_reference}",
            "amount": amount,
            "transaction_type": "Online Purchase",
            "location": location,
            "transaction_date": "2026-09-10T12:00:00Z",
        },
        headers=headers,
    )


def test_analysis_endpoints_and_report_generation(client, auth_headers):
    normal_response = create_transaction(
        client,
        auth_headers,
        "TXN-ANALYSIS-001",
        5000,
        "Lagos",
    )
    suspicious_response = create_transaction(
        client,
        auth_headers,
        "TXN-ANALYSIS-002",
        150000,
        "Abuja",
    )

    assert normal_response.status_code == 201
    assert suspicious_response.status_code == 201

    summary_response = client.get("/api/analysis/summary", headers=auth_headers)

    assert summary_response.status_code == 200

    summary = summary_response.json()
    assert summary["total_transactions"] == 2
    assert summary["normal_transactions"] == 1
    assert summary["suspicious_transactions"] == 1
    assert summary["fraud_alert_count"] == 1

    trends_response = client.get("/api/analysis/trends", headers=auth_headers)
    type_response = client.get("/api/analysis/by-type", headers=auth_headers)
    location_response = client.get(
        "/api/analysis/by-location",
        headers=auth_headers,
    )
    fraud_response = client.get("/api/analysis/fraud", headers=auth_headers)
    breakdown_response = client.get(
        "/api/analysis/breakdown",
        headers=auth_headers,
    )

    assert trends_response.status_code == 200
    assert len(trends_response.json()) == 1
    assert type_response.status_code == 200
    assert len(type_response.json()) == 1
    assert location_response.status_code == 200
    assert len(location_response.json()) == 2
    assert fraud_response.status_code == 200
    assert fraud_response.json()["total_alerts"] == 1
    assert breakdown_response.status_code == 200

    breakdown = breakdown_response.json()
    assert len(breakdown["by_user"]) == 1
    assert len(breakdown["by_card"]) == 2
    assert breakdown["by_type"][0]["count"] == 2
    assert breakdown["suspicious_rate"] == 0.5

    report_response = client.post(
        "/api/reports/generate",
        json={
            "report_type": "transaction_analysis",
            "start_date": "2026-09-01T00:00:00Z",
            "end_date": "2026-09-30T23:59:59Z",
        },
        headers=auth_headers,
    )

    assert report_response.status_code == 201

    report = report_response.json()
    assert report["report_type"] == "transaction_analysis"
    assert report["report_data"]["summary"]["total_transactions"] == 2
    assert report["report_data"]["summary"]["fraud_alert_count"] == 1

    report_list_response = client.get("/api/reports", headers=auth_headers)

    assert report_list_response.status_code == 200
    assert report_list_response.json()["total"] == 1
