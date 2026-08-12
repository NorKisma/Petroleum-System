import os

filepath = r"c:\Users\hp\OneDrive\Desktop\Advanced-Inventory-POS-Accounting-System\Advanced-Inventory-POS-Accounting-System\app\templates\layouts\base.html"

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if 'class="nav flex-column my-1 ps-4"' in line:
        # Avoid double adding if script is run twice
        if i + 1 < len(lines) and 'AI Intelligence' in lines[i+1]:
            continue
            
        indent = line[:len(line) - len(line.lstrip())] + "    "
        ai_link = f'{indent}<a href="{{{{ url_for(\'ai.dashboard\') }}}}" class="nav-link py-2 text-decoration-none small" style="color: #a78bfa; font-weight: 700;"><i class="fas fa-magic me-2"></i> AI Intelligence</a>\n'
        new_lines.append(ai_link)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Injected AI links into all modules!")
