import pymupdf
from datetime import date
from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI()


def add_text_field(page, name, point, value, fontsize, width, height=None, align=0):
    """Add an editable AcroForm text field to `page`.

    `point` is the text baseline (same anchor insert_text uses), so existing
    coordinates keep working; the widget box is built around it.
    """
    x, y = point
    height = height or fontsize * 1.6
    rect = pymupdf.Rect(x - 2, y - fontsize, x - 2 + width, y - fontsize + height)

    widget = pymupdf.Widget()
    widget.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
    widget.field_name = name
    widget.rect = rect
    widget.field_value = value or ""
    widget.text_font = "Helv"
    widget.text_fontsize = fontsize
    widget.text_color = (0, 0, 0)
    widget.text_maxlen = 0          # unlimited
    widget.fill_color = None        # transparent, keeps the template visible
    widget.border_width = 0
    widget.text_align = align       # 0 left, 1 center, 2 right

    return page.add_widget(widget)


def generate_form(pol, name, email, phone, billing):
    is_pacstar = pol[0] == "P"

    template_file = "templates/pacstar.pdf" if is_pacstar else "templates/anchor.pdf"
    today_date = date.today().strftime("%m/%d/%Y")

    delta1 = 32 if is_pacstar else 0
    delta2 = 55 if is_pacstar else 0

    parts = billing.split(",")
    billing1 = ",".join(parts[0:-2]).strip()
    billing2 = ",".join(parts[-2:]).strip()

    # (field_name, point, value, fontsize, width)
    fields = [
        ("date",     (50, 148 + delta1),  today_date, 8,  80),
        ("name",     (122, 159 + delta1), name,       8,  220),
        ("policy",   (120, 170 + delta1), pol,        8,  220),
        ("billing1", (115, 360 + delta2), billing1,   12, 230),
        ("billing2", (115, 395 + delta2), billing2,   12, 230),
        ("phone",    (375, 360 + delta2), phone,      12, 180),
        ("email",    (375, 395 + delta2), email,      12, 220),
        ("cc_holder_name",    (430, 490 + delta2), name, 12, 180),
        ("acc_no",    (430, 515 + delta2), "",      12, 180),
        ("exp_date",   (385, 538 + delta2), "",      12, 80),
        ("cvc",    (385, 560 + delta2), "",      12, 80),
    ]

    doc = pymupdf.open(template_file)
    page = doc[0]

    for field_name, point, value, size, width in fields:
        add_text_field(page, field_name, point, value, size, width)

    pdf_bytes = doc.tobytes(garbage=3, deflate=True)
    doc.close()
    return pdf_bytes


@app.get("/form.pdf")
def form(pol: str, name: str, email: str, phone: str, billing: str):
    pdf = generate_form(pol, name, email, phone, billing)
    return Response(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{pol}.pdf"'},
    )