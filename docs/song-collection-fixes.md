# Song Collection Script Fixes

## Issues Resolved

### 1. Date Parsing Error (ISO Format with Z suffix)
**Problem**: `Invalid isoformat string: '2025-08-14T17:06:51.710Z'`
- Spotify API returns timestamps with 'Z' suffix 
- Python's `datetime.fromisoformat()` doesn't handle 'Z' directly

**Solution**: Modified `spotispy/spotify.py:52` to replace 'Z' with '+00:00' before parsing:
```python
"played_at": datetime.fromisoformat(song_data['played_at'].replace('Z', '+00:00')).isoformat(),
```

### 2. Database Schema Error (Release Date Format)
**Problem**: `invalid input syntax for type date: "1976"`
- Spotify returns release dates in various formats: "1976", "1967-08", "1973-01-01"
- Database expects consistent YYYY-MM-DD format

**Solution**: Added `normalize_release_date()` function in `spotispy/spotify.py`:
- "1976" → "1976-01-01"
- "1967-08" → "1967-08-01" 
- "1973-01-01" → unchanged

### 3. Timestamp Parsing Error (Microseconds)
**Problem**: `Invalid isoformat string: '2025-08-14T17:06:51.71+00:00'`
- Inconsistent microsecond precision (2 digits vs expected 6)
- Occurred in duplicate checking logic

**Solution**: Added robust `parse_datetime_robust()` function in `spotispy/database.py`:
- Handles Z suffix and +00:00 timezone formats
- Normalizes microseconds to 6 digits by padding with zeros
- Used in all datetime parsing operations

### 4. Missing Dependencies
**Problem**: `ModuleNotFoundError: No module named 'dotenv'`
- Virtual environment missing required packages

**Solution**: Installed requirements:
```bash
source spotispyvenv/bin/activate && python3 -m pip install -r requirements.txt
```

### 5. SSL Warning Suppression
**Problem**: Noisy urllib3 OpenSSL compatibility warning
**Solution**: Added to `write_recent_song.sh`:
```bash
export PYTHONWARNINGS="ignore"
```

## Files Modified

1. **spotispy/spotify.py**
   - Added `normalize_release_date()` function
   - Fixed timestamp parsing with Z suffix replacement

2. **spotispy/database.py** 
   - Added `parse_datetime_robust()` function
   - Enhanced error logging for database operations
   - Replaced all `datetime.fromisoformat()` calls with robust parser

3. **write_recent_song.sh**
   - Updated base path for macOS
   - Added warning suppression
   - No functional changes to core logic

## Testing Results

Script now runs successfully:
- ✅ Fetches songs from Spotify API
- ✅ Handles all release date formats  
- ✅ Parses timestamps with varying precision
- ✅ Saves songs to database without errors
- ✅ Runs without warnings

## Status
All issues resolved. The `write_recent_song.sh` script is now fully functional.