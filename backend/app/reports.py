from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm

def make_report(result, outdir):
    outdir=Path(outdir); outdir.mkdir(parents=True,exist_ok=True)
    path=outdir/f"{result['transaction']['id']}_investigation.pdf"
    styles=getSampleStyleSheet()
    doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=15*mm,leftMargin=15*mm,topMargin=15*mm,bottomMargin=15*mm)
    story=[Paragraph("Multi-Agent Fraud Investigation Report",styles["Title"]),
           Spacer(1,8),
           Paragraph(f"<b>Transaction:</b> {result['transaction']['id']} &nbsp; <b>Customer:</b> {result['transaction']['customer_name']}",styles["BodyText"]),
           Paragraph(f"<b>Amount:</b> ₹{result['transaction']['amount']:,.2f} &nbsp; <b>Risk:</b> {result['risk_level']} &nbsp; <b>Confidence:</b> {result['confidence']}%",styles["BodyText"]),
           Spacer(1,10)]
    data=[["Evidence","Severity","Explanation"]]
    for e in result["evidence"]:
        data.append([e["category"],e["severity"],e["explanation"]])
    table=Table(data,colWidths=[38*mm,25*mm,112*mm],repeatRows=1)
    table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightgrey),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story += [Paragraph("Evidence Trail",styles["Heading2"]),table,Spacer(1,10),
              Paragraph(f"<b>Recommendation:</b> {result['recommendation']}",styles["BodyText"]),
              Paragraph("<b>Agent Trace:</b> Transaction Pattern Agent → Customer History Agent → Risk Scoring Agent → Human Analyst",styles["BodyText"])]
    doc.build(story)
    return str(path)
