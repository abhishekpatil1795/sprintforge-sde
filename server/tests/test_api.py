def test_health(client):
    r = client.get('/api/health'); assert r.status_code == 200 and r.json() == {'status':'ok'}

def test_register_and_me(client, registered_user):
    r = client.get('/api/auth/me', headers={'Authorization': f"Bearer {registered_user['token']}"})
    assert r.status_code == 200 and r.json()['email'] == 'test@example.com'
    assert 'password_hash' not in r.json()

def test_duplicate_email_returns_409(client, registered_user):
    r = client.post('/api/auth/register', json={'name':'Second User','email':'TEST@example.com','password':'correct-horse-battery'})
    assert r.status_code == 409

def test_invalid_login(client, registered_user):
    r = client.post('/api/auth/login', json={'email':'test@example.com','password':'wrong-password'})
    assert r.status_code == 401 and r.json()['detail'] == 'Invalid email or password'

def test_protected_route_requires_token(client): assert client.get('/api/projects').status_code == 401

def test_create_project_and_task(client, auth_headers):
    p = client.post('/api/projects', headers=auth_headers, json={'name':'Interview Prep','description':'Portfolio project'})
    assert p.status_code == 201 and p.json()['task_count'] == 0
    pid = p.json()['id']
    t = client.post(f'/api/projects/{pid}/tasks', headers=auth_headers, json={'title':'Write README','priority':'HIGH'})
    assert t.status_code == 201 and t.json()['status'] == 'TODO'
    listing = client.get(f'/api/projects/{pid}/tasks', headers=auth_headers).json()
    assert listing['pagination']['total'] == 1 and listing['tasks'][0]['priority'] == 'HIGH'

def test_owner_scoped_access_blocks_other_user(client, auth_headers):
    p = client.post('/api/projects', headers=auth_headers, json={'name':'Private Project'}).json()
    other = client.post('/api/auth/register', json={'name':'Other User','email':'other@example.com','password':'another-secure-password'}).json()
    h = {'Authorization': f"Bearer {other['token']}"}
    assert client.get(f"/api/projects/{p['id']}", headers=h).status_code == 404
    assert client.get(f"/api/projects/{p['id']}/tasks", headers=h).status_code == 404

def test_task_update_and_delete(client, auth_headers):
    p = client.post('/api/projects', headers=auth_headers, json={'name':'Build App'}).json()
    t = client.post(f"/api/projects/{p['id']}/tasks", headers=auth_headers, json={'title':'Build API'}).json()
    r = client.patch(f"/api/tasks/{t['id']}", headers=auth_headers, json={'status':'DONE'})
    assert r.status_code == 200 and r.json()['status'] == 'DONE'
    assert client.delete(f"/api/tasks/{t['id']}", headers=auth_headers).status_code == 204
    assert client.patch(f"/api/tasks/{t['id']}", headers=auth_headers, json={'status':'TODO'}).status_code == 404

def test_validation_rejects_bad_registration(client):
    r = client.post('/api/auth/register', json={'name':'x','email':'not-an-email','password':'short'})
    assert r.status_code == 422

def test_status_filter_and_pagination(client, auth_headers):
    p = client.post('/api/projects', headers=auth_headers, json={'name':'Tasks'}).json(); pid = p['id']
    ids = []
    for title in ['One task','Second task','Third task']:
        ids.append(client.post(f'/api/projects/{pid}/tasks', headers=auth_headers, json={'title':title}).json()['id'])
    first = client.get(f'/api/projects/{pid}/tasks?page=1&limit=2', headers=auth_headers).json()
    assert len(first['tasks']) == 2 and first['pagination']['total'] == 3
    client.patch(f"/api/tasks/{ids[0]}", headers=auth_headers, json={'status':'DONE'})
    done = client.get(f'/api/projects/{pid}/tasks?status=DONE', headers=auth_headers).json()
    assert len(done['tasks']) == 1
