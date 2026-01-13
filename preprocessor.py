
import re
import pandas as pd

def preprocess(data):
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?:\s?(?:AM|PM|am|pm))?\s?[-–]\s'

    messages = re.split(pattern,data)[1:]
    dates = re.findall(pattern,data)

#     df = pd.DataFrame({'user_message':messages, 'datetime':dates})
#     df['datetime'] = pd.to_datetime(
#     df['datetime'].str.replace("\u202f", " ", regex=False).str.replace(" -", "", regex=False).str.strip(),
#     errors="coerce",
#     dayfirst=True,
#     infer_datetime_format=True
# )
    

    df = pd.DataFrame({'user_message': messages, 'datetime': dates})

    df['datetime'] = df['datetime'].astype(str)

    df['datetime'] = pd.to_datetime(
    df['datetime'].str.replace("\u202f", " ", regex=False).str.replace(" -", "", regex=False).str.strip(),
    errors="coerce",
    dayfirst=True,
    infer_datetime_format=True)

    df = df.dropna(subset=['datetime'])


    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s',message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages

    df.drop(columns=['user_message'],axis=1,inplace=True)

    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month_name()
    df['day'] = df['datetime'].dt.day
    df['hour'] = df['datetime'].dt.hour
    df['minute'] = df['datetime'].dt.minute
    df['month_num'] = df['datetime'].dt.month
    df['date'] = df['datetime'].dt.date
    df['day_name'] = df['datetime'].dt.day_name()

    period = []
    for hour in df[['day_name','hour']]['hour']:
        if hour == '23':
            period.append('23-00')
        elif hour == '0':
            period.append('00-01')
        else:
            period.append(f"{hour}-{hour+1}")

    df['period'] = period

    return df