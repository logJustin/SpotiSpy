# 🧪 TDD Implementation Guide for Enhanced SpotiSpy

## 🎯 Test-Driven Development Approach

### Phase Structure: Red → Green → Refactor
1. **Red**: Write failing tests first
2. **Green**: Write minimal code to pass tests  
3. **Refactor**: Improve code while keeping tests green

## 📁 Test Project Structure

```
tests/
├── conftest.py                 # Pytest configuration & fixtures
├── fixtures/
│   ├── __init__.py
│   ├── sample_data.py         # Realistic test data
│   └── mock_responses.py      # Mock API responses
├── unit/
│   ├── test_album_binge_detection.py
│   ├── test_artist_analysis.py  
│   ├── test_visual_charts.py
│   └── test_message_formatting.py
├── integration/
│   ├── test_daily_analysis_pipeline.py
│   └── test_weekly_summary_pipeline.py
└── test_data/
    ├── realistic_day_sample.json
    └── realistic_week_sample.json
```

## 🎵 Test Fixtures & Sample Data

### Core Test Data Setup

```python
# tests/conftest.py
import pytest
from datetime import datetime, timedelta

@pytest.fixture
def sample_listening_day():
    """Realistic day of listening data"""
    base_time = datetime(2025, 3, 15, 9, 0, 0)
    
    return [
        # Morning Arctic Monkeys
        {'song': 'Do I Wanna Know?', 'artist': 'Arctic Monkeys', 'album': 'AM', 
         'played_at': base_time.isoformat(), 'duration': 263},
        {'song': 'R U Mine?', 'artist': 'Arctic Monkeys', 'album': 'AM',
         'played_at': (base_time + timedelta(minutes=4)).isoformat(), 'duration': 201},
         
        # Afternoon Weeknd binge
        {'song': 'Alone Again', 'artist': 'The Weeknd', 'album': 'After Hours',
         'played_at': (base_time + timedelta(hours=5)).isoformat(), 'duration': 294},
        {'song': 'Too Late', 'artist': 'The Weeknd', 'album': 'After Hours',
         'played_at': (base_time + timedelta(hours=5, minutes=5)).isoformat(), 'duration': 239},
        {'song': 'Hardest To Love', 'artist': 'The Weeknd', 'album': 'After Hours',
         'played_at': (base_time + timedelta(hours=5, minutes=9)).isoformat(), 'duration': 231},
        {'song': 'Scared To Live', 'artist': 'The Weeknd', 'album': 'After Hours',
         'played_at': (base_time + timedelta(hours=5, minutes=13)).isoformat(), 'duration': 311},
         
        # Evening variety
        {'song': 'Holocene', 'artist': 'Bon Iver', 'album': 'Bon Iver, Bon Iver',
         'played_at': (base_time + timedelta(hours=10)).isoformat(), 'duration': 337},
    ]

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
            'duration': 250  # Average song length
        })
    
    return songs

@pytest.fixture
def mixed_listening_day():
    """Day with no clear patterns - variety listening"""
    # Different artists, albums, scattered timing
    pass
```

## 🧪 Feature-by-Feature TDD Implementation

### 1. Album Binge Detection

#### First: Write the Tests
```python
# tests/unit/test_album_binge_detection.py
import pytest
from scripts.message.analysis.insights.pattern_analyzer import detect_album_binges

class TestAlbumBingeDetection:
    
    def test_detects_clear_album_binge(self, weeknd_album_binge):
        """Should detect when 3+ consecutive songs from same album"""
        result = detect_album_binges(weeknd_album_binge)
        
        assert len(result) == 1
        binge = result[0]
        assert binge['album'] == 'After Hours'
        assert binge['artist'] == 'The Weeknd'
        assert binge['song_count'] == 8
        assert binge['total_duration'] > 1800  # 30+ minutes
    
    def test_ignores_single_songs(self, mixed_listening_day):
        """Scattered songs shouldn't trigger binge detection"""
        result = detect_album_binges(mixed_listening_day)
        assert len(result) == 0
    
    def test_requires_minimum_three_songs(self):
        """Two songs in a row isn't a binge"""
        two_songs = [
            {'song': 'Song 1', 'artist': 'Artist', 'album': 'Album', 'duration': 200},
            {'song': 'Song 2', 'artist': 'Artist', 'album': 'Album', 'duration': 180}
        ]
        
        result = detect_album_binges(two_songs)
        assert len(result) == 0
    
    def test_calculates_binge_duration(self, weeknd_album_binge):
        """Should calculate total time spent in album binge"""
        result = detect_album_binges(weeknd_album_binge)
        binge = result[0]
        
        expected_duration = sum(song['duration'] for song in weeknd_album_binge)
        assert binge['total_duration'] == expected_duration
    
    def test_identifies_binge_timespan(self, weeknd_album_binge):
        """Should know when binge started and ended"""
        result = detect_album_binges(weeknd_album_binge)
        binge = result[0]
        
        assert 'start_time' in binge
        assert 'end_time' in binge
        assert binge['start_time'] < binge['end_time']
```

#### Second: Write Minimal Implementation
```python
# scripts/message/analysis/insights/pattern_analyzer.py
from datetime import datetime
from collections import defaultdict

def detect_album_binges(songs_data, min_songs=3):
    """
    Detect when user listened to multiple consecutive songs from same album
    
    Args:
        songs_data: List of song dictionaries with album, artist, played_at, duration
        min_songs: Minimum consecutive songs to count as binge (default: 3)
    
    Returns:
        List of detected album binges with metadata
    """
    if not songs_data or len(songs_data) < min_songs:
        return []
    
    binges = []
    current_binge = []
    
    for song in songs_data:
        # Check if this song continues current album sequence
        if (current_binge and 
            song['album'] == current_binge[-1]['album'] and 
            song['artist'] == current_binge[-1]['artist']):
            current_binge.append(song)
        else:
            # Check if previous sequence was a binge
            if len(current_binge) >= min_songs:
                binges.append(_create_binge_summary(current_binge))
            
            # Start new potential binge
            current_binge = [song]
    
    # Don't forget the last sequence
    if len(current_binge) >= min_songs:
        binges.append(_create_binge_summary(current_binge))
    
    return binges

def _create_binge_summary(binge_songs):
    """Create summary object for an album binge"""
    first_song = binge_songs[0]
    last_song = binge_songs[-1]
    
    return {
        'album': first_song['album'],
        'artist': first_song['artist'], 
        'song_count': len(binge_songs),
        'songs': [song['song'] for song in binge_songs],
        'total_duration': sum(song['duration'] for song in binge_songs),
        'start_time': first_song['played_at'],
        'end_time': last_song['played_at']
    }
```

#### Third: Run Tests (Should Pass)
```bash
pytest tests/unit/test_album_binge_detection.py -v
```

### 2. ASCII Chart Generation

#### First: Write the Tests
```python
# tests/unit/test_visual_charts.py
import pytest
from scripts.message.formatters.visual_elements import create_weekly_chart, create_progress_bar

class TestVisualCharts:
    
    def test_creates_weekly_listening_chart(self):
        """Should create ASCII bar chart for week's listening"""
        daily_hours = {
            'Mon': 3.2, 'Tue': 4.1, 'Wed': 1.8, 'Thu': 4.5, 
            'Fri': 3.7, 'Sat': 2.9, 'Sun': 4.2
        }
        
        chart = create_weekly_chart(daily_hours)
        
        # Should have all days
        for day in daily_hours.keys():
            assert day[:3] in chart  # Mon, Tue, etc.
        
        # Should have filled and empty bars
        assert '█' in chart  # Filled portions
        assert '░' in chart  # Empty portions
        
        # Should be properly formatted
        lines = chart.split('\n')
        assert len(lines) == 7  # One line per day
    
    def test_chart_proportions_correct(self):
        """Bars should be proportional to values"""
        daily_hours = {'Day1': 2.0, 'Day2': 4.0}  # Day2 should be 2x longer
        chart = create_weekly_chart(daily_hours, max_width=10)
        
        lines = chart.split('\n')
        day1_bars = lines[0].count('█')
        day2_bars = lines[1].count('█')
        
        # Day2 should have roughly twice as many bars
        assert day2_bars >= day1_bars * 1.5
    
    def test_progress_bar_percentages(self):
        """Progress bars should accurately represent percentages"""
        bar_75 = create_progress_bar(75, max_width=10)
        bar_25 = create_progress_bar(25, max_width=10)
        
        assert bar_75.count('█') == 7  # 75% of 10
        assert bar_75.count('░') == 3  # 25% empty
        
        assert bar_25.count('█') == 2  # 25% of 10  
        assert bar_25.count('░') == 8  # 75% empty
```

#### Second: Implement Visual Elements
```python
# scripts/message/formatters/visual_elements.py
def create_weekly_chart(daily_data, max_width=10):
    """
    Create ASCII bar chart for weekly listening data
    
    Args:
        daily_data: Dict like {'Mon': 3.2, 'Tue': 4.1, ...}
        max_width: Maximum width of bars in characters
        
    Returns:
        Multi-line string with ASCII chart
    """
    if not daily_data:
        return "No data available"
    
    max_value = max(daily_data.values())
    if max_value == 0:
        return "No listening detected"
    
    chart_lines = []
    
    for day, hours in daily_data.items():
        # Calculate bar width proportional to max value
        bar_width = int((hours / max_value) * max_width)
        empty_width = max_width - bar_width
        
        # Create visual bar
        bar = "█" * bar_width + "░" * empty_width
        
        # Format with day and duration
        formatted_hours = f"{hours:.1f}h"
        line = f"  {day[:3]} {bar}  {formatted_hours}"
        
        chart_lines.append(line)
    
    return "\n".join(chart_lines)

def create_progress_bar(percentage, max_width=10):
    """Create progress bar for percentages (0-100)"""
    if percentage > 100:
        percentage = 100
    elif percentage < 0:
        percentage = 0
        
    filled_width = int((percentage / 100) * max_width)
    empty_width = max_width - filled_width
    
    return "█" * filled_width + "░" * empty_width
```

### 3. Artist Domination Analysis

#### First: Tests
```python
# tests/unit/test_artist_analysis.py
class TestArtistAnalysis:
    
    def test_calculates_artist_percentages(self, sample_listening_day):
        """Should calculate what % of day each artist occupied"""
        result = calculate_artist_percentages(sample_listening_day)
        
        assert 'The Weeknd' in result
        assert 'Arctic Monkeys' in result
        
        # Weeknd had more songs, should be higher percentage
        assert result['The Weeknd']['percentage'] > result['Arctic Monkeys']['percentage']
        
        # All percentages should add up to ~100%
        total_percentage = sum(artist['percentage'] for artist in result.values())
        assert 95 <= total_percentage <= 105  # Allow for rounding
    
    def test_identifies_dominant_artist(self, sample_listening_day):
        """Should identify when one artist dominates listening"""
        result = calculate_artist_percentages(sample_listening_day)
        dominant = get_dominant_artist(result, threshold=25)  # 25%+ = dominant
        
        assert dominant is not None
        assert dominant['artist'] == 'The Weeknd'  # Based on our sample data
        assert dominant['percentage'] >= 25
```

## 🎯 TDD Development Workflow

### Daily Development Cycle

#### 1. **Morning**: Write Tests (Red Phase)
```bash
# Start with failing test
pytest tests/unit/test_album_binge_detection.py::test_detects_clear_album_binge -v
# Should fail because function doesn't exist yet
```

#### 2. **Implementation**: Make Tests Pass (Green Phase)
- Write minimal code to pass the test
- Don't over-engineer, just make it work
- Run test again - should pass

#### 3. **Refactor**: Improve Code Quality
- Clean up implementation
- Add error handling
- Optimize for readability
- Tests should still pass

#### 4. **Integration**: Add to Main Pipeline
- Import new function into main analysis
- Test integration with existing code
- Update main message formatting

### Example TDD Session: Album Binge Feature

```bash
# Day 1: Red Phase - Write failing tests
touch tests/unit/test_album_binge_detection.py
# Write tests (they fail)
pytest tests/unit/test_album_binge_detection.py

# Day 1: Green Phase - Make tests pass  
touch scripts/message/analysis/insights/pattern_analyzer.py
# Write minimal implementation
pytest tests/unit/test_album_binge_detection.py  # Should pass

# Day 2: Refactor Phase
# Improve code quality, add edge case handling
pytest tests/unit/test_album_binge_detection.py  # Still passes

# Day 2: Integration
# Add to main send_analysis.py
# Test full pipeline
pytest tests/integration/test_daily_analysis_pipeline.py
```

## 📊 Testing Strategy by Feature

### Core Features Testing Priority

1. **Album Binge Detection** (High Priority)
   - Multiple test cases for different scenarios
   - Edge cases: no data, single songs, mixed albums

2. **ASCII Charts** (High Priority)  
   - Visual accuracy testing
   - Different data ranges
   - Empty data handling

3. **Artist Analysis** (Medium Priority)
   - Percentage calculations
   - Dominant artist detection
   - Multiple artists edge cases

4. **Message Formatting** (Medium Priority)
   - Template rendering
   - Tone appropriateness
   - Length validation

5. **Weekly Aggregation** (Lower Priority)
   - Data collection across days
   - Summary calculations
   - Performance with large datasets

### Continuous Integration Setup

```bash
# .github/workflows/test.yml (if using GitHub)
name: SpotiSpy Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: pip install -r requirements.txt pytest
    - name: Run tests
      run: pytest tests/ -v --coverage
```

This TDD approach ensures each feature works correctly before moving to the next, building confidence as we enhance your SpotiSpy experience!