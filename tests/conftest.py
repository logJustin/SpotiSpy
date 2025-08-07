import pytest
import sys
import os
from datetime import datetime, timedelta

# Add project root to path so we can import spotispy modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture
def sample_songs_with_audio_features():
    """Sample songs with energy and valence data for mood analysis"""
    return [
        {
            'song': 'Blinding Lights',
            'artist': 'The Weeknd', 
            'album': 'After Hours',
            'energy': 0.85,
            'valence': 0.72,  # Happy song
            'played_at': '2025-03-15T10:30:00Z',
            'duration': 200,
            'song_popularity': 87
        },
        {
            'song': 'Mad World',
            'artist': 'Gary Jules',
            'album': 'Trading Snakeoil for Wolftickets',
            'energy': 0.25,
            'valence': 0.12,  # Sad song
            'played_at': '2025-03-15T11:00:00Z', 
            'duration': 190,
            'song_popularity': 45
        },
        {
            'song': 'Pumped Up Kicks',
            'artist': 'Foster the People',
            'album': 'Torches',
            'energy': 0.78,
            'valence': 0.45,  # Energetic but neutral mood
            'played_at': '2025-03-15T11:30:00Z',
            'duration': 240,
            'song_popularity': 72
        }
    ]

@pytest.fixture  
def high_energy_day():
    """Day with consistently high energy music"""
    return [
        {'energy': 0.9, 'valence': 0.8, 'duration': 200, 'song_popularity': 80},
        {'energy': 0.85, 'valence': 0.75, 'duration': 180, 'song_popularity': 75},
        {'energy': 0.92, 'valence': 0.82, 'duration': 220, 'song_popularity': 85}
    ]

@pytest.fixture
def low_energy_day():
    """Day with low energy, sad music"""
    return [
        {'energy': 0.15, 'valence': 0.2, 'duration': 200, 'song_popularity': 60},
        {'energy': 0.22, 'valence': 0.18, 'duration': 180, 'song_popularity': 55}, 
        {'energy': 0.18, 'valence': 0.25, 'duration': 220, 'song_popularity': 62}
    ]

@pytest.fixture
def sample_analysis_results():
    """Sample analysis results for message formatting tests"""
    return {
        'total_songs': 87,
        'total_time': '4:23:15',
        'total_time_formatted': '4 hours, 23 minutes, and 15 seconds',
        'top_songs': {'Blinding Lights by The Weeknd': 4, 'Good 4 U by Olivia Rodrigo': 3},
        'top_artists': {'The Weeknd': 8, 'Arctic Monkeys': 5},
        'top_albums': {'After Hours by The Weeknd': 2},
        'most_popular': {'song': 'Blinding Lights', 'artist': 'The Weeknd', 'song_popularity': 87},
        'peak_hour': '15:00',
        'peak_minutes': 83,
        'energy_level': 75,
        'mood_level': 68
    }

@pytest.fixture
def weeknd_album_binge():
    """Perfect example of album deep dive"""
    base_time = datetime(2025, 3, 15, 14, 30, 0)
    
    weeknd_songs = [
        'Alone Again', 'Too Late', 'Hardest To Love', 'Scared To Live', 
        'Snowchild', 'Escape From LA', 'Heartless', 'Faith'
    ]
    
    songs = []
    for i, song in enumerate(weeknd_songs):
        songs.append({
            'song': song, 'artist': 'The Weeknd', 'album': 'After Hours',
            'played_at': (base_time + timedelta(minutes=i*4)).isoformat(),
            'duration': 250,  # Average song length
            'energy': 0.8,
            'valence': 0.6,
            'song_popularity': 80
        })
    
    return songs