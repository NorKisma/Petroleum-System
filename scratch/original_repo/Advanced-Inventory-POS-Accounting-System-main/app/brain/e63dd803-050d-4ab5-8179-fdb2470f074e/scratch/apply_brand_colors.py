import os

def replace_colors_in_dir(directory):
    replacements = {
        '#4f46e5': '#4ba3e3',
        '#6366f1': '#50a5e6',
        '#4338ca': '#318bce',
        '#7c3aed': '#4ba3e3',
        '#a78bfa': '#4ba3e3', # AI light purple
        '#3b82f6': '#4ba3e3', # Primary blue
        '#ef4444': '#f94a4a', # Primary red
    }
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.html', '.css', '.js')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    changed = False
                    for old, new in replacements.items():
                        if old in content or old.upper() in content:
                            content = content.replace(old, new)
                            content = content.replace(old.upper(), new)
                            changed = True
                            
                    if changed:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"Updated colors in: {path}")
                except Exception as e:
                    pass

replace_colors_in_dir(r'c:\Users\hp\OneDrive\Desktop\Advanced-Inventory-POS-Accounting-System\Advanced-Inventory-POS-Accounting-System\app')
print("Color replacement complete.")
