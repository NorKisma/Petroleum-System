import os

filepath = r"c:\Users\hp\OneDrive\Desktop\Advanced-Inventory-POS-Accounting-System\Advanced-Inventory-POS-Accounting-System\app\templates\layouts\base.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the old Staff and User links from inside Admin Control
old_links = """                            <a href="{{ url_for('settings.manage_users') }}"
                                class="nav-link py-2 text-decoration-none small {% if request.endpoint == 'settings.manage_users' %}active{% endif %}">User
                                Management</a>

                            {% if company_settings.module_hrm %}
                            <a href="{{ url_for('staff.list_staff') }}"
                                class="nav-link py-2 text-decoration-none small {% if request.endpoint == 'staff.list_staff' %}active{% endif %}">Staff
                                Management</a>
                            {% endif %}

                            {% if company_settings.module_service_staff %}
                            <a href="#" class="nav-link py-2 text-decoration-none small">Service Staff</a>
                            {% endif %}"""

content = content.replace(old_links, "")

# 2. Insert the combined link before "Admin Control"
new_staff_link = """                <!-- Staff & Users -->
                {% if current_user.role in ['admin', 'developer'] or current_user.is_super_admin %}
                <div class="nav-item mb-1">
                    <a href="{{ url_for('staff.list_staff') }}"
                        class="nav-link sidebar-tooltip {% if 'staff' in request.endpoint or 'manage_users' in request.endpoint %}active{% endif %}"
                        data-tooltip="Staff & Users">
                        <div class="nav-link-content">
                            <i class="main-icon fas fa-users"></i>
                            <span>Staff & Users</span>
                        </div>
                    </a>
                </div>
                {% endif %}

                <!-- Admin Control -->"""

content = content.replace("<!-- Admin Control -->", new_staff_link)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Moved Staff and Users out of Admin Control!")
