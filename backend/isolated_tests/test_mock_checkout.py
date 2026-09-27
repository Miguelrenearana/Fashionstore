from datetime import date
from uuid import uuid4

import pytest

from conftest import auth
from app.core.exceptions import PaymentError
from app.models import Branch, Employee, Payment, Receipt, Role, Sale
from app.payments.domain.entities import PaymentStatusResult
from app.payments.factory import get_payment_service


def purchase(ctx):
    client, db, owner, _, _, variant = ctx
    headers = auth(owner)
    assert client.get('/api/v1/payments/config').json() == {"gateway": "mock"}
    response = client.post('/api/v1/cart/items', headers=headers,
                           json={"variant_id": variant.id, "quantity": 2})
    assert response.status_code == 200, response.text
    response = client.post('/api/v1/cart/purchase', headers=headers,
                           json={"payment_method": "qr"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body['sale']['status'] == 'PENDING'
    assert body['payment']['status'] == 'PENDING'
    assert body['payment']['sale_id'] == body['sale']['id']
    assert db.query(Receipt).count() == 0
    return body['sale']['id'], body['payment']['gateway_reference']


def confirm(client, user, ref):
    return client.post('/api/v1/payments/confirm', headers=auth(user),
                       json={"gateway_reference": ref})


def test_purchase_confirm_receipt_and_idempotent_retry(checkout_api):
    client, db, owner, *_ = checkout_api
    sale_id, ref = purchase(checkout_api)
    assert confirm(client, owner, ref).json() == {"reference": ref, "status": "COMPLETED"}
    paid_at = db.get(Sale, sale_id).paid_at
    assert confirm(client, owner, ref).json()['status'] == 'COMPLETED'
    assert db.get(Sale, sale_id).paid_at == paid_at
    assert db.query(Sale).count() == db.query(Payment).count() == db.query(Receipt).count() == 1
    receipt = client.get(f'/api/v1/sales/{sale_id}/receipt', headers=auth(owner))
    assert receipt.status_code == 200
    assert receipt.json()['sale_id'] == sale_id
    assert receipt.json()['total_amount'] == 50
    assert client.get('/api/v1/cart', headers=auth(owner)).json()['details'] == []


@pytest.mark.parametrize('status', ['PENDING', 'DECLINED', 'TIMEOUT'])
def test_non_completed_status_does_not_issue_receipt(checkout_api, monkeypatch, status):
    client, db, owner, *_ = checkout_api
    sale_id, ref = purchase(checkout_api)
    monkeypatch.setattr(get_payment_service(), 'status', lambda r: PaymentStatusResult(r, status))
    assert confirm(client, owner, ref).json()['status'] == status
    assert db.get(Sale, sale_id).status != 'PAID'
    assert db.query(Receipt).count() == 0
    assert client.get(f'/api/v1/sales/{sale_id}/receipt', headers=auth(owner)).status_code == 404
    monkeypatch.setattr(get_payment_service(), 'status', lambda r: PaymentStatusResult(r, 'COMPLETED'))
    final = confirm(client, owner, ref).json()['status']
    assert final == ('COMPLETED' if status == 'PENDING' else status)
    assert db.query(Sale).count() == db.query(Payment).count() == 1


def test_gateway_error_can_retry_same_reference(checkout_api, monkeypatch):
    client, db, owner, *_ = checkout_api
    _, ref = purchase(checkout_api)
    service = get_payment_service()
    original = service.status

    def fail(_):
        raise PaymentError('Temporary gateway failure')

    monkeypatch.setattr(service, 'status', fail)
    assert confirm(client, owner, ref).status_code == 402
    assert db.query(Payment).one().status == 'PENDING'
    assert db.query(Receipt).count() == 0
    monkeypatch.setattr(service, 'status', original)
    assert confirm(client, owner, ref).json()['status'] == 'COMPLETED'
    assert db.query(Sale).count() == 1


def test_confirmation_requires_owner_and_authentication(checkout_api, monkeypatch):
    client, db, owner, other, *_ = checkout_api
    _, ref = purchase(checkout_api)

    def forbidden_gateway_call(_):
        pytest.fail('Unauthorized request reached gateway')

    monkeypatch.setattr(get_payment_service(), 'status', forbidden_gateway_call)
    assert client.post('/api/v1/payments/confirm', json={"gateway_reference": ref}).status_code == 401
    assert confirm(client, other, ref).status_code == 403
    assert confirm(client, owner, 'missing-reference').status_code == 404
    assert db.query(Payment).one().status == 'PENDING'
    assert db.query(Receipt).count() == 0


@pytest.mark.parametrize('role,same_branch,allowed', [
    ('ADMIN', False, True), ('CASHIER', True, True), ('MANAGER', True, True),
    ('CASHIER', False, False), ('MANAGER', False, False), ('CLIENT', True, False),
])
def test_staff_scope(checkout_api, role, same_branch, allowed):
    client, db, _, staff, branch, _ = checkout_api
    _, ref = purchase(checkout_api)
    staff.roles.append(Role(name=role))
    if not same_branch:
        branch = Branch(city_id=branch.city_id, name='Other branch', address='Test')
        db.add(branch)
        db.flush()
    db.add(Employee(user=staff, branch=branch, first_name='Staff', last_name='Test', hire_date=date.today()))
    db.commit()
    response = confirm(client, staff, ref)
    assert response.status_code == (200 if allowed else 403)
    assert db.query(Receipt).count() == (1 if allowed else 0)


@pytest.mark.parametrize('employee_active', [None, False])
def test_staff_needs_active_branch_assignment(checkout_api, employee_active):
    client, db, _, staff, branch, _ = checkout_api
    sale_id, ref = purchase(checkout_api)
    # A sale without a client must not make a user without a client its owner.
    db.get(Sale, sale_id).client_id = None
    staff.roles.append(Role(name='CASHIER'))
    if employee_active is not None:
        db.add(Employee(user=staff, branch=branch, first_name='Staff', last_name='Test',
                        hire_date=date.today(), is_active=employee_active))
    db.commit()
    assert confirm(client, staff, ref).status_code == 403
    assert db.query(Payment).one().status == 'PENDING'
    assert db.query(Receipt).count() == 0


def test_completed_payment_repairs_sale_and_receipt_idempotently(checkout_api, monkeypatch):
    client, db, owner, other, *_ = checkout_api
    sale_id, ref = purchase(checkout_api)
    db.query(Payment).one().status = 'COMPLETED'
    db.commit()
    monkeypatch.setattr(get_payment_service(), 'status', lambda _: pytest.fail('Already completed'))
    assert confirm(client, other, ref).status_code == 403
    assert db.get(Sale, sale_id).status == 'PENDING'
    assert confirm(client, owner, ref).json()['status'] == 'COMPLETED'
    paid_at = db.get(Sale, sale_id).paid_at
    assert db.get(Sale, sale_id).status == 'PAID'
    assert paid_at is not None
    assert confirm(client, owner, ref).status_code == 200
    assert db.get(Sale, sale_id).paid_at == paid_at
    assert db.query(Receipt).count() == 1


def test_gateway_completed_at_initiation_is_reconciled(checkout_api, monkeypatch):
    client, db, owner, _, _, variant = checkout_api
    service = get_payment_service()
    original = service.pay

    def completed(**kwargs):
        result = original(**kwargs)
        result.status = 'COMPLETED'
        return result

    monkeypatch.setattr(service, 'pay', completed)
    headers = auth(owner)
    client.post('/api/v1/cart/items', headers=headers, json={'variant_id': variant.id, 'quantity': 1})
    created = client.post('/api/v1/cart/purchase', headers=headers, json={'payment_method': 'qr'})
    assert created.status_code == 200
    body = created.json()
    assert body['payment']['status'] == 'COMPLETED'
    assert body['sale']['status'] == 'PENDING'
    reference = body['payment']['gateway_reference']
    assert confirm(client, owner, reference).json()['status'] == 'COMPLETED'
    assert confirm(client, owner, reference).json()['status'] == 'COMPLETED'
    assert db.get(Sale, body['sale']['id']).status == 'PAID'
    assert db.query(Receipt).count() == 1


def test_purchase_token_recovers_lost_response_without_second_sale(checkout_api):
    client, db, owner, other, _, variant = checkout_api
    token = str(uuid4())
    headers = auth(owner)
    payload = {'payment_method': 'qr', 'checkout_token': token}
    assert client.get(f'/api/v1/cart/purchase/{token}', headers=headers).status_code == 404
    # Validation failure happens before creating a sale and can be corrected.
    assert client.post('/api/v1/cart/purchase', headers=headers, json=payload).status_code == 422
    assert db.query(Sale).count() == 0
    client.post('/api/v1/cart/items', headers=headers, json={'variant_id': variant.id, 'quantity': 1})
    first = client.post('/api/v1/cart/purchase', headers=headers, json=payload)
    assert first.status_code == 200, first.text
    replay = client.post('/api/v1/cart/purchase', headers=headers, json=payload)
    recovered = client.get(f'/api/v1/cart/purchase/{token}', headers=headers)
    assert replay.json() == recovered.json() == first.json()
    assert client.get(f'/api/v1/cart/purchase/{token}', headers=auth(other)).status_code == 404
    assert db.query(Sale).count() == db.query(Payment).count() == 1


def test_recovery_of_sale_without_payment_does_not_create_another_sale(checkout_api, monkeypatch):
    client, db, owner, _, _, variant = checkout_api
    headers = auth(owner)
    token = str(uuid4())
    client.post('/api/v1/cart/items', headers=headers, json={'variant_id': variant.id, 'quantity': 1})

    def fail(**kwargs):
        raise PaymentError('Gateway unavailable after sale creation')

    monkeypatch.setattr(get_payment_service(), 'pay', fail)
    payload = {'payment_method': 'qr', 'checkout_token': token}
    assert client.post('/api/v1/cart/purchase', headers=headers, json=payload).status_code == 402
    recovered = client.get(f'/api/v1/cart/purchase/{token}', headers=headers)
    assert recovered.status_code == 200
    assert recovered.json()['payment'] is None
    assert client.post('/api/v1/cart/purchase', headers=headers, json=payload).json() == recovered.json()
    assert db.query(Sale).count() == 1
