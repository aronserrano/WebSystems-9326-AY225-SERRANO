"""
GeeksforGeeks Academic Scraper Web Application
Flask interface for scraping and PDF generation
"""

from flask import Flask, render_template, request, jsonify, send_file
from scraper import GeeksforGeeksScraper
from pdf_generator import PDFGenerator
import os
from datetime import datetime

app = Flask(__name__)

# Initialize components
scraper = GeeksforGeeksScraper()
pdf_gen = PDFGenerator()
articles_data = []


@app.route('/')
def index():
    """Home page"""
    global articles_data
    articles_data = scraper.load_data()
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    return render_template('index.html', 
                         articles=articles_data,
                         current_date=current_date,
                         pdfs=pdf_gen.get_pdf_list())


@app.route('/scrape', methods=['POST'])
def scrape():
    """Scrape new articles"""
    global articles_data
    
    try:
        data = request.get_json() or {}
        count = data.get('count', 10)
        
        scraper.clear_data()
        articles = scraper.scrape_multiple(count)
        
        if articles:
            scraper.save_data()
            articles_data = articles
            return jsonify({
                'success': True,
                'message': f'Scraped {len(articles)} articles',
                'count': len(articles)
            })
        
        return jsonify({'success': False, 'message': 'No articles scraped'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """Generate PDF from scraped data"""
    try:
        if not articles_data:
            return jsonify({'success': False, 'message': 'No data available'})
        
        pdf_path = pdf_gen.generate_pdf(articles_data)
        
        if pdf_path and os.path.exists(pdf_path):
            return jsonify({
                'success': True,
                'message': 'PDF generated successfully',
                'pdf_name': os.path.basename(pdf_path)
            })
        
        return jsonify({'success': False, 'message': 'PDF generation failed'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/download/<filename>')
def download_pdf(filename):
    """Download generated PDF"""
    try:
        filepath = os.path.join(pdf_gen.output_dir, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/filter')
def filter_articles():
    """Filter articles"""
    search = request.args.get('search', '').lower()
    difficulty = request.args.get('difficulty', '').lower()
    
    filtered = articles_data
    
    if search:
        filtered = [a for a in filtered if search in a.get('title', '').lower()]
    
    if difficulty and difficulty != 'all':
        filtered = [a for a in filtered if difficulty in a.get('difficulty', '').lower()]
    
    return jsonify(filtered)


@app.route('/stats')
def get_stats():
    """Get statistics"""
    if not articles_data:
        return jsonify({'total': 0, 'difficulties': {}, 'pdfs': 0})
    
    difficulties = {'Easy': 0, 'Medium': 0, 'Hard': 0, 'Not Available': 0}
    for a in articles_data:
        d = a.get('difficulty', 'Not Available')
        if d in difficulties:
            difficulties[d] += 1
        else:
            difficulties['Not Available'] += 1
    
    return jsonify({
        'total': len(articles_data),
        'difficulties': difficulties,
        'pdfs': len(pdf_gen.get_pdf_list())
    })


@app.route('/reset', methods=['POST'])
def reset_data():
    """Reset all data"""
    global articles_data
    
    try:
        articles_data = []
        json_path = os.path.join('data', 'scraped_data.json')
        if os.path.exists(json_path):
            os.remove(json_path)
        return jsonify({'success': True, 'message': 'Data reset successful'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)