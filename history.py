import streamlit as st
import pandas as pd
from io import StringIO
from plotly import graph_objs as go
from database import get_user_predictions, delete_prediction


def show_history_page():
    st.markdown("<h1 class='page-title'>📚 Prediction History</h1>", unsafe_allow_html=True)

    if st.session_state.user_id:
        predictions = get_user_predictions(st.session_state.user_id)

        if predictions:
            for pred in predictions:
                try:
                    forecast_data = pd.read_json(StringIO(pred[7]))

                    # Create a card for each prediction
                    st.markdown(f"""
                    <div class="history-card">
                        <div class="history-header">
                            <h3>{pred[2]}</h3>
                            <span class="history-date">{pred[8].split()[0]}</span>
                        </div>
                        <div class="history-details">
                            <span>Period: {pred[3]} to {pred[4]}</span>
                            <span>Forecast: {pred[5]} days</span>
                            <span>Confidence: {pred[6] * 100:.1f}%</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Mini chart
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=forecast_data['ds'],
                        y=forecast_data['yhat'],
                        name='Predicted',
                        line=dict(color='#1f77b4')
                    ))
                    fig.add_trace(go.Scatter(
                        x=forecast_data['ds'],
                        y=forecast_data['yhat_lower'],
                        fill=None,
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False
                    ))
                    fig.add_trace(go.Scatter(
                        x=forecast_data['ds'],
                        y=forecast_data['yhat_upper'],
                        fill='tonexty',
                        mode='lines',
                        line=dict(width=0),
                        name='Confidence Interval',
                        fillcolor='rgba(31, 119, 180, 0.2)'
                    ))
                    fig.update_layout(
                        height=200,
                        margin=dict(l=0, r=0, t=0, b=0),
                        showlegend=False,
                        xaxis=dict(
                            showgrid=False,
                            zeroline=False
                        ),
                        yaxis=dict(
                            showgrid=False,
                            zeroline=False
                        ),
                        plot_bgcolor='white'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("View Details", key=f"view_{pred[0]}"):
                            st.session_state.prediction_ticker = pred[2]
                            st.session_state.active_tab = "📊 Stock Prediction"
                            st.session_state.run_prediction = True
                            st.rerun()
                    with col2:
                        if st.button("Delete", key=f"delete_{pred[0]}"):
                            success = delete_prediction(pred[0], st.session_state.user_id)
                            if success:
                                st.success(f"Deleted prediction for {pred[2]}")
                                st.rerun()
                            else:
                                st.error("Failed to delete prediction")

                    st.markdown("<hr>", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error loading prediction {pred[0]}: {str(e)}")
        else:
            st.info("No prediction history found")
            # Suggest making a prediction
            st.markdown("""
            <div class="info-card">
                <h3>Make your first prediction</h3>
                <p>Head over to the Stock Prediction tab to analyze your first stock!</p>
                <button id="go-to-predict" class="streamlit-button primary">Start Predicting</button>
            </div>
            """, unsafe_allow_html=True)

            # Since HTML button can't trigger Python, add a regular button
            if st.button("Start Predicting"):
                st.session_state.active_tab = "📊 Stock Prediction"
                st.rerun()
    else:
        st.error("Please login to view history")
