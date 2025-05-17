import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io

# Set page configuration
st.set_page_config(
    page_title="Stock Price Dashboard",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("📈 Stock Price Dashboard")
st.markdown("""
This dashboard allows you to upload an Excel file containing stock price data and visualize it interactively.
Each sheet in the Excel file should contain date and price information for different stocks.
""")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=['xlsx'])

if uploaded_file is not None:
    try:
        # Read all sheets from the Excel file
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        
        # Create a dictionary to store dataframes
        dfs = {}
        
        # Read each sheet
        for sheet in sheet_names:
            df = pd.read_excel(uploaded_file, sheet_name=sheet)
            # Ensure the dataframe has the required columns
            if 'date' in df.columns and 'price' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                dfs[sheet] = df
            else:
                st.warning(f"Sheet '{sheet}' does not contain required 'date' and 'price' columns")
        
        if dfs:
            # Sidebar for stock selection
            selected_stock = st.sidebar.selectbox(
                "Select Stock",
                options=list(dfs.keys())
            )
            
            # Get the selected dataframe
            df = dfs[selected_stock]
            
            # Create two columns for metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                current_price = df['price'].iloc[-1]
                st.metric("Current Price", f"${current_price:.2f}")
            
            with col2:
                price_change = df['price'].iloc[-1] - df['price'].iloc[0]
                st.metric("Total Change", f"${price_change:.2f}")
            
            with col3:
                percent_change = (price_change / df['price'].iloc[0]) * 100
                st.metric("Percentage Change", f"{percent_change:.2f}%")
            
            # Create the main chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['price'],
                mode='lines',
                name=selected_stock,
                line=dict(width=2)
            ))
            
            fig.update_layout(
                title=f"{selected_stock} Price History",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                hovermode='x unified',
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display raw data
            st.subheader("Raw Data")
            st.dataframe(df)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    st.info("Please upload an Excel file to begin.") 