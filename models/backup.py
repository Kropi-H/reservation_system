import os
import subprocess
import shutil
import socket
import hashlib
import getpass
from datetime import datetime, timedelta
from pathlib import Path
from config import get_database_config, get_database_type
from models.settings import get_settings, save_settings
import logging

# Nastavení logování
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupManager:
    """Správce záloh PostgreSQL databáze."""
    
    def __init__(self):
        self.db_config = get_database_config()
        self.db_type = get_database_type()
        
        # Identifikátor instance (hostname + hash pro stabilitu)
        # Vytvoří stabilní ID na základě hostname + username + working directory
        stable_data = f"{socket.gethostname()}_{getpass.getuser()}_{os.getcwd()}"
        instance_hash = hashlib.md5(stable_data.encode()).hexdigest()[:8]
        self.instance_id = f"{socket.gethostname()}_{instance_hash}"
        
        # Výchozí nastavení záloh (globální)
        self.backup_dir = self._get_backup_directory()
        max_backups_setting = get_settings("max_backups")
        self.max_backups = int(max_backups_setting) if max_backups_setting else 10
        
        # Per-instance nastavení automatických záloh
        instance_setting = get_settings(f"auto_backup_enabled_{self.instance_id}")
        if instance_setting is not None:
            self.auto_backup_enabled = str(instance_setting).lower() == "true"
        else:
            # Výchozí hodnota pro novou instanci - vypnuto (aby se předešlo kolizím)
            self.auto_backup_enabled = False
        
        frequency_setting = get_settings("backup_frequency_days")  
        self.backup_frequency_days = int(frequency_setting) if frequency_setting else 1
        
    def _get_backup_directory(self):
        """Získá nebo vytvoří adresář pro zálohy."""
        backup_path = get_settings("backup_directory")
        if not backup_path:
            # Výchozí adresář - ve složce aplikace
            backup_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")
        
        Path(backup_path).mkdir(parents=True, exist_ok=True)
        return backup_path
    
    def _find_pg_dump(self):
        """Najde cestu k pg_dump.exe na Windows."""
        # Možné cesty k PostgreSQL
        possible_paths = [
            "C:\\Program Files\\PostgreSQL\\17\\bin\\pg_dump.exe",
            "C:\\Program Files\\PostgreSQL\\16\\bin\\pg_dump.exe", 
            "C:\\Program Files\\PostgreSQL\\15\\bin\\pg_dump.exe",
            "C:\\Program Files\\PostgreSQL\\14\\bin\\pg_dump.exe",
            "C:\\Program Files (x86)\\PostgreSQL\\17\\bin\\pg_dump.exe",
            "C:\\Program Files (x86)\\PostgreSQL\\16\\bin\\pg_dump.exe",
        ]
        
        # Zkus najít pg_dump v PATH
        pg_dump_path = shutil.which("pg_dump")
        if pg_dump_path:
            return pg_dump_path
            
        # Pokud není v PATH, zkus standardní cesty
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        raise FileNotFoundError("pg_dump.exe nebyl nalezen. Ujistěte se, že je PostgreSQL nainstalován.")
    
    def _find_psql(self):
        """Najde cestu k psql.exe na Windows."""
        # Možné cesty k PostgreSQL
        possible_paths = [
            "C:\\Program Files\\PostgreSQL\\17\\bin\\psql.exe",
            "C:\\Program Files\\PostgreSQL\\16\\bin\\psql.exe",
            "C:\\Program Files\\PostgreSQL\\15\\bin\\psql.exe", 
            "C:\\Program Files\\PostgreSQL\\14\\bin\\psql.exe",
            "C:\\Program Files (x86)\\PostgreSQL\\17\\bin\\psql.exe",
            "C:\\Program Files (x86)\\PostgreSQL\\16\\bin\\psql.exe",
        ]
        
        # Zkus najít psql v PATH
        psql_path = shutil.which("psql")
        if psql_path:
            return psql_path
            
        # Pokud není v PATH, zkus standardní cesty
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        raise FileNotFoundError("psql.exe nebyl nalezen. Ujistěte se, že je PostgreSQL nainstalován.")
    
    def create_backup(self, backup_name=None):
        """
        Vytvoří zálohu databáze.
        
        Args:
            backup_name (str, optional): Název zálohy. Pokud není zadán, použije se timestamp.
            
        Returns:
            tuple: (success: bool, message: str, backup_path: str)
        """
        if self.db_type != 'postgresql':
            return False, "Zálohy jsou podporovány pouze pro PostgreSQL databáze.", ""
            
        if not self.db_config:
            return False, "Konfigurace databáze není dostupná.", ""
        
        try:
            # Najdi pg_dump
            pg_dump_path = self._find_pg_dump()
            
            # Vytvoř název zálohy
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}"
            
            backup_filename = f"{backup_name}.sql"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Připrav příkaz pro pg_dump
            cmd = [
                pg_dump_path,
                f"--host={self.db_config['host']}",
                f"--port={self.db_config['port']}",
                f"--username={self.db_config['user']}",
                f"--dbname={self.db_config['database']}",
                "--verbose",
                "--clean", 
                "--if-exists",
                "--create",
                f"--file={backup_path}"
            ]
            
            # Nastav proměnné prostředí
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            logger.info(f"Spouštím zálohu: {backup_filename}")
            
            # Spusť pg_dump
            result = subprocess.run(
                cmd, 
                env=env, 
                capture_output=True, 
                text=True,
                check=True
            )
            
            # Zkontroluj, zda byl soubor vytvořen a není prázdný
            if os.path.exists(backup_path) and os.path.getsize(backup_path) > 0:
                logger.info(f"Záloha úspěšně vytvořena: {backup_path}")
                
                # Vymaž staré zálohy
                self._cleanup_old_backups()
                
                return True, f"Záloha byla úspěšně vytvořena: {backup_filename}", backup_path
            else:
                return False, "Záloha nebyla vytvořena nebo je prázdná.", ""
                
        except subprocess.CalledProcessError as e:
            error_msg = f"Chyba při vytváření zálohy: {e.stderr if e.stderr else str(e)}"
            logger.error(error_msg)
            return False, error_msg, ""
        except FileNotFoundError as e:
            logger.error(str(e))
            return False, str(e), ""
        except Exception as e:
            error_msg = f"Neočekávaná chyba při vytváření zálohy: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, ""
    
    def restore_backup(self, backup_path):
        """
        Obnoví databázi ze zálohy.
        
        Args:
            backup_path (str): Cesta k záložnímu souboru
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if self.db_type != 'postgresql':
            return False, "Obnova je podporována pouze pro PostgreSQL databáze."
            
        if not os.path.exists(backup_path):
            return False, f"Záložní soubor neexistuje: {backup_path}"
        
        try:
            # Najdi psql
            psql_path = self._find_psql()
            
            # Připrav příkaz pro psql
            cmd = [
                psql_path,
                f"--host={self.db_config['host']}",
                f"--port={self.db_config['port']}",
                f"--username={self.db_config['user']}",
                f"--dbname={self.db_config['database']}",
                f"--file={backup_path}"
            ]
            
            # Nastav proměnné prostředí
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            logger.info(f"Spouštím obnovu ze souboru: {backup_path}")
            
            # Spusť psql
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Obnova databáze byla úspěšná")
            return True, "Databáze byla úspěšně obnovena ze zálohy."
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Chyba při obnově databáze: {e.stderr if e.stderr else str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except FileNotFoundError as e:
            logger.error(str(e))
            return False, str(e)
        except Exception as e:
            error_msg = f"Neočekávaná chyba při obnově databáze: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_backup_list(self):
        """
        Vrátí seznam dostupných záloh.
        
        Returns:
            list: Seznam tuple (filename, path, size, created_date)
        """
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
            
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.sql'):
                filepath = os.path.join(self.backup_dir, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    size = stat.st_size
                    created = datetime.fromtimestamp(stat.st_ctime)
                    backups.append((filename, filepath, size, created))
        
        # Seřaď podle data vytvoření (nejnovější první)
        backups.sort(key=lambda x: x[3], reverse=True)
        return backups
    
    def delete_backup(self, backup_path):
        """
        Smaže záložní soubor.
        
        Args:
            backup_path (str): Cesta k záložnímu souboru
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                logger.info(f"Záloha smazána: {backup_path}")
                return True, "Záloha byla úspěšně smazána."
            else:
                return False, "Záložní soubor neexistuje."
        except Exception as e:
            error_msg = f"Chyba při mazání zálohy: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _cleanup_old_backups(self):
        """Smaže staré zálohy podle nastavení max_backups."""
        backups = self.get_backup_list()
        
        if len(backups) > self.max_backups:
            # Smaž nejstarší zálohy
            backups_to_delete = backups[self.max_backups:]
            for filename, filepath, size, created in backups_to_delete:
                try:
                    os.remove(filepath)
                    logger.info(f"Stará záloha smazána: {filename}")
                except Exception as e:
                    logger.error(f"Chyba při mazání staré zálohy {filename}: {str(e)}")
    
    def should_create_auto_backup(self):
        """
        Zkontroluje, zda by měla být vytvořena automatická záloha.
        
        Returns:
            bool: True pokud by měla být vytvořena záloha
        """
        if not self.auto_backup_enabled:
            return False
            
        last_backup_date = get_settings("last_backup_date")
        if not last_backup_date:
            return True
            
        try:
            last_backup = datetime.strptime(last_backup_date, "%Y-%m-%d")
            days_since_backup = (datetime.now() - last_backup).days
            return days_since_backup >= self.backup_frequency_days
        except ValueError:
            return True
    
    def create_auto_backup(self):
        """
        Vytvoří automatickou zálohu a aktualizuje datum poslední zálohy.
        
        Returns:
            tuple: (success: bool, message: str, backup_path: str)
        """
        # Použij timestamp pro automatické zálohy - každá má unikátní název
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"auto_backup_{timestamp}"
        
        success, message, backup_path = self.create_backup(backup_name)
        
        if success:
            # Aktualizuj datum poslední zálohy
            save_settings({"last_backup_date": datetime.now().strftime("%Y-%m-%d")})
            logger.info("Automatická záloha dokončena")
        
        return success, message, backup_path
    
    def get_backup_settings(self):
        """Vrátí aktuální nastavení záloh."""
        return {
            "backup_directory": self.backup_dir,
            "max_backups": self.max_backups,
            "auto_backup_enabled": self.auto_backup_enabled,
            "backup_frequency_days": self.backup_frequency_days
        }
    
    def update_backup_settings(self, settings):
        """
        Aktualizuje nastavení záloh.
        
        Args:
            settings (dict): Nové nastavení
        """
        settings_to_save = {
            "backup_directory": settings.get("backup_directory", self.backup_dir),
            "max_backups": str(settings.get("max_backups", self.max_backups)),
            "backup_frequency_days": str(settings.get("backup_frequency_days", self.backup_frequency_days))
        }
        
        # Per-instance nastavení pro automatické zálohy
        if "auto_backup_enabled" in settings:
            settings_to_save[f"auto_backup_enabled_{self.instance_id}"] = str(settings["auto_backup_enabled"])
        
        save_settings(settings_to_save)
        
        # Aktualizuj lokální hodnoty
        self.backup_dir = settings.get("backup_directory", self.backup_dir)
        self.max_backups = settings.get("max_backups", self.max_backups)
        self.auto_backup_enabled = settings.get("auto_backup_enabled", self.auto_backup_enabled)
        self.backup_frequency_days = settings.get("backup_frequency_days", self.backup_frequency_days)
        
        # Vytvoř adresář pokud neexistuje
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
    
    def get_instance_info(self):
        """Vrátí informace o této instanci."""
        return {
            "instance_id": self.instance_id,
            "hostname": socket.gethostname(),
            "hash": self.instance_id.split("_")[1] if "_" in self.instance_id else "unknown",
            "auto_backup_enabled": self.auto_backup_enabled
        }
    
    def get_all_instances_info(self):
        """Vrátí informace o všech registrovaných instancích."""
        from models.databaze import get_connection
        
        instances = []
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT setting_name, setting_value 
                FROM Settings 
                WHERE setting_name LIKE 'auto_backup_enabled_%'
            """)
            
            for setting_name, setting_value in cur.fetchall():
                instance_id = setting_name.replace("auto_backup_enabled_", "")
                hostname = instance_id.split("_")[0] if "_" in instance_id else "unknown"
                instance_hash = instance_id.split("_")[1] if "_" in instance_id else "unknown"
                
                instances.append({
                    "instance_id": instance_id,
                    "hostname": hostname, 
                    "hash": instance_hash,
                    "auto_backup_enabled": setting_value.lower() == "true",
                    "is_current": instance_id == self.instance_id
                })
        
        return instances


# Globální instance pro snadné použití
backup_manager = BackupManager()