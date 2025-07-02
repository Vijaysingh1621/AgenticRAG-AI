import sys
sys.path.append('.')

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF
import os

def create_test_pdf():
    """Create a test PDF with text and simple graphics for testing MultiModal RAG"""
    filename = "test_document.pdf"
    
    # Create a simple PDF with text and basic graphics
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Page 1: Company Overview
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "TechCorp Annual Report 2024")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, "Executive Summary:")
    c.drawString(50, height - 120, "• Revenue increased by 25% to $50M")
    c.drawString(50, height - 140, "• Customer base grew to 10,000 active users")
    c.drawString(50, height - 160, "• Launched 3 new AI-powered products")
    c.drawString(50, height - 180, "• Expanded to 5 new markets globally")
    
    # Simple bar chart representation
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 220, "Revenue Growth Chart:")
    
    # Draw simple bars
    c.setFillColor(colors.blue)
    c.rect(50, height - 280, 60, 30, fill=1)  # 2022
    c.rect(120, height - 300, 60, 50, fill=1)  # 2023
    c.rect(190, height - 320, 60, 70, fill=1)  # 2024
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    c.drawString(55, height - 290, "2022")
    c.drawString(55, height - 300, "$30M")
    c.drawString(125, height - 310, "2023")
    c.drawString(125, height - 320, "$40M")
    c.drawString(195, height - 330, "2024")
    c.drawString(195, height - 340, "$50M")
    
    c.showPage()
    
    # Page 2: Technical Specifications
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "AI Platform Technical Details")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, "System Architecture:")
    c.drawString(50, height - 120, "• Microservices architecture with Docker containers")
    c.drawString(50, height - 140, "• FastAPI backend with Python 3.12")
    c.drawString(50, height - 160, "• React frontend with TypeScript")
    c.drawString(50, height - 180, "• ChromaDB vector database for RAG")
    c.drawString(50, height - 200, "• OpenAI Whisper for speech-to-text")
    
    # Draw a simple system diagram
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 240, "System Flow Diagram:")
    
    # Draw boxes for system components
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.lightblue)
    
    # Frontend box
    c.rect(50, height - 300, 80, 30, fill=1)
    c.setFillColor(colors.black)
    c.drawString(60, height - 290, "Frontend")
    c.drawString(65, height - 305, "(React)")
    
    # Backend box
    c.setFillColor(colors.lightgreen)
    c.rect(200, height - 300, 80, 30, fill=1)
    c.setFillColor(colors.black)
    c.drawString(210, height - 290, "Backend")
    c.drawString(215, height - 305, "(FastAPI)")
    
    # Database box
    c.setFillColor(colors.lightyellow)
    c.rect(350, height - 300, 80, 30, fill=1)
    c.setFillColor(colors.black)
    c.drawString(360, height - 290, "Database")
    c.drawString(365, height - 305, "(ChromaDB)")
    
    # Draw arrows
    c.line(130, height - 285, 200, height - 285)  # Frontend to Backend
    c.line(280, height - 285, 350, height - 285)  # Backend to Database
    
    c.showPage()
    
    # Page 3: Performance Metrics
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Performance Metrics & KPIs")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, "Key Performance Indicators:")
    c.drawString(50, height - 120, "• Query Response Time: 1.2 seconds average")
    c.drawString(50, height - 140, "• Voice Recognition Accuracy: 95.8%")
    c.drawString(50, height - 160, "• PDF Processing Speed: 5 pages/second")
    c.drawString(50, height - 180, "• System Uptime: 99.9%")
    c.drawString(50, height - 200, "• User Satisfaction: 4.8/5 stars")
    
    # Performance chart
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 240, "Monthly Active Users:")
    
    # Draw line chart points
    points = [(50, height - 300), (100, height - 280), (150, height - 290), 
              (200, height - 260), (250, height - 250), (300, height - 240)]
    
    # Draw lines between points
    c.setStrokeColor(colors.red)
    c.setLineWidth(2)
    for i in range(len(points) - 1):
        c.line(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
    
    # Draw points
    c.setFillColor(colors.red)
    for point in points:
        c.circle(point[0], point[1], 3, fill=1)
    
    # Add month labels
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    for i, month in enumerate(months):
        c.drawString(45 + i*50, height - 320, month)
    
    c.save()
    print(f"Created test PDF: {filename}")
    return filename

if __name__ == "__main__":
    create_test_pdf()
