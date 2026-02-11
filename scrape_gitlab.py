import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

PAGES_TO_SCRAPE = {
    "GitLab_Values": "https://handbook.gitlab.com/handbook/values/",
    "GitLab_Communication": "https://handbook.gitlab.com/handbook/communication/",
    "GitLab_Remote_Work": "https://handbook.gitlab.com/handbook/company/culture/all-remote/guide/",
}

def clean_text(text):
    return text.strip().replace('\n', ' ')

def scrape_and_create_pdf(title, url, output_dir="documents"):
    print(f"🌍 Fetching {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Try to find the main content area
    # GitLab handbook typically uses <main> or specific classes
    content = soup.find('main')
    if not content:
        content = soup.find('article')
    if not content:
        content = soup.find('div', class_='content')
    if not content:
        # Fallback: looks for H1 and takes parent
        h1 = soup.find('h1')
        if h1:
            content = h1.parent
        else:
            print(f"⚠️ Could not identify content content for {title}")
            return

    # Prepare PDF generation
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filename = os.path.join(output_dir, f"{title}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title Style
    title_style = styles['Title']
    h1_style = styles['Heading1']
    h2_style = styles['Heading2']
    h3_style = styles['Heading3']
    normal_style = styles['Normal']
    
    # Custom Normal style for better reading
    normal_style.spaceAfter = 12

    story.append(Paragraph(f"Handbook: {title}", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Source: {url}", normal_style))
    story.append(Spacer(1, 24))

    # Extract text content elements
    # logic: iterate over headers and paragraphs
    for element in content.find_all(['h1', 'h2', 'h3', 'p', 'li']):
        text = element.get_text().strip()
        if not text:
            continue
            
        try:
            if element.name == 'h1':
                story.append(Paragraph(text, h1_style))
            elif element.name == 'h2':
                story.append(Paragraph(text, h2_style))
            elif element.name == 'h3':
                story.append(Paragraph(text, h3_style))
            elif element.name == 'li':
                story.append(Paragraph(f"• {text}", normal_style))
            else:
                story.append(Paragraph(text, normal_style))
        except Exception:
            # Skip chars that fail encoding/reportlab rendering
            continue

    doc.build(story)
    print(f"✅ Saved PDF: {filename}")

def main():
    print("🚀 Starting GitLab Handbook Scraper...")
    for title, url in PAGES_TO_SCRAPE.items():
        scrape_and_create_pdf(title, url)
    print("✨ All done!")

if __name__ == "__main__":
    main()
