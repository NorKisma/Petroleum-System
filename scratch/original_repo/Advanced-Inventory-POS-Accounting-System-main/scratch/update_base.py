import re

file_path = 'app/templates/layouts/base.html'
with open(file_path, 'r') as f:
    content = f.read()

# Remove sidebar entirely
# From <button class="mobile-nav-toggle... to </nav> right before <!-- Page Content -->
sidebar_pattern = re.compile(r'<button class="mobile-nav-toggle.*?</nav>', re.DOTALL)
content = sidebar_pattern.sub('', content)

# Remove sidebarOverlay
content = re.sub(r'<div class="sidebar-overlay" id="sidebarOverlay"></div>\s*', '', content)

# Change #page-content-wrapper style if needed? The CSS handles it but since sidebar is gone, 
# there might be a left margin. I'll add inline style for now or update style.css later.
# Let's add a style to head.
style_addition = """
        /* Hide sidebar margin */
        #page-content-wrapper {
            width: 100% !important;
            margin-left: 0 !important;
        }
        .navbar-elite {
            padding-left: 1rem !important;
        }
"""
content = content.replace('</style>', style_addition + '\n    </style>')

# Replace the hamburger menu with Apps icon
hamburger_pattern = r'<button type="button" id="sidebarCollapse" class="btn btn-link p-0 me-4 border-0">.*?<i class="fas fa-bars fs-4"></i>.*?</button>'

apps_icon = """<a href="{{ url_for('main.dashboard') }}" class="btn btn-link p-0 me-4 border-0 text-white" title="Apps Menu">
                            <i class="fas fa-th fs-4"></i>
                        </a>"""
content = re.sub(hamburger_pattern, apps_icon, content, flags=re.DOTALL)

# Add Top Navbar Dropdowns based on endpoint
dropdowns = """
                        <!-- App Menus -->
                        <div class="d-none d-md-flex ms-3 gap-2">
                            {% set ep = request.endpoint or '' %}
                            
                            {% if 'inventory' in ep %}
                            <div class="dropdown">
                                <button class="btn btn-link text-white text-decoration-none dropdown-toggle" type="button" data-bs-toggle="dropdown">Products</button>
                                <ul class="dropdown-menu shadow border-0 mt-2 rounded-3">
                                    <li><a class="dropdown-item" href="{{ url_for('inventory.list_products') }}">All Products</a></li>
                                    <li><a class="dropdown-item" href="{{ url_for('inventory.list_categories') }}">Categories</a></li>
                                    {% if company_settings.module_stock_transfer %}
                                    <li><a class="dropdown-item" href="{{ url_for('inventory.list_transfers') }}">Stock Transfers</a></li>
                                    {% endif %}
                                    {% if company_settings.module_stock_adjustment %}
                                    <li><a class="dropdown-item" href="{{ url_for('inventory.stock_adjustment') }}">Stock Adjustment</a></li>
                                    {% endif %}
                                    <li><a class="dropdown-item" href="{{ url_for('inventory.import_opening_stock') }}">Import Stock</a></li>
                                </ul>
                            </div>
                            {% endif %}

                            {% if 'sale' in ep or 'pos' in ep or 'customer' in ep %}
                            <div class="dropdown">
                                <button class="btn btn-link text-white text-decoration-none dropdown-toggle" type="button" data-bs-toggle="dropdown">Sales</button>
                                <ul class="dropdown-menu shadow border-0 mt-2 rounded-3">
                                    <li><a class="dropdown-item" href="{{ url_for('sales.list_sales') }}">All Sales</a></li>
                                    {% if company_settings.module_pos %}
                                    <li><a class="dropdown-item" href="{{ url_for('sales.pos') }}">POS Terminal</a></li>
                                    {% endif %}
                                    <li><a class="dropdown-item" href="{{ url_for('sales.list_returns') }}">Sales Returns</a></li>
                                    <li><hr class="dropdown-divider"></li>
                                    <li><a class="dropdown-item" href="{{ url_for('customers.list_customers') }}">Customers</a></li>
                                    <li><a class="dropdown-item" href="{{ url_for('customers.receipts') }}">Receipts</a></li>
                                </ul>
                            </div>
                            {% endif %}
                            
                            {% if 'vendor' in ep %}
                            <div class="dropdown">
                                <button class="btn btn-link text-white text-decoration-none dropdown-toggle" type="button" data-bs-toggle="dropdown">Purchases</button>
                                <ul class="dropdown-menu shadow border-0 mt-2 rounded-3">
                                    <li><a class="dropdown-item" href="{{ url_for('vendor.purchases', view='list') }}">All Purchases</a></li>
                                    <li><a class="dropdown-item" href="{{ url_for('vendor.purchases', view='add') }}">Add Purchase</a></li>
                                    <li><a class="dropdown-item" href="{{ url_for('vendor.returns', view='list') }}">Purchase Returns</a></li>
                                    <li><hr class="dropdown-divider"></li>
                                    <li><a class="dropdown-item" href="{{ url_for('vendor.list_vendors') }}">Suppliers</a></li>
                                </ul>
                            </div>
                            {% endif %}
                            
                            {% if 'accounting' in ep %}
                            <div class="dropdown">
                                <button class="btn btn-link text-white text-decoration-none dropdown-toggle" type="button" data-bs-toggle="dropdown">Financial</button>
                                <ul class="dropdown-menu shadow border-0 mt-2 rounded-3">
                                    <li><a class="dropdown-item" href="{{ url_for('accounting.general_ledger') }}">General Ledger</a></li>
                                    <li><a class="dropdown-item" href="{{ url_for('accounting.chart_of_accounts') }}">Chart of Accounts</a></li>
                                    <li><a class="dropdown-item" href="{{ url_for('accounting.bank_accounts') }}">Bank Accounts</a></li>
                                    <li><a class="dropdown-item" href="{{ url_for('accounting.expenses') }}">Expenses</a></li>
                                    <li><hr class="dropdown-divider"></li>
                                    <li><a class="dropdown-item" href="{{ url_for('accounting.reports_hub') }}">All Reports</a></li>
                                </ul>
                            </div>
                            {% endif %}
                            
                            {% if 'settings' in ep or 'staff' in ep %}
                            <div class="dropdown">
                                <button class="btn btn-link text-white text-decoration-none dropdown-toggle" type="button" data-bs-toggle="dropdown">Configuration</button>
                                <ul class="dropdown-menu shadow border-0 mt-2 rounded-3">
                                    <li><a class="dropdown-item" href="{{ url_for('settings.index') }}">Business Settings</a></li>
                                    <li><a class="dropdown-item" href="{{ url_for('staff.list_staff') }}">Staff & Users</a></li>
                                </ul>
                            </div>
                            {% endif %}
                        </div>
"""
# Insert after the status-dot container
status_dot_pattern = r'<div class="d-flex align-items-center me-4 pe-4">.*?<span class="status-dot"></span>\s*</div>'
content = re.sub(status_dot_pattern, lambda m: m.group(0) + '\n' + dropdowns, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

print("Updated base.html successfully.")
