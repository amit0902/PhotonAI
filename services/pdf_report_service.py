from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from io import BytesIO
#import plotly.io as pio
from datetime import datetime
from services.financial_graph_service import generate_breakeven_chart_image


# ------------------------------------------------
# Header / Footer
# ------------------------------------------------

def header_footer(canvas, doc):

    canvas.saveState()

    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(40, 800, "PhotonAI")

    canvas.setFont("Helvetica", 10)
    canvas.drawRightString(550, 800, "Solar Consultancy Proposal")

    canvas.line(40, 795, 550, 795)

    canvas.line(40, 40, 550, 40)

    canvas.setFont("Helvetica", 9)
    canvas.drawString(40, 25, "PhotonAI Solar Advisory Platform")

    canvas.drawRightString(550, 25, f"Page {doc.page}")

    canvas.restoreState()


# ------------------------------------------------
# Main PDF Generator
# ------------------------------------------------

def generate_pdf_report(state):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=80,
        bottomMargin=60
    )

    elements = []

    styles = getSampleStyleSheet()

    # Custom Styles
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1f4e79"),
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor("#2c5f8d"),
        spaceBefore=16,
        spaceAfter=10
    )

    text_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )

    # ------------------------------------------------
    # Extract Data from State
    # ------------------------------------------------

    name = state.get("name", "Customer")
    city = state.get("city", "-")
    monthly_units = state.get("monthly_units", 0)
    annual_consumption = state.get("annual_consumption", 0)

    system_kw = state.get("system_kw", 0)
    annual_kwh = state.get("annual_kwh", 0)

    panel_name = state.get("panel_name", "-")
    panel_count = state.get("panel_count", 0)

    inverter_name = state.get("inverter_name", "-")
    inverter_kw = state.get("inverter_kw", 0)

    battery_name = state.get("battery_name", "Not Included")
    battery_kwh = state.get("battery_kwh", 0)

    series = state.get("series", 0)
    parallel = state.get("parallel", 0)

    tilt = state.get("tilt", 0)
    azimuth = state.get("azimuth", 180)

    system_cost = state.get("system_cost", 0)
    subsidy = state.get("subsidy_amount", 0)
    net_cost = state.get("net_system_cost", 0)

    annual_savings = state.get("annual_savings", 0)
    payback = state.get("breakeven_years", 0)
    lifetime_savings = state.get("lifetime_savings", 0)

    goal = state.get("installation_goal", "Full Offset")

    proposal_date = datetime.now().strftime("%B %d, %Y")

    # Environmental calculations
    emission_factor = 0.82
    avoided_co2 = round((annual_kwh * emission_factor) / 1000, 2)
    trees = round((annual_kwh * emission_factor) / 21)

    # ------------------------------------------------
    # Title Page
    # ------------------------------------------------

    elements.append(Paragraph("SOLAR ROOFTOP SYSTEM PROPOSAL", title_style))

    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"<b>Prepared for:</b> {name}", text_style))
    elements.append(Paragraph(f"<b>Location:</b> {city}", text_style))
    elements.append(Paragraph(f"<b>Date:</b> {proposal_date}", text_style))
    elements.append(Paragraph(f"<b>Project Type:</b> {goal}", text_style))

    elements.append(Spacer(1, 25))

    # ------------------------------------------------
    # Executive Summary
    # ------------------------------------------------

    elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))

    elements.append(Paragraph(
        f"This proposal outlines a solar photovoltaic system designed "
        f"to meet the electricity needs of {name} located in {city}. "
        f"The proposed system will generate approximately "
        f"<b>{annual_kwh:,.0f} kWh of clean electricity annually</b>, "
        f"reducing electricity bills while contributing to environmental sustainability.",
        text_style
    ))

    # ------------------------------------------------
    # Customer Energy Profile
    # ------------------------------------------------

    elements.append(Paragraph("CUSTOMER ENERGY PROFILE", heading_style))

    energy_table = Table([
        ["Monthly Electricity Consumption", f"{monthly_units:,.0f} kWh"],
        ["Annual Electricity Consumption", f"{annual_consumption:,.0f} kWh"],
        ["Roof Tilt Angle", f"{tilt} degrees"],
        ["Roof Azimuth Direction", f"{azimuth} degrees"]
    ])

    energy_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.whitesmoke)
    ]))

    elements.append(energy_table)

    # ------------------------------------------------
    # Proposed Solar System
    # ------------------------------------------------

    elements.append(Paragraph("PROPOSED SOLAR SYSTEM DESIGN", heading_style))

    system_table = Table([
        ["System Capacity", f"{system_kw:.2f} kW"],
        ["Estimated Annual Generation", f"{annual_kwh:,.0f} kWh"],
        ["Panel Model", panel_name],
        ["Number of Panels", panel_count],
        ["Array Layout", f"{series} in series × {parallel} strings"],
        ["Inverter", f"{inverter_name} ({inverter_kw:.1f} kW)"],
        ["Battery Storage", f"{battery_name} ({battery_kwh} kWh)"]
    ])

    system_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.whitesmoke)
    ]))

    elements.append(system_table)

    # ------------------------------------------------
    # Environmental Impact
    # ------------------------------------------------

    elements.append(Paragraph("ENVIRONMENTAL IMPACT", heading_style))

    elements.append(Paragraph(
        f"The proposed solar system will avoid approximately "
        f"<b>{avoided_co2} tonnes of carbon emissions annually</b>. "
        f"This is equivalent to planting about <b>{trees} trees</b> every year. "
        f"Over 25 years, the system will significantly reduce dependence "
        f"on fossil fuels and support a cleaner energy future.",
        text_style
    ))

    # ------------------------------------------------
    # Financial Analysis
    # ------------------------------------------------
    elements.append(PageBreak())
    elements.append(Paragraph("FINANCIAL ANALYSIS", heading_style))

    financial_table = Table([
        ["Total System Cost", f"Rs {system_cost:,.0f}"],
        ["Government Subsidy", f"Rs {subsidy:,.0f}"],
        ["Net Investment", f"Rs {net_cost:,.0f}"],
        ["Annual Electricity Savings", f"Rs {annual_savings:,.0f}"],
        ["Payback Period", f"{payback:.1f} years"],
        ["25-Year Lifetime Savings", f"Rs {lifetime_savings:,.0f}"]
    ])

    financial_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.whitesmoke)
    ]))

    elements.append(financial_table)

    # ------------------------------------------------
    # Break-even Chart
    # ------------------------------------------------

    if state.get("breakeven_chart"):

        elements.append(Paragraph("BREAK-EVEN ANALYSIS", heading_style))

        chart_bytes = generate_breakeven_chart_image(
            state.get("net_system_cost"),
            state.get("monthly_units") * 12 * 7
        )

        chart_image = Image(chart_bytes, width=6*inch, height=3*inch)

        # chart_bytes = BytesIO()

        # pio.write_image(
        #     state["breakeven_chart"],
        #     chart_bytes,
        #     format="png",
        #     width=700,
        #     height=400
        # )

        # chart_bytes.seek(0)

        # chart_img = Image(chart_bytes, width=6*inch, height=3*inch)

        elements.append(chart_image)
        elements.append(Spacer(1, 20))

    # ------------------------------------------------
    # System Benefits
    # ------------------------------------------------

    elements.append(Paragraph("SYSTEM BENEFITS", heading_style))

    benefits = [
        "Reduce electricity bills significantly",
        "Energy independence from rising grid tariffs",
        "Government subsidy support under PM Surya Ghar scheme",
        "Low maintenance solar technology",
        "Increase property value",
        "Clean renewable energy generation"
    ]

    for b in benefits:
        elements.append(Paragraph(f"• {b}", text_style))

    # ------------------------------------------------
    # Next Steps
    # ------------------------------------------------

    elements.append(Paragraph("NEXT STEPS", heading_style))

    steps = [
        "Review the proposal",
        "Schedule a site inspection",
        "Finalize system design",
        "Apply for government subsidy",
        "Installation and commissioning"
    ]

    for i, step in enumerate(steps, 1):
        elements.append(Paragraph(f"{i}. {step}", text_style))

    # ------------------------------------------------
    # Build PDF
    # ------------------------------------------------

    doc.build(
        elements,
        onFirstPage=header_footer,
        onLaterPages=header_footer
    )

    buffer.seek(0)

    return buffer