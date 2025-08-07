import os
import random
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




def format_daily_summary(analysis_results):
    """
    Format daily summary with butler greeting and mobile-optimized styling
    
    Args:
        analysis_results: Dictionary from analyze_listening_day()
        
    Returns:
        String with mobile-optimized enhanced formatted message
    """
    message_parts = []
    
    # Butler greeting - randomized daily message
    butler_greeting = random.choice(BUTLER_GREETINGS)
    message_parts.append(butler_greeting)
    
    # Listening Overview - more compact with decimal hours
    formatted_time = format_time_decimal_hours(analysis_results['total_time'])
    overview = f"*LISTENING STATS*\n"
    overview += f"══════════════════\n"
    overview += f"🎧 {formatted_time}\n"
    overview += f"🎵 {analysis_results['total_songs']} songs"
    message_parts.append(overview)
    
    # Mood & Energy (if available) - shorter progress bars for mobile
    if analysis_results['energy_level'] > 0 or analysis_results['mood_level'] > 0:
        energy_bar = create_progress_bar(analysis_results['energy_level'], max_width=8)
        mood_bar = create_progress_bar(analysis_results['mood_level'], max_width=8)
        
        vibe_section = f"*MOOD & ENERGY*\n"
        vibe_section += f"══════════════════\n"
        vibe_section += f"⚡ Energy: {energy_bar} {analysis_results['energy_level']}%\n"
        vibe_section += f"😊 Mood: {mood_bar} {analysis_results['mood_level']}%"
        message_parts.append(vibe_section)
    
    # Top Hits (mobile-optimized format)
    if analysis_results['top_songs']:
        top_songs = sorted(analysis_results['top_songs'].items(), key=lambda x: x[1], reverse=True)[:3]
        
        hits_section = "*TOP HITS*\n"
        hits_section += "══════════════════\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, (song, count) in enumerate(top_songs):
            medal = medals[i] if i < 3 else f"{i+1}."
            # Let Slack handle long song names naturally
            hits_section += f"{medal} {song} ({count}x)\n"
        
        message_parts.append(hits_section.rstrip())
    
    # Peak Activity - let Slack handle text wrapping
    if analysis_results['peak_hour'] and analysis_results['most_popular']:
        peak_section = f"*PEAK ACTIVITY*\n"
        peak_section += f"══════════════════\n"
        
        # Peak hour - with decimal format
        peak_time = format_minutes_decimal(analysis_results['peak_minutes'])
        peak_section += f"🕒 Peak Hour: {analysis_results['peak_hour']} ({peak_time})\n"
        
        # Most popular - with artist and no "popularity" text
        song = analysis_results['most_popular']
        peak_section += f"🎯 Most Popular: {song['song']} by {song['artist']} ({song['song_popularity']}%)"
        
        message_parts.append(peak_section)
    
    return "\n\n".join(message_parts)


def send_daily_analysis(analysis_results):
    """
    Send the daily analysis to Slack
    
    Args:
        analysis_results: Dictionary from analyze_listening_day()
        
    Returns:
        Boolean indicating success
    """
    logger = get_logger()
    
    try:
        message = format_daily_summary(analysis_results)
        
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