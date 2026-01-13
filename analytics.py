from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import pandas as pd 
import emoji
from textblob import TextBlob

def fetch_stats(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch total number of messages
    num_messages = df.shape[0]

    # fetch total number of words in messages
    words = []
    for message in df['message']:
        words.extend(message.split())
    num_words = len(words)

    # fetch total number of media messages
    num_media = df[df['message'] == '<Media omitted>\n'].shape[0]

    # fetch total number of links
    extractor = URLExtract()

    links = []
    for message in df['message']:
        links.extend(extractor.find_urls(message))
    num_links = len(links)

    return num_messages, num_words, num_media, num_links
    
def most_busy_users(df):
    x = df['user'].value_counts().head()
    new_df = round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns={'user':'name', 'count':'percent'})
    return x, new_df

def create_wordcloud(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    file = open('stop_hinglish.txt','r')
    stop_words = file.read()

    def remove_stop_words(message):
        words = []
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

        return " ".join(words)
    
    temp['message'] = temp['message'].apply(remove_stop_words)
    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    wc_df = wc.generate(temp['message'].str.cat(sep=' '))

    return wc_df

def most_common_words(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    temp = df[df['user'] != 'group notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    file = open('stop_hinglish.txt','r')
    stop_words = file.read()

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_20_words = pd.DataFrame(Counter(words).most_common(20))

    return most_common_20_words

def emoji_analysis(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])
    
    return pd.DataFrame(Counter(emojis).most_common(), columns=["emoji", "count"])

def monthly_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    timeline = df.groupby(['year','month','month_num']).count()['message'].reset_index()
    
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + '-' + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby('date').count()['message'].reset_index()

    return timeline

def weekly_activity(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    return df['day_name'].value_counts().reset_index()

def monthly_activity(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    return df['month'].value_counts().reset_index()

def activity_heatmap(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    activity_pivot_table = df.pivot_table(index='day_name',columns='period',values='message',aggfunc='count').fillna(0)

    return activity_pivot_table

def sentiment_analysis(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    sentiments = []
    for message in df['message']:
        if message.strip():
            sentiments.append(TextBlob(message).sentiment.polarity)

    if not sentiments:
        return 0, "Neutral"

    avg_sentiment = sum(sentiments) / len(sentiments)

    if avg_sentiment > 0.05:
        label = "Positive 😊"
    elif avg_sentiment < -0.05:
        label = "Negative 😠"
    else:
        label = "Neutral 😐"
    

    return round(avg_sentiment, 3), label