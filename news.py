import streamlit as st
import requests
from prediction import STOCK_LIST

# News API Key
NEWS_API_KEY = "a223e9edb806410fa167eef7d26d4955"


def get_company_news(company_name):
    """Fetch news articles for a given company using News API"""
    url = f"https://newsapi.org/v2/everything?q={company_name}&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        return []


def show_news_page():
    st.markdown("<h1 class='page-title'>📰 Stock-Specific News Dashboard</h1>", unsafe_allow_html=True)

    # Market and company selection
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        market = st.selectbox("Select Market", list(STOCK_LIST.keys()))
        stocks = STOCK_LIST[market]
        company_names = [name for _, name in stocks]
        selected_company = st.selectbox("Select Company", company_names)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # Fetch and display news
        st.markdown(f"<h3 class='section-title'>Latest News: {selected_company}</h3>", unsafe_allow_html=True)

        with st.spinner("Fetching news..."):
            news_articles = get_company_news(selected_company)

        if news_articles:
            for article in news_articles:
                with st.container():
                    st.markdown(f"""
                    <div class="news-card" style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 24px; transition: transform 0.3s ease, box-shadow 0.3s ease; overflow: hidden; display: flex; flex-direction: column; height: 100%;">
    <div class="news-card-content" style="padding: 20px; flex-grow: 1; display: flex; flex-direction: column;">
        <h4 style="font-size: 18px; font-weight: 600; color: #2c3e50; margin-top: 0; margin-bottom: 12px; line-height: 1.4;">{article["title"]}</h4>
        <p style="font-size: 14px; color: #596275; line-height: 1.6; margin-bottom: 16px; flex-grow: 1;">{article["description"]}</p>
        <a href="{article['url']}" target="_blank" style="display: inline-block; background-color: #007bff; color: white; text-decoration: none; padding: 8px 16px; border-radius: 4px; font-weight: 500; font-size: 14px; margin-bottom: 16px; align-self: flex-start; transition: background-color 0.2s ease;">Read more</a>
        <div class="news-source" style="font-size: 12px; color: #8395a7; display: flex; justify-content: space-between; border-top: 1px solid #f1f2f6; padding-top: 12px;">
            <span style="display: flex; align-items: center;">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 5px;">
                    <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                </svg>
                Source: {article.get('source', {}).get('name', 'Unknown')}
            </span>
            <span style="display: flex; align-items: center;">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 5px;">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                Published: {article.get('publishedAt', 'Unknown date').split('T')[0]}
            </span>
        </div>
    </div>
</div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No news articles found or API limit reached.")
