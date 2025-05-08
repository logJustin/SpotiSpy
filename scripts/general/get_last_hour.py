from datetime import datetime, timedelta

def last_hour():
    current_time = datetime.now()
    previous_hour = current_time.replace(
        minute=0, second=0, microsecond=0) - timedelta(hours=0)
    return int(previous_hour.timestamp() * 1000)

if __name__ == '__main__':
    test = last_hour()
    print(test)
