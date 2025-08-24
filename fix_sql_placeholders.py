import os
import re
import glob

def fix_sql_placeholders():
    """Opraví všechny SQL placeholders z ? na %s v models souborech"""
    
    model_files = [
        'models/doktori.py',
        'models/ordinace.py', 
        'models/rezervace.py',
        'models/settings.py',
        'models/users.py'
    ]
    
    print("=== OPRAVA SQL PLACEHOLDERS ===")
    
    for file_path in model_files:
        if not os.path.exists(file_path):
            print(f"⚠️  Soubor {file_path} neexistuje, přeskakuji")
            continue
            
        print(f"🔧 Opravuji {file_path}...")
        
        # Načti obsah souboru
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Nahraď ? za %s pouze v SQL kontextu (uvnitř execute())
        # Hledá pattern: execute("...?...", nebo execute('''...?...''',
        def replace_placeholders(match):
            sql_part = match.group(1)
            # Nahraď všechny ? za %s v SQL části
            sql_part = sql_part.replace('?', '%s')
            return f'execute({sql_part},'
        
        # Pattern pro execute() s SQL obsahujícím ?
        pattern = r'execute\(([^,]+?),'
        
        # Najdi všechny execute() volání
        matches = re.finditer(pattern, content, re.DOTALL)
        
        changes = 0
        new_content = content
        
        # Projdi matches odzadu (aby se neposouvaly indexy)
        for match in reversed(list(matches)):
            sql_part = match.group(1).strip()
            if '?' in sql_part:
                new_sql_part = sql_part.replace('?', '%s')
                new_content = new_content[:match.start(1)] + new_sql_part + new_content[match.end(1):]
                changes += 1
        
        # Ulož změněný soubor
        if new_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ {file_path} - provedeno {changes} změn")
        else:
            print(f"✓ {file_path} - žádné změny potřebné")
    
    print("✅ Oprava dokončena!")

if __name__ == "__main__":
    fix_sql_placeholders()
