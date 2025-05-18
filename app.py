import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io
import yfinance as yf

# Define market indices
MARKET_INDICES = {
    'NASDAQ': '^IXIC',
    'DJIA': '^DJI',
    'S&P 500': '^GSPC',
    'Russell 2000': '^RUT',
    'FTSE 100': '^FTSE',
    'Shanghai Composite': '000001.SS'
}

def fetch_index_data(start_date, end_date):
    """
    Fetch data for all market indices for the given date range
    """
    index_data = {}
    for index_name, ticker in MARKET_INDICES.items():
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
            if not data.empty:
                # Rename columns to match our format
                data = data.reset_index()
                data = data.rename(columns={'Date': 'Date', 'Close': 'Price'})
                index_data[index_name] = data
        except Exception as e:
            st.warning(f"Could not fetch data for {index_name}: {str(e)}")
    return index_data

def check_rows(df):
    """
    Validates and cleans the dataframe by iterating through rows and checking:
    1. Null values
    2. Date format
    3. Price values (must be numeric and positive)
    Returns the cleaned dataframe and validation messages
    """
    original_rows = len(df)
    messages = []
    valid_rows = []
    invalid_rows = []
    
    # Iterate through each row
    for index, row in df.iterrows():
        is_valid = True
        row_messages = []
        
        # Check for null values
        if row.isnull().any():
            is_valid = False
            row_messages.append("Contains null values")
        
        # Validate date
        try:
            date_val = pd.to_datetime(row['Date'])
        except Exception:
            is_valid = False
            row_messages.append("Invalid date format")
        
        # Validate price
        try:
            price_val = pd.to_numeric(row['Price'], errors='coerce')
            if pd.isna(price_val) or price_val <= 0:
                is_valid = False
                row_messages.append("Invalid price value")
        except Exception:
            is_valid = False
            row_messages.append("Price is not numeric")
        
        # Store row based on validation
        if is_valid:
            valid_rows.append(row)
        else:
            invalid_rows.append({
                'index': index,
                'messages': row_messages
            })
    
    # Create new dataframe with only valid rows
    if valid_rows:
        cleaned_df = pd.DataFrame(valid_rows)
        # Ensure date column is datetime
        cleaned_df['Date'] = pd.to_datetime(cleaned_df['Date'])
        # Ensure price column is numeric
        cleaned_df['Price'] = pd.to_numeric(cleaned_df['Price'])
    else:
        return None, ["No valid rows found in the data"]
    
    # Generate validation messages
    if invalid_rows:
        messages.append(f"Removed {len(invalid_rows)} invalid rows:")
        for invalid in invalid_rows:
            messages.append(f"Row {invalid['index'] + 1}: {', '.join(invalid['messages'])}")
    
    # Add summary message
    removed_rows = original_rows - len(cleaned_df)
    if removed_rows > 0:
        messages.append(f"Total rows removed: {removed_rows}")
    
    return cleaned_df, messages

def prepare_candlestick_data(df):
    """
    Prepare OHLC data for candlestick chart by resampling daily data
    """
    # Set date as index for resampling
    df = df.set_index('Date')
    
    # Resample to daily OHLC
    ohlc = df['Price'].resample('D').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last'
    }).dropna()
    
    # Rename 'Close' to 'Price' to match the original data
    ohlc = ohlc.rename(columns={'Close': 'Price'})
    
    return ohlc

def create_line_chart(df, selected_stock, index_data=None):
    """
    Create a line chart visualization with optional market indices
    """
    fig = go.Figure()
    
    # Add main stock data
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Price'],
        mode='lines',
        name=selected_stock,
        line=dict(width=2)
    ))
    
    # Add market indices if available
    if index_data:
        for index_name, index_df in index_data.items():
            fig.add_trace(go.Scatter(
                x=index_df['Date'],
                y=index_df['Price'],
                mode='lines',
                name=index_name,
                line=dict(width=1, dash='dash'),
                opacity=0.7
            ))
    
    fig.update_layout(
        title=f"{selected_stock} Price History with Market Indices",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        hovermode='x unified',
        template='plotly_white',
        showlegend=True
    )
    
    return fig

def create_candlestick_chart(df, selected_stock, index_data=None):
    """
    Create a candlestick chart visualization with optional market indices
    """
    ohlc_data = prepare_candlestick_data(df)
    
    fig = go.Figure()
    
    # Add main stock candlestick
    fig.add_trace(go.Candlestick(
        x=ohlc_data.index,
        open=ohlc_data['Open'],
        high=ohlc_data['High'],
        low=ohlc_data['Low'],
        close=ohlc_data['Price'],
        name=selected_stock
    ))
    
    # Add market indices if available
    if index_data:
        for index_name, index_df in index_data.items():
            fig.add_trace(go.Scatter(
                x=index_df['Date'],
                y=index_df['Price'],
                mode='lines',
                name=index_name,
                line=dict(width=1, dash='dash'),
                opacity=0.7
            ))
    
    # Add volume bars at the bottom
    fig.add_trace(go.Bar(
        x=ohlc_data.index,
        y=ohlc_data['Price'] - ohlc_data['Open'],
        name='Volume',
        marker_color=['red' if price < open else 'green' 
                    for price, open in zip(ohlc_data['Price'], ohlc_data['Open'])],
        opacity=0.3
    ))
    
    fig.update_layout(
        title=f"{selected_stock} Price History with Market Indices",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        template='plotly_white',
        xaxis_rangeslider_visible=False,
        yaxis=dict(
            autorange=True,
            fixedrange=False
        ),
        showlegend=True
    )
    
    return fig

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
                #else:
                #    st.error(f"Sheet '{sheet}' has invalid data: {'; '.join(messages)}")
            #else:
            #    st.warning(f"Sheet '{sheet}' does not contain required 'Date' and 'Price' columns")
        
        if dfs:
            # Display validation messages
            '''for sheet, messages in validation_messages.items():
                if messages:
                    with st.expander(f"Data Validation Results for {sheet}"):
                        for msg in messages:
                            st.info(msg)'''
            
            # Sidebar controls
            st.sidebar.header("Chart Controls")
            
            # Stock selection
            selected_stock = st.sidebar.selectbox(
                "Select Stock",
                options=list(dfs.keys())
            )
            
            # Chart type selection
            chart_type = st.sidebar.radio(
                "Select Chart Type",
                options=["Line Chart", "Candlestick Chart"],
                index=0
            )
            
            # Market indices toggle
            show_indices = st.sidebar.checkbox("Show Market Indices", value=True)
            
            # Get the selected dataframe
            df = dfs[selected_stock]
            
            # Fetch market indices data if enabled
            index_data = None
            if show_indices:
                with st.spinner("Fetching market indices data..."):
                    start_date = df['Date'].min()
                    end_date = df['Date'].max()
                    index_data = fetch_index_data(start_date, end_date)
            
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
            
            # Create the selected chart type
            if chart_type == "Line Chart":
                fig = create_line_chart(df, selected_stock, index_data)
            else:
                fig = create_candlestick_chart(df, selected_stock, index_data)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display raw data
            st.subheader("Raw Data")
            st.dataframe(df)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    st.info("Please upload an Excel file to begin.") 