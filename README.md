# Smart Expense Analyzer

A web application built with Python and Streamlit that analyzes financial transactions from CSV files, provides spending insights, and calculates an expense health score in Indian Rupees (₹).

## Features

- **File Upload**: Upload CSV files with transaction data
- **Data Processing**: Parses dates, amounts, and categories
- **Smart Category Guessing**: Fills missing categories using description keywords
- **Visualizations**: Expense charts for categories and monthly trend
- **Smart Insights**: Clear guidance on spending habits
- **Health Score**: Simplified financial health rating
- **Report Export**: Download insight summaries

## Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt`

## Installation

1. Open the project folder
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   streamlit run app.py
   ```

2. Open your browser to `http://localhost:8501`

3. Upload a CSV file with the following format:
   - Columns: `date`, `description`, `amount`, `category`
   - Date format: YYYY-MM-DD
   - Amount: positive values for expenses, negative for income

## CSV Example

```csv
date,description,amount,category
2023-01-01,Grocery shopping,1500,Food
2023-01-02,Salary,-30000,Income
2023-01-03,Restaurant dinner,750,Food
```

## Docker Support

Build and run with Docker:

```bash
docker build -t expense-analyzer .
docker run -p 8501:8501 expense-analyzer
```

## Sample Data

Use `sample_expenses.csv` to test the application with sample rupee-based expenses.

## Analysis Rules

- **Overspending Warning**: Shown when total expenses exceed total income
- **High Category Spending**: Flags categories above 40% of total expenses
- **Health Score**: Starts at 100 and deducts points for risk factors
- **Trend Detection**: Shows whether monthly expenses are increasing or stable