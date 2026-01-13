import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from preprocessor import preprocess
from analytics import fetch_stats, most_busy_users, create_wordcloud, most_common_words, emoji_analysis
from analytics import monthly_timeline, daily_timeline, weekly_activity, monthly_activity, activity_heatmap
from analytics import sentiment_analysis

st.sidebar.title('WhatsApp Chat Analyzer')

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()     # To read file as bytes:
    try:
        data = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            data = bytes_data.decode("utf-16")
        except UnicodeDecodeError:
            data = bytes_data.decode("latin-1")
        df = preprocess(data)

    st.dataframe(df)

    user_list = df['user'].unique().tolist()
    if 'group notification' in user_list:
        user_list.remove('group notification')
    user_list.sort()
    user_list.insert(0,'Overall')

    selected_user = st.sidebar.selectbox("Show Analyst Wrt",user_list)

    if st.sidebar.button('Show Analysis'):

        # Stats Area
        st.title('Top Statistics')
        num_messages, num_words, num_media, num_links = fetch_stats(selected_user,df)

        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.write("Total Messages")
            st.title(num_messages)

        with col2:
            st.write("Total Words") 
            st.title(num_words)
        
        with col3:
            st.write("Media Shared") 
            st.title(num_media)
        
        with col4:
            st.write("Links Shared") 
            st.title(num_links)

        # Monthly Timeline 
        st.title('Monthly Timeline')
        timeline = monthly_timeline(selected_user,df)
        fig,ax = plt.subplots()
        ax.plot(timeline['time'],timeline['message'],color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
        
        # Daily Timeline 
        st.title('Daily Timeline')
        date_timeline = daily_timeline(selected_user,df)
        fig,ax = plt.subplots()
        ax.plot(date_timeline['date'],date_timeline['message'],color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Weekly and Monthly Activity
        week_day = weekly_activity(selected_user,df)
        monthly = monthly_activity(selected_user,df)
        
        st.title('Map Activity')

        col1,col2 = st.columns(2)

        with col1:
            st.header('Most Busy Day')
            fig, ax = plt.subplots()
            ax.bar(week_day['day_name'],week_day['count'])
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        with col2:
            st.header('Most Busy Month')
            fig, ax = plt.subplots()
            ax.bar(monthly['month'],monthly['count'],color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # Acitvity Heatmap
        activity_pivot_table = activity_heatmap(selected_user,df)

        st.title('Weekly Activity Heatmap')
        fig,ax = plt.subplots()
        ax = sns.heatmap(activity_pivot_table,cmap="rocket_r")
        st.pyplot(fig)

        # Finding the busiest user in chat group
        if selected_user == 'Overall':
            st.title('Most Busy User')

            x, new_df = most_busy_users(df)

            col1,col2 = st.columns(2)

            with col1:
                fig, ax = plt.subplots()
                ax.bar(x.index,x.values,color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)
        
        # WordCloud
        st.title('Word Cloud')
        wc_df = create_wordcloud(selected_user,df)
        fig, ax = plt.subplots()
        ax.imshow(wc_df)
        st.pyplot(fig)

        # Most Common Words
        st.title('Most Common Words')
        most_common_20_words = most_common_words(selected_user,df)
        fig, ax = plt.subplots()
        ax.barh(most_common_20_words[0],most_common_20_words[1],color='orange')
        st.pyplot(fig)

        # Emoji Analysis
        st.title('Emoji Analysis')
        emoji_df = emoji_analysis(selected_user,df)

        col1, col2 = st.columns(2)
        
        with col1:
            st.dataframe(emoji_df)

        with col2:
            import plotly.express as px

            top_emojis = emoji_df
            fig = px.pie(top_emojis, values='count', names='emoji', title="Top Emojis",color_discrete_sequence=px.colors.sequential.Viridis)
            st.plotly_chart(fig)

        # Sentiment Analysis
        st.title("Chat Sentiment Analysis")

        sentiment_score, sentiment_label = sentiment_analysis(selected_user, df)

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Average Sentiment Score", sentiment_score)

        with col2:
            st.metric("Overall Sentiment", sentiment_label)