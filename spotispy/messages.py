import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from spotispy.helpers import get_logger

load_dotenv()

# Initialize Slack client
client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
SPOTIFY_CHANNEL_ID = "C063HV2H62V"

# Butler greetings - Ready Player One inspired digital archivist
BUTLER_GREETINGS = [
    "🎮 *materializes from digital archive* Your musical data has been catalogued and indexed, user:",
    "💾 *accessing yesterday's audio logs* Musical analysis complete. Compiling report from the archives:",
    "🖥️ *holographic display activates* Greetings, music aficionado. Your sonic data awaits retrieval:",
    "🤖 *digital butler protocol initiated* Yesterday's musical patterns have been processed and archived:",
    "⚡ *system online* Welcome back to your personal music vault. Daily statistics compiled:",
    "🎧 *adjusting virtual monocle* Ah, another day of exquisite musical taste documented for posterity:",
    "📡 *transmitting from the audio archives* Your daily sonic chronicle is ready for download:",
    "🎵 *emerging from the musical matrix* Greetings, curator of sound. Your data analysis is complete:",
    "🔍 *scanning musical databases* Fascinating listening patterns detected. Report generated:",
    "⭐ *constellation of sound waves appears* Your musical journey through spacetime has been mapped:"
]


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
    Create ASCII chart showing genre distribution
    
    Args:
        songs_data: List of song dictionaries with genre information
        
    Returns:
        String with genre distribution chart or None if no genre data
    """
    if not songs_data:
        return None
    
    # Count genres (mock data for now - would need genre info in real data)
    # This is a placeholder - you'd extract actual genres from Spotify API
    genre_counts = {}
    
    # Simulate genre distribution based on song characteristics
    for song in songs_data:
        # Simple mock logic - in reality you'd use actual genre data
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
    Format daily summary with butler greeting, mobile-optimized styling, and ASCII charts
    
    Args:
        analysis_results: Dictionary from analyze_listening_day()
        songs_data: Raw list of songs for ASCII chart generation (optional)
        
    Returns:
        String with mobile-optimized enhanced formatted message with ASCII charts
    """
    message_parts = []
    
    # Butler greeting - randomized daily message
    butler_greeting = random.choice(BUTLER_GREETINGS)
    message_parts.append(butler_greeting)
    
    # Listening Overview - more compact with decimal hours
    formatted_time = format_time_decimal_hours(analysis_results['total_time'])
    overview = f"*LISTENING STATS*\n"    
    overview += f"🎧 {formatted_time}\n"
    overview += f"🎵 {analysis_results['total_songs']} songs"
    message_parts.append(overview)
    
    # Mood & Energy (if available) - shorter progress bars for mobile
    if analysis_results['energy_level'] > 0 or analysis_results['mood_level'] > 0:
        energy_bar = create_progress_bar(analysis_results['energy_level'], max_width=8)
        mood_bar = create_progress_bar(analysis_results['mood_level'], max_width=8)
        
        vibe_section = f"*MOOD & ENERGY*\n"        
        vibe_section += f"⚡ Energy: {energy_bar} {analysis_results['energy_level']}%\n"
        vibe_section += f"😊 Mood: {mood_bar} {analysis_results['mood_level']}%"
        message_parts.append(vibe_section)
    
    # Top Hits (mobile-optimized format)
    if analysis_results['top_songs']:
        top_songs = sorted(analysis_results['top_songs'].items(), key=lambda x: x[1], reverse=True)[:3]
        
        hits_section = "*TOP HITS*\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, (song, count) in enumerate(top_songs):
            medal = medals[i] if i < 3 else f"{i+1}."
            # Let Slack handle long song names naturally
            hits_section += f"{medal} {song} ({count}x)\n"
        
        message_parts.append(hits_section.rstrip())
    
    # Peak Activity - let Slack handle text wrapping
    if analysis_results['peak_hour'] and analysis_results['most_popular']:
        peak_section = f"*PEAK ACTIVITY*\n"        
        
        # Peak hour - with decimal format
        peak_time = format_minutes_decimal(analysis_results['peak_minutes'])
        peak_section += f"🕒 Peak Hour: {analysis_results['peak_hour']} ({peak_time})\n"
        
        # Most popular - with artist and no "popularity" text
        song = analysis_results['most_popular']
        peak_section += f"🎯 Most Popular: {song['song']} by {song['artist']} ({song['song_popularity']}%)"
        
        message_parts.append(peak_section)
    
    # ASCII Charts - randomly selected visual data insights
    if songs_data:
        ascii_charts = generate_random_ascii_charts(songs_data, num_charts=2)
        for chart_title, chart_content in ascii_charts:
            chart_section = f"*{chart_title}*\n"            
            chart_section += chart_content
            message_parts.append(chart_section)
    
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