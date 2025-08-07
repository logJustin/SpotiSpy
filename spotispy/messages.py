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

# Butler greetings - randomized daily messages
BUTLER_GREETINGS = [
    "🎩 Good morning, sir. Your musical affairs from yesterday, served fresh:",
    "🍵 *adjusts white gloves* Your daily musical digest has arrived, sir:",
    "🎭 *bows gracefully* Allow me to present yesterday's sonic selections:",
    "🕰️ Right on schedule, sir. Your listening report, prepared to perfection:",
    "🎼 *polishes monocle* The musical chronicles of your yesterday, sir:",
    "🚪 *knocks politely* Your daily wrapped is ready for your review, sir:",
    "🧐 *straightens tie* I've tallied your musical endeavors, sir. The results:",
    "🎪 *tips hat* Your sonic adventures from yesterday, curated with care:",
    "☕ *serves report on silver platter* Today's musical intelligence, sir:",
    "🎯 *clears throat professionally* The daily music briefing, sir. As requested:"
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


def format_basic_daily_summary(analysis_results):
    """
    Format the current-style daily summary message
    
    Args:
        analysis_results: Dictionary from analyze_listening_day()
        
    Returns:
        String with formatted message
    """
    message_parts = []
    
    # Top songs
    if analysis_results['top_songs']:
        top_songs_msg = format_top_items(analysis_results['top_songs'], 'songs', 'listens')
        message_parts.append(top_songs_msg)
    
    # Top albums  
    if analysis_results['top_albums']:
        top_albums_msg = format_top_items(analysis_results['top_albums'], 'albums', 'listens')
        message_parts.append(top_albums_msg)
    
    # Top artists
    if analysis_results['top_artists']:
        top_artists_msg = format_top_items(analysis_results['top_artists'], 'artists', 'songs')
        message_parts.append(top_artists_msg)
    
    # Most popular song
    if analysis_results['most_popular']:
        song = analysis_results['most_popular']
        popular_msg = f'The most popular song you listened to yesterday was *{song["song"]}* by *{song["artist"]}* with a popularity score of {song["song_popularity"]}.'
        message_parts.append(popular_msg)
    
    # Peak listening hour
    if analysis_results['peak_hour']:
        hour = analysis_results['peak_hour']
        minutes = int(analysis_results['peak_minutes'])
        hours_display, mins_display = divmod(minutes, 60)
        peak_msg = f'Yesterday, the hour you listened to most music was at {hour} with a listen time of {hours_display:02d}:{mins_display:02d}'
        message_parts.append(peak_msg)
    
    # Total listening time
    if analysis_results['total_time_formatted']:
        total_msg = f'You listened to {analysis_results["total_time_formatted"]} of music today across {analysis_results["total_songs"]} songs!'
        message_parts.append(total_msg)
    
    return "\n\n".join(message_parts)


def format_enhanced_daily_summary(analysis_results):
    """
    Format an enhanced daily summary optimized for iPhone 15
    
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
    overview = f"📊 LISTENING\n"
    overview += f"🎧 {formatted_time}\n"
    overview += f"🎵 {analysis_results['total_songs']} songs"
    message_parts.append(overview)
    
    # Mood & Energy (if available) - shorter progress bars for mobile
    if analysis_results['energy_level'] > 0 or analysis_results['mood_level'] > 0:
        energy_bar = create_progress_bar(analysis_results['energy_level'], max_width=8)
        mood_bar = create_progress_bar(analysis_results['mood_level'], max_width=8)
        
        vibe_section = f"🌟 VIBE CHECK\n"
        vibe_section += f"⚡ {energy_bar} {analysis_results['energy_level']}%\n"
        vibe_section += f"😊 {mood_bar} {analysis_results['mood_level']}%"
        message_parts.append(vibe_section)
    
    # Top Hits (mobile-optimized format)
    if analysis_results['top_songs']:
        top_songs = sorted(analysis_results['top_songs'].items(), key=lambda x: x[1], reverse=True)[:3]
        
        hits_section = "🏆 TOP HITS\n"
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (song, count) in enumerate(top_songs):
            medal = medals[i] if i < 3 else f"{i+1}."
            # Let Slack handle long song names naturally
            hits_section += f"{medal} {song} ({count}x)\n"
        
        message_parts.append(hits_section.rstrip())
    
    # Peak Activity - let Slack handle text wrapping
    if analysis_results['peak_hour'] and analysis_results['most_popular']:
        peak_section = f"⚡ PEAK HOUR\n"
        
        # Peak hour - with decimal format
        peak_time = format_minutes_decimal(analysis_results['peak_minutes'])
        peak_section += f"🕒 {analysis_results['peak_hour']} ({peak_time})\n"
        
        # Most popular - with artist and no "popularity" text
        song = analysis_results['most_popular']
        peak_section += f"🎯 Most popular: {song['song']} by {song['artist']} ({song['song_popularity']}%)"
        
        message_parts.append(peak_section)
    
    return "\n\n".join(message_parts)


def send_daily_analysis(analysis_results, use_enhanced_format=False):
    """
    Send the daily analysis to Slack
    
    Args:
        analysis_results: Dictionary from analyze_listening_day()
        use_enhanced_format: Boolean - use enhanced or basic format
        
    Returns:
        Boolean indicating success
    """
    logger = get_logger()
    
    try:
        if use_enhanced_format:
            message = format_enhanced_daily_summary(analysis_results)
        else:
            message = format_basic_daily_summary(analysis_results)
        
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
    
    # Test both formats
    basic_msg = format_basic_daily_summary(sample_results)
    enhanced_msg = format_enhanced_daily_summary(sample_results)
    
    logger.info("Basic format length: %s characters", len(basic_msg))
    logger.info("Enhanced format length: %s characters", len(enhanced_msg))
    
    print("ENHANCED FORMAT:")
    print(enhanced_msg)