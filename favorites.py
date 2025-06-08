import streamlit as st
import yfinance as yf
from database import get_favorites, remove_favorite
from prediction import STOCK_LIST


def show_favorites_page():
    st.markdown(
        """
        <style>
        .page-title {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 1rem;
            text-align: center;
        }
        .favorites-container {
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
            justify-content: center;
            padding: 1rem 0;
        }
        .favorite-card {
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            padding: 1rem 1.5rem;
            width: 280px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .favorite-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        .favorite-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }
        .favorite-header h3 {
            margin: 0;
            font-size: 1.5rem;
            color: #34495e;
        }
        .exchange-badge {
            background-color: #3498db;
            color: white;
            font-size: 0.85rem;
            font-weight: 600;
            padding: 0.25rem 0.6rem;
            border-radius: 20px;
            user-select: none;
        }
        .stock-suggestion {
            background: #f9f9f9;
            border-radius: 10px;
            padding: 0.8rem 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            text-align: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            cursor: default;
            transition: background-color 0.3s ease;
        }
        .stock-suggestion:hover {
            background-color: #e1f0ff;
        }
        .stock-suggestion h4 {
            margin: 0 0 0.3rem 0;
            font-size: 1.1rem;
            color: #2c3e50;
        }
        .stock-suggestion .symbol {
            font-size: 0.9rem;
            color: #7f8c8d;
            margin: 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h1 class='page-title'>⭐ Favorite Stocks</h1>", unsafe_allow_html=True)

    if st.session_state.user_id:
        favorites = get_favorites(st.session_state.user_id)

        if favorites:
            st.markdown("<div class='favorites-container'>", unsafe_allow_html=True)
            for symbol in favorites:
                exchange = ""
                if ".NS" in symbol:
                    exchange = "🇮🇳 NSE"
                elif ".BO" in symbol:
                    exchange = "🇮🇳 BSE"
                else:
                    exchange = "🌎 International"

                st.markdown(f"""
                <div class="favorite-card">
                    <div class="favorite-header">
                        <h3>{symbol.split('.')[0]}</h3>
                        <span class="exchange-badge">{exchange}</span>
                    </div>
                """, unsafe_allow_html=True)

                try:
                    stock = yf.Ticker(symbol)
                    info = stock.info

                    if 'regularMarketPrice' in info:
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric(
                                "Price",
                                f"₹{info.get('regularMarketPrice', 'N/A'):.2f}" if exchange.startswith(
                                    "🇮🇳") else f"${info.get('regularMarketPrice', 'N/A'):.2f}"
                            )
                        with col2:
                            st.metric(
                                "Change",
                                f"{info.get('regularMarketChangePercent', 'N/A'):.2f}%",
                                f"{info.get('regularMarketChange', 'N/A'):.2f}"
                            )
                        with col3:
                            st.metric(
                                "Open",
                                f"₹{info.get('regularMarketOpen', 'N/A'):.2f}" if exchange.startswith(
                                    "🇮🇳") else f"${info.get('regularMarketOpen', 'N/A'):.2f}"
                            )
                        with col4:
                            st.metric(
                                "Volume",
                                f"{info.get('regularMarketVolume', 'N/A'):,}"
                            )

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Predict", key=f"quick_predict_{symbol}"):
                                st.session_state.prediction_ticker = symbol
                                st.session_state.active_tab = "📊 Stock Prediction"
                                st.session_state.run_prediction = True
                                st.rerun()

                        with col2:
                            if st.button(f"Remove", key=f"remove_{symbol}"):
                                remove_favorite(st.session_state.user_id, symbol)
                                st.success(f"Removed {symbol} from favorites")
                                st.rerun()
                    else:
                        st.warning(f"No data available for {symbol}")

                except Exception as e:
                    st.error(f"Error loading data for {symbol}: {str(e)}")

                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("You haven't added any favorite stocks yet.")

            # Suggest popular stocks
            st.markdown("<h3>Popular Stocks</h3>", unsafe_allow_html=True)
            st.markdown("Here are some popular stocks you might want to follow:")

            # Create tabs for different markets
            market_tabs = st.tabs(list(STOCK_LIST.keys()))

            for i, market in enumerate(STOCK_LIST.keys()):
                with market_tabs[i]:
                    stocks = STOCK_LIST[market]
                    cols = st.columns(3)
                    for idx, (symbol, name) in enumerate(stocks):
                        with cols[idx % 3]:
                            st.markdown(f"""
                            <div class="stock-suggestion">
                                <h4>{name}</h4>
                                <p class="symbol">{symbol}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            if st.button(f"Add to Favorites", key=f"add_{symbol}"):
                                from database import add_favorite
                                add_favorite(st.session_state.user_id, symbol)
                                st.success(f"Added {symbol} to favorites")
                                st.rerun()
    else:
        st.error("Please login to view favorites")
