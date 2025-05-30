def test_create_post(client):
    client.post('/api/auth/register', json={
        'username': 'john',
        'email': 'john@example.com',
        'password': 'TestPass123',
        'confirm_password': 'TestPass123'
    })
    login = client.post('/api/auth/login', json={
        'username': 'john',
        'password': 'TestPass123'
    })
    token = login.json['access_token']
    response = client.post('/api/posts', json={
        'title': 'My First Post',
        'content': 'This is the content of the post'
    }, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 201
    assert 'post' in response.json
