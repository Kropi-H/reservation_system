from models.databaze import get_connection


def get_all_users():
  with get_connection():
    cur = get_connection().cursor()
    cur.execute('SELECT * FROM Users')
    return cur.fetchall()  # Returns a list of tuples with user data


def add_user(user):
  pass

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