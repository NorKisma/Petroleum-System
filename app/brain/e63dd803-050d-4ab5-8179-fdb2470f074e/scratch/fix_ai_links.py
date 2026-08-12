import os

filepath = r"c:\Users\hp\OneDrive\Desktop\Advanced-Inventory-POS-Accounting-System\Advanced-Inventory-POS-Accounting-System\app\templates\layouts\base.html"

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'url_for(\'ai.dashboard\')' in line and 'AI Intelligence' in line and 'class="nav-link py-2' in line:
        # Skip the lines we injected inside the sub-menus
        continue
    new_lines.append(line)

# Now, we need to add the AI Intelligence link right after the Dashboard link.
# Let's find the Dashboard closing div.
dashboard_block_end = -1
for i, line in enumerate(new_lines):
    if '<!-- Contacts -->' in line:
        dashboard_block_end = i
        break

if dashboard_block_end != -1:
    ai_link_block = """
                <!-- AI Intelligence Center -->
                <div class="nav-item mb-1">
                    <a href="{{ url_for('ai.dashboard') }}"
                        class="nav-link sidebar-tooltip {% if 'ai.' in request.endpoint %}active{% endif %}"
                        data-tooltip="AI Intelligence"
                        style="background: {% if 'ai.' in request.endpoint %}var(--primary){% else %}rgba(75, 163, 227, 0.15){% endif %}; border-radius: 10px;">
                        <div class="nav-link-content">
                            <i class="main-icon fas fa-robot" style="color: var(--primary);"></i>
                            <span style="color: var(--primary); font-weight: 700;">AI Intelligence</span>
                        </div>
                        <span class="badge ms-auto" style="background:rgba(75, 163, 227, 0.3);color:var(--primary);font-size:0.6rem;">NEW</span>
                    </a>
                </div>
"""
    new_lines.insert(dashboard_block_end, ai_link_block)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Removed AI links from sub-menus and added it below Dashboard.")
