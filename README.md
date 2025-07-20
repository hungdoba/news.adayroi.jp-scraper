# News Scraper for Adayroi.jp

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
news.adayroi.jp-scraper/
├── src/
│   ├── main.py                 # Main pipeline orchestrator
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
├── .env                        # Environment variables
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
└── processed_ids.txt          # Processed article IDs log
```

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd news.adayroi.jp-scraper
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

```bash
python src/main.py
```

### Run Individual Steps

```python
from src.main import *

# Step 1: Scrape news feed
news_feed = step_1_scrape_news_feed()

# Step 2: Group articles with AI
group_articles = step_2_group_articles(news_feed)

# Step 3: Merge related articles
step_3_merge_articles(group_articles, DIR_STEP_3)

# Continue with other steps...
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
- Google Gemini API for AI processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions, please open an issue on GitHub.
