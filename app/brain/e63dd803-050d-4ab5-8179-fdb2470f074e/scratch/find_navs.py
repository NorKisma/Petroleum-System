with open('app/templates/layouts/base.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'class="nav flex-column my-1 ps-4"' in line:
            print(f'Line {i+1}: inner nav found.')
