import os

# Files to update
files = [
    r"c:\Users\hp\OneDrive\Desktop\Advanced-Inventory-POS-Accounting-System\Advanced-Inventory-POS-Accounting-System\app\modules\settings\routes.py",
    r"c:\Users\hp\OneDrive\Desktop\Advanced-Inventory-POS-Accounting-System\Advanced-Inventory-POS-Accounting-System\app\templates\settings\index.html",
    r"c:\Users\hp\OneDrive\Desktop\Advanced-Inventory-POS-Accounting-System\Advanced-Inventory-POS-Accounting-System\app\templates\layouts\base.html",
]

for fp in files:
    if os.path.exists(fp):
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace instances of ['admin', 'developer'] with ['developer']
        new_content = content.replace("['admin', 'developer']", "['developer']")
        new_content = new_content.replace('["admin", "developer"]', '["developer"]')
        
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(new_content)

print("Removed Admin from Business Settings access.")
