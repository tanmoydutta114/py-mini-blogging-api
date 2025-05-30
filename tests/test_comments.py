def test_add_comment(client):
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
    
    # Create post first
    post = client.post('/api/posts', json={
        'title': 'Test Post',
        'content': 'Content here'
    }, headers={'Authorization': f'Bearer {token}'}).json['post']

    # Now comment on it
    response = client.post('/api/comments', json={
        'name': 'John',
        'content': 'Great post!',
        'post_id': post['id']
    }, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 201
    assert 'comment' in response.json
