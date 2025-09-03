#!/usr/bin/env python3
"""
Database listener pro real-time notifikace změn v PostgreSQL databázi
"""
import json
import select
import threading
from datetime import datetime

from PySide6.QtCore import QObject, Signal
from models.connection_pool import get_pooled_connection


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
                print(f"📡 Poslouchám kanál: {channel}")
            
            self.listening = True
            
            # Spusť listener thread
            self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listener_thread.start()
            
        except Exception as e:
            print(f"⚠️ Chyba při spuštění database listeneru: {e}")
    
    def _listen_loop(self):
        """Hlavní smyčka pro poslouchání notifikací."""
        while self.listening and self.connection:
            try:
                # Čekej na notifikace (timeout 1 sekunda)
                if select.select([self.connection], [], [], 1) == ([], [], []):
                    continue
                
                self.connection.poll()
                
                while self.connection.notifies:
                    notify = self.connection.notifies.pop(0)
                    self._handle_notification(notify.channel, notify.payload)
                    
            except Exception as e:
                print(f"⚠️ Chyba v database listener loop: {e}")
                break
    
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
        self.listening = False
        if self.listener_thread:
            self.listener_thread.join(timeout=2)
        if self.connection:
            try:
                self.connection.close()
            except:
                pass


def notify_database_change(table_type, operation, data):
    """
    Pošle notifikaci o změně v databázi
    table_type: 'reservation', 'doctor', 'ordinace', etc.
    operation: 'INSERT', 'UPDATE', 'DELETE', 'DEACTIVATE'
    data: slovník s daty změny
    """
    try:
        with get_pooled_connection() as conn:
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
            print(f"📡 Notifikace odeslána: {table_type} {operation}")
            
    except Exception as e:
        print(f"⚠️ Chyba při odesílání notifikace: {e}")
