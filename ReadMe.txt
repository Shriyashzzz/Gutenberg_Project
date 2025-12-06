Project Gutenberg Word Frequency Analyzer
A web application that searches and analyzes word frequencies in Project Gutenberg books. The application stores results in a local SQLite database for quick retrieval.
Features

🔍 Search by Title: Query the local database for previously analyzed books
📊 Word Frequency Analysis: Automatically analyzes and displays the top 10 most frequent words
🌐 Web Scraping: Fetches books directly from Project Gutenberg
💾 Local Database: Stores book information and word frequencies using SQLite3
🎨 Modern UI: Clean, responsive web interface built with Flask
🚫 Stop Word Filtering: Automatically filters out common words that don't add meaning

Technologies Used

Python 3.x
Flask - Web framework
SQLite3 - Local database
Requests - Web scraping
HTML/CSS/JavaScript - Frontend interface

Installation

Clone this repository:


cd gutenberg-analyzer

Install required packages:

bashpip install -r requirements.txt

Run the application:

bashpython app.py

Open your browser and navigate to:

http://localhost:5000
Usage
Search by Title

Enter a book title in the "Search by Title" field
Click "Search Database"
If found, the top 10 most frequent words will be displayed

Add New Book

Find a book on Project Gutenberg
Copy the plain text URL (usually ends with .txt)
Paste the URL in the "Add New Book by URL" field
Click "Analyze & Store"
The book will be analyzed and stored in the database

Example URLs

Little Women: https://www.gutenberg.org/cache/epub/37106/pg37106.txt
Pride and Prejudice: https://www.gutenberg.org/cache/epub/1342/pg1342.txt
Alice in Wonderland: https://www.gutenberg.org/cache/epub/11/pg11.txt

Database Schema
Books Table

id (INTEGER PRIMARY KEY)
title (TEXT UNIQUE)
url (TEXT)

Word Frequencies Table

id (INTEGER PRIMARY KEY)
book_id (INTEGER FOREIGN KEY)
word (TEXT)
frequency (INTEGER)

Project Structure
gutenberg-analyzer/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── gutenberg_books.db    # SQLite database (created on first run)
Exception Handling
The application includes comprehensive error handling for:

Database connection errors
Network request failures
Invalid URLs
Missing book titles
Text parsing errors

Stop Words
The application filters out common English words that don't contribute to meaning, including:

Articles (the, a, an)
Pronouns (I, you, he, she, it)
Prepositions (in, on, at, to, from)
Conjunctions (and, or, but)
Common verbs (is, are, was, were, be)

Future Enhancements

User authentication
Book recommendation system
Advanced filtering options
Export results to CSV
Visualization of word frequencies
Support for multiple languages

Author
Shriyash Ghimire
Date :  3 December 2025
License
This project is created for educational purposes as part of a course assignment.