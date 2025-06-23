import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
from transformers import pipeline
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textblob import TextBlob

# Download necessary NLP resources
nltk.download('punkt')
nltk.download('stopwords')

# --- Load CSVs from GitHub ---
COMMENTS_URL = "https://raw.githubusercontent.com/sireeshy/gmat-reddit-analysis/refs/heads/master/gmat_comments.csv"
POSTS_URL = "https://raw.githubusercontent.com/sireeshy/gmat-reddit-analysis/refs/heads/master/gmat_posts.csv"

@st.cache_data
def load_data():
    comments = pd.read_csv(COMMENTS_URL)
    posts = pd.read_csv(POSTS_URL)
    return comments, posts

comments, posts = load_data()

# --- Text Cleaning ---
stop_words = set(stopwords.words('english'))
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\\S+|www\\S+|https\\S+", '', text)
    text = re.sub(r'\\@\\w+|\\#','', text)
    text = re.sub(r'[^a-zA-Z\\s]', '', text)
    tokens = word_tokenize(text)
    filtered = [w for w in tokens if w not in stop_words and len(w) > 2]
    return ' '.join(filtered)

comments['clean_body'] = comments['body'].apply(clean_text)

# --- UI Layout ---
st.set_page_config(page_title="GMAT Reddit Dashboard", layout="wide")
st.title("📊 GMAT Reddit Analysis Dashboard")
st.write("Insights from GMAT-related Reddit conversations including sentiment, section struggles, and summarized user pain points.")

# --- Section Tagging ---
section_keywords = {
    'Quant': ['quant', 'math', 'algebra', 'geometry', 'arithmetic', 'data sufficiency'],
    'Verbal': ['verbal', 'rc', 'reading comprehension', 'sentence correction', 'sc', 'cr', 'critical reasoning'],
    'Data Insights': ['data insights', 'di section', 'charts', 'tables', 'data interpretation', 'graphs', 'multi-source', 'di question']
}

for section, keywords in section_keywords.items():
    comments[section] = comments['clean_body'].apply(lambda x: 1 if any(kw in x for kw in keywords) else 0)

# --- Sidebar Filters ---
st.sidebar.title("🔎 Filters")
selected_section = st.sidebar.selectbox("Filter by GMAT Section", ["All"] + list(section_keywords.keys()))

filtered_comments = comments.copy()
if selected_section != "All":
    filtered_comments = comments[comments[selected_section] == 1]

# --- Sentiment Analysis ---
filtered_comments['sentiment'] = filtered_comments['clean_body'].apply(lambda text: TextBlob(text).sentiment.polarity)
filtered_comments['sentiment_label'] = filtered_comments['sentiment'].apply(lambda x: 'positive' if x > 0.1 else 'negative' if x < -0.1 else 'neutral')

st.subheader("💬 Sentiment Distribution")
sentiment_counts = filtered_comments['sentiment_label'].value_counts()
st.bar_chart(sentiment_counts)

# --- Section Mentions Chart ---
st.subheader("📘 GMAT Section Mentions")
section_counts = comments[['Quant', 'Verbal', 'Data Insights']].sum().sort_values(ascending=False)
st.bar_chart(section_counts)

# --- Word Cloud ---
st.subheader("🔤 Word Cloud")
all_words = ' '.join(filtered_comments['clean_body'])
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_words)
st.image(wordcloud.to_array())

# --- LLM Summarization with HuggingFace ---
st.subheader("🧠 AI Summary of Reddit Comments")
with st.spinner("Generating summary using BART model..."):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    sample_text = " ".join(filtered_comments['clean_body'].sample(n=min(30, len(filtered_comments)), random_state=42))
    if len(sample_text) > 4000:
        sample_text = sample_text[:4000]
    summary = summarizer(sample_text, max_length=120, min_length=30, do_sample=False)[0]['summary_text']
st.markdown(f"**Summary:** {summary}")
