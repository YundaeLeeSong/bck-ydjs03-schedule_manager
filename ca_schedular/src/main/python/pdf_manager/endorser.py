from pathlib import Path
from typing import Optional
import sys
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import red
from PyPDF2 import PdfReader, PdfWriter
import os

def create_stamp_image(
    text: str,
    output_path: Path,
    size: int = 200,  # Reduced size
    font_size: int = 32,  # Adjusted font size
    border_width: int = 6,
    color: tuple = (220, 0, 0),  # Slightly darker red
    rotation: int = -25,  # Counter-clockwise rotation in degrees (negative for clockwise)
) -> None:
    """
    Creates a professional-looking circular stamp image with the given text.

    Args:
        text: The text to display in the stamp
        output_path: Where to save the stamp image
        size: Size of the stamp in pixels
        font_size: Font size for the text
        border_width: Width of the circle border
        color: RGB color tuple for the stamp
        rotation: Rotation in degrees (negative for clockwise)
    """
    # Create a new image with transparent background
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Draw the outer circle
    margin = border_width
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        outline=color,
        width=border_width
    )

    # Draw the inner circle
    inner_margin = margin + 10
    draw.ellipse(
        [inner_margin, inner_margin, size - inner_margin, size - inner_margin],
        outline=color,
        width=1
    )

    # Load font and calculate text size
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Draw the text
    text = text.upper()
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 5  # Slight offset upward
    
    draw.text((x, y), text, font=font, fill=color)

    # Rotate the image (negative for clockwise)
    image = image.rotate(rotation, expand=True, resample=Image.BICUBIC)

    # Save the image
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, 'PNG')


def stamp_pdf_with_image(
    input_pdf: Path,
    stamp_image: Path,
    output_pdf: Path,
    margin_inch: float = 0.25,  # Reduced margin to move stamp more to corner
    stamp_scale: float = 0.8,  # Reduced scale
) -> None:
    """
    Stamps an image onto each page of a PDF in the top-right corner, positioned slightly above the document
    to create a more realistic stamp effect.

    Args:
        input_pdf: Path to the input PDF file
        stamp_image: Path to the stamp image file
        output_pdf: Path where the output PDF will be saved
        margin_inch: Margin from the edges in inches
        stamp_scale: Scale factor for the stamp size (1.0 = original size)
    """
    try:
        # Read the input PDF
        reader = PdfReader(str(input_pdf))
        writer = PdfWriter()

        # Constants
        pt_per_inch = 72
        margin = margin_inch * pt_per_inch

        total_pages = len(reader.pages)
        print(f"Processing {total_pages} pages...")

        for i, page in enumerate(reader.pages, 1):
            # Get page size
            page_w = float(page.mediabox.width)
            page_h = float(page.mediabox.height)
            
            # Create a new PDF with the same size as the input page
            temp_pdf = Path(f"temp_page_{i}.pdf")
            c = canvas.Canvas(str(temp_pdf), pagesize=(page_w, page_h))

            # Calculate stamp position (top-right corner)
            stamp_size = 150 * stamp_scale  # Reduced base size in points
            tx = page_w - margin - stamp_size
            # Position the stamp slightly above the document (negative offset)
            ty = page_h - margin - stamp_size + 40  # Added 20 points offset upward

            # Draw the stamp image
            c.drawImage(
                str(stamp_image),
                tx, ty,
                width=stamp_size,
                height=stamp_size,
                preserveAspectRatio=True,
                mask='auto'
            )
            c.save()

            # Merge the stamped page with the original
            stamped_page = PdfReader(str(temp_pdf)).pages[0]
            
            # Copy the original page's rotation
            if hasattr(page, '/Rotate'):
                stamped_page.rotate = page['/Rotate']
            
            page.merge_page(stamped_page)
            writer.add_page(page)

            # Clean up temporary file
            temp_pdf.unlink()
            
            if i % 10 == 0 or i == total_pages:
                print(f"Processed {i}/{total_pages} pages")

        # Write output
        with open(output_pdf, "wb") as fp:
            writer.write(fp)

    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred - {e}", file=sys.stderr)
        sys.exit(1)


def endorse_pdf(
    input_pdf: str | Path,
    output_pdf: str | Path | None = None,
    stamp_text: str = "Endorsed",
    margin_inch: float = 0.15,  # Reduced margin to move stamp more to corner
    stamp_scale: float = 0.8,
    stamp_size: int = 200,
    font_size: int = 32,
    rotation: int = -25,
) -> None:
    """
    Endorse a PDF file with a stamp in the top-right corner.

    Args:
        input_pdf: Path to the input PDF file
        output_pdf: Path where the output PDF will be saved. If None, will use input path with "-endorsed" suffix
        stamp_text: Text to display in the stamp
        margin_inch: Margin from the edges in inches (default: 0.15)
        stamp_scale: Scale factor for the stamp size
        stamp_size: Size of the stamp in pixels
        font_size: Font size for the text
        rotation: Rotation in degrees (negative for clockwise)
    """
    # Convert string paths to Path objects
    input_pdf = Path(input_pdf)
    
    # Generate output path if not provided
    if output_pdf is None:
        output_pdf = input_pdf.parent / f"endorsed/{input_pdf.stem}-endorsed{input_pdf.suffix}"
        output_pdf.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_pdf = Path(output_pdf)
        
    stamp_image = Path("images/endorse.png")

    try:
        # Create the stamp image
        create_stamp_image(
            text=stamp_text,
            output_path=stamp_image,
            size=stamp_size,
            font_size=font_size,
            border_width=6,
            color=(220, 0, 0),  # Slightly darker red
            rotation=rotation
        )

        # Apply the stamp to all pages
        stamp_pdf_with_image(
            input_pdf=input_pdf,
            stamp_image=stamp_image,
            output_pdf=output_pdf,
            margin_inch=margin_inch,
            stamp_scale=stamp_scale
        )

        print(f"Successfully created stamped PDF at: {output_pdf}")

    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred - {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """
    Example usage of the PDF endorsement function.
    """
    # Example usage with automatic output path
    endorse_pdf(
        input_pdf="input.pdf",
        stamp_text="Week 3.4",
        # stamp_text="Endorsed: Hi",
        margin_inch=0.02,  # Reduced margin to move stamp more to corner
        stamp_scale=0.8
    )


if __name__ == "__main__":
    main()
