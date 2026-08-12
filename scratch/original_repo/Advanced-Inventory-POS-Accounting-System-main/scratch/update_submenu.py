import re

file_path = 'app/templates/layouts/base.html'
with open(file_path, 'r') as f:
    content = f.read()

old_menus = """                        <!-- App Menus -->
                        <div class="d-flex ms-3 gap-2">
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
                        </div>"""

new_menus = """                        <!-- App Menus -->
                        <div class="d-flex ms-3 gap-2">
                            {% set ep = request.endpoint or '' %}
                            
                            {% if 'inventory' in ep %}
                            <div class="dropdown">
                                <button class="btn btn-link text-white text-decoration-none dropdown-toggle" type="button" data-bs-toggle="dropdown">Inventory</button>
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

                            {% if 'pos' in ep %}
                            <div class="dropdown">
                                <button class="btn btn-link text-white text-decoration-none dropdown-toggle" type="button" data-bs-toggle="dropdown">Point of Sale</button>
                                <ul class="dropdown-menu shadow border-0 mt-2 rounded-3">
                                    <li><a class="dropdown-item" href="{{ url_for('sales.pos') }}">Terminal</a></li>
                                </ul>
                            </div>
                            {% endif %}

                            {% if 'sale' in ep and 'pos' not in ep %}
                            <div class="dropdown">
                                <button class="btn btn-link text-white text-decoration-none dropdown-toggle" type="button" data-bs-toggle="dropdown">Sales</button>
                                <ul class="dropdown-menu shadow border-0 mt-2 rounded-3">
                                    <li><a class="dropdown-item" href="{{ url_for('sales.list_sales') }}">All Sales</a></li>
                                    <li><a class="dropdown-item" href="{{ url_for('sales.list_returns') }}">Sales Returns</a></li>
                                </ul>
                            </div>
                            {% endif %}

                            {% if 'customer' in ep %}
                            <div class="dropdown">
                                <button class="btn btn-link text-white text-decoration-none dropdown-toggle" type="button" data-bs-toggle="dropdown">Contacts</button>
                                <ul class="dropdown-menu shadow border-0 mt-2 rounded-3">
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
                            
                            {% if 'accounting' in ep and 'expenses' not in ep and 'report' not in ep %}
                            <div class="dropdown">
                                <button class="btn btn-link text-white text-decoration-none dropdown-toggle" type="button" data-bs-toggle="dropdown">Accounting</button>
                                <ul class="dropdown-menu shadow border-0 mt-2 rounded-3">
                                    <li><a class="dropdown-item" href="{{ url_for('accounting.general_ledger') }}">General Ledger</a></li>
                                    <li><a class="dropdown-item" href="{{ url_for('accounting.chart_of_accounts') }}">Chart of Accounts</a></li>
                                    <li><a class="dropdown-item" href="{{ url_for('accounting.bank_accounts') }}">Bank Accounts</a></li>
                                </ul>
                            </div>
                            {% endif %}

                            {% if 'expenses' in ep %}
                            <div class="dropdown">
                                <button class="btn btn-link text-white text-decoration-none dropdown-toggle" type="button" data-bs-toggle="dropdown">Expenses</button>
                                <ul class="dropdown-menu shadow border-0 mt-2 rounded-3">
                                    <li><a class="dropdown-item" href="{{ url_for('accounting.expenses') }}">All Expenses</a></li>
                                </ul>
                            </div>
                            {% endif %}

                            {% if 'report' in ep %}
                            <div class="dropdown">
                                <button class="btn btn-link text-white text-decoration-none dropdown-toggle" type="button" data-bs-toggle="dropdown">Reports</button>
                                <ul class="dropdown-menu shadow border-0 mt-2 rounded-3">
                                    <li><a class="dropdown-item" href="{{ url_for('accounting.reports_hub') }}">All Reports</a></li>
                                </ul>
                            </div>
                            {% endif %}
                            
                            {% if 'settings' in ep %}
                            <div class="dropdown">
                                <button class="btn btn-link text-white text-decoration-none dropdown-toggle" type="button" data-bs-toggle="dropdown">Settings</button>
                                <ul class="dropdown-menu shadow border-0 mt-2 rounded-3">
                                    <li><a class="dropdown-item" href="{{ url_for('settings.index') }}">Business Settings</a></li>
                                </ul>
                            </div>
                            {% endif %}

                            {% if 'staff' in ep and 'payroll' not in ep %}
                            <div class="dropdown">
                                <button class="btn btn-link text-white text-decoration-none dropdown-toggle" type="button" data-bs-toggle="dropdown">Employees</button>
                                <ul class="dropdown-menu shadow border-0 mt-2 rounded-3">
                                    <li><a class="dropdown-item" href="{{ url_for('staff.list_staff') }}">Staff List</a></li>
                                </ul>
                            </div>
                            {% endif %}

                            {% if 'payroll' in ep %}
                            <div class="dropdown">
                                <button class="btn btn-link text-white text-decoration-none dropdown-toggle" type="button" data-bs-toggle="dropdown">Payroll</button>
                                <ul class="dropdown-menu shadow border-0 mt-2 rounded-3">
                                    <li><a class="dropdown-item" href="{{ url_for('staff.list_payroll') }}">All Payrolls</a></li>
                                </ul>
                            </div>
                            {% endif %}
                        </div>"""

if old_menus in content:
    content = content.replace(old_menus, new_menus)
    with open(file_path, 'w') as f:
        f.write(content)
    print("Updated submenus successfully.")
else:
    print("Could not find old menus block.")
