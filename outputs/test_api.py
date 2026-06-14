import urllib.request, json

req = urllib.request.Request("http://localhost:8000/api/auth/login",
    data=json.dumps({"username":"admin","password":"admin123"}).encode(),
    headers={"Content-Type":"application/json"})
r = urllib.request.urlopen(req)
login = json.loads(r.read())
token = login["access_token"]
print(f"LOGIN OK - token: {token[:30]}...")

r2 = urllib.request.Request("http://localhost:8000/api/auth/profile",
    headers={"Authorization": f"Bearer {token}"})
profile = json.loads(urllib.request.urlopen(r2).read())
print(f"PROFILE: {profile['username']} ({profile.get('real_name','')})")

r3 = urllib.request.Request("http://localhost:8000/api/departments",
    headers={"Authorization": f"Bearer {token}"})
depts = json.loads(urllib.request.urlopen(r3).read())
print(f"DEPARTMENTS: {len(depts)} nodes")

count = 0
for d in depts:
    count += 1
    children = d.get("children", [])
    for c in children:
        count += 1
        grandchildren = c.get("children", [])
        count += len(grandchildren)
print(f"Total department nodes: {count}")
print("系统验证全部通过！")
