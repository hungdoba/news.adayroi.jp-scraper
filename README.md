# News Scraper for hungba.net

A Python-based news scraping and processing pipeline that fetches articles from some news resource in the internet, groups them, translates content, and deploys to a Next.js website.

## Features

- 🔍 **News Scraping**: Fetches articles from various news sources on the internet
- 🤖 **AI Grouping**: Groups related articles using Gemini AI
- 📝 **Content Processing**: Converts HTML to Markdown format
- 🌐 **Translation**: Translates articles using AI
- 🖼️ **Image Processing**: Downloads and processes article images
- 🚀 **Auto Deployment**: Deploys to Next.js website

## Project Structure

```
news.hungba.net-scraper/
├── run.py                      # Main launcher script (run this!)
├── src/
│   ├── main.py                 # Main application logic
│   ├── pipeline.py             # Pipeline orchestrator
│   ├── config.py               # Configuration management
│   ├── logging_config.py       # Logging setup
│   ├── exceptions.py           # Custom exceptions
│   ├── core/                   # Core business logic
│   │   ├── scraper.py         # Web scraping functionality
│   │   ├── gemini.py          # AI processing (grouping, translation)
│   │   ├── image.py           # Image processing utilities
│   │   └── deploy.py          # Deployment logic
│   ├── models/                 # Data models
│   │   └── new_feed.py        # NewsFeed data model
│   └── utils/                  # Utility functions
│       ├── file.py            # File operations
│       ├── html.py            # HTML processing
│       ├── log.py             # Logging utilities
│       └── execute.py         # Command execution
├── data/                       # Data processing pipeline folders
│   ├── 1.raw_html/            # Raw scraped HTML
│   ├── 2.groups/              # Grouped articles JSON
│   ├── 3.merged/              # Merged HTML files
│   ├── 4.markdown/            # Converted markdown
│   ├── 5.translated/          # Translated content
│   └── 6.images/              # Downloaded images
├── logs/                       # Application logs
├── .env                        # Environment variables (create from .env.example)
├── .env.example                # Environment variables template
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
├── processed_ids.txt          # Processed article IDs log
└── README.md                  # This file
```

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd news.hungba.net-scraper
   ```

2. **Create virtual environment**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Configuration

Key environment variables in `.env`:

- `FEED_URL`: News search URL
- `NEWS_FEED_SELECTOR`: CSS selector for news items
- `GOOGLE_API_KEY`: Google Gemini API key
- `NEXTJS_DIR`: Path to Next.js deployment directory
- `OBSIDIAN_PATH`: Path to Obsidian executable

## Usage

### Run Complete Pipeline

By default, the pipeline **skips opening Obsidian** for automated workflows:

```bash
python run.py
```

### Run Pipeline With Obsidian

If you want to review content in Obsidian before deployment:

```bash
python run.py --use-obsidian
```

### Run Individual Steps

```bash
# Run specific pipeline steps
python run.py --step scrape      # Scrape news feed
python run.py --step group       # Group articles with AI
python run.py --step merge       # Merge related articles
python run.py --step convert     # Convert to Markdown
python run.py --step translate   # Translate content
python run.py --step images      # Download images
python run.py --step clean       # Clean data directories
```

### View Help

```bash
python run.py --help
```

### Set Log Level

```bash
python run.py --log-level DEBUG
```

## Pipeline Steps

1. **Scrape News Feed**: Fetches new articles from News
2. **Group Articles**: Uses AI to group related articles
3. **Merge Articles**: Combines related articles into single files
4. **Convert to Markdown**: Converts HTML to Markdown format
5. **Translate Content**: Translates articles to target language
6. **Download Images**: Fetches and processes article images
7. **Open Obsidian**: Opens content in Obsidian for review
8. **Copy to Next.js**: Moves content to Next.js project
9. **Deploy**: Builds and deploys the website

## Dependencies

- `beautifulsoup4`: HTML parsing
- `markitdown`: HTML to Markdown conversion
- `requests`: HTTP requests
- `python-dotenv`: Environment variable management
- `google-genai`: Google Gemini API for AI processing
- `Pillow`: Image processing

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
