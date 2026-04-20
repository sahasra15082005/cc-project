import os
from datetime import datetime, timezone

import boto3
import pandas as pd
import plotly.express as px
import streamlit as st
from botocore.exceptions import BotoCoreError, ClientError

st.set_page_config(
    page_title="Smart Expense Analyzer",
    page_icon="💰",
    layout="wide"
)

st.title("Smart Expense Analyzer")
st.markdown("Analyze your expenses quickly and clearly in Indian Rupees (₹)")

category_keywords = {
    "food": "Food",
    "grocery": "Food",
    "supermarket": "Food",
    "restaurant": "Food",
    "salary": "Income",
    "pay": "Income",
    "bonus": "Income",
    "freelance": "Income",
    "rent": "Housing",
    "electricity": "Utilities",
    "water": "Utilities",
    "internet": "Utilities",
    "fuel": "Transportation",
    "taxi": "Transportation",
    "uber": "Transportation",
    "bus": "Transportation",
    "train": "Transportation",
    "movie": "Entertainment",
    "netflix": "Entertainment",
    "shopping": "Shopping",
    "clothing": "Shopping",
    "pharmacy": "Health",
    "medical": "Health",
    "doctor": "Health",
    "travel": "Travel",
    "flight": "Travel",
    "hotel": "Travel",
}


def format_inr(amount: float) -> str:
    rounded = round(amount)
    return f"₹{rounded:,.0f}"


def get_s3_settings() -> dict:
    return {
        "enabled": os.getenv("ENABLE_S3_ARCHIVE", "false").lower() == "true",
        "bucket": os.getenv("S3_BUCKET_NAME", "").strip(),
        "region": os.getenv("AWS_REGION", "").strip() or None,
        "upload_prefix": os.getenv("S3_UPLOAD_PREFIX", "uploads").strip("/") or "uploads",
        "report_prefix": os.getenv("S3_REPORT_PREFIX", "reports").strip("/") or "reports",
    }


@st.cache_resource
def get_s3_client(region_name: str | None):
    return boto3.client("s3", region_name=region_name)


def upload_bytes_to_s3(file_bytes: bytes, object_name: str, prefix: str, content_type: str) -> tuple[bool, str]:
    settings = get_s3_settings()
    if not settings["enabled"]:
        return False, "S3 archiving is disabled."
    if not settings["bucket"]:
        return False, "S3_BUCKET_NAME is not configured."

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    object_key = f"{prefix}/{timestamp}-{object_name}"

    try:
        client = get_s3_client(settings["region"])
        client.put_object(
            Bucket=settings["bucket"],
            Key=object_key,
            Body=file_bytes,
            ContentType=content_type,
        )
        return True, object_key
    except (BotoCoreError, ClientError) as exc:
        return False, str(exc)


def infer_category(description: str) -> str:
    text = str(description).lower()
    for keyword, category in category_keywords.items():
        if keyword in text:
            return category
    return "Other"

with st.sidebar:
    st.header("Upload CSV")
    uploaded_file = st.file_uploader("Choose your transaction file", type="csv")
    st.markdown("---")
    st.markdown("**CSV format required**")
    st.markdown(
        "`date,description,amount,category`  \nAmount positive = expense, negative = income"
    )
    st.markdown("**Example:** `2023-01-01,Groceries,1200,Food`")
    s3_settings = get_s3_settings()
    if s3_settings["enabled"]:
        st.markdown("---")
        st.markdown("**AWS archiving**")
        st.caption(
            f"Files and reports will be copied to s3://{s3_settings['bucket'] or 'configure-bucket-name'}"
        )

if uploaded_file is not None:
    try:
        uploaded_file_bytes = uploaded_file.getvalue()
        df = pd.read_csv(uploaded_file)
        required_cols = ["date", "description", "amount", "category"]
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            st.error(f"Missing columns: {', '.join(missing)}")
            st.stop()

        df = df[required_cols].copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df = df.dropna(subset=["date", "amount"])

        df["category"] = df["category"].fillna("").astype(str).str.strip()
        missing_category = df["category"] == ""
        if missing_category.any():
            df.loc[missing_category, "category"] = df.loc[missing_category, "description"].apply(infer_category)
        df.loc[df["category"] == "", "category"] = "Other"

        expenses = df[df["amount"] > 0].copy()
        incomes = df[df["amount"] < 0].copy()

        total_expense = expenses["amount"].sum()
        total_income = abs(incomes["amount"].sum())
        net_balance = total_income - total_expense
        transaction_count = len(df)
        categories_used = df["category"].nunique()

        if not expenses.empty:
            cat_exp = expenses.groupby("category")["amount"].sum().sort_values(ascending=False)
            expenses["month"] = expenses["date"].dt.to_period("M")
            monthly_exp = (
                expenses.groupby("month", sort=True)["amount"]
                .sum()
                .reset_index()
                .sort_values("month")
            )
            monthly_exp["month"] = monthly_exp["month"].astype(str)
        else:
            cat_exp = pd.Series(dtype="float64")
            monthly_exp = pd.DataFrame(columns=["month", "amount"])

        st.subheader("Overview")
        col1, col2, col3, col4 = st.columns(4, gap="large")
        with col1:
            st.write(f"**Income**")
            st.write(f"# {format_inr(total_income)}")
        with col2:
            st.write(f"**Expense**")
            st.write(f"# {format_inr(total_expense)}")
        with col3:
            st.write(f"**Balance**")
            st.write(f"# {format_inr(net_balance)}")
        with col4:
            st.write(f"**Transactions**")
            st.write(f"# {transaction_count}")

        st.markdown("---")
        if expenses.empty:
            st.warning("No expense rows found. Make sure positive amounts represent expenses.")
        else:
            chart_cols = st.columns(2)
            with chart_cols[0]:
                st.write("### Expense by Category")
                fig1 = px.bar(
                    cat_exp,
                    x=cat_exp.index,
                    y=cat_exp.values,
                    labels={"x": "Category", "y": "Amount (₹)"},
                    title="Category-wise Expense",
                )
                fig1.update_layout(xaxis_title=None, yaxis_title="Amount (₹)")
                st.plotly_chart(fig1, use_container_width=True)

            with chart_cols[1]:
                st.write("### Trend by Month")
                if not monthly_exp.empty:
                    fig2 = px.line(
                        monthly_exp,
                        x="month",
                        y="amount",
                        labels={"month": "Month", "amount": "Amount (₹)"},
                        title="Monthly Expense Trend",
                    )
                    fig2.update_layout(xaxis_title=None, yaxis_title="Amount (₹)")
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Not enough monthly expense data to display a trend.")

            st.write("### Category Distribution")
            fig3 = px.pie(
                cat_exp,
                names=cat_exp.index,
                values=cat_exp.values,
                title="Expense Distribution by Category",
            )
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown("---")
        st.subheader("Smart Insights")
        insights = []

        if total_expense > total_income and total_income > 0:
            insights.append("⚠️ You are spending more than you earn.")
        elif total_income == 0:
            insights.append("ℹ️ No income detected, so total expenses are shown without earnings.")
        else:
            insights.append("✅ Your income covers your expenses.")

        if total_expense > 0 and not cat_exp.empty:
            top_cat = cat_exp.idxmax()
            top_cat_share = cat_exp.iloc[0] / total_expense
            insights.append(f"💰 Highest spending is in {top_cat}.")
            if top_cat_share > 0.4:
                insights.append(f"🚨 {top_cat} accounts for {top_cat_share:.0%} of your expenses.")

        if len(monthly_exp) > 1:
            first_value = float(monthly_exp.iloc[0]["amount"])
            last_value = float(monthly_exp.iloc[-1]["amount"])
            if first_value != 0 and last_value > first_value:
                increase_pct = (last_value - first_value) / first_value * 100
                insights.append(f"📈 Expenses rose by {increase_pct:.1f}% from first to last month.")
            else:
                insights.append("📉 Your monthly expense trend is stable or improving.")

        for insight in insights:
            st.write(insight)

        if s3_settings["enabled"]:
            st.markdown("---")
            st.subheader("AWS Archive")
            upload_ok, upload_result = upload_bytes_to_s3(
                file_bytes=uploaded_file_bytes,
                object_name=uploaded_file.name,
                prefix=s3_settings["upload_prefix"],
                content_type="text/csv",
            )
            if upload_ok:
                st.success(f"Uploaded source CSV to s3://{s3_settings['bucket']}/{upload_result}")
            else:
                st.warning(f"CSV archive skipped: {upload_result}")

        st.markdown("---")
        st.subheader("Expense Health Score")
        health_score = 100
        if total_expense > total_income:
            health_score -= 30
        if not cat_exp.empty and cat_exp.iloc[0] > 0.4 * total_expense:
            health_score -= 20
        health_score = max(0, min(100, health_score))

        score_col, message_col = st.columns([1, 2])
        score_col.metric("Health Score", f"{health_score}/100")
        if health_score >= 80:
            message_col.success("Good job! Keep tracking expenses and saving more.")
        elif health_score >= 50:
            message_col.warning("Moderate health. Review big categories and control overspending.")
        else:
            message_col.error("Financial health is weak. Cut big spending and improve savings.")

        if insights:
            report_text = "\n".join(insights)
            st.download_button(
                label="Download Insights Report",
                data=report_text,
                file_name="expense_insights.txt",
                mime="text/plain",
            )
            if s3_settings["enabled"]:
                report_ok, report_result = upload_bytes_to_s3(
                    file_bytes=report_text.encode("utf-8"),
                    object_name="expense_insights.txt",
                    prefix=s3_settings["report_prefix"],
                    content_type="text/plain",
                )
                if report_ok:
                    st.success(f"Uploaded insights report to s3://{s3_settings['bucket']}/{report_result}")
                else:
                    st.warning(f"Report archive skipped: {report_result}")

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.info("Please verify the CSV fields and try again.")
else:
    uploaded_file = None
    st.info("Upload a CSV file using the sidebar to start analysis.")
    st.write("Upload should include columns: date, description, amount, category.")
    st.write("Amounts should be positive for expenses and negative for income.")
