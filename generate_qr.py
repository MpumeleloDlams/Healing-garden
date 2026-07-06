import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask

# Configuration
URL = "https://mpumelelodlams.github.io/Healing-garden/"
# Project brand color: --sage: #8A9A7B
SAGE_COLOR = (138, 154, 123)  # RGB for #8A9A7B
OUTPUT_FILE = "healing_garden_qr.png"

def generate_qr():
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(URL)
    qr.make(fit=True)

    # Create the image with custom styling
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(back_color=(255, 255, 255), front_color=SAGE_COLOR)
    )

    img.save(OUTPUT_FILE)
    print(f"QR code generated and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_qr()
