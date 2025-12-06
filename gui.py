"""
Project Gutenberg Word Frequency Analyzer
A web application that searches and analyzes word frequencies in Project Gutenberg books.
Stores results in a local SQLite database for quick retrieval.

Author: Shriyash Ghimire
Date: December 3, 2025
"""

import sqlite3
import requests
from collections import Counter
import re
from flask import Flask, render_template_string, request, jsonify, render_template

app = Flask(__name__)

# Set of common words to filter out (stop words)
STOP_WORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
    'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
    'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
    'take', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see',
    'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
    'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
    'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
    'give', 'day', 'most', 'us', 'is', 'was', 'are', 'been', 'has', 'had',
    'were', 'said', 'did', 'having', 'may', 'should', 'am', 'being', 'much',
    'more', 'very', 'such', 'here', 'where', 'why', 'upon', 'through', 'shall'
}

def init_database():
    """
    Initialize the SQLite database with the required schema.
    Creates a table for storing book titles and word frequencies.
    """
    conn = sqlite3.connect('gutenberg_books.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            url TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS word_frequencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            word TEXT NOT NULL,
            frequency INTEGER NOT NULL,
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    ''')

    conn.commit()
    conn.close()

def search_local_database(title):
    """
    Search for a book title in the local database.

    Args:
        title (str): The book title to search for

    Returns:
        tuple: (actual_title, word_list) or (None, None) if not found
    """
    try:
        conn = sqlite3.connect('gutenberg_books.db')
        cursor = conn.cursor()

        # Search for the book title (case-insensitive)
        cursor.execute('''
            SELECT id, title FROM books WHERE LOWER(title) = LOWER(?)
        ''', (title,))

        result = cursor.fetchone()

        if result:
            book_id = result[0]
            actual_title = result[1]

            # Get the top 10 most frequent words
            cursor.execute('''
                SELECT word, frequency FROM word_frequencies
                WHERE book_id = ?
                ORDER BY frequency DESC
                LIMIT 10
            ''', (book_id,))

            words = cursor.fetchall()
            conn.close()
            return actual_title, words

        conn.close()
        return None, None

    except Exception as e:
        print(f"Database error: {e}")
        return None, None

def extract_title_from_text(text):
    """
    Extract the book title from Project Gutenberg text.
    Removes everything after semicolon and cleans up prefixes.

    Args:
        text (str): The full text of the book

    Returns:
        str: The extracted title or "Unknown Title"
    """
    lines = text.split('\n')
    for i, line in enumerate(lines[:50]):  # Check first 50 lines
        if 'Title:' in line:
            title = line.split('Title:')[1].strip()

            # Remove everything after semicolon
            if ';' in title:
                title = title.split(';')[0].strip()

            # Remove common prefixes
            prefixes_to_remove = [
                'The Project Gutenberg eBook of ',
                'The Project Gutenberg EBook of ',
                'Project Gutenberg eBook of ',
                'Project Gutenberg EBook of ',
                'The Project Gutenberg ',
                'Project Gutenberg '
            ]

            for prefix in prefixes_to_remove:
                if title.startswith(prefix):
                    title = title[len(prefix):].strip()
                    break

            return title
    return "Unknown Title"

def analyze_text(text):
    """
    Analyze text and return the top 10 most frequent words.
    Filters out stop words and non-alphabetic characters.

    Args:
        text (str): The text to analyze

    Returns:
        list: List of tuples containing (word, frequency)
    """
    # Convert to lowercase and extract words
    words = re.findall(r'\b[a-z]+\b', text.lower())

    # Filter out stop words and short words
    filtered_words = [word for word in words
                     if word not in STOP_WORDS and len(word) > 2]

    # Count word frequencies
    word_counts = Counter(filtered_words)

    # Return top 10 most common words
    return word_counts.most_common(10)

def scrape_gutenberg_book(url):
    """
    Scrape a book from Project Gutenberg and analyze word frequencies.

    Args:
        url (str): The URL of the book on Project Gutenberg

    Returns:
        tuple: (title, word_frequency_list) or (None, None) if failed
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        text = response.text
        title = extract_title_from_text(text)

        # Analyze the text
        word_frequencies = analyze_text(text)

        return title, word_frequencies

    except requests.exceptions.RequestException as e:
        print(f"Error scraping URL: {e}")
        return None, None

def save_to_database(title, url, word_frequencies):
    """
    Save book information and word frequencies to the database.

    Args:
        title (str): The book title
        url (str): The URL of the book
        word_frequencies (list): List of (word, frequency) tuples
    """
    try:
        conn = sqlite3.connect('gutenberg_books.db')
        cursor = conn.cursor()

        # Insert or ignore the book
        cursor.execute('''
            INSERT OR IGNORE INTO books (title, url) VALUES (?, ?)
        ''', (title, url))

        # Get the book_id
        cursor.execute('SELECT id FROM books WHERE title = ?', (title,))
        book_id = cursor.fetchone()[0]

        # Delete old word frequencies for this book
        cursor.execute('DELETE FROM word_frequencies WHERE book_id = ?', (book_id,))

        # Insert new word frequencies
        for word, frequency in word_frequencies:
            cursor.execute('''
                INSERT INTO word_frequencies (book_id, word, frequency)
                VALUES (?, ?, ?)
            ''', (book_id, word, frequency))

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error saving to database: {e}")


@app.route('/')
def index():
    """Render the main page."""
    return render_template('gutenberg.html')

@app.route('/search_title', methods=['POST'])
def search_title():
    """
    API endpoint to search for a book by title in the local database.

    Returns:
        JSON response with book information or error message
    """
    try:
        data = request.get_json()
        title = data.get('title', '')

        actual_title, words = search_local_database(title)

        if actual_title and words:
            return jsonify({
                'found': True,
                'title': actual_title,
                'words': words
            })
        else:
            return jsonify({'found': False})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search_url', methods=['POST'])
def search_url():
    """
    API endpoint to scrape a book from Project Gutenberg and store it.

    Returns:
        JSON response with analysis results or error message
    """
    try:
        data = request.get_json()
        url = data.get('url', '')

        if not url:
            return jsonify({'success': False, 'message': 'No URL provided'})

        # Scrape and analyze the book
        title, word_frequencies = scrape_gutenberg_book(url)

        if title and word_frequencies:
            # Save to database
            save_to_database(title, url, word_frequencies)

            return jsonify({
                'success': True,
                'title': title,
                'words': word_frequencies
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Book was not found or could not be analyzed'
            })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_database()

    # Run the Flask application
    app.run(debug=True, port=5000)