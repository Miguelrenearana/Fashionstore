def _create_paid_sale(client, headers):
    r = client.post(
        "/api/v1/sales",
        json={"branch_id": 1, "items": [{"variant_id": 1, "quantity": 1}]},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    sale_id = r.json()["id"]

    r = client.post(f"/api/v1/payments/initiate?sale_id={sale_id}&method=cash", headers=headers)
    assert r.status_code == 200, r.text
    ref = r.json()["gateway_reference"]

    r = client.post("/api/v1/payments/confirm", json={"gateway_reference": ref}, headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "COMPLETED"
    return sale_id


def test_receipt_not_issued_before_payment(client, admin_headers):
    r = client.post(
        "/api/v1/sales",
        json={"branch_id": 1, "items": [{"variant_id": 2, "quantity": 1}]},
        headers=admin_headers,
    )
    sale_id = r.json()["id"]
    r = client.get(f"/api/v1/sales/{sale_id}/receipt", headers=admin_headers)
    assert r.status_code == 404


def test_receipt_issued_on_payment_and_credit_note_on_refund(client, admin_headers):
    sale_id = _create_paid_sale(client, admin_headers)

    r = client.get(f"/api/v1/sales/{sale_id}/receipt", headers=admin_headers)
    assert r.status_code == 200, r.text
    receipt = r.json()
    assert receipt["type"] == "invoice"
    assert receipt["rnc_or_cuf"].startswith("CUF-")
    assert receipt["document_url"].endswith(".pdf")

    r = client.get(f"/api/v1/sales/{sale_id}", headers=admin_headers)
    assert r.json()["status"] == "PAID"

    ref = _gateway_ref(sale_id)
    r = client.post(f"/api/v1/payments/refund?gateway_reference={ref}", headers=admin_headers)
    assert r.status_code == 200, r.text

    r = client.get(f"/api/v1/sales/{sale_id}/receipt", headers=admin_headers)
    assert r.status_code == 200, r.text
    receipts = r.json()
    assert receipts["type"] == "credit_note"
    assert receipts["rnc_or_cuf"].startswith("NC-")


def _gateway_ref(sale_id: int) -> str:
    from app.core.database import SessionLocal
    from app.models.sales import Payment

    db = SessionLocal()
    try:
        payment = db.query(Payment).filter(Payment.sale_id == sale_id).first()
        assert payment, "no payment for sale"
        return payment.gateway_reference
    finally:
        db.close()
