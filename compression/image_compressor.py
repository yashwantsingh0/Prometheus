# compression/image_compressor.py

from PIL import Image
import os

def compress_image(
    input_path,
    output_path=None,
    quality=85,
    resize_percent=None,
    dpi=None,
    background_color="white"
):
    try:
        img = Image.open(input_path)
        img_format = img.format or "JPEG"

        # Resize image
        if resize_percent and 0 < resize_percent < 100:
            new_size = (
                int(img.width * resize_percent / 100),
                int(img.height * resize_percent / 100)
            )
            img = img.resize(new_size, Image.ANTIALIAS)

        # Handle transparency
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, background_color)
            background.paste(img, mask=img.split()[3])  # Alpha channel
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Output path
        if not output_path:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_compressed{ext}"

        # Save image
        save_kwargs = {"quality": quality, "optimize": True}
        if dpi:
            save_kwargs["dpi"] = (dpi, dpi)
        img.save(output_path, format=img_format, **save_kwargs)

        return output_path
    except Exception as e:
        print(f"Image compression failed: {e}")
        return None
