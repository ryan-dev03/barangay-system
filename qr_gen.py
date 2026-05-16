import qrcode

VM_IP = '192.168.18.150'
PORT = '80'

units = ['HU-001', 'HU-002', 'HU-003']

for unit in units:
    url = f'http://{VM_IP}:{PORT}/unit/{unit}'
    img = qrcode.make(url)
    img.save(f'static/qr/{unit}.png')
    print(f'Generated: {unit} → {url}')

print('Done! All 3 QR codes saved to static/qr/')
