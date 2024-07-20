import praw
from dotenv import load_dotenv
import os
import streamlit as st
from datetime import datetime, timedelta
import pytz
from collections import defaultdict

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)

def fetch_hot_posts(users, days=7, top_n=5):
    posts = []
    now = datetime.now(pytz.utc)
    time_threshold = now - timedelta(days=days)
    
    user_subreddits = defaultdict(set)
    
    for user_name in users:
        try:
            user = reddit.redditor(user_name)
            for submission in user.submissions.new(limit=None):
                submission_date = datetime.fromtimestamp(submission.created_utc, tz=pytz.utc)
                if submission_date >= time_threshold:
                    user_subreddits[user_name].add(submission.subreddit.display_name)
        except Exception as e:
            st.warning(f"An error occurred while fetching posts for user '{user_name}': {str(e)}")
    
    all_subreddits = set.union(*user_subreddits.values())
    total_subreddits = len(all_subreddits)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, subreddit_name in enumerate(all_subreddits, 1):
        status_text.text(f"Searching subreddit {i} of {total_subreddits}: r/{subreddit_name}")
        progress_bar.progress(i / total_subreddits)
        
        try:
            subreddit = reddit.subreddit(subreddit_name)
            for submission in subreddit.hot(limit=top_n):
                if submission.author and submission.author.name in users:
                    submission_date = datetime.fromtimestamp(submission.created_utc, tz=pytz.utc)
                    if submission_date >= time_threshold:
                        posts.append({
                            'title': submission.title,
                            'url': submission.url,
                            'author': submission.author.name,
                            'subreddit': subreddit_name,
                            'upvotes': submission.ups,
                            'created_utc': submission_date
                        })
        except Exception as e:
            st.warning(f"An error occurred while fetching posts from subreddit '{subreddit_name}': {str(e)}")
    
    status_text.text(f"Finished searching {total_subreddits} subreddits.")
    progress_bar.empty()
    
    return posts

st.title('Reddit User Hot Posts Fetcher')
users_input = st.text_input('Enter usernames (comma-separated)')
days = st.slider('Number of days to look back', 1, 30, 7)
top_n = st.slider('Number of top posts to check in each subreddit', 1, 20, 5)

if st.button('Fetch User Posts'):
    if not users_input:
        st.warning('Please enter usernames')
        st.stop()
    users = set(u.strip() for u in users_input.replace(" ", "").split(","))
    
    with st.spinner('Fetching posts...'):
        posts = fetch_hot_posts(users, days, top_n)
    
    if posts:
        st.success(f'Found {len(posts)} posts')
        for post in posts:
            st.markdown(f"### [{post['title']}]({post['url']})")
            st.write(f"Subreddit: r/{post['subreddit']}")
            st.write(f"Author: {post['author']}")
            st.write(f"Upvotes: {post['upvotes']}")
            st.write(f"Created: {post['created_utc'].strftime('%Y-%m-%d %H:%M:%S UTC')}")
            st.write('---')
    else:
        st.warning('No posts found')