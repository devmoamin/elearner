
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor


def generate_certificate(response, user, course, enrollment):
    full_name = user.get_full_name() or user.username
    instructor_name = course.instructor.name
    completion_date = enrollment.completed_date.strftime('%B %d, %Y')

    # Canvas setup
    pdf_canvas = canvas.Canvas(response, pagesize=landscape(A4))
    width, height = landscape(A4)

    color_indigo = "#4f46e5"
    color_gray_dark = "#374151"
    color_gray_light = "#6b7280"

    # --- Add Margin Before the Border ---
    margin = 30
    border_color = HexColor(color_indigo)
    border_width = 2  # Thin border

    pdf_canvas.setStrokeColor(border_color)
    pdf_canvas.setLineWidth(border_width)
    pdf_canvas.rect(margin, margin, width - 2 * margin, height - 2 * margin)

    # --- Certificate Title ---
    pdf_canvas.setFont("Times-Bold", 44)
    pdf_canvas.setFillColor(HexColor(color_gray_dark))
    pdf_canvas.drawCentredString(width / 2, height - 100, "Certificate of Completion")

    # --- Recipient Name ---
    pdf_canvas.setFont("Helvetica-Bold", 36)
    pdf_canvas.setFillColor(HexColor(color_indigo))
    pdf_canvas.drawCentredString(width / 2, height - 210, full_name)

    # --- Course Completion Message ---
    pdf_canvas.setFont("Times-Roman", 22)
    pdf_canvas.setFillColor(HexColor(color_gray_dark))
    pdf_canvas.drawCentredString(width / 2, height - 280, f"has successfully completed the course")

    # --- Course Title ---
    pdf_canvas.setFont("Helvetica-Bold", 30)
    pdf_canvas.setFillColor(HexColor(color_indigo))
    pdf_canvas.drawCentredString(width / 2, height - 320, f"“{course.title}”")

    # --- Certificate Message ---
    pdf_canvas.setFont("Times-Italic", 16)
    pdf_canvas.setFillColor(HexColor(color_gray_light))  # Gray font color
    pdf_canvas.drawCentredString(width / 2, height - 390, "This certificate is presented in recognition of the dedication, hard work,")
    pdf_canvas.drawCentredString(width / 2, height - 410, "and commitment demonstrated in successfully completing this course.")

    # --- Decorative Line ---
    line_width = 300
    pdf_canvas.setStrokeColor(HexColor(color_indigo))
    pdf_canvas.setLineWidth(2)
    pdf_canvas.line((width / 2) - (line_width / 2), height - 125, (width / 2) + (line_width / 2), height - 125)

    # --- Signature Section at the Bottom ---
    signature_y = 110  # Adjusted for bottom placement
    pdf_canvas.setStrokeColor(HexColor(color_indigo))
    pdf_canvas.line(width / 4 - 80, signature_y, width / 4 + 80, signature_y)  # Instructor
    pdf_canvas.line((3 * width / 4) - 80, signature_y, (3 * width / 4) + 80, signature_y)  # E-Learner

    # Signatures Text
    pdf_canvas.setFont("Times-Italic", 16)
    pdf_canvas.setFillColor(HexColor(color_gray_dark))
    pdf_canvas.drawCentredString(width / 4, signature_y - 30, "Instructor")
    pdf_canvas.drawCentredString(3 * width / 4, signature_y - 30, "E-Learner")

    # --- Date Under E-Learner Signature ---
    pdf_canvas.setFont("Times-Italic", 14)
    pdf_canvas.setFillColor(HexColor(color_gray_light))
    pdf_canvas.drawCentredString(width / 4, signature_y - 50, instructor_name)  # Instructor Name
    pdf_canvas.drawCentredString(3 * width / 4, signature_y - 50, f"{completion_date}")

    # --- Finalize PDF ---
    pdf_canvas.showPage()
    pdf_canvas.save()
