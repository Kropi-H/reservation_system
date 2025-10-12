#!/usr/bin/env python3
"""
Database listener pro real-time notifikace změn v PostgreSQL databázi
"""
import json
import threading
import platform
from datetime import datetime

from PySide6.QtCore import QObject, Signal
from models.connection_pool import get_pooled_connection, put_pooled_connection

# Detekce OS pro specifické nastavení
CURRENT_OS = platform.system()
print(f"🖥️ Database listener běží na: {CURRENT_OS}")


class DatabaseListener(QObject):
    """Třída pro poslouchání database notifikací přes PostgreSQL NOTIFY/LISTEN."""
    
    # Signály pro různé typy změn
    reservation_changed = Signal(dict)
    doctor_changed = Signal(dict)
    ordinace_changed = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.connection = None
        self.listener_thread = None
        self.listening = False
    
    def start_listening(self, channels):
        """Spustí poslouchání na zadaných kanálech."""
        try:
            self.connection = get_pooled_connection()
            
            # Nastav autocommit pro LISTEN/NOTIFY
            self.connection.autocommit = True
            cur = self.connection.cursor()
            
            # Registruj se na všechny kanály
            for channel in channels:
                cur.execute(f"LISTEN {channel}")
                print(f"📡 Poslouchám kanál: {channel} ({CURRENT_OS})")
            
            self.listening = True
            
            # Spusť listener thread s univerzálním polling
            print(f"🔄 Použití polling metody pro {CURRENT_OS} (kompatibilní se všemi platformami)")
                
            self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listener_thread.start()
            
        except Exception as e:
            print(f"⚠️ Chyba při spuštění database listeneru ({CURRENT_OS}): {e}")
            # Zkusíme fallback metodu pro všechny platformy
            try:
                print(f"🔄 {CURRENT_OS}: Zkouším fallback metodu bez connection pool...")
                self._start_listening_fallback(channels)
            except Exception as fallback_error:
                print(f"❌ {CURRENT_OS} fallback také selhal: {fallback_error}")
            
    def _start_listening_fallback(self, channels):
        """Fallback metoda pro všechny platformy - přímé připojení bez poolu."""
        from config import get_database_config
        import psycopg2
        
        config = get_database_config()
        self.connection = psycopg2.connect(**config)
        self.connection.autocommit = True
        
        cur = self.connection.cursor()
        for channel in channels:
            cur.execute(f"LISTEN {channel}")
            print(f"📡 Fallback poslouchám kanál: {channel} ({CURRENT_OS})")
        
        self.listening = True
        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener_thread.start()
    
    def _listen_loop(self):
        """Hlavní smyčka pro poslouchání notifikací."""
        retry_count = 0
        max_retries = 5
        
        while self.listening:
            try:
                # Zkontroluj připojení před použitím
                if not self.connection or self.connection.closed:
                    print(f"🔄 Připojení uzavřeno, obnovujem... ({CURRENT_OS})")
                    self._reconnect()
                    retry_count = 0  # Reset počítadla při úspěšném připojení
                
                # Univerzální řešení - použij polling pro všechny platformy
                import time
                time.sleep(0.1)  # Krátká pauza (100ms)
                
                # Zkus polling s kontrolou stavu připojení
                if self.connection and not self.connection.closed:
                    self.connection.poll()
                    
                    # Zpracuj všechny dostupné notifikace
                    while self.connection.notifies:
                        notify = self.connection.notifies.pop(0)
                        self._handle_notification(notify.channel, notify.payload)
                else:
                    print(f"⚠️ Připojení je uzavřeno, pokouším se obnovit...")
                    continue
                    
            except Exception as e:
                retry_count += 1
                print(f"⚠️ Chyba v database listener loop ({CURRENT_OS}) - pokus {retry_count}/{max_retries}: {e}")
                
                # Pokud je příliš mnoho chyb, zastavíme listener
                if retry_count >= max_retries:
                    print(f"❌ Příliš mnoho chyb, zastavujem database listener")
                    self.listening = False
                    break
                
                # Vyčkej před dalším pokusem
                import time
                time.sleep(min(retry_count * 2, 10))  # Exponenciální backoff, max 10s
                
                # Pokus o obnovení připojení
                try:
                    self._reconnect()
                except Exception as reconnect_error:
                    print(f"⚠️ Nepodařilo se obnovit připojení: {reconnect_error}")
                    continue
                    
        print(f"🛑 Database listener ukončen ({CURRENT_OS})")
    
    def _reconnect(self):
        """Obnovení připojení k databázi."""
        # Zavři staré připojení
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None
        
        # Vytvoř nové připojení
        try:
            # Nejprve zkus connection pool
            self.connection = get_pooled_connection()
            print(f"🔄 Nové připojení z poolu vytvořeno ({CURRENT_OS})")
        except Exception as pool_error:
            print(f"⚠️ Pool připojení nedostupný: {pool_error}")
            # Fallback na přímé připojení
            try:
                from config import get_database_config
                import psycopg2
                
                config = get_database_config()
                self.connection = psycopg2.connect(**config)
                print(f"🔄 Fallback připojení vytvořeno ({CURRENT_OS})")
            except Exception as direct_error:
                print(f"❌ Nepodařilo se vytvořit ani fallback připojení: {direct_error}")
                raise
        
        # Nastav autocommit a obnovit LISTEN
        if self.connection:
            self.connection.autocommit = True
            cur = self.connection.cursor()
            
            # Znovu se registruj na všechny kanály
            channels = ['reservation_changes', 'doctor_changes', 'ordinace_changes']
            for channel in channels:
                cur.execute(f"LISTEN {channel}")
                print(f"📡 Obnoveno poslouchání kanálu: {channel} ({CURRENT_OS})")
    
    def _handle_notification(self, channel, payload):
        """Zpracuje notifikaci z databáze."""
        try:
            data = json.loads(payload)
            print(f"📨 Notifikace přijata: {channel} - {data}")
            
            # Rozešli na správný signál podle kanálu
            if channel == 'reservation_changes':
                self.reservation_changed.emit(data)
            elif channel == 'doctor_changes':
                self.doctor_changed.emit(data)
            elif channel == 'ordinace_changes':
                self.ordinace_changed.emit(data)
                
        except Exception as e:
            print(f"⚠️ Chyba při zpracování notifikace: {e}")
    
    def stop_listening(self):
        """Zastaví poslouchání notifikací."""
        print(f"🛑 Zastavujem database listener ({CURRENT_OS})")
        self.listening = False
        
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=5)  # Delší timeout
            if self.listener_thread.is_alive():
                print(f"⚠️ Listener thread se nepodařilo ukončit v časovém limitu")
        
        if self.connection:
            try:
                # Pokus o graceful ukončení
                if not self.connection.closed:
                    cur = self.connection.cursor()
                    cur.execute("UNLISTEN *")  # Odregistruj všechny kanály
                    cur.close()
                    
                # Zavři připojení
                self.connection.close()
                print(f"✅ Database listener připojení uzavřeno ({CURRENT_OS})")
            except Exception as e:
                print(f"⚠️ Chyba při zavírání připojení: {e}")
            finally:
                self.connection = None


def notify_database_change(table_type, operation, data):
    """
    Pošle notifikaci o změně v databázi
    table_type: 'reservation', 'doctor', 'ordinace', etc.
    operation: 'INSERT', 'UPDATE', 'DELETE', 'DEACTIVATE'
    data: slovník s daty změny
    """
    try:
        # Pokus o použití connection poolu
        conn = get_pooled_connection()
        cur = conn.cursor()
        
        # Vytvoř JSON payload
        payload = {
            'table': table_type,
            'operation': operation,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Pošli notifikaci přes PostgreSQL NOTIFY na správný kanál
        if table_type == 'reservation':
            cur.execute("NOTIFY reservation_changes, %s", (json.dumps(payload),))
        elif table_type == 'doctor':
            cur.execute("NOTIFY doctor_changes, %s", (json.dumps(payload),))
        elif table_type == 'ordinace':
            cur.execute("NOTIFY ordinace_changes, %s", (json.dumps(payload),))
        
        conn.commit()
        cur.close()
        put_pooled_connection(conn)
        print(f"📡 Notifikace odeslána: {table_type} {operation}")
        
    except Exception as e:
        if "pool exhausted" in str(e).lower():
            print(f"⚠️ Connection pool vyčerpán, zkouším přímé připojení...")
            # Fallback: přímé připojení bez poolu
            try:
                _notify_database_change_fallback(table_type, operation, data)
            except Exception as fallback_error:
                print(f"❌ Fallback notifikace selhala: {fallback_error}")
        else:
            print(f"⚠️ Chyba při odesílání notifikace: {e}")

def _notify_database_change_fallback(table_type, operation, data):
    """Fallback metoda pro notifikace bez connection poolu."""
    from config import get_database_config
    import psycopg2
    
    config = get_database_config()
    conn = psycopg2.connect(**config)
    
    try:
        cur = conn.cursor()
        
        payload = {
            'table': table_type,
            'operation': operation,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        if table_type == 'reservation':
            cur.execute("NOTIFY reservation_changes, %s", (json.dumps(payload),))
        elif table_type == 'doctor':
            cur.execute("NOTIFY doctor_changes, %s", (json.dumps(payload),))
        elif table_type == 'ordinace':
            cur.execute("NOTIFY ordinace_changes, %s", (json.dumps(payload),))
        
        conn.commit()
        print(f"📡 Fallback notifikace odeslána: {table_type} {operation}")
        
    finally:
        conn.close()
