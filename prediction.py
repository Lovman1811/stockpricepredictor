import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date, datetime
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
from prophet.diagnostics import cross_validation, performance_metrics
from plotly import graph_objs as go
from database import save_prediction, add_favorite, remove_favorite, get_favorites

# Stock List Data
STOCK_LIST = {
    "NSE (India)": [
        ("RELIANCE.NS", "Reliance Industries"),
        ("TCS.NS", "Tata Consultancy Services"),
        ("INFY.NS", "Infosys"),
        ("HDFCBANK.NS", "HDFC Bank"),
        ("ASIANPAINT.NS", "Asian Paints")
    ],
    "BSE (India)": [
        ("TATAMOTORS.BO", "Tata Motors"),
        ("SBIN.BO", "State Bank of India"),
        ("LT.BO", "Larsen & Toubro"),
        ("ITC.BO", "ITC Limited"),
        ("MARUTI.BO", "Maruti Suzuki")
    ],
    "NASDAQ (US)": [
        ("AAPL", "Apple Inc"),
        ("GOOGL", "Alphabet Inc (Google)"),
        ("AMZN", "Amazon.com"),
        ("MSFT", "Microsoft"),
        ("TSLA", "Tesla Inc")
    ],
    "NYSE (US)": [
        ("JPM", "JPMorgan Chase"),
        ("V", "Visa Inc"),
        ("WMT", "Walmart"),
        ("BA", "Boeing"),
        ("DIS", "Walt Disney")
    ]
}


# Data Loading and Processing
@st.cache_data(ttl=3600)
def get_stock_data(symbol, start, end):
    try:
        if "." not in symbol:
            st.warning("⚠️ For Indian stocks, use exchange suffix (.NS for NSE/.BO for BSE)")

        stock = yf.Ticker(symbol)

        if ".NS" in symbol or ".BO" in symbol:
            if not stock.info.get('currency') == 'INR':
                st.error("₹ Invalid Indian stock symbol - check exchange suffix")
                return pd.DataFrame()

        data = yf.download(symbol, start, end)
        if data.empty:
            st.error("No data available for selected dates")
            return pd.DataFrame()

        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Data loading error: {str(e)}")
        return pd.DataFrame()


# Prediction Page
def show_prediction_page():


    st.markdown("<h1 class='page-title'>📈 Stock Price Prediction</h1>", unsafe_allow_html=True)

    # Create two columns - parameters on left, chart on right
    col1, col2 = st.columns([1, 3])

    with col1:
        with st.container():
            st.markdown("<div class='panel'><h3>Parameters</h3>", unsafe_allow_html=True)

            # Create flattened list of stocks with market prefixes
            stock_options = []
            for market, stocks in STOCK_LIST.items():
                for symbol, name in stocks:
                    stock_options.append(f"{market}: {name} ({symbol})")

            # Add custom option at start
            stock_options.insert(0, "Custom Symbol (Enter Manually)")

            # Stock selection dropdown
            selected_stock = st.selectbox(
                "Select or Search Stock",
                options=stock_options,
                index=0,
                help="Select from popular stocks or choose custom to enter manually"
            )

            # Handle custom symbol input
            if selected_stock == "Custom Symbol (Enter Manually)":
                ticker = st.text_input(
                    "Enter Stock Symbol",
                    value="RELIANCE.NS",
                    placeholder="E.g.: AAPL, RELIANCE.NS, TCS.BO",
                    help="For Indian stocks use .NS (NSE) or .BO (BSE) suffix"
                ).upper()
            else:
                # Extract symbol from selected option
                ticker = selected_stock.split("(")[-1].split(")")[0].strip()

            st.markdown(f"<div class='selected-symbol'><b>Selected Symbol:</b> {ticker}</div>", unsafe_allow_html=True)

            # Rest of the parameters remain the same
            col_a, col_b = st.columns(2)
            with col_a:
                start_date = st.date_input("Start date", value=date(2015, 1, 1), key="prediction_start_date")
            with col_b:
                end_date = st.date_input("End date", value=date.today(), key="prediction_end_date")

            forecast_days = st.slider(
                "Forecast period (days)",
                min_value=30,
                max_value=365,
                value=90,
                key="prediction_forecast_days"
            )

            confidence_level = st.slider(
                "Confidence interval",
                0.7, 0.99, 0.95,
                key="prediction_confidence_level"
            )

            if st.button("Predict", key="predict_button", use_container_width=True):
                st.session_state.run_prediction = True
                st.session_state.prediction_ticker = ticker

            st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        if 'run_prediction' in st.session_state and st.session_state.run_prediction:
            ticker = st.session_state.prediction_ticker

            with st.spinner("🔍 Loading stock data..."):
                df = get_stock_data(ticker, start_date, end_date)

            if not df.empty:
                try:
                    prophet_df = df[['Date', 'Close']].copy()
                    prophet_df.columns = ['ds', 'y']
                    prophet_df['ds'] = pd.to_datetime(prophet_df['ds'], errors='coerce')
                    prophet_df['y'] = pd.to_numeric(prophet_df['y'], errors='coerce')
                    prophet_df = prophet_df.dropna()

                    if len(prophet_df) < 30:
                        st.error("❌ Minimum 30 days of valid data required")
                    else:
                        model = Prophet(
                            daily_seasonality=False,
                            yearly_seasonality=True,
                            weekly_seasonality=True,
                            seasonality_mode='multiplicative',
                            interval_width=confidence_level
                        )

                        with st.spinner("🧠 Training prediction model..."):
                            model.fit(prophet_df)

                        future = model.make_future_dataframe(periods=forecast_days)

                        with st.spinner("🔮 Generating forecasts..."):
                            forecast = model.predict(future)

                        st.markdown(f"<h3 class='chart-title'>📈 {ticker} Price Forecast</h3>", unsafe_allow_html=True)

                        fig = plot_plotly(model, forecast)
                        fig.update_layout(
                            height=600,
                            xaxis_title="Date",
                            yaxis_title="Price (USD/INR)",
                            hovermode="x unified",
                            template='plotly_white'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        latest_pred = forecast.iloc[-1]
                        current_price = prophet_df['y'].iloc[-1]

                        # Create metrics row
                        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                        with metrics_col1:
                            st.metric("Current Price",
                                      f"₹{current_price:.2f}" if ".NS" in ticker or ".BO" in ticker else f"${current_price:.2f}")
                        with metrics_col2:
                            change = (latest_pred['yhat'] / current_price) - 1
                            st.metric(
                                "Predicted Price",
                                f"₹{latest_pred['yhat']:.2f}" if ".NS" in ticker or ".BO" in ticker else f"${latest_pred['yhat']:.2f}",
                                delta=f"{change:.2%}"
                            )
                        with metrics_col3:
                            st.metric(
                                "Confidence Range",
                                f"₹{latest_pred['yhat_lower']:.2f}-₹{latest_pred['yhat_upper']:.2f}"
                                if ".NS" in ticker or ".BO" in ticker
                                else f"${latest_pred['yhat_lower']:.2f}-${latest_pred['yhat_upper']:.2f}"
                            )

                        if st.session_state.user_id:
                            save_prediction(
                                st.session_state.user_id,
                                ticker,
                                start_date.strftime("%Y-%m-%d"),
                                end_date.strftime("%Y-%m-%d"),
                                forecast_days,
                                confidence_level,
                                forecast
                            )

                            favorites = get_favorites(st.session_state.user_id)
                            if ticker in favorites:
                                if st.button(f"⭐ Remove {ticker} from Favorites"):
                                    remove_favorite(st.session_state.user_id, ticker)
                                    st.rerun()
                            else:
                                if st.button(f"⭐ Add {ticker} to Favorites"):
                                    add_favorite(st.session_state.user_id, ticker)
                                    st.rerun()

                        # Tabbed sections for details
                        tab1, tab2, tab3 = st.tabs(["Forecast Components", "Model Performance", "Export Data"])

                        with tab1:
                            components_fig = plot_components_plotly(model, forecast)
                            st.plotly_chart(components_fig)

                        with tab2:
                            try:
                                df_cv = cross_validation(
                                    model,
                                    initial='730 days',
                                    period='180 days',
                                    horizon='90 days'
                                )
                                df_p = performance_metrics(df_cv)

                                perf_col1, perf_col2, perf_col3 = st.columns(3)
                                perf_col1.metric("MAE",
                                                 f"₹{df_p['mae'].mean():.2f}" if ".NS" in ticker or ".BO" in ticker else f"${df_p['mae'].mean():.2f}")
                                perf_col2.metric("RMSE",
                                                 f"₹{df_p['rmse'].mean():.2f}" if ".NS" in ticker or ".BO" in ticker else f"${df_p['rmse'].mean():.2f}")
                                perf_col3.metric("MAPE", f"{df_p['mape'].mean():.2%}")

                                error_fig = go.Figure()
                                error_fig.add_trace(go.Scatter(
                                    x=df_cv['ds'], y=df_cv['yhat'], name='Predicted'
                                ))
                                error_fig.add_trace(go.Scatter(
                                    x=df_cv['ds'], y=df_cv['y'], name='Actual'
                                ))
                                error_fig.update_layout(title="Backtesting Results")
                                st.plotly_chart(error_fig)
                            except Exception as e:
                                st.warning(f"Performance analysis failed: {str(e)}")

                        with tab3:
                            csv = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_csv(index=False)
                            st.download_button(
                                label="Download Forecast CSV",
                                data=csv,
                                file_name=f"{ticker}_forecast.csv",
                                mime="text/csv"
                            )

                except Exception as e:
                    st.error(f"❌ Prediction failed: {str(e)}")
        else:
            st.info("Please configure your prediction parameters and click 'Predict'")