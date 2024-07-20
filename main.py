import praw
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)


def fetch_posts(subreddits: list, users: set , n: int = 5) -> list:
    posts = []
    for subreddit_name in subreddits:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            for submission in subreddit.hot(limit=n):  # Adjust the limit as needed
                if submission.author and submission.author.name in users:
                    posts.append({
                        'title': submission.title,
                        'url': submission.url,
                        'author': submission.author.name,
                        'subreddit': subreddit_name,
                        'upvotes': submission.ups,
                    })
        except Exception as e:
            st.warning(f"Error fetching posts from r/{subreddit_name}")
        
    return posts


st.title('Reddit Post Fetcher')

subreddits_input = st.text_input('Enter subreddits (comma-separated)')
users_input = st.text_input('Enter usernames (comma-separated)')
top = st.number_input("Top", min_value=1, max_value=100, value=5)

if st.button('Fetch Posts'):
    if not subreddits_input:
        st.warning('Please enter subreddits')
        st.stop()
    
    if not users_input:
        st.warning('Please enter usernames')
        st.stop()

    subreddits = [s.strip() for s in subreddits_input.replace(" ", "").split(",")]
    users = set([u.strip() for u in users_input.replace(" ", "").split(",")])
    
    with st.spinner('Fetching posts...'):
        posts = fetch_posts(subreddits, users, top)
    
    if posts:
        st.success(f'Found {len(posts)} posts')
        for post in posts:
            st.markdown(f"### [{post['title']}]({post['url']})")
            st.write(f"Subreddit: r/{post['subreddit']}")
            st.write(f"Author: {post['author']}")
            st.write(f"Upvotes: {post['upvotes']}")
            st.write('---')
    else:
        st.warning('No posts found')