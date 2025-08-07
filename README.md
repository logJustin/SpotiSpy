# 🎮 SpotiSpy - Your Digital Music Archivist 🤖

SpotiSpy is your sophisticated music tracking companion that delivers personalized daily "Spotify Wrapped" reports with a Ready Player One inspired digital archivist personality. Get beautiful, mobile-optimized summaries of your listening habits delivered fresh to Slack every morning.

## ✨ Features

### 🎭 **Digital Archivist Daily Reports**
- **10 randomized OASIS-inspired greetings** - Your personal digital music curator with Ready Player One flair
- **iPhone 15 optimized formatting** - Perfect for mobile viewing
- **Enhanced visual elements** - Progress bars, emojis, and clean layout

### 📊 **Rich Music Analytics**
- **Smart time formatting** - Shows "4.5 hours" for long sessions, "45 minutes" for shorter ones  
- **Top hits tracking** - Your most-played songs, artists, and albums with medal rankings 🥇🥈🥉
- **Peak activity analysis** - Discover your most musical hour of the day
- **Mood & energy analysis** - Visual progress bars when audio features are available
- **Popular track insights** - See your highest Spotify-rated songs with artist info
- **ASCII Charts** - 2 random visual charts per day showing genre breakdowns, weekly patterns, discovery ratios, and social trends

### 🗓️ **Weekly Summaries** 
- **Sunday weekly wraps** - Comprehensive week-in-review reports
- **Trend analysis** - Compare daily patterns and streaks

## 🚀 Quick Start

### 1. **Clone & Setup**
```bash
git clone <your-repo>
cd SpotiSpy
python3 -m venv spotispyvenv
source spotispyvenv/bin/activate  # On Windows: spotispyvenv\Scripts\activate
pip install -r requirements.txt
```

### 2. **Configure Environment**
Copy `.env.example` to `.env` and fill in your credentials:

```bash
# Spotify API (from https://developer.spotify.com/dashboard/)
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8080/callback

# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Slack Bot (from https://api.slack.com/apps)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
```

### 3. **Run Daily Analysis**
```bash
# Basic format
./analysis.sh

# Daily butler analysis (default format)
python main.py

# Weekly summary only
python main.py --weekly
```

## 📱 Sample Output

Your digital archivist will greet you with messages like:

```
🎮 *materializes from digital archive* Your musical data has been catalogued and indexed, user:

🎵 DAILY WRAPPED 🎵
━━━━━━━━━━━━━━━━━━
📊 LISTENING
🎧 4.5 hours
🎵 82 songs
🏆 TOP HITS
🥇 Blinding Lights by The Weeknd (4x)
🥈 Good 4 U by Olivia Rodrigo (3x)  
🥉 Levitating by Dua Lipa (2x)
⚡ PEAK HOUR
🕒 15:00 (1.4 hours)
🎯 Most popular: Blinding Lights by The Weeknd (87%)

*WEEKLY PATTERN*
══════════════════
Mon: ████░░░░ 2.1h
Tue: ███░░░░░ 1.8h
Wed: ████████ 4.2h ← Today
Thu: ██░░░░░░ 0.9h
Fri: ███████░ 3.7h

*GENRE BREAKDOWN*
══════════════════
Pop          ████░░░░ 50%
Rock         ██░░░░░░ 25%
Indie        ██░░░░░░ 25%
```

## 🏗️ Architecture

### **Clean 5-File System**
```
spotispy/
├── spotify.py      # Spotify API integration
├── database.py     # Supabase data management  
├── analysis.py     # Music analysis & insights
├── messages.py     # Slack formatting & butler personality
└── helpers.py      # Utilities & logging
```

### **Entry Points**
- `main.py` - Daily analysis (replaces old send_analysis.py)
- `weekly.py` - Sunday weekly summaries
- `analysis.sh` - Cronjob script (no changes needed!)

### **Testing**
```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/test_messages.py -v
```

## ⚙️ Setup Details

### **Spotify API Setup**
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Create a new application
3. Add redirect URI: `http://localhost:8080/callback`
4. Copy Client ID and Client Secret to `.env`

### **Supabase Database**
1. Create account at [Supabase](https://supabase.com)
2. Create new project
3. Create `songs` table with your listening data structure
4. Copy URL and anon key to `.env`

### **Slack Integration**
1. Go to [Slack API](https://api.slack.com/apps)
2. Create new app
3. Add bot token scopes: `chat:write`
4. Install app to workspace
5. Copy bot token to `.env`
6. Update `SPOTIFY_CHANNEL_ID` in `spotispy/messages.py`

### **Cronjob (Raspberry Pi)**
Add to crontab for daily 9 AM reports:
```bash
0 9 * * * cd /path/to/SpotiSpy && ./analysis.sh
```

## 🎨 Customization

### **Digital Archivist Personality**
Edit the `BUTLER_GREETINGS` array in `spotispy/messages.py` to add your own OASIS-inspired messages.

### **Message Format**
- `format_daily_summary()` - Mobile-optimized butler format with professional styling

### **Analysis Options**
```bash
python main.py               # Daily archivist analysis (default)
python main.py --weekly      # Weekly summary only  
python main.py --help        # Show all options
```

## 🧪 Development

### **Adding New Features**
1. Write tests first: `tests/test_*.py`
2. Implement in appropriate module: `spotispy/*.py`
3. Run tests: `pytest tests/`
4. Test integration: `python main.py`

### **File Structure Philosophy**
- **Simple**: 5 core files, easy to understand
- **Clean**: No deep nesting or complex imports
- **Testable**: Comprehensive test coverage
- **Mobile-first**: Optimized for iPhone 15 viewing

## 📊 Data Flow

```
Supabase → Database Module → Analysis Module → Messages Module → Slack
    ↑                            ↑                    ↑
Historical Data          Daily Insights      Butler Personality
```

## 🎯 Command Reference

```bash
# Development
python main.py                 # Daily butler analysis
python main.py --weekly        # Weekly summary only
pytest tests/                  # Run all tests
python spotispy/messages.py    # Test message formatting

# Production (Cronjob)
./analysis.sh                  # Your existing cronjob (butler format)
```

## 🤝 Contributing

This is a personal project, but feel free to fork and adapt for your own musical journey! The clean architecture makes it easy to add new features or modify existing ones.

---

*Let your digital music archivist deliver the perfect daily dose of sonic intelligence from the OASIS! 🎮🤖*