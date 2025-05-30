def test_register_user(client):
    response = client.post('/api/auth/register', json={
        'username': 'john',
        'email': 'john@example.com',
        'password': 'TestPass123',
        'confirm_password': 'TestPass123'
    })
    assert response.status_code == 201
    assert 'access_token' in response.json

def test_login_user(client):
    client.post('/api/auth/register', json={
        'username': 'john',
        'email': 'john@example.com',
        'password': 'TestPass123',
        'confirm_password': 'TestPass123'
    })
    response = client.post('/api/auth/login', json={
        'username': 'john',
        'password': 'TestPass123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json
