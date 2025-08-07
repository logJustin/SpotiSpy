import pytest
from spotispy.analysis import (
    calculate_daily_energy, 
    calculate_daily_mood,
    analyze_listening_day,
    find_top_items,
    find_most_popular_song
)


class TestMoodAnalysis:
    
    def test_calculates_average_energy_level(self, sample_songs_with_audio_features):
        """Should calculate weighted average energy based on song duration"""
        result = calculate_daily_energy(sample_songs_with_audio_features)
        
        # Should return percentage (0-100)
        assert 0 <= result <= 100
        assert isinstance(result, (int, float))
    
    def test_calculates_average_mood_level(self, sample_songs_with_audio_features):
        """Should calculate weighted average valence (mood) based on duration"""
        result = calculate_daily_mood(sample_songs_with_audio_features)
        
        # Should return percentage (0-100)  
        assert 0 <= result <= 100
        assert isinstance(result, (int, float))
    
    def test_high_energy_day_returns_high_percentage(self, high_energy_day):
        """Day with high energy songs should return >70% energy"""
        result = calculate_daily_energy(high_energy_day)
        assert result > 70
    
    def test_low_energy_day_returns_low_percentage(self, low_energy_day):
        """Day with low energy songs should return <30% energy"""
        result = calculate_daily_energy(low_energy_day)
        assert result < 30
    
    def test_weights_by_song_duration(self):
        """Longer songs should have more influence on daily average"""
        songs = [
            {'energy': 1.0, 'valence': 1.0, 'duration': 600},  # 10 min, very happy/energetic
            {'energy': 0.0, 'valence': 0.0, 'duration': 60}    # 1 min, very sad/low energy
        ]
        
        energy_result = calculate_daily_energy(songs)
        mood_result = calculate_daily_mood(songs)
        
        # Should be closer to high values due to longer duration
        assert energy_result > 80  # Weighted toward the longer, high-energy song
        assert mood_result > 80    # Weighted toward the longer, happy song
    
    def test_handles_empty_song_list(self):
        """Should handle case with no songs gracefully"""
        empty_songs = []
        
        energy_result = calculate_daily_energy(empty_songs)
        mood_result = calculate_daily_mood(empty_songs)
        
        assert energy_result == 0
        assert mood_result == 0
    
    def test_handles_missing_audio_features(self):
        """Should handle songs without energy/valence data"""
        songs_missing_features = [
            {'song': 'Test Song', 'artist': 'Test Artist', 'duration': 200}
            # Missing 'energy' and 'valence' keys
        ]
        
        energy_result = calculate_daily_energy(songs_missing_features)
        mood_result = calculate_daily_mood(songs_missing_features)
        
        # Should return 0 when no usable data
        assert energy_result == 0
        assert mood_result == 0


class TestAnalysisIntegration:
    
    def test_analyze_listening_day_returns_complete_results(self, sample_songs_with_audio_features):
        """Should return all expected analysis fields"""
        result = analyze_listening_day(sample_songs_with_audio_features)
        
        expected_fields = [
            'total_songs', 'total_time', 'total_time_formatted',
            'top_songs', 'top_artists', 'top_albums', 
            'most_popular', 'peak_hour', 'energy_level', 'mood_level'
        ]
        
        for field in expected_fields:
            assert field in result
    
    def test_analyze_empty_day(self):
        """Should handle empty song list gracefully"""
        result = analyze_listening_day([])
        
        assert result['total_songs'] == 0
        assert result['total_time'] == '0:00:00'
        assert result['energy_level'] == 0
        assert result['mood_level'] == 0
    
    def test_find_top_items_songs(self, sample_songs_with_audio_features):
        """Should find repeated songs"""
        # Add a duplicate song to make it show up as "top"
        songs_with_repeat = sample_songs_with_audio_features + [sample_songs_with_audio_features[0]]
        
        from spotispy.database import group_songs_by_hour
        day_data = group_songs_by_hour(songs_with_repeat)
        
        top_songs = find_top_items(day_data, 'song')
        
        # Should find the repeated Blinding Lights
        assert len(top_songs) > 0
        assert any('Blinding Lights' in song_name for song_name in top_songs.keys())
    
    def test_find_most_popular_song(self, sample_songs_with_audio_features):
        """Should identify the song with highest popularity"""
        from spotispy.database import group_songs_by_hour
        day_data = group_songs_by_hour(sample_songs_with_audio_features)
        
        most_popular = find_most_popular_song(day_data['history'])
        
        assert most_popular is not None
        assert most_popular['song'] == 'Blinding Lights'  # Highest popularity in sample data
        assert most_popular['song_popularity'] == 87