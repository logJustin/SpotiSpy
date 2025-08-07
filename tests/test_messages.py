import pytest
from spotispy.messages import (
    create_progress_bar,
    create_ascii_bar,
    format_top_items,
    format_daily_summary,
    create_genre_distribution_chart,
    create_weekly_pattern_chart,
    create_new_vs_familiar_chart,
    create_social_discovery_chart,
    generate_random_ascii_charts
)


class TestProgressBars:
    
    def test_creates_progress_bar_with_correct_length(self):
        """Progress bar should be exactly the specified length"""
        bar = create_progress_bar(50, max_width=10)
        assert len(bar) == 10
        
        bar_20 = create_progress_bar(75, max_width=20) 
        assert len(bar_20) == 20
    
    def test_progress_bar_shows_correct_percentage(self):
        """50% should show half filled, half empty"""
        bar = create_progress_bar(50, max_width=10)
        
        filled_chars = bar.count('█')
        empty_chars = bar.count('░')
        
        assert filled_chars == 5  # 50% of 10
        assert empty_chars == 5   # 50% empty
        
    def test_progress_bar_handles_edge_cases(self):
        """Test 0%, 100%, and over 100%"""
        # 0% should be all empty
        bar_0 = create_progress_bar(0, max_width=10)
        assert bar_0.count('█') == 0
        assert bar_0.count('░') == 10
        
        # 100% should be all filled  
        bar_100 = create_progress_bar(100, max_width=10)
        assert bar_100.count('█') == 10
        assert bar_100.count('░') == 0
        
        # Over 100% should cap at 100%
        bar_over = create_progress_bar(150, max_width=10)
        assert bar_over.count('█') == 10
        assert bar_over.count('░') == 0
    
    def test_progress_bar_handles_negative_values(self):
        """Negative percentages should show as 0%"""
        bar = create_progress_bar(-25, max_width=10)
        assert bar.count('█') == 0
        assert bar.count('░') == 10
    
    def test_progress_bar_rounding(self):
        """Test that rounding works correctly for odd percentages"""
        # 33% of 10 should round to 3
        bar = create_progress_bar(33, max_width=10)
        filled_chars = bar.count('█')
        assert filled_chars == 3
        
        # 77% of 10 should round to 7 or 8
        bar_77 = create_progress_bar(77, max_width=10)
        filled_chars_77 = bar_77.count('█')
        assert filled_chars_77 in [7, 8]  # Allow for rounding differences


class TestMessageFormatting:
    
    def test_format_top_items_with_data(self):
        """Should format top items correctly"""
        items = {'Song A by Artist A': 4, 'Song B by Artist B': 3, 'Song C by Artist C': 2}
        
        result = format_top_items(items, 'songs', 'listens')
        
        assert '*Your top 3 songs from yesterday!*' in result
        assert '4 listens: Song A by Artist A' in result
        assert '3 listens: Song B by Artist B' in result
        assert '2 listens: Song C by Artist C' in result
    
    def test_format_top_items_single_item(self):
        """Should handle single item correctly"""
        items = {'Only Song by Only Artist': 5}
        
        result = format_top_items(items, 'songs', 'listens')
        
        assert '*Your top song from yesterday!*' in result
        assert '5 listens: Only Song by Only Artist' in result
    
    def test_format_top_items_empty(self):
        """Should handle empty items gracefully"""
        items = {}
        
        result = format_top_items(items, 'songs', 'listens')
        
        assert 'No repeated songs from yesterday!' in result
    
    def test_daily_summary_format_content(self, sample_analysis_results):
        """Should format daily summary with correct content"""
        message = format_daily_summary(sample_analysis_results)
        
        # Should contain key information
        assert 'Blinding Lights' in message  # Top song
        assert 'The Weeknd' in message       # Artist
        assert '15:00' in message            # Peak hour
        assert '4.4 hours' in message  # Total time (decimal format)
        assert '🎵 87 songs' in message      # Song count with emoji
    
    def test_daily_summary_format_structure(self, sample_analysis_results):
        """Should format daily summary with butler greeting and progress bars"""
        message = format_daily_summary(sample_analysis_results)
        
        # Should contain butler greeting and mobile-optimized formatting
        # Check for any digital archivist greeting pattern (Ready Player One inspired)
        assert message.startswith(('🎮', '💾', '🖥️', '🤖', '⚡', '🎧', '📡', '🎵', '🔍', '⭐'))  # Digital butler greeting should be present
        assert '*LISTENING STATS*' in message
        assert '*MOOD & ENERGY*' in message
        assert '*TOP HITS*' in message
        assert '*PEAK ACTIVITY*' in message
        
        # Should contain progress bars
        assert '█' in message  # Filled bar characters
        assert '░' in message  # Empty bar characters
        
        # Should contain section borders and content emojis
        assert '══════════════════' in message  # Section borders
        assert '🎧' in message  # Time emoji
        assert '🎵' in message  # Songs emoji
        assert '🥇' in message  # Medal emoji
    
    def test_enhanced_format_handles_missing_mood_data(self):
        """Should handle missing mood/energy data gracefully"""
        analysis_without_mood = {
            'total_songs': 50,
            'total_time': '2:30:00',
            'top_songs': {'Test Song by Test Artist': 3},
            'top_artists': {},
            'top_albums': {},
            'most_popular': {'song': 'Test Song', 'artist': 'Test Artist', 'song_popularity': 70},
            'peak_hour': '14:00',
            'peak_minutes': 45,
            'energy_level': 0,  # No mood data
            'mood_level': 0     # No mood data
        }
        
        message = format_daily_summary(analysis_without_mood)
        
        # Should still format correctly without mood section
        assert message.startswith(('🎮', '💾', '🖥️', '🤖', '⚡', '🎧', '📡', '🎵', '🔍', '⭐'))  # Digital butler greeting should be present
        assert '*LISTENING STATS*' in message
        # Should NOT contain mood section when no data
        assert '*MOOD & ENERGY*' not in message
    
    def test_message_length_reasonable(self, sample_analysis_results):
        """Messages should not be too long for Slack"""
        message = format_daily_summary(sample_analysis_results)
        
        # Slack has a 4000 character limit per message
        assert len(message) < 4000
        
        # Should not be too short either (empty messages)
        assert len(message) > 100
    
    def test_message_tone_appropriateness(self, sample_analysis_results):
        """Ensure messages have fun but not excessive tone"""
        message = format_daily_summary(sample_analysis_results)
        
        # Should have reasonable emoji usage (excluding border characters ═)
        emoji_count = sum(1 for char in message if ord(char) > 127 and char != '═')  # Rough emoji count
        assert 8 <= emoji_count <= 35  # Not too few, not too many (with fun content emojis)
        
        # Should not have excessive phrases
        excessive_phrases = ['OMG', 'BESTIE', 'LITERALLY', 'PERIODT', '!!!']
        message_upper = message.upper()
        for phrase in excessive_phrases:
            assert phrase not in message_upper


class TestAsciiCharts:
    
    def test_create_ascii_bar_basic(self):
        """Should create ASCII bars with custom characters"""
        bar = create_ascii_bar(50, max_width=10)
        assert len(bar) == 10
        assert bar.count('█') == 5
        assert bar.count('░') == 5
    
    def test_create_ascii_bar_custom_chars(self):
        """Should work with custom fill and empty characters"""
        bar = create_ascii_bar(75, max_width=8, filled_char="●", empty_char="○")
        assert len(bar) == 8
        assert bar.count('●') == 6  # 75% of 8
        assert bar.count('○') == 2
    
    def test_genre_distribution_chart(self):
        """Should create genre distribution chart from song data"""
        mock_songs = [
            {'energy': 0.8, 'valence': 0.9},  # Pop
            {'energy': 0.9, 'valence': 0.1},  # Rock
            {'energy': 0.3, 'valence': 0.2},  # Indie
            {'energy': 0.3, 'valence': 0.2},  # Indie
        ]
        
        chart = create_genre_distribution_chart(mock_songs)
        
        assert chart is not None
        assert 'Indie' in chart
        assert '█' in chart  # Should contain ASCII bars
        assert '%' in chart  # Should contain percentages
    
    def test_weekly_pattern_chart(self):
        """Should create weekly pattern chart with horizontal bars"""
        chart = create_weekly_pattern_chart()
        
        assert chart is not None
        assert 'Mon:' in chart  # Should contain day labels
        assert 'Today' in chart  # Should highlight today
        assert '█' in chart  # Should contain ASCII bars
        assert 'h' in chart  # Should show hours
    
    def test_new_vs_familiar_chart(self):
        """Should categorize songs as new vs familiar"""
        mock_songs = [
            {'song_popularity': 30},  # New (low popularity)
            {'song_popularity': 80},  # Familiar (high popularity)
            {'song_popularity': 45},  # New
            {'song_popularity': 75},  # Familiar
        ]
        
        chart = create_new_vs_familiar_chart(mock_songs)
        
        assert chart is not None
        assert '🆕 New:' in chart
        assert '🔄 Familiar:' in chart
        assert '█' in chart or '░' in chart  # Should contain ASCII bars
        assert '%' in chart
    
    def test_social_discovery_chart(self):
        """Should categorize songs as mainstream vs underground"""
        mock_songs = [
            {'song_popularity': 85},  # Mainstream
            {'song_popularity': 45},  # Underground
            {'song_popularity': 75},  # Mainstream
            {'song_popularity': 30},  # Underground
        ]
        
        chart = create_social_discovery_chart(mock_songs)
        
        assert chart is not None
        assert '📈 Mainstream:' in chart
        assert '🔍 Underground:' in chart
        assert '█' in chart or '░' in chart
        assert '%' in chart
    
    def test_generate_random_ascii_charts(self):
        """Should generate random selection of charts"""
        mock_songs = [
            {'energy': 0.8, 'valence': 0.9, 'song_popularity': 85},
            {'energy': 0.3, 'valence': 0.2, 'song_popularity': 45}
        ]
        
        charts = generate_random_ascii_charts(mock_songs, num_charts=2)
        
        assert isinstance(charts, list)
        assert len(charts) <= 2  # Should not exceed requested number
        
        for title, content in charts:
            assert isinstance(title, str)
            assert isinstance(content, str)
            assert content  # Should not be empty
    
    def test_format_daily_summary_with_ascii_charts(self, sample_analysis_results):
        """Should include ASCII charts when songs_data is provided"""
        mock_songs = [
            {'energy': 0.8, 'valence': 0.9, 'song_popularity': 85},
            {'energy': 0.3, 'valence': 0.2, 'song_popularity': 45}
        ]
        
        message_without_charts = format_daily_summary(sample_analysis_results)
        message_with_charts = format_daily_summary(sample_analysis_results, mock_songs)
        
        # Message with charts should be longer
        assert len(message_with_charts) > len(message_without_charts)
        
        # Should contain at least one chart section
        chart_indicators = ['GENRE BREAKDOWN', 'WEEKLY PATTERN', 'DISCOVERY RATIO', 'SOCIAL DISCOVERY']
        has_chart = any(indicator in message_with_charts for indicator in chart_indicators)
        assert has_chart