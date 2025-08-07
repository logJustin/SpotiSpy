# 📱 Slack Message Formatting Enhancement Guide

## Current vs. Enhanced Formatting

### Current Format (Basic Text)
```
*Your top 3 songs from yesterday!*
4 listens: Blinding Lights by The Weeknd
3 listens: Good 4 U by Olivia Rodrigo
2 listens: Levitating by Dua Lipa

The most popular song you listened to yesterday was *Blinding Lights* by *The Weekend* with a popularity score of 87.

Yesterday, the hour you listened to most music was at 15:00 with a listen time of 01:23

You listened to 4 hours, 23 minutes, and 15 seconds of music today across 87 songs!
```

### Enhanced Format (Rich Blocks + Visual Elements)
```
🎵 DAILY SPOTIFY WRAPPED 🎵
━━━━━━━━━━━━━━━━━━━━━━━━━

📊 LISTENING OVERVIEW
🎧 4h 23m  |  🎵 87 songs  |  🎤 23 artists

🌟 TODAY'S ENERGY: Uplifting Vibes
Mood: ████████░░ 82% Happy
Energy: ███████░░░ 74% High

🏆 YOUR TOP HITS
🥇 Blinding Lights - The Weeknd (4x)
🥈 Good 4 U - Olivia Rodrigo (3x)  
🥉 Levitating - Dua Lipa (2x)

⚡ PEAK ACTIVITY
🕒 3-4 PM was your power hour (1h 23m)
🎯 Most popular track: Blinding Lights (87% popularity)

💫 DISCOVERY INSIGHTS
🆕 5 new songs discovered today
📅 Average song age: 3.2 years
🎭 Top genre: Pop (45% of listening time)

🔥 STREAK STATUS: 7 days strong! 💪
```

## Slack Block Kit Implementation

### 1. Header Section
```python
def create_header_block():
    return {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": "🎵 Your Daily Spotify Wrapped",
            "emoji": True
        }
    }
```

### 2. Stats Overview Section
```python
def create_stats_section(total_time, song_count, artist_count):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"📊 *LISTENING OVERVIEW*"
        },
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"*🎧 Time:*\n{total_time}"
            },
            {
                "type": "mrkdwn",
                "text": f"*🎵 Songs:*\n{song_count} tracks"
            },
            {
                "type": "mrkdwn",
                "text": f"*🎤 Artists:*\n{artist_count} different"
            },
            {
                "type": "mrkdwn",
                "text": f"*💿 Albums:*\n{album_count} explored"
            }
        ]
    }
```

### 3. Mood/Energy Visualization
```python
def create_mood_section(energy_level, valence_level):
    energy_bar = create_progress_bar(energy_level)
    mood_bar = create_progress_bar(valence_level)
    
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"🌟 *TODAY'S VIBE*\n"
                   f"Energy: {energy_bar} {energy_level}%\n"
                   f"Mood: {mood_bar} {valence_level}% Happy"
        }
    }

def create_progress_bar(percentage, length=10):
    filled = int(percentage / 10)
    empty = length - filled
    return "█" * filled + "░" * empty
```

### 4. Top Tracks with Rich Formatting
```python
def create_top_tracks_section(top_tracks):
    medals = ["🥇", "🥈", "🥉"]
    track_text = "*🏆 YOUR TOP HITS*\n"
    
    for i, (track, count) in enumerate(top_tracks[:3]):
        medal = medals[i] if i < 3 else f"{i+1}."
        track_text += f"{medal} {track} ({count}x)\n"
    
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": track_text
        }
    }
```

### 5. Interactive Elements
```python
def create_action_section():
    return {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "📊 View Full Stats",
                    "emoji": True
                },
                "value": "view_full_stats",
                "action_id": "view_stats"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "🎵 Create Playlist",
                    "emoji": True
                },
                "value": "create_playlist",
                "action_id": "create_playlist"
            }
        ]
    }
```

## Visual Elements Library

### Progress Bars
```python
class VisualElements:
    @staticmethod
    def progress_bar(value, max_val=100, length=10, filled_char="█", empty_char="░"):
        percentage = (value / max_val) * 100
        filled_length = int(percentage / (100 / length))
        empty_length = length - filled_length
        return filled_char * filled_length + empty_char * empty_length
    
    @staticmethod
    def mini_chart(values, height=5):
        """Create ASCII bar chart"""
        max_val = max(values)
        chart_lines = []
        
        for level in range(height, 0, -1):
            line = ""
            for val in values:
                if val >= (max_val / height * level):
                    line += "█"
                else:
                    line += " "
            chart_lines.append(line)
        
        return "\n".join(chart_lines)
```

### Emoji Mappings
```python
class EmojiLibrary:
    MOOD_EMOJIS = {
        (0.0, 0.2): "😢",    # Very sad
        (0.2, 0.4): "😔",    # Sad
        (0.4, 0.6): "😐",    # Neutral
        (0.6, 0.8): "🙂",    # Happy
        (0.8, 1.0): "😄"     # Very happy
    }
    
    ENERGY_EMOJIS = {
        (0.0, 0.2): "😴",    # Very low energy
        (0.2, 0.4): "😌",    # Low energy
        (0.4, 0.6): "🚶",    # Medium energy
        (0.6, 0.8): "🏃",    # High energy
        (0.8, 1.0): "⚡"     # Very high energy
    }
    
    TIME_EMOJIS = {
        range(6, 12): "🌅",   # Morning
        range(12, 17): "☀️",  # Afternoon
        range(17, 21): "🌇",  # Evening
        range(21, 24): "🌙",  # Night
        range(0, 6): "🌚"     # Late night
    }
    
    GENRE_EMOJIS = {
        "pop": "🎵", "rock": "🎸", "hip-hop": "🎤",
        "electronic": "🎛️", "jazz": "🎺", "classical": "🎼",
        "country": "🤠", "r&b": "🎶", "indie": "🎸"
    }
```

## Message Templates System

### Template Structure
```python
class MessageTemplates:
    def __init__(self, data):
        self.data = data
        self.visual = VisualElements()
        self.emoji = EmojiLibrary()
    
    def daily_summary(self):
        """Complete daily summary template"""
        blocks = [
            self.create_header_block(),
            {"type": "divider"},
            self.create_stats_section(),
            self.create_mood_section(),
            {"type": "divider"},
            self.create_highlights_section(),
            self.create_discovery_section(),
            {"type": "divider"},
            self.create_fun_facts_section()
        ]
        
        return {"blocks": blocks}
    
    def quick_update(self):
        """Shorter format for mid-day updates"""
        # Simplified version with key stats only
        pass
    
    def weekend_special(self):
        """Special format for weekend summaries"""
        # Enhanced with week comparison
        pass
```

### Dynamic Content Generation
```python
def generate_personalized_message(user_data, historical_data):
    """Generate personalized insights based on listening patterns"""
    insights = []
    
    # Compare to personal averages
    if user_data['energy'] > historical_data['avg_energy'] * 1.2:
        insights.append("⚡ You're feeling extra energetic today!")
    
    # Discovery insights
    new_songs = user_data['new_songs_count']
    if new_songs > 5:
        insights.append(f"🔍 Explorer mode: {new_songs} new discoveries!")
    
    # Mood insights
    avg_valence = user_data['avg_valence']
    mood_emoji = get_mood_emoji(avg_valence)
    insights.append(f"{mood_emoji} Today's mood: {get_mood_description(avg_valence)}")
    
    return insights
```

## Implementation Priority

### Phase 1: Basic Rich Formatting
1. Convert current plain text to Slack blocks
2. Add emojis and basic visual elements
3. Implement progress bars for stats

### Phase 2: Interactive Elements
1. Add action buttons for expanded views
2. Implement callback handlers
3. Create detailed stats views

### Phase 3: Advanced Visuals
1. ASCII charts for trends
2. Dynamic emoji selection
3. Contextual formatting based on data

### Phase 4: Personalization
1. User preference system
2. Adaptive message formats
3. Smart insight generation

## Testing Message Formats

```python
def test_message_formatting():
    """Test different message formats with sample data"""
    
    sample_data = {
        'total_time': '4:23:15',
        'song_count': 87,
        'top_tracks': [('Blinding Lights', 4), ('Good 4 U', 3)],
        'energy_level': 82,
        'mood_level': 74
    }
    
    # Test basic formatting
    basic_msg = MessageTemplates(sample_data).daily_summary()
    
    # Test edge cases
    minimal_data = {'total_time': '0:15:30', 'song_count': 3}
    minimal_msg = MessageTemplates(minimal_data).daily_summary()
    
    # Validate message structure
    assert 'blocks' in basic_msg
    assert len(basic_msg['blocks']) > 0
```