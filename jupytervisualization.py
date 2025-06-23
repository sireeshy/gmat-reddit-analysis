import webbrowser
import os
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import base64
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO

# Download VADER sentiment lexicon
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# Load the dataset
posts = pd.read_csv(r'C:\Users\ysire\PycharmProjects\PythonProject\gmat_reddit_conversations.csv')
posts['selftext'] = posts['selftext'].fillna('')

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "GMAT Reddit Posts Dashboard"

# App layout
app.layout = html.Div([
    html.H1("GMAT Reddit Post Insights"),
    html.Div([
        html.Label("Filter by keyword:"),
        dcc.Input(id='keyword-input', type='text', value='', placeholder='Enter keyword...'),
        html.Label("Sentiment filter:"),
        dcc.Dropdown(
            id='sentiment-filter',
            options=[
                {'label': 'All', 'value': 'all'},
                {'label': 'Positive', 'value': 'positive'},
                {'label': 'Neutral', 'value': 'neutral'},
                {'label': 'Negative', 'value': 'negative'},
            ],
            value='all',
            clearable=False
    )
], style={'padding': '10px'}),
    dcc.Tabs([
        dcc.Tab(label='🔥 Top Posts by Score', children=[
            dcc.Graph(id='top-posts')
        ]),
        dcc.Tab(label='☁️ Word Cloud of Posts', children=[
            html.Img(id='wordcloud-img')
        ]),
        dcc.Tab(label='🧪 Sentiment Analysis', children=[
            dcc.Graph(id='post-sentiment-dist')
        ])
    ])
])

# Callbacks
@app.callback(
    Output('top-posts', 'figure'),
    Output('wordcloud-img', 'src'),
    Output('post-sentiment-dist', 'figure'),
    Input('keyword-input', 'value'),
    Input('sentiment-filter', 'value')
)
def update_dashboard(keyword, sentiment_filter):
    df = posts.copy()

    # Apply keyword filter
    if keyword:
        df = df[df['selftext'].str.contains(keyword, case=False, na=False)]

    # Sentiment classification
    df['sentiment'] = df['selftext'].apply(lambda x: sia.polarity_scores(x)['compound'])
    df['sentiment_label'] = df['sentiment'].apply(
        lambda s: 'positive' if s > 0.05 else 'negative' if s < -0.05 else 'neutral'
    )

    if sentiment_filter != 'all':
        df = df[df['sentiment_label'] == sentiment_filter]

    # Top posts
    top_posts = df.nlargest(10, 'score')
    top_fig = px.bar(top_posts, x='score', y='title', orientation='h', title='Top Reddit Posts by Score')

    # Word Cloud
    combined_text = ' '.join(df['selftext'].tolist())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(combined_text)
    img = BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    wordcloud_src = 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

    # Sentiment Distribution
    sentiment_fig = px.histogram(df, x='sentiment', nbins=20, title="Sentiment Distribution of Posts")

    return top_fig, wordcloud_src, sentiment_fig
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
webbrowser.get('edge').open("http://127.0.0.1:8050")
# Run the app
if __name__ == '__main__':
    app.run(debug=True)