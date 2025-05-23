# Stock Price Dashboard

A Streamlit application that creates an interactive dashboard for visualizing stock price data from Excel files.

## Features

- Upload Excel files containing stock price data
- Multiple sheets support (each sheet represents a different stock)
- Interactive price charts using Plotly
- Key metrics display (current price, total change, percentage change)
- Raw data table view
- Responsive and user-friendly interface

## Excel File Format

Your Excel file should follow this format:
- Each sheet should represent a different stock
- Each sheet must contain two columns:
  - `date`: The date of the price (will be automatically converted to datetime)
  - `price`: The stock price value

Example:
```
Sheet1 (AAPL):
date        | price
2024-01-01  | 150.25
2024-01-02  | 151.30
...

Sheet2 (MSFT):
date        | price
2024-01-01  | 280.50
2024-01-02  | 282.75
...
```

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

## Deployment on Streamlit Cloud

1. Push your code to a GitHub repository
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and connect it to your repository
4. Select the main file (app.py)
5. Deploy!

## Requirements

- Python 3.7+
- Dependencies listed in requirements.txt #   s t o c k - p r i c e - s t r e a m l i t - d a s h b o a r d 
 
 
change price
