from db.fake_db import users

def get_users():
          return users
def get_user(user_id: int):
          
          for user in users:
                    if user["id"] == user_id:
                              return user
          return None
def create_user(user: dict):
          for u in users:
                    if u["username"] == user["username"]:
                              return {"Error" : "this name already exists"}
                    if u["email"] == user["email"]:
                              return {"Error": "Email already exists"}
          new_user = {
          "id": generate_id(),
          **user
          }

          users.append(new_user)
          return new_user
def redact_user(user_id : int, new_user : dict):
          
          for i, user in enumerate(users):
                    if user["id"] == user_id:
                              users[i] = {
                              "id": user["id"],
                              **new_user
                              }
                              return users[i]
          return None
          
def delete_user(user_id: int):
    for i, user in enumerate(users):
        if user["id"] == user_id:
            users.pop(i)
            return True
    return None
def generate_id():
    if not users:
        return 1
    return max(user["id"] for user in users) + 1
def search_user(username: str):
          results = []
          for user in users:
                if username.lower() in user["username"].lower():
                        results.append(user)
          return results
def search_active():
          results = []
          for user in users:
                  if user["is_active"] == True:
                          results.append(user)
          return results
          
                
        
        


        