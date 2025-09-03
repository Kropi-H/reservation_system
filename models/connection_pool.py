#!/usr/bin/env python3
"""
Connection pool pro PostgreSQL databázi
"""
import psycopg2
from psycopg2 import pool
from config import get_database_config
import threading

# Thread-safe singleton pro connection pool
class ConnectionPool:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._pool = None
        return cls._instance
    
    def get_pool(self):
        if self._pool is None:
            config = get_database_config()
            if not config:
                raise Exception("Nelze získat konfiguraci databáze")
            
            try:
                self._pool = psycopg2.pool.SimpleConnectionPool(
                    2,   # minimální počet připojení (zvýšeno z 1)
                    20,  # maximální počet připojení (zvýšeno z 5)
                    **config
                )
                print("Connection pool vytvořen (2-20 připojení)")
            except Exception as e:
                raise Exception(f"Nelze vytvořit connection pool: {e}")
        
        return self._pool
    
    def get_connection(self):
        pool = self.get_pool()
        return pool.getconn()
    
    def put_connection(self, conn):
        pool = self.get_pool()
        pool.putconn(conn)
    
    def close_all_connections(self):
        if self._pool:
            self._pool.closeall()
            print("Všechna připojení v poolu zavřena")
    
    def reset_pool(self):
        """Restartuje connection pool - uzavře všechna připojení a vytvoří nový pool."""
        if self._pool:
            try:
                self._pool.closeall()
                print("Starý connection pool uzavřen")
            except Exception as e:
                print(f"Chyba při zavírání starého poolu: {e}")
            finally:
                self._pool = None
        
        # Vytvoří nový pool při dalším požadavku
        print("Connection pool bude obnoven při dalším použití")

# Singleton instance
_connection_pool = ConnectionPool()

def get_pooled_connection():
    """Získá připojení z poolu"""
    return _connection_pool.get_connection()

def put_pooled_connection(conn):
    """Vrátí připojení zpět do poolu"""
    _connection_pool.put_connection(conn)

class PooledConnection:
    """Context manager pro pooled připojení"""
    def __init__(self):
        self.conn = None
    
    def __enter__(self):
        self.conn = get_pooled_connection()
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is not None:
                self.conn.rollback()
            else:
                # Commitneme při úspěšném ukončení
                self.conn.commit()
            put_pooled_connection(self.conn)
    
    # Přidání metod pro přímé použití (fallback)
    def cursor(self, *args, **kwargs):
        if not self.conn:
            self.conn = get_pooled_connection()
        return self.conn.cursor(*args, **kwargs)
    
    def commit(self):
        if self.conn:
            self.conn.commit()
    
    def rollback(self):
        if self.conn:
            self.conn.rollback()

def reset_connection_pool():
    """Restartuje connection pool - užitečné při problémech s připojeními."""
    global _connection_pool
    _connection_pool.reset_pool()
    
    def close(self):
        if self.conn:
            put_pooled_connection(self.conn)
            self.conn = None
