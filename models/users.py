from models.databaze import get_connection
from views.update_user_password import UpdatePasswordDialog


def insert_admin_user(u_name, password, u_role="admin"):
  hashed_password = UpdatePasswordDialog.password_crypt(password)
          
  # Vložení výchozího uživatele (pokud neexistuje)
  with get_connection() as conn:
      cur = conn.cursor()
      cur.execute('''
        INSERT OR IGNORE INTO Users (username, password, user_role)
        VALUES (?, ?, ? );
      ''', (u_name, hashed_password, u_role))
      conn.commit()

def get_all_users():
  with get_connection():
    cur = get_connection().cursor()
    cur.execute('SELECT * FROM Users')
    return cur.fetchall()  # Returns a list of tuples with user data


def get_user_by_id(user_id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM Users WHERE user_id=?;', (user_id,))
        user = cur.fetchone()
        if user is None:
            raise ValueError("Uživatel nenalezen.")
        return user

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
            conn.commit()
    except ValueError as ve:
        print(f"ValueError: {ve}")
        raise
    except Exception as e:
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
      with get_connection() as conn:
          cur = conn.cursor()
          cur.execute('UPDATE Users SET username = ?, user_role = ? WHERE user_id = ?', (user_data['username'], user_data['role'], user_id))
          conn.commit()
    except Exception as e:
      print(f"Error updating user: {e}")
      
def update_user_pass(user_data, user_id):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('UPDATE Users SET password = ? WHERE user_id = ?', (user_data, user_id))
            conn.commit()
    except Exception as e:
        print(f"Error updating user password: {e}")
        
def get_user_by_name(username):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM Users WHERE username=?;', (username,))
        user = cur.fetchone()
        if user:
            return True  # User exists