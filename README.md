# 📚 NextRead - AI Book Recommendation System

An intelligent ML-powered web application that helps users choose books from their bookshelf using AI vision, mood analysis, and reinforcement learning.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![Supabase](https://img.shields.io/badge/Supabase-Auth%20%2B%20DB-green)

## ✨ Features

- **📸 Book Detection** - Upload a photo of your bookshelf, Gemini Vision AI identifies book titles
- **📖 Multi-Source Metadata** - Fetches from Google Books → Open Library → Gemini AI (fallback)
- **💭 Mood-Based Recommendations** - Describe your mood and get personalized suggestions
- **🎯 Smart Scoring** - Books scored on mood match, genre preference, and popularity
- **🤖 Adaptive Learning** - Q-Learning AI improves with your feedback (persists in cloud!)
- **🔐 Multi-User Auth** - Supabase authentication with per-user data
- **🎨 Dynamic Book Covers** - Auto-generates beautiful SVG covers when real covers unavailable
- **🌙 Dark UI** - Modern glassmorphic design

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [Gemini API Key](https://aistudio.google.com/app/apikey)
- [Supabase Project](https://supabase.com) (free tier works)

### Installation

```bash
# Clone repository
git clone https://github.com/projects08k/NextRead.git
cd NextRead

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('vader_lexicon')"

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Run Locally

```bash
streamlit run app.py
```

App opens at `http://localhost:8501`

## 🔧 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key for vision + text |
| `SUPABASE_URL` | ✅ | Supabase project URL |
| `SUPABASE_ANON_KEY` | ✅ | Supabase anonymous key (public) |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Supabase service role key (for RL persistence) |
| `GOOGLE_BOOKS_API_KEY` | ❌ | Optional (Open Library fallback) |

> ⚠️ **Security**: Never expose `SUPABASE_SERVICE_ROLE_KEY` in frontend code. It's only used server-side for RL model updates.

## 🏗️ Project Structure

```
NextRead/
├── app.py                    # Main Streamlit app
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
├── supabase_schema.sql      # Database schema
│
├── src/
│   ├── auth/                # Supabase authentication
│   ├── database/            # Supabase repository (cloud-only)
│   ├── vision/              # Gemini book detection
│   ├── metadata/            # Book metadata (multi-source)
│   ├── sentiment/           # Mood analysis (VADER NLP)
│   ├── recommendation/      # Scoring engine
│   ├── rl/                  # Q-Learning agent (Supabase-backed)
│   └── ui/                  # Streamlit pages & styles
```

## 🚀 Deployment

### HuggingFace Spaces

1. Create new Space → Select **Streamlit** SDK
2. Upload files or connect GitHub
3. Add secrets in **Settings → Variables and secrets**:
   ```
   GEMINI_API_KEY=your_key
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   ```

### Streamlit Cloud

1. Push to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Add secrets in dashboard (Settings → Secrets):
   ```toml
   GEMINI_API_KEY = "your_key"
   SUPABASE_URL = "https://xxx.supabase.co"
   SUPABASE_ANON_KEY = "your_anon_key"
   SUPABASE_SERVICE_ROLE_KEY = "your_service_role_key"
   ```

## 📋 Supabase Setup

Run `supabase_schema.sql` in your Supabase SQL Editor to create:

| Table | Purpose |
|-------|---------|
| `reading_history` | User's accepted book recommendations |
| `feedback` | Accept/reject data for analytics |
| `user_preferences` | Genre preferences per user |
| `rl_model` | Global Q-Learning model (shared learning) |

All tables have Row Level Security (RLS) enabled.

## 🎨 Features Detail

### Mood Categories
😌 Relaxed | 🗺️ Adventurous | 💕 Romantic | 🤔 Thoughtful | 🎉 Excited  
🌧️ Melancholic | 🔍 Curious | 🚀 Escapist | 💪 Motivated | 🧘 Contemplative

### Scoring Weights
| Factor | Weight |
|--------|--------|
| Mood Match | 40% |
| Genre Preference | 25% |
| Reading History | 15% |
| Difficulty | 10% |
| Popularity | 10% |

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

Made with ❤️ for book lovers
