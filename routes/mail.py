import json
import logging

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from pytz import timezone

from routes import app

logger = logging.getLogger(__name__)

@app.route('/mailtime', methods=['POST'])
def calculate_mailtime():
    data = request.json
    
    # Process the input data to calculate response times
    response_times = calculate_response_times(data, advanced=True)
    
    return jsonify(response_times)

def calculate_response_times(data, advanced=False):
    emails = data['emails']
    users = {user['name']: user['officeHours'] for user in data['users']}

    # Sort emails by timeSent
    emails.sort(key=lambda x: datetime.fromisoformat(x['timeSent']))
    
    response_times = {}
    response_counts = {}

    def get_user_office_hours(user_name):
        user_info = users[user_name]
        tz = timezone(user_info['timeZone'])
        start = user_info['start']
        end = user_info['end']
        return tz, start, end

    for i in range(1, len(emails)):
        previous_email = emails[i - 1]
        current_email = emails[i]

        sender = current_email['sender']
        receiver = previous_email['sender']

        previous_time = datetime.fromisoformat(previous_email['timeSent'])
        current_time = datetime.fromisoformat(current_email['timeSent'])
        
        response_time = (current_time - previous_time).total_seconds()

        if advanced:
            previous_tz, prev_start, prev_end = get_user_office_hours(receiver)
            current_tz, curr_start, curr_end = get_user_office_hours(sender)

            previous_time = previous_time.astimezone(previous_tz)
            current_time = current_time.astimezone(current_tz)

            response_time = calculate_working_time(previous_time, current_time, prev_start, prev_end, curr_start, curr_end)

        if sender not in response_times:
            response_times[sender] = 0
            response_counts[sender] = 0
        
        response_times[sender] += response_time
        response_counts[sender] += 1

    result = {}
    for user, total_time in response_times.items():
        result[user] = round(total_time / response_counts[user])

    return {"response": result}

def calculate_working_time(start_time, end_time, start_hour, end_hour, user_start, user_end):
    working_seconds = 0

    # If the start time is after end time, there is no working time
    if start_time >= end_time:
        return 0

    # Calculate working time in seconds
    current_time = start_time

    # Loop through each time slice until the end time
    while current_time < end_time:
        # If it's a weekend, skip to the next Monday
        if current_time.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            current_time += timedelta(days=(7 - current_time.weekday()))
            continue

        # Check if current time is within working hours
        start_of_work = current_time.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end_of_work = current_time.replace(hour=end_hour, minute=0, second=0, microsecond=0)

        if current_time < start_of_work:
            current_time = start_of_work
        
        # If we're still within working hours
        if current_time < end_of_work:
            # Calculate the time spent in working hours
            working_end = min(end_of_work, end_time)
            working_seconds += (working_end - current_time).total_seconds()
            current_time = working_end

        # If we reach the end of working hours, go to the next day
        if current_time >= end_of_work:
            current_time += timedelta(days=1)
            current_time = current_time.replace(hour=start_hour, minute=0)

    return working_seconds

if __name__ == '__main__':
    app.run(debug=True)
