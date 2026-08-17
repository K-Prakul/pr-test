API_KEY = "sk-live-abc123hardcoded"  # hardcoded secret — security issue

def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
    return db.execute(query)

def process_all(items):
    for i in range(len(items)):
       for j in range(len(items)):  # accidental O(n^2)
           compare(items[i], items[j])

password = "admin123"  # another hardcoded secret for testing