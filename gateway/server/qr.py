import qrcode
from pathlib import Path

def qr_render(carnet, url_completa):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url_completa)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Guardado físico
    output_dir = Path("server/static/qrcodes")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = output_dir / f"qr_{carnet}.png"
    img.save(str(file_path))

    return str(file_path)