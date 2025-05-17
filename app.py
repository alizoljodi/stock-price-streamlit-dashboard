import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io

def check_rows(df):
    """
    Validates and cleans the dataframe by:
    1. Checking for null values
    2. Validating date format
    3. Validating price values (must be numeric and positive)
    Returns the cleaned dataframe and any validation messages
    """
    original_rows = len(df)
    messages = []
    
    # Check for null values
    null_rows = df.isnull().any(axis=1)
    if null_rows.any():
        df = df.dropna()
        messages.append(f"Removed {null_rows.sum()} rows with null values")
    
    # Validate date column
    try:
        df['Date'] = pd.to_datetime(df['Date'])
    except Exception as e:
        messages.append(f"Error converting dates: {str(e)}")
        return None, messages
    
    # Validate price column
    try:
        # Convert price to numeric, coercing errors to NaN
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        # Remove rows with negative or zero prices
        invalid_prices = (df['Price'] <= 0) | df['Price'].isna()
        if invalid_prices.any():
            df = df[~invalid_prices]
            messages.append(f"Removed {invalid_prices.sum()} rows with invalid prices")
    except Exception as e:
        messages.append(f"Error processing prices: {str(e)}")
        return None, messages
    
    # Add summary message
    removed_rows = original_rows - len(df)
    if removed_rows > 0:
        messages.append(f"Total rows removed: {removed_rows}")
    
    return df, messages

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
        validation_messages = {}
        
        # Read each sheet
        for sheet in sheet_names:
            df = pd.read_excel(uploaded_file, sheet_name=sheet)
            # Ensure the dataframe has the required columns
            if 'Date' in df.columns and 'Price' in df.columns:
                # Validate and clean the data
                cleaned_df, messages = check_rows(df)
                if cleaned_df is not None:
                    dfs[sheet] = cleaned_df
                    validation_messages[sheet] = messages
                else:
                    st.error(f"Sheet '{sheet}' has invalid data: {'; '.join(messages)}")
            else:
                st.warning(f"Sheet '{sheet}' does not contain required 'Date' and 'Price' columns")
        
        if dfs:
            # Display validation messages
            for sheet, messages in validation_messages.items():
                if messages:
                    with st.expander(f"Data Validation Results for {sheet}"):
                        for msg in messages:
                            st.info(msg)
            
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
                current_price = df['Price'].iloc[-1]
                st.metric("Current Price", f"${current_price:.2f}")
            
            with col2:
                price_change = df['Price'].iloc[-1] - df['Price'].iloc[0]
                st.metric("Total Change", f"${price_change:.2f}")
            
            with col3:
                percent_change = (price_change / df['Price'].iloc[0]) * 100
                st.metric("Percentage Change", f"{percent_change:.2f}%")
            
            # Create the main chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Price'],
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