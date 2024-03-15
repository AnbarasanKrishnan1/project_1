import pandas as pd
import time
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector as sql
from googleapiclient.discovery import build
from PIL import Image
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
# pip install SQLAlchemy==1.4.0
import json 
import requests 
from streamlit_lottie import st_lottie 
import streamlit.components.v1 as com
import matplotlib.pyplot as plt



# SETTING PAGE CONFIGURATIONS
icon = Image.open("Youtube_logo.png")
st.set_page_config(page_title= "Youtube Data Harvesting and Warehousing | By Anbarasan",
                   page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded",
                   menu_items={'About': """# This app is created by *Anbarasan*"""})  

#Streamlit Title & Header 
with st.sidebar:
        #animation
    def animation():
            path = "D:\Guvi\YTlogo.json"
            with open(path,"r") as file: 
                url = json.load(file) 
                

            st_lottie(url, 
                reverse=True, 
                #height=300, 
                width=300, 
                speed=1, 
                loop=True, 
                quality='high', 
                key='logo12'
            ) 
            return st_lottie
    animation()
    selected = option_menu(None, ["Home", "Extract and Transform", "View","Learn_More"],
                        #   icons=[":arrow_forward:", "tools", "card-text"],
                           default_index=0,
                           orientation="vertical",
                           styles={"nav-link": {"font-size": "15x", "text-align": "centre", "margin": "25px",
                                                "--hover-color": "#87CEEB"},
                                   "icon": {"font-size": "30px"},
                                   "container": {"max-width": "6000px"},
                                   "nav-link-selected": {"background-color": "#87CEEB"}})
    st.markdown("""
        <style>
        sidebar .sidebar-content {
            background-color: #111 !important;
        }
        </style>
            """, unsafe_allow_html=True)

# Bridging a connection with MongoDB Atlas and Creating a new database(youtube_data)
# mongoDB database
uri = "mongodb+srv://anbu:anbu@cluster0.npcfhv9.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
db = client['youtube_data']

# CONNECTING WITH MYSQL DATABASE
mydb = sql.connect(host="localhost",
                   user="root",
                   password="",
                   database="youtube_db"
                   )
mycursor = mydb.cursor(buffered=True)

# BUILDING CONNECTION WITH YOUTUBE API
api_key = "AIzaSyDaSDG_TXHlAJnPanMgsgusX3eN9twnv60"
youtube = build('youtube', 'v3', developerKey=api_key)


# FUNCTION TO GET CHANNEL DETAILS
def get_channel_details(channel_id):
    ch_data = [] 
    response = youtube.channels().list(
               part='snippet,contentDetails,statistics',
               id=channel_id).execute()

    for item in response['items']:
        data = dict(Channel_id=item['id'],  # Use 'item' directly
                    Channel_name=item['snippet']['title'],
                    Playlist_id=item['contentDetails']['relatedPlaylists']['uploads'],
                    Subscribers=item['statistics']['subscriberCount'],
                    Views=item['statistics']['viewCount'],
                    Total_videos=item['statistics']['videoCount'],
                    Description=item['snippet']['description'],
                    Country=item['snippet'].get('country')
                    )
        ch_data.append(data)
    return ch_data

# FUNCTION TO GET VIDEO IDS
def get_channel_videos(channel_id):
    video_ids = []
    # get Uploads playlist id
    res = youtube.channels().list(id=channel_id,
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    #pageToken parameter identifies a specific page in the result set that should be returned. In an API response, the nextPageToken properties identify other pages that could be retrieved.
    #so we give the next page token None
    next_page_token = None

    while True:
        res = youtube.playlistItems().list(playlistId=playlist_id,
                                           part='snippet',
                                           maxResults=50,
                                           pageToken=next_page_token).execute()

        for items in (res['items']):
            video_ids.append(items['snippet']['resourceId']['videoId'])
        next_page_token = res.get('nextPageToken')

        if next_page_token is None:
            break
    return video_ids

# FUNCTION TO GET VIDEO DETAILS
def get_video_details(v_ids):
    video_stats = []

    for i in range(0, len(v_ids), 50):
        response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(v_ids[i:i + 50])).execute()
        for video in response['items']:
            video_details = dict(Channel_name=video['snippet']['channelTitle'],
                                 Channel_id=video['snippet']['channelId'],
                                 Video_id=video['id'],
                                 Title=video['snippet']['title'],
                                 Tags=video['snippet'].get('tags'),
                                 Thumbnail=video['snippet']['thumbnails']['default']['url'],
                                 Description=video['snippet']['description'],
                                 Published_date=video['snippet']['publishedAt'],
                                 Duration=video['contentDetails']['duration'],
                                 Views=video['statistics']['viewCount'],
                                 Likes=video['statistics'].get('likeCount'),
                                 Comments=video['statistics'].get('commentCount'),
                                 Favorite_count=video['statistics']['favoriteCount'],
                                 Definition=video['contentDetails']['definition'],
                                 Caption_status=video['contentDetails']['caption']
                                 )
            video_stats.append(video_details)
    return video_stats

# FUNCTION TO GET COMMENT DETAILS
def get_comments_details(v_id):
    comment_data = []
    try:
        next_page_token = None
        while True:
            response = youtube.commentThreads().list(part="snippet,replies",
                                                     videoId=v_id,
                                                     maxResults=100,
                                                     pageToken=next_page_token).execute()
            for cmt in response['items']:
                data = dict(Comment_id=cmt['id'],
                            Video_id=cmt['snippet']['videoId'],
                            Comment_text=cmt['snippet']['topLevelComment']['snippet']['textDisplay'],
                            Comment_author=cmt['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                            Comment_posted_date=cmt['snippet']['topLevelComment']['snippet']['publishedAt'],
                            Like_count=cmt['snippet']['topLevelComment']['snippet']['likeCount'],
                            Reply_count=cmt['snippet']['totalReplyCount']
                            )
                comment_data.append(data)
            next_page_token = response.get('nextPageToken')
            if next_page_token is None:
                break
    except:
        pass
    return comment_data


# FUNCTION TO CHECK IF CHANNEL EXISTS
def channel_exist(channel_name):
    return db.channel_details.find_one({"Channel_name": channel_name}) is not None


# FUNCTION TO GET CHANNEL NAMES FROM MONGODB
def channel_names():
    ch_name = []
    for i in db.channel_details.find():
        ch_name.append(i['Channel_name'])
    return ch_name


# HOME PAGE
if selected == "Home": 
    #animation
    def animation():
            path = "D:\Guvi\ytlogo1.json"
            with open(path,"r") as file: 
                url = json.load(file) 
                

            st_lottie(url, 
                reverse=True, 
                height=400, 
                # width=400, 
                speed=1, 
                loop=True, 
                quality='high', 
                key='logo1'
            ) 
            return st_lottie
    animation()
    st.markdown("<h1 style='text-align: center;'>Social Media Data Integration Project</h1>", unsafe_allow_html=True)
    st.subheader("Overview")
    st.write("""This project utilizes a combination of Python, MongoDB, YouTube Data API, MySQL, and Streamlit to streamline the retrieval, storage, 
             and presentation of YouTube channel data. It involves a systematic process of fetching data from the YouTube API, storing it in MongoDB 
             for initial storage, migrating and transforming the data into a structured SQL database, and ultimately presenting it through a user-friendly 
             Streamlit application.""")
    st.subheader("Key Technologies Used:")
    st.markdown('''  
             - Python
             - MongoDB
             - YouTube Data API
             - MySQL
             - Streamlit ''')
    st.subheader("Process Overview:")
    st.markdown('''
                - Data Retrieval: Utilizing the YouTube Data API to fetch channel data.
                - Storage: Storing the retrieved data in MongoDB as a data lake for initial storage.
                - Migration and Transformation: Converting and organizing the data into a SQL database for structured storage and enhanced querying capabilities.
                - Data Presentation: Displaying the queried data through a Streamlit application, providing users with a seamless interface for accessing and analyzing YouTube channel insights.
                ''')

# EXTRACT and TRANSFORM PAGE
if selected == "Extract and Transform":
    tab1, tab2 = st.columns(2)  # Define two columns for tabs


    # EXTRACT TAB    
    with tab1:
        #animation
        def animation(): 
            path = "D:\Guvi\demo.json"
            with open(path,"r") as file: 
                url = json.load(file) 

            st_lottie(url, 
                reverse=True, 
                height=200, 
                width=200, 
                speed=1, 
                loop=True, 
                quality='high', 
                key='demo'
            ) 
            return st_lottie
        animation()
        st.markdown("# ")
        st.write("### Enter YouTube Channel_ID below :")
        ch_id = st.text_input("Hint : In youtube, Go to the channel home page, click this > aero mark scroll down, then click share channel, and copy channel ID and paste it. If Mulit channel ID use comma" ).split(',')

        if ch_id and st.button("Extract Data"):
            ch_details = get_channel_details(ch_id)
            st.write(f'##### Extracted data from :blue["{ch_details[0]["Channel_name"]}"] channel')
            st.table(ch_details)

        if st.button("Upload to MongoDB"):
            with st.spinner('Please Wait for Uploading to MongoDB...'): 
                ch_details = get_channel_details(ch_id)
                v_ids = get_channel_videos(ch_id)
                vid_details = get_video_details(v_ids)

                def comments():
                    com_d = []
                    for i in v_ids:
                        com_d += get_comments_details(i)
                    return com_d
                comm_details = comments()

                # Check if channel already exists
                existing_channel = channel_exist(ch_details[0]["Channel_name"])
                if not existing_channel:
                    db.channel_details.insert_many(ch_details)
                    db.video_details.insert_many(vid_details)
                    db.comments_details.insert_many(comm_details)
                    st.success("Upload to MongoDB successful !!")
                else:
                    st.error("Channel details already exist in MongoDB!")

    # TRANSFORM TAB
    with tab2:
        #animation
        def animation():           
            path = "D:\Guvi\dataupload.json"
            with open(path,"r") as file: 
                url = json.load(file) 

            st_lottie(url, 
                reverse=True, 
                height=200, 
                width=200, 
                speed=1, 
                loop=True, 
                quality='high', 
                key='dataupload'
            ) 
            return st_lottie
        animation()
        st.markdown("#   ")
        st.markdown("### Select a channel to begin Transformation to SQL")

        ch_names = channel_names()
        user_inp = st.selectbox("Select channel", options=ch_names)

        # Define MySQL table creation queries
        create_channels_table_query = """
        CREATE TABLE IF NOT EXISTS youtube_db.channels (
            Channel_id VARCHAR(255) PRIMARY KEY,
            Channel_name VARCHAR(255),
            Playlist_id VARCHAR(255),
            Subscribers INT,
            Views INT,
            Total_videos INT,
            Description TEXT,
            Country VARCHAR(255)
        )
        """

        create_videos_table_query = """
        CREATE TABLE IF NOT EXISTS youtube_db.videos (
            Channel_name VARCHAR(255),
            Channel_id VARCHAR(255),
            Video_id VARCHAR(255) PRIMARY KEY,
            Title VARCHAR(255),
            Thumbnail TEXT,
            Description TEXT,
            Published_date DATETIME,
            Duration VARCHAR(50),
            Views INT,
            Likes INT,
            Comments INT,
            Favorite_count INT,
            Definition VARCHAR(50),
            Caption_status VARCHAR(50)
        )
        """

        create_comments_table_query = """
        CREATE TABLE IF NOT EXISTS youtube_db.comments (
            Comment_id VARCHAR(255) PRIMARY KEY,
            Video_id VARCHAR(255),
            Comment_text TEXT,
            Comment_author VARCHAR(255),
            Comment_posted_date DATETIME,
            Like_count INT,
            Reply_count INT
        )
        """

        # Execute table creation queries
        mycursor.execute(create_channels_table_query)
        mycursor.execute(create_videos_table_query)
        mycursor.execute(create_comments_table_query)
        mydb.commit()

        def insert_into_channels():
            query = """INSERT INTO channels (Channel_id, Channel_name, Playlist_id, Subscribers, Views, Total_videos, Description, Country)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    Channel_id = VALUES(Channel_id),
                    Channel_name = VALUES(Channel_name),
                    Playlist_id = VALUES(Playlist_id),
                    Subscribers = VALUES(Subscribers),
                    Views = VALUES(Views),
                    Total_videos = VALUES(Total_videos),
                    Description = VALUES(Description),
                    Country = VALUES(Country)"""

            for doc in db.channel_details.find({"Channel_name": user_inp}):
                values = (doc['Channel_id'], doc['Channel_name'], doc['Playlist_id'], doc['Subscribers'],
                        doc['Views'], doc['Total_videos'], doc['Description'], doc['Country'])
                mycursor.execute(query, values)
                mydb.commit()

        def insert_into_videos():
            query = """INSERT INTO videos (Channel_name, Channel_id, Video_id, Title, Thumbnail, Description, Published_date, Duration, Views, Likes, Comments, Favorite_count, Definition, Caption_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    Channel_name = VALUES(Channel_name),
                    Channel_id = VALUES(Channel_id),
                    Title = VALUES(Title),
                    Thumbnail = VALUES(Thumbnail),
                    Description = VALUES(Description),
                    Published_date = VALUES(Published_date),
                    Duration = VALUES(Duration),
                    Views = VALUES(Views),
                    Likes = VALUES(Likes),
                    Comments = VALUES(Comments),
                    Favorite_count = VALUES(Favorite_count),
                    Definition = VALUES(Definition),
                    Caption_status = VALUES(Caption_status)"""

            for doc in db.video_details.find({"Channel_name": user_inp}):
                values = (doc['Channel_name'], doc['Channel_id'], doc['Video_id'], doc['Title'], 
                        doc['Thumbnail'], doc['Description'], doc['Published_date'], doc['Duration'],
                        doc['Views'], doc['Likes'], doc['Comments'], doc['Favorite_count'],
                        doc['Definition'], doc['Caption_status'])
                mycursor.execute(query, values)
                mydb.commit()

        def insert_into_comments():
            query = """INSERT INTO comments (Comment_id, Video_id, Comment_text, Comment_author, Comment_posted_date, Like_count, Reply_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    Comment_id = VALUES(Comment_id),
                    Video_id = VALUES(Video_id),
                    Comment_text = VALUES(Comment_text),
                    Comment_author = VALUES(Comment_author),
                    Comment_posted_date = VALUES(Comment_posted_date),
                    Like_count = VALUES(Like_count),
                    Reply_count = VALUES(Reply_count)"""

            for vid in db.video_details.find({"Channel_name": user_inp}):
                for doc in db.comments_details.find({'Video_id': vid['Video_id']}):
                    values = (doc['Comment_id'], doc['Video_id'], doc['Comment_text'], doc['Comment_author'],
                              doc['Comment_posted_date'], doc['Like_count'], doc['Reply_count'])
                    mycursor.execute(query, values)
                    mydb.commit()

        if st.button("Submit"): 
            try:
                insert_into_channels()
                insert_into_videos()
                insert_into_comments()
                st.success("Transformation to MySQL Successful!!!")
            except Exception as e:
                st.error(f"Error occurred: {e}")

# VIEW PAGE
if selected == "View":
    #         #animation
    # def animation():
    #         path = "D:\Guvi\search.json"
    #         with open(path,"r") as file: 
    #             url = json.load(file) 
                
    #         st_lottie(url, 
    #             reverse=True, 
    #             #height=300, 
    #             width=300, 
    #             speed=1, 
    #             loop=True, 
    #             quality='high', 
    #             key='logo12'
    #         ) 
    #         return st_lottie
    # animation()
    st.markdown("""
        <style>
        body {
            color: #fff;
            background-color: #111;
        }
        </style>
            """, unsafe_allow_html=True)
            
    st.write("## :blue[Select any question to get Insights]")
    questions = st.selectbox('Questions',
                            ['Click the question that you would like to query',
                            '1. What are the names of all the videos and their corresponding channels?',
                            '2. Which channels have the most number of videos, and how many videos do they have?',
                            '3. What are the top 10 most viewed videos and their respective channels?',
                            '4. How many comments were made on each video, and what are their corresponding video names?',
                            '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
                            '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
                            '7. What is the total number of views for each channel, and what are their corresponding channel names?',
                            '8. What are the names of all the channels that have published videos in the year 2022?',
                            '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                            '10. Which videos have the highest number of comments, and what are their corresponding channel names?'])
                            
    if questions == '1. What are the names of all the videos and their corresponding channels?':
        mycursor.execute("""SELECT title AS Video_Title, channel_name AS Channel_Name FROM videos ORDER BY channel_name""")
        df = pd.DataFrame(mycursor.fetchall(),
                          columns=mycursor.column_names)
        st.write(df)
        st.write(" :blue[ HINT : This allows you to retrieve all of the video names along with their channels. It will assist you in determining which names can be utilized in the competition.]")      
        
    elif questions == '2. Which channels have the most number of videos, and how many videos do they have?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, 
                        total_videos AS Total_Videos 
                        FROM channels
                        ORDER BY total_videos DESC""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Number of videos in each channel :]")
        fig = px.bar(df,
                     x=mycursor.column_names[0],
                     y=mycursor.column_names[1],
                     orientation='v',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        st.write(" :blue[ HINT : This will help you to know the how many video other channel will published.]")      

        
    elif questions == '3. What are the top 10 most viewed videos and their respective channels?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, title AS Video_Title, views AS Views 
                            FROM videos
                            ORDER BY views DESC
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Top 10 most viewed videos :]")
        fig = px.bar(df,
                     x=mycursor.column_names[2],
                     y=mycursor.column_names[1],
                     orientation='h',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        st.write(" :blue[ HINT :  This will help you to know which video will good performade, This Analyze will help you to improved your next video.]") 
              
    elif questions == '4. How many comments were made on each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT a.video_id AS Video_id, a.title AS Video_Title, b.Total_Comments
                            FROM videos AS a
                            LEFT JOIN (SELECT video_id,COUNT(comment_id) AS Total_Comments
                            FROM comments GROUP BY video_id) AS b
                            ON a.video_id = b.video_id
                            ORDER BY b.Total_Comments DESC""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)


    elif questions == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name,title AS Title,likes AS Likes_Count 
                            FROM videos
                            ORDER BY likes DESC
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Top 10 most liked videos :]")
        fig = px.bar(df,
                     x=mycursor.column_names[2],
                     y=mycursor.column_names[1],
                     orientation='h',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        st.write(" :blue[ HINT :  This will help you to know which video will good performade, This Analyze will help you to improved your next video.]") 

        
    elif questions == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT title AS Title, likes AS Likes_Count
                            FROM videos
                            ORDER BY likes DESC""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
        st.write(" :blue[ HINT :  This will help you to know which video will good Response, This Analyze will help you to improved your next video.]") 

        
    elif questions == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, SUM(views) AS Total_Views
                            FROM videos
                            GROUP BY channel_name""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        st.write(" :blue[ HINT :  This will help you to know which channel have high number view.]") 

        
    elif questions == '8. What are the names of all the channels that have published videos in the year 2022?':
        mycursor.execute("""SELECT channel_name AS Channel_Name
                            FROM videos
                            WHERE YEAR(published_date) = 2022
                            GROUP BY channel_name""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name, 
                                CONCAT(
                                    LPAD(FLOOR(avg_duration / 3600), 2, '0'), ':', 
                                    LPAD(FLOOR((avg_duration % 3600) / 60), 2, '0'), ':', 
                                    LPAD(avg_duration % 60, 2, '0')
                                ) AS average_duration
                            FROM (
                                SELECT channel_name, 
                                    AVG(duration_sec) AS avg_duration
                                FROM (
                                    SELECT channel_name, 
                                        CASE
                                            WHEN duration LIKE '%H%M%S' THEN 
                                                TIME_TO_SEC(CONCAT(
                                                    SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'H', 1), 'T', -1), ':',
                                                    SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'M', 1), 'H', -1), ':',
                                                    SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'S', 1), 'M', -1)
                                                ))
                                            WHEN duration LIKE '%M%S' THEN 
                                                TIME_TO_SEC(CONCAT(
                                                    '0:', SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'M', 1), 'T', -1), ':',
                                                    SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'S', 1), 'M', -1)
                                                ))
                                            WHEN duration LIKE '%S' THEN 
                                                TIME_TO_SEC(CONCAT('0:0:', SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'S', 1), 'T', -1)))
                                        END AS duration_sec
                                    FROM videos
                                ) AS subquery
                                GROUP BY channel_name
                            ) AS avg_subquery""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

        st.write("### :green[Average video duration for channels :]")
            # Plotting using Plotly
        fig = px.bar(df, x='channel_name', y='average_duration', labels={'channel_name': 'Channel Name', 'average_duration': 'Average Duration'})
        fig.update_layout(title='Average Video Duration for Each Channel')
        st.plotly_chart(fig)


    elif questions == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        mycursor.execute("""SELECT a.Channel_name, a.Title AS Video_Title, b.Total_Comments
                            FROM videos AS a
                            LEFT JOIN (SELECT Video_id, COUNT(Comment_id) AS Total_Comments
                            FROM comments
                            GROUP BY Video_id) AS b
                            ON a.Video_id = b.Video_id
                            ORDER BY b.Total_Comments DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

# Learn_More
if selected == "Learn_More":

    st.write("## :blue[Get More Analysis of this data - Select any question to get Insights]")
    questions = st.selectbox('Questions',
                            ['Click the question that you would like to query',
                            '1. Which channels have the highest subscriber count, and what are their subscriber counts?',
                            '2. What is the average number of views, likes, and comments per video for each channel?',
                            '3. Which videos have the highest engagement rate (likes + comments) relative to their views?',
                            '4. Which channels have the highest growth rate in terms of subscribers over a specific time period?'])
    
    # Query to fetch channels sorted by subscriber count
    if questions == '1. Which channels have the highest subscriber count, and what are their subscriber counts?':
        mycursor.execute("""SELECT Channel_name, Subscribers
                            FROM channels
                            ORDER BY Subscribers DESC""")
        df_subscribers = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df_subscribers)
        st.write(":blue[ HINT :Using this, you can simply locate your rivals' subscribers.]")

    elif questions == '2. What is the average number of views, likes, and comments per video for each channel?':
            # Query to calculate average views, likes, and comments per video for each channel
        mycursor.execute("""SELECT Channel_name,
                        AVG(Views) AS Avg_Views,
                        AVG(Likes) AS Avg_Likes,
                        AVG(Comments) AS Avg_Comments
                        FROM videos
                        GROUP BY Channel_name""")
        df_avg_stats = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df_avg_stats)

        # Bar chart for average views per video
        fig_views = px.bar(df_avg_stats, x='Channel_name', y='Avg_Views',
                        title='Average Views per Video for Each Channel')
        st.plotly_chart(fig_views, use_container_width=True)

        # Bar chart for average likes per video
        fig_likes = px.bar(df_avg_stats, x='Channel_name', y='Avg_Likes',
                        title='Average Likes per Video for Each Channel')
        st.plotly_chart(fig_likes, use_container_width=True)

        # Bar chart for average comments per video
        fig_comments = px.bar(df_avg_stats, x='Channel_name', y='Avg_Comments',
                            title='Average Comments per Video for Each Channel')
        st.plotly_chart(fig_comments, use_container_width=True)

        # Query to calculate engagement rate for each video
    elif questions == '3. Which videos have the highest engagement rate (likes + comments) relative to their views?':
        mycursor.execute("""SELECT Title AS Video_Title,
                            (Likes + Comments) / Views AS Engagement_Rate
                            FROM videos
                            ORDER BY Engagement_Rate DESC
                            LIMIT 10""")
        df_engagement = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df_engagement)
        # Create bar chart for engagement rate
        fig_engagement = px.bar(df_engagement, x='Engagement_Rate', y='Video_Title',
                        title='Top 10 Videos by Engagement Rate')
        st.plotly_chart(fig_engagement, use_container_width=True)

    elif questions == '4. Which channels have the most active communities based on the number of comments relative to views?':
        mycursor.execute("""SELECT Channel_name,
                            SUM(Comments) / SUM(Views) AS Comment_to_View_Ratio
                            FROM videos
                            GROUP BY Channel_name
                            ORDER BY Comment_to_View_Ratio DESC
                            LIMIT 10""")
        df_comment_ratio = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df_comment_ratio)




    



    
