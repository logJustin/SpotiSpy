1. Build excel workbook of songs listened to `python excel.py`    
    1. Creates workbook titled by date w/ worksheet titled by hour
        1. Saves it to a data subdirectory
        2. Overwrites worksheets if already exists
    2. Determines epoch time of start of current hour
    3. Fetches the songs played in the last hour: `get_recently_played.py`

# To Do
1. Handle if worksheet already exists
2. Fetch, analyze, and summarize daily listen information
3. Add more data of songs listened to in workbook