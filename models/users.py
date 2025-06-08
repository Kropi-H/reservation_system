from models.databaze import get_connection


def get_all_users():
  with get_connection():
    cur = get_connection().cursor()
    cur.execute('SELECT * FROM Users')
    return cur.fetchall()  # Returns a list of tuples with user data


def add_user(user):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM Users WHERE username=?;', (user['username'],))
            if cur.fetchone() is not None:
                raise ValueError("Uživatel existuje.")
            else:
                cur.execute('INSERT INTO Users (username, password, user_role) VALUES (?, ?, ?);',
                            (user['username'], user['password'], user['role']))
                print(f"{user['username']} úspěšně přidán.")
            conn.commit()
    except ValueError as ve:
        print(f"ValueError: {ve}")
        raise
    except Exception as e:
        print(f"Error adding user: {e}")
        raise

def remove_user(user_id, username):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM Users WHERE user_id=? AND username=?;', (user_id, username))
            conn.commit()  # Commit the changes to the database
    except Exception as e:
        print(f"Error removing user: {e}")


def update_user(user_id, user_data):
    try:
      with get_connection():
          cur = get_connection().cursor()
          cur.execute('UPDATE Users SET username = ?, role = ? WHERE user_id = ?', (user_data['username'], user_data['role'], user_id))
          get_connection().commit()
    except Exception as e:
      print(f"Error updating user: {e}")