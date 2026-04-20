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

## AWS Deployment

This repo now includes deployment support for:

- `EC2` to run the Streamlit app
- `S3` to archive uploaded CSV files and generated insight reports

Files added for AWS deployment:

- `deploy/AWS-DEPLOYMENT.md`
- `deploy/EC2-LAUNCH-CHECKLIST.md`
- `deploy/ec2-bootstrap.sh`
- `deploy/expense-analyzer.env.example`
- `deploy/expense-analyzer.service`
- `deploy/iam-policy-s3-template.json`
- `deploy/nginx-expense-analyzer.conf`
- `.streamlit/config.toml`

### S3 Archiving Configuration

The application supports optional S3 archiving through environment variables:

```bash
ENABLE_S3_ARCHIVE=true
S3_BUCKET_NAME=your-bucket-name
AWS_REGION=ap-south-1
S3_UPLOAD_PREFIX=uploads
S3_REPORT_PREFIX=reports
```

When enabled, the app uploads:

- the original CSV file the user uploads
- the generated insights report text file

Use an EC2 IAM role with S3 permissions instead of hardcoding AWS keys.

## Sample Data

Use `sample_expenses.csv` to test the application with sample rupee-based expenses.

## Analysis Rules

- **Overspending Warning**: Shown when total expenses exceed total income
- **High Category Spending**: Flags categories above 40% of total expenses
- **Health Score**: Starts at 100 and deducts points for risk factors
- **Trend Detection**: Shows whether monthly expenses are increasing or stable
