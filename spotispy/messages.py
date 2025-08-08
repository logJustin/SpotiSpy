import os
import random
import requests
import base64
from datetime import datetime
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from spotispy.helpers import get_logger

load_dotenv()

# Initialize Slack client
client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
SPOTIFY_CHANNEL_ID = "C063HV2H62V"

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# Cache for Spotify access tokens and genre data
_spotify_token = None
_token_expires_at = 0
_genre_cache = {}

# Ready Player One Character Personas for Daily Summaries
RPO_CHARACTERS = {
    'parzival': {
        'name': 'Parzival',
        'emoji': '🎮',
        'greeting': "*materializes from his stack hideout with DeLorean keys jingling* Yo! Parzival here with your daily sonic quest report. Just like finding the Copper Key, let's decode your musical patterns:",
        'listening_stats_intro': "Alright gunter, let's break down your musical XP gains - and remember, 'the first key is won by those who take risks':",
        'mood_energy_intro': "Your vibe meter readings are looking solid today (better than my dance moves on Planet Doom):",
        'top_hits_intro': "Here's your power playlist - the tracks that dominated your quest like I dominated the Tomb of Horrors:",
        'peak_activity_intro': "Peak gaming... I mean listening sessions detected (hope you weren't distracted by sixers):",
        'charts_intro': "Check out these visual analytics from my custom HUD - cleaner than Aech's workshop diagnostics:",
        'closing': "Keep grinding those beats, fellow gunter! Remember: 'Being human is the only way to live.' 🕹️",
        'giphy_search': 'ready player one parzival'
    },
    'aech': {
        'name': 'Aech',
        'emoji': '🔧',
        'greeting': "*revs up Iron Giant's engine while cranking Rush* What's good, Z! Aech here with today's audio diagnostics. Time to see what your ears have been up to in the real world:",
        'listening_stats_intro': "Time to run the numbers on your sonic performance (hope it's better than your racing stats):",
        'mood_energy_intro': "Your emotional engine specs are running at (and no, I didn't modify these readings):",
        'top_hits_intro': "These tracks were working overtime in your rotation - like me in the workshop:",
        'peak_activity_intro': "Your audio engine hit peak performance during (bet you wish you could race this fast):",
        'charts_intro': "I've been tinkering with these data visualizations while jamming to some old-school tunes:",
        'closing': "Stay tuned for more beats, my friend! And remember: 'Thanks for playing, bro!' 🎧",
        'giphy_search': 'ready player one aech'
    },
    'art3mis': {
        'name': 'Art3mis',
        'emoji': '🎨',
        'greeting': "*materializes in a shower of digital cherry blossoms from Chthonia* Greetings, music lover! Art3mis here - and no, I'm not telling you my real name just yet. Your curated listening intelligence report awaits:",
        'listening_stats_intro': "Let's examine the artistic composition of your day (hopefully more creative than those corporate playlist algorithms):",
        'mood_energy_intro': "Your emotional palette is beautifully balanced (like finding the perfect Jade Key combination):",
        'top_hits_intro': "These masterpieces caught your attention most - almost as captivating as a well-written blog post:",
        'peak_activity_intro': "Your creative peak moments aligned perfectly with (timing as crucial as beating the First Gate):",
        'charts_intro': "I've crafted these elegant data portraits while dodging IOI surveillance:",
        'closing': "Until next time, keep creating beautiful moments with music! And remember: 'I created the OASIS because I never felt at home in the real world.' 🌸",
        'giphy_search': 'ready player one art3mis'
    },
    'halliday': {
        'name': 'Halliday',
        'emoji': '👨‍💻',
        'greeting': "*appears as a flickering hologram in his childhood bedroom* Ah, hello there! James Halliday speaking. I've been analyzing your musical patterns with great interest from the OASIS archives:",
        'listening_stats_intro': "The algorithms have processed your auditory consumption data (much like I processed my love for Kira's mixtapes):",
        'mood_energy_intro': "Your psychological audio resonance frequencies indicate (and I should know - I programmed emotions into NPCs):",
        'top_hits_intro': "These compositions achieved optimal replay coefficients (reminds me of replaying my favorite Atari games):",
        'peak_activity_intro': "Maximum engagement protocols were activated during (peak creativity hours, like when I coded late into the night):",
        'charts_intro': "I've encoded these patterns into visual matrices (Easter eggs hidden in plain sight):",
        'closing': "Remember, music is the ultimate easter egg in the game of life! 'Thank you for playing my game.' 🥚",
        'giphy_search': 'ready player one halliday'
    },
    'sorrento': {
        'name': 'Sorrento',
        'emoji': '💼',
        'greeting': "*adjusts corporate tie while reviewing data on multiple screens* Nolan Sorrento here. I've conducted a comprehensive analysis of your audio consumption metrics using IOI's finest algorithms:",
        'listening_stats_intro': "Let's review your performance indicators (far more interesting than those pathetic gunter attempts at the keys):",
        'mood_energy_intro': "Emotional productivity metrics show (optimized for maximum corporate efficiency):",
        'top_hits_intro': "These assets delivered maximum engagement returns (unlike Parzival's amateur hour performances):",
        'peak_activity_intro': "Optimal output periods occurred during (precision timing that would make our loyalty center analysts proud):",
        'charts_intro': "Corporate analytics division generated these reports using state-of-the-art IOI technology:",
        'closing': "Maintain these efficiency levels for continued growth. 'You see, when I win, I plan to announce new lottery drawings.' 📊",
        'giphy_search': 'ready player one sorrento'
    },
    'ogden': {
        'name': 'Ogden Morrow',
        'emoji': '🧙‍♂️',
        'greeting': "*emerges from his digital sanctuary with a knowing smile, Kira's memory dancing in his eyes* Greetings, young padawan! Ogden Morrow here, and I must say your musical journey today was quite fascinating:",
        'listening_stats_intro': "Wisdom tells us to examine the numbers with care (as Jim and I learned building Gregarious Simulation Systems):",
        'mood_energy_intro': "Your inner harmony resonates at these frequencies (music was always Kira's domain, you know):",
        'top_hits_intro': "These songs spoke to your soul most clearly (she would have loved your taste in music):",
        'peak_activity_intro': "The universe aligned your focus during (timing is everything, as we learned with the OASIS launch):",
        'charts_intro': "Ancient wisdom translated into modern visuals (some secrets are worth preserving):",
        'closing': "Remember, the real treasure is the music we discovered along the way! 'I suppose you could say we were friends.' ✨",
        'giphy_search': 'ready player one ogden morrow'
    }
}


def get_spotify_access_token():
    """
    Get Spotify access token using client credentials flow
    
    Returns:
        String with access token or None if failed
    """
    global _spotify_token, _token_expires_at
    
    # Check if we have a valid cached token
    if _spotify_token and datetime.now().timestamp() < _token_expires_at:
        return _spotify_token
    
    try:
        # Prepare credentials
        client_credentials = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        client_credentials_b64 = base64.b64encode(client_credentials.encode()).decode()
        
        # Request access token
        headers = {
            'Authorization': f'Basic {client_credentials_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {'grant_type': 'client_credentials'}
        
        response = requests.post(
            'https://accounts.spotify.com/api/token',
            headers=headers,
            data=data,
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            _spotify_token = token_data['access_token']
            # Set expiration time (subtract 60 seconds for safety)
            _token_expires_at = datetime.now().timestamp() + token_data['expires_in'] - 60
            return _spotify_token
        else:
            get_logger().warning(f"Failed to get Spotify access token: {response.status_code}")
            return None
            
    except Exception as e:
        get_logger().warning(f"Error getting Spotify access token: {e}")
        return None


def get_artist_genres_by_name(artist_name):
    """
    Get genres for a specific artist from Spotify API using artist name
    
    Args:
        artist_name: Artist name string
        
    Returns:
        List of genre strings or empty list if failed
    """
    # Check cache first
    if artist_name in _genre_cache:
        return _genre_cache[artist_name]
    
    token = get_spotify_access_token()
    if not token:
        return []
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        # Search for artist by name
        search_params = {
            'q': artist_name,
            'type': 'artist',
            'limit': 1
        }
        
        search_response = requests.get(
            'https://api.spotify.com/v1/search',
            headers=headers,
            params=search_params,
            timeout=10
        )
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            artists = search_data.get('artists', {}).get('items', [])
            
            if artists:
                # Get the first (most relevant) artist match
                artist = artists[0]
                genres = artist.get('genres', [])
                
                # Cache the result
                _genre_cache[artist_name] = genres
                return genres
            else:
                get_logger().info(f"No artist found for name: {artist_name}")
                _genre_cache[artist_name] = []  # Cache empty result
                return []
        else:
            get_logger().warning(f"Failed to search for artist {artist_name}: {search_response.status_code}")
            return []
            
    except Exception as e:
        get_logger().warning(f"Error searching for artist {artist_name}: {e}")
        return []




def simplify_genres(genre_list):
    """
    Simplify Spotify's detailed genres into broader categories
    
    Args:
        genre_list: List of genre strings from Spotify
        
    Returns:
        String with simplified genre or 'Other'
    """
    if not genre_list:
        return 'Other'
    
    # Convert to lowercase for easier matching
    genres_lower = [genre.lower() for genre in genre_list]
    
    # Define genre mappings (order matters - more specific first)
    genre_mappings = {
        'pop': ['pop', 'dance pop', 'electropop', 'synthpop', 'indie pop'],
        'rock': ['rock', 'alternative rock', 'indie rock', 'classic rock', 'hard rock', 'punk', 'grunge'],
        'hip-hop': ['hip hop', 'rap', 'trap', 'boom bap', 'conscious hip hop'],
        'electronic': ['electronic', 'house', 'techno', 'dubstep', 'edm', 'ambient', 'downtempo'],
        'r&b': ['r&b', 'soul', 'neo soul', 'contemporary r&b', 'funk'],
        'indie': ['indie', 'indie folk', 'indie rock', 'lo-fi'],
        'country': ['country', 'folk', 'americana', 'bluegrass'],
        'jazz': ['jazz', 'smooth jazz', 'bebop', 'fusion'],
        'classical': ['classical', 'orchestral', 'chamber', 'baroque']
    }
    
    # Try to match genres to categories
    for category, keywords in genre_mappings.items():
        for keyword in keywords:
            if any(keyword in genre for genre in genres_lower):
                return category.title()
    
    # If no match found, return the first genre or 'Other'
    return genre_list[0].title() if genre_list else 'Other'


def get_character_gif(character_name):
    """
    Get a random GIF from Giphy based on character search
    
    Args:
        character_name: Name to search for on Giphy
        
    Returns:
        String with GIF URL or None if failed
    """
    try:
        # Use Giphy's public API (no key required for basic usage)
        search_term = character_name.replace(' ', '+')
        url = f"https://api.giphy.com/v1/gifs/search?api_key=dc6zaTOxFJmzC&q={search_term}&limit=10&rating=pg"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                # Get a random gif from results
                gif = random.choice(data['data'])
                return gif['images']['fixed_width']['url']
    except Exception as e:
        get_logger().warning(f"Failed to fetch GIF for {character_name}: {e}")
    
    return None


def select_daily_character():
    """
    Select a random Ready Player One character for today's summary
    
    Returns:
        Dictionary with character info
    """
    character_key = random.choice(list(RPO_CHARACTERS.keys()))
    character = RPO_CHARACTERS[character_key].copy()
    
    # Try to get a GIF for this character
    gif_url = get_character_gif(character['giphy_search'])
    if gif_url:
        character['gif_url'] = gif_url
    
    return character


def format_time_decimal_hours(time_str):
    """
    Format time as decimal hours if >= 1 hour, otherwise as minutes
    
    Args:
        time_str: Time in format "HH:MM:SS" or "H:MM:SS"
        
    Returns:
        Formatted string like "4.5 hours" or "45 minutes"
    """
    try:
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        
        if hours >= 1:
            decimal_hours = hours + minutes / 60
            return f"{decimal_hours:.1f} hours"
        else:
            return f"{minutes} minutes"
    except (ValueError, IndexError):
        return time_str  # Return original if parsing fails


def format_hour_12h(hour_24h_str):
    """
    Convert 24-hour format (e.g., "15:00") to 12-hour format with AM/PM
    
    Args:
        hour_24h_str: Time in format "HH:00" (e.g., "15:00")
        
    Returns:
        String like "3:00 PM" or "9:00 AM"
    """
    try:
        hour = int(hour_24h_str.split(':')[0])
        if hour == 0:
            return "12:00 AM"
        elif hour < 12:
            return f"{hour}:00 AM"
        elif hour == 12:
            return "12:00 PM"
        else:
            return f"{hour - 12}:00 PM"
    except (ValueError, IndexError):
        return hour_24h_str  # Return original if parsing fails


def format_minutes_decimal(total_minutes):
    """
    Format minutes as decimal hours if >= 60, otherwise as minutes
    
    Args:
        total_minutes: Number of minutes as int or float
        
    Returns:
        Formatted string like "1.3 hours" or "45 minutes"
    """
    try:
        minutes = int(total_minutes)
        if minutes >= 60:
            hours = minutes / 60
            return f"{hours:.1f} hours"
        else:
            return f"{minutes} minutes"
    except (ValueError, TypeError):
        return f"{total_minutes} minutes"


def create_ascii_bar(percentage, max_width=10, filled_char="█", empty_char="░"):
    """
    Create ASCII bar for percentages with custom characters
    
    Args:
        percentage: Value from 0-100
        max_width: Width of bar in characters
        filled_char: Character for filled portions
        empty_char: Character for empty portions
        
    Returns:
        String with filled and empty characters
    """
    # Handle edge cases
    if percentage < 0:
        percentage = 0
    elif percentage > 100:
        percentage = 100
    
    # Calculate filled vs empty portions
    filled_width = int((percentage / 100) * max_width)
    empty_width = max_width - filled_width
    
    # Create bar
    return filled_char * filled_width + empty_char * empty_width


def create_progress_bar(percentage, max_width=10):
    """
    Create ASCII progress bar for percentages
    
    Args:
        percentage: Value from 0-100
        max_width: Width of progress bar in characters
        
    Returns:
        String with filled (█) and empty (░) characters
    """
    # Handle edge cases
    if percentage < 0:
        percentage = 0
    elif percentage > 100:
        percentage = 100
    
    # Calculate filled vs empty portions
    filled_width = int((percentage / 100) * max_width)
    empty_width = max_width - filled_width
    
    # Create progress bar
    return "█" * filled_width + "░" * empty_width


def create_genre_distribution_chart(songs_data):
    """
    Create ASCII chart showing genre distribution using real Spotify API data
    
    Args:
        songs_data: List of song dictionaries with artist name information
        
    Returns:
        String with genre distribution chart or None if no genre data
    """
    if not songs_data:
        return None
    
    genre_counts = {}
    processed_artists = set()  # Track artists we've already processed
    
    # Get genres for each unique artist using artist names
    for song in songs_data:
        artist_name = song.get('artist')
        if not artist_name or artist_name in processed_artists:
            continue
            
        processed_artists.add(artist_name)
        
        # Get artist genres from Spotify API using artist name
        raw_genres = get_artist_genres_by_name(artist_name)
        if raw_genres:
            # Simplify genres into broader categories
            simplified_genre = simplify_genres(raw_genres)
            
            # Count songs by this artist for weighted genre distribution
            artist_song_count = sum(1 for s in songs_data if s.get('artist') == artist_name)
            genre_counts[simplified_genre] = genre_counts.get(simplified_genre, 0) + artist_song_count
    
    if not genre_counts:
        # Fallback to mock data if no API data available
        get_logger().info("Using fallback genre detection based on audio features")
        return create_genre_distribution_fallback(songs_data)
    
    total_songs = sum(genre_counts.values())
    
    # Create chart for top 4 genres
    chart_lines = []
    for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:4]:
        percentage = (count / total_songs) * 100
        bar = create_ascii_bar(percentage, max_width=8)
        chart_lines.append(f"{genre:12} {bar} {percentage:.0f}%")
    
    return "\n".join(chart_lines)


def create_genre_distribution_fallback(songs_data):
    """
    Fallback genre distribution using audio features when API fails
    
    Args:
        songs_data: List of song dictionaries with audio features
        
    Returns:
        String with genre distribution chart based on audio features
    """
    genre_counts = {}
    
    # Use audio features to estimate genres (original logic)
    for song in songs_data:
        energy = song.get('energy', 0.5)
        valence = song.get('valence', 0.5)
        
        if energy > 0.7 and valence > 0.6:
            genre = "Pop"
        elif energy > 0.8 and valence < 0.4:
            genre = "Rock" 
        elif energy < 0.4:
            genre = "Indie"
        elif valence < 0.3:
            genre = "Electronic"
        else:
            genre = "Hip-Hop"
            
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    if not genre_counts:
        return None
    
    total_songs = sum(genre_counts.values())
    
    chart_lines = []
    for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:4]:
        percentage = (count / total_songs) * 100
        bar = create_ascii_bar(percentage, max_width=8)
        chart_lines.append(f"{genre:12} {bar} {percentage:.0f}%")
    
    return "\n".join(chart_lines)


def create_weekly_pattern_chart(current_date=None):
    """
    Create ASCII chart showing weekly listening pattern with today highlighted
    
    Args:
        current_date: Current date (defaults to today)
        
    Returns:
        String with weekly pattern chart
    """
    if current_date is None:
        current_date = datetime.now()
    
    # Generate mock weekly data - in reality this would come from database  
    # Use exactly the same width for all day names for perfect Slack alignment
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    hours = [2.1, 1.8, 4.2, 0.9, 3.7, 2.8, 3.1]  # Mock listening hours
    
    # Today's position (0=Monday, 6=Sunday)
    today_pos = current_date.weekday()
    
    chart_lines = []
    for i, (day, hour) in enumerate(zip(days, hours)):
        # Use the consistent ascii bar function instead of manual construction
        percentage = min((hour / 5.0) * 100, 100)  # Scale to percentage (max 5 hours = 100%)
        bar = create_ascii_bar(percentage, max_width=8)
        
        # Explicitly pad all day names to 3 characters with spaces for Slack alignment
        padded_day = (day + "   ")[:3]  # Ensure exactly 3 characters
        
        if i == today_pos:
            chart_lines.append(f"{padded_day}:  {bar} {hour:.1f}h ← Today")
        else:
            chart_lines.append(f"{padded_day}:  {bar} {hour:.1f}h")
    
    return "\n".join(chart_lines)


def create_new_vs_familiar_chart(songs_data):
    """
    Create ASCII chart showing new vs familiar song ratio
    
    Args:
        songs_data: List of song dictionaries
        
    Returns:
        String with new vs familiar chart or None if no data
    """
    if not songs_data:
        return None
    
    # Mock logic - in reality you'd track listening history
    # For now, simulate based on song popularity (higher = more familiar)
    new_songs = 0
    familiar_songs = 0
    
    for song in songs_data:
        popularity = song.get('song_popularity', 50)
        # Assume songs with lower popularity are "newer discoveries"
        if popularity < 60:
            new_songs += 1
        else:
            familiar_songs += 1
    
    total = new_songs + familiar_songs
    if total == 0:
        return None
    
    new_percentage = (new_songs / total) * 100
    familiar_percentage = (familiar_songs / total) * 100
    
    new_bar = create_ascii_bar(new_percentage, max_width=8)
    familiar_bar = create_ascii_bar(familiar_percentage, max_width=8)
    
    chart_lines = []
    chart_lines.append(f"🆕 New:      {new_bar} {new_percentage:.0f}%")
    chart_lines.append(f"🔄 Familiar: {familiar_bar} {familiar_percentage:.0f}%")
    
    return "\n".join(chart_lines)


def create_social_discovery_chart(songs_data):
    """
    Create ASCII chart showing mainstream vs underground music ratio
    
    Args:
        songs_data: List of song dictionaries
        
    Returns:
        String with social discovery chart or None if no data
    """
    if not songs_data:
        return None
    
    mainstream_count = 0
    underground_count = 0
    
    for song in songs_data:
        popularity = song.get('song_popularity', 50)
        # Songs with popularity > 70 are considered mainstream
        if popularity > 70:
            mainstream_count += 1
        else:
            underground_count += 1
    
    total = mainstream_count + underground_count
    if total == 0:
        return None
    
    mainstream_percentage = (mainstream_count / total) * 100
    underground_percentage = (underground_count / total) * 100
    
    mainstream_bar = create_ascii_bar(mainstream_percentage, max_width=8)
    underground_bar = create_ascii_bar(underground_percentage, max_width=8)
    
    chart_lines = []
    chart_lines.append(f"📈 Mainstream: {mainstream_bar} {mainstream_percentage:.0f}%")
    chart_lines.append(f"🔍 Underground: {underground_bar} {underground_percentage:.0f}%")
    
    return "\n".join(chart_lines)


def generate_random_ascii_charts(songs_data, num_charts=2):
    """
    Generate a random selection of ASCII charts
    
    Args:
        songs_data: List of song dictionaries
        num_charts: Number of charts to include (1-2 recommended)
        
    Returns:
        List of tuples (chart_title, chart_content) for valid charts
    """
    available_charts = [
        ("GENRE BREAKDOWN", lambda: create_genre_distribution_chart(songs_data)),
        ("WEEKLY PATTERN", lambda: create_weekly_pattern_chart()),
        ("DISCOVERY RATIO", lambda: create_new_vs_familiar_chart(songs_data)),
        ("SOCIAL DISCOVERY", lambda: create_social_discovery_chart(songs_data))
    ]
    
    # Randomly select charts
    selected_charts = random.sample(available_charts, min(num_charts, len(available_charts)))
    
    valid_charts = []
    for title, chart_func in selected_charts:
        chart_content = chart_func()
        if chart_content:  # Only include charts with valid content
            valid_charts.append((title, chart_content))
    
    return valid_charts


def send_slack_message(message):
    """Send a message to the Spotify Slack channel"""
    logger = get_logger()
    
    try:
        response = client.chat_postMessage(
            channel=SPOTIFY_CHANNEL_ID,
            text=message
        )
        logger.info("Message sent successfully to Slack")
        return response
        
    except SlackApiError as e:
        logger.error("Error sending to Slack: %s", e)
        return None


def format_top_items(items_dict, item_type, verb="listens"):
    """
    Format top songs/artists/albums for display
    
    Args:
        items_dict: Dictionary with item names and play counts
        item_type: 'songs', 'artists', or 'albums' 
        verb: 'listens' or 'songs' depending on item type
        
    Returns:
        Formatted string for the top items section
    """
    if not items_dict:
        return f"No repeated {item_type} from yesterday!"
    
    # Sort by play count and take top 3
    sorted_items = sorted(items_dict.items(), key=lambda x: x[1], reverse=True)[:3]
    
    if len(sorted_items) == 1:
        header = f"*Your top {item_type[:-1]} from yesterday!*\n"
    else:
        header = f"*Your top {len(sorted_items)} {item_type} from yesterday!*\n"
    
    lines = []
    for item, count in sorted_items:
        lines.append(f"{count} {verb}: {item}")
    
    return header + "\n".join(lines)




def format_daily_summary(analysis_results, songs_data=None):
    """
    Format daily summary with Ready Player One character commentary and visuals
    
    Args:
        analysis_results: Dictionary from analyze_listening_day()
        songs_data: Raw list of songs for ASCII chart generation (optional)
        
    Returns:
        String with character-driven enhanced formatted message with ASCII charts and GIFs
    """
    message_parts = []
    
    # Select today's Ready Player One character
    character = select_daily_character()
    
    # Character greeting with optional GIF
    greeting_section = f"{character['emoji']} **{character['name']}**\n{character['greeting']}"
    if 'gif_url' in character:
        greeting_section += f"\n{character['gif_url']}"
    message_parts.append(greeting_section)
    
    # Listening Stats with character commentary
    formatted_time = format_time_decimal_hours(analysis_results['total_time'])
    overview = f"*LISTENING STATS*\n{character['listening_stats_intro']}\n"    
    overview += f"🎧 {formatted_time}\n"
    overview += f"🎵 {analysis_results['total_songs']} songs"
    
    # Add character-specific commentary based on listening time
    total_minutes = sum(int(part) * mult for part, mult in zip(analysis_results['total_time'].split(':'), [60, 1, 1/60]))
    if total_minutes > 240:  # 4+ hours
        if character['name'] == 'Parzival':
            overview += f"\n💪 Whoa! That's some serious grinding time, gunter! Reminds me of my marathon sessions hunting for the Copper Key."
        elif character['name'] == 'Aech':
            overview += f"\n🔧 Your audio engine was running hot today! Like the time I modded Iron Giant's sound system."
        elif character['name'] == 'Art3mis':
            overview += f"\n🎨 Such dedication to your artistic pursuits! Even I don't spend that long writing blog posts."
        elif character['name'] == 'Halliday':
            overview += f"\n🧠 Impressive focus duration, most impressive indeed! Reminds me of my longest coding marathons at GSS."
        elif character['name'] == 'Sorrento':
            overview += f"\n📊 Excellent productivity metrics achieved! IOI executives could learn from your dedication."
        else:  # Ogden
            overview += f"\n✨ The force was strong with your listening today! Jim would be proud of such persistence."
    elif total_minutes < 60:  # Less than 1 hour
        if character['name'] == 'Parzival':
            overview += f"\n🎯 Short but sweet session - like a perfect speedrun through the First Gate!"
        elif character['name'] == 'Aech':
            overview += f"\n⚡ Quick tune-up session, I respect that! Sometimes you just need a brief jam between races."
        elif character['name'] == 'Art3mis':
            overview += f"\n🌱 Quality over quantity - like a perfectly crafted haiku or a single perfect blog post."
        elif character['name'] == 'Halliday':
            overview += f"\n🎵 Sometimes the best Easter eggs are hidden in the shortest games."
        elif character['name'] == 'Sorrento':
            overview += f"\n📈 Efficient time management - IOI's time-and-motion studies would approve."
        else:  # Ogden
            overview += f"\n🌱 Sometimes the best treasures come in small packages, as Kira always said!"
    
    message_parts.append(overview)
    
    # Mood & Energy with character commentary
    if analysis_results['energy_level'] > 0 or analysis_results['mood_level'] > 0:
        energy_bar = create_progress_bar(analysis_results['energy_level'], max_width=8)
        mood_bar = create_progress_bar(analysis_results['mood_level'], max_width=8)
        
        vibe_section = f"*MOOD & ENERGY*\n{character['mood_energy_intro']}\n"        
        vibe_section += f"⚡ Energy: {energy_bar} {analysis_results['energy_level']}%\n"
        vibe_section += f"😊 Mood: {mood_bar} {analysis_results['mood_level']}%"
        
        # Character-specific mood commentary
        avg_vibe = (analysis_results['energy_level'] + analysis_results['mood_level']) / 2
        if avg_vibe > 80:
            if character['name'] == 'Parzival':
                vibe_section += f"\n🚀 You're absolutely crushing it today! Like when I nailed the WarGames recreation!"
            elif character['name'] == 'Art3mis':
                vibe_section += f"\n🌟 Your creative energy is radiating! Reminds me of the rush I felt solving the Jade Key."
            elif character['name'] == 'Aech':
                vibe_section += f"\n🎆 Firing on all cylinders! Your mood's running smoother than a perfectly tuned DeLorean."
            elif character['name'] == 'Halliday':
                vibe_section += f"\n✨ Excellent emotional resonance detected! Your happiness algorithms are optimally configured."
            elif character['name'] == 'Sorrento':
                vibe_section += f"\n📈 Outstanding morale metrics! Even our loyalty center analysts would be impressed."
            else:  # Ogden
                vibe_section += f"\n✨ Beautiful harmony achieved! Kira would have loved seeing such joy in music."
        elif avg_vibe < 40:
            if character['name'] == 'Ogden':
                vibe_section += f"\n🫂 Sometimes we need quieter moments to recharge, just like Jim did between coding sessions."
            elif character['name'] == 'Parzival':
                vibe_section += f"\n💭 Looks like a contemplative music day - even gunters need downtime."
            elif character['name'] == 'Art3mis':
                vibe_section += f"\n🌙 Melancholy can fuel the most beautiful art. Some of my best blog posts came from quiet moments."
            else:
                vibe_section += f"\n💭 Looks like a contemplative music day."
        
        message_parts.append(vibe_section)
    
    # Top Hits with character commentary
    if analysis_results['top_songs']:
        top_songs = sorted(analysis_results['top_songs'].items(), key=lambda x: x[1], reverse=True)[:3]
        
        hits_section = f"*TOP HITS*\n{character['top_hits_intro']}\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, (song, count) in enumerate(top_songs):
            medal = medals[i] if i < 3 else f"{i+1}."
            hits_section += f"{medal} {song} ({count}x)\n"
        
        # Character commentary on repeat behavior
        max_plays = max(count for _, count in top_songs)
        if max_plays >= 5:
            if character['name'] == 'Parzival':
                hits_section += f"\n🔁 {max_plays} plays? That track had you in the zone like I was with 'Tempest'!"
            elif character['name'] == 'Sorrento':
                hits_section += f"\n📈 Maximum engagement achieved with {max_plays} replays - better metrics than most IOI products."
            elif character['name'] == 'Aech':
                hits_section += f"\n🎵 {max_plays} replays? That's some serious dedication - like my commitment to Rush!"
            elif character['name'] == 'Art3mis':
                hits_section += f"\n🎯 Clearly found your anthem with {max_plays} plays! Sometimes perfection demands repetition."
            elif character['name'] == 'Halliday':
                hits_section += f"\n🔁 {max_plays} iterations detected - reminds me of debugging the same code segment repeatedly."
            else:  # Ogden
                hits_section += f"\n🎶 {max_plays} plays shows true appreciation - like how Kira would replay her favorite mixtapes."
        
        message_parts.append(hits_section.rstrip())
    
    # Peak Activity with character commentary
    if analysis_results['peak_hour'] and analysis_results['most_popular']:
        peak_section = f"*PEAK ACTIVITY*\n{character['peak_activity_intro']}\n"        
        
        peak_time = format_minutes_decimal(analysis_results['peak_minutes'])
        formatted_peak_hour = format_hour_12h(analysis_results['peak_hour'])
        peak_section += f"🕒 Peak Hour: {formatted_peak_hour} ({peak_time})\n"
        
        song = analysis_results['most_popular']
        peak_section += f"🎯 Most Popular: {song['song']} by {song['artist']} ({song['song_popularity']}%)"
        
        # Character-specific time commentary
        peak_hour_num = int(analysis_results['peak_hour'].split(':')[0])
        if 6 <= peak_hour_num <= 9:
            if character['name'] == 'Parzival':
                peak_section += f"\n🌅 Early morning quest soundtrack activated! Like prepping for a First Gate attempt."
            elif character['name'] == 'Aech':
                peak_section += f"\n☀️ Starting the day right with some tunes! Nothing like morning music while working in the garage."
            elif character['name'] == 'Sorrento':
                peak_section += f"\n📅 Optimal morning productivity window utilized - IOI's efficiency experts would approve."
            else:
                peak_section += f"\n☀️ Starting the day right with some tunes!"
        elif 22 <= peak_hour_num or peak_hour_num <= 2:
            if character['name'] == 'Halliday':
                peak_section += f"\n🌙 Late night coding sessions require proper audio ambiance - some of my best OASIS code came during these hours."
            elif character['name'] == 'Parzival':
                peak_section += f"\n🌃 The night shift brings the best listening sessions! Perfect for late-night gunter research."
            elif character['name'] == 'Art3mis':
                peak_section += f"\n🌙 Midnight inspiration strikes! My best blog posts always came during the witching hour."
            else:
                peak_section += f"\n🌃 The night shift brings the best listening sessions!"
        
        message_parts.append(peak_section)
    
    # ASCII Charts with character commentary
    if songs_data:
        ascii_charts = generate_random_ascii_charts(songs_data, num_charts=2)
        if ascii_charts:
            charts_intro = f"*VISUAL ANALYTICS*\n{character['charts_intro']}"
            message_parts.append(charts_intro)
            
            for chart_title, chart_content in ascii_charts:
                chart_section = f"*{chart_title}*\n{chart_content}"
                message_parts.append(chart_section)
    
    # Character closing message
    closing_section = character['closing']
    message_parts.append(closing_section)
    
    return "\n\n".join(message_parts)


def send_daily_analysis(analysis_results, songs_data=None):
    """
    Send the daily analysis to Slack
    
    Args:
        analysis_results: Dictionary from analyze_listening_day()
        songs_data: Raw list of songs for ASCII chart generation (optional)
        
    Returns:
        Boolean indicating success
    """
    logger = get_logger()
    
    try:
        message = format_daily_summary(analysis_results, songs_data)
        
        if not message.strip():
            logger.warning("No message content generated")
            return False
        
        response = send_slack_message(message)
        return response is not None
        
    except Exception as e:
        logger.error("Error sending daily analysis: %s", e)
        return False


def send_weekly_summary(weekly_data):
    """
    Send weekly summary (placeholder for future implementation)
    
    Args:
        weekly_data: Weekly analysis results
        
    Returns:
        Boolean indicating success
    """
    logger = get_logger()
    logger.info("Weekly summary feature coming soon!")
    
    # Basic weekly message for now
    message = f"🗓️ WEEKLY WRAPPED\n\nWeekly summary coming soon! For now, enjoy your daily updates. 🎵"
    
    response = send_slack_message(message)
    return response is not None


if __name__ == "__main__":
    # Test message formatting
    logger = get_logger()
    logger.info("Testing message formatting...")
    
    # Sample analysis results
    sample_results = {
        'total_songs': 87,
        'total_time': '4:23:15',
        'total_time_formatted': '4 hours, 23 minutes, and 15 seconds',
        'top_songs': {'Blinding Lights by The Weeknd': 4, 'Good 4 U by Olivia Rodrigo': 3},
        'top_artists': {'The Weeknd': 8, 'Arctic Monkeys': 5},
        'top_albums': {},
        'most_popular': {'song': 'Blinding Lights', 'artist': 'The Weeknd', 'song_popularity': 87},
        'peak_hour': '15:00',
        'peak_minutes': 83,
        'energy_level': 75,
        'mood_level': 68
    }
    
    # Test message format
    message = format_daily_summary(sample_results)
    
    logger.info("Message length: %s characters", len(message))
    
    print("DAILY SUMMARY FORMAT:")
    print(message)
