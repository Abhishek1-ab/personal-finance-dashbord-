import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="💰",
    layout="wide"
)


# =========================================================
# CONSTANTS
# =========================================================

CATEGORIES_FILE = "categories.json"


# =========================================================
# CATEGORY FUNCTIONS
# =========================================================

def load_categories():
    default_categories = {
        "uncategorized": []
    }

    if os.path.exists(CATEGORIES_FILE):
        try:
            with open(CATEGORIES_FILE, "r") as f:
                data = json.load(f)

            if isinstance(data, dict):
                return data

        except Exception:
            pass

    return default_categories


def save_categories():
    with open(CATEGORIES_FILE, "w") as f:
        json.dump(
            st.session_state.categories,
            f,
            indent=4
        )


def categorize_transactions(df):
    """
    Automatically assigns categories
    using saved keywords.
    """

    df = df.copy()

    # Make sure Category column exists
    df["Category"] = "uncategorized"

    for category, keywords in st.session_state.categories.items():

        if category == "uncategorized":
            continue

        if not keywords:
            continue

        keywords = [
            str(keyword).lower().strip()
            for keyword in keywords
        ]

        for idx, row in df.iterrows():

            details = str(
                row.get("Details", "")
            ).lower().strip()

            if any(
                keyword in details
                for keyword in keywords
            ):
                df.at[idx, "Category"] = category

    return df


# =========================================================
# CSV PROCESSING
# =========================================================

def load_transactions(file):

    try:

        df = pd.read_csv(file)

        # Clean column names
        df.columns = [
            str(col).strip()
            for col in df.columns
        ]

        # Required columns
        required_columns = [
            "Date",
            "Details",
            "Amount",
            "Debit/Credit"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            st.error(
                "Missing columns: "
                + ", ".join(missing_columns)
            )

            st.info(
                "Required columns: "
                + ", ".join(required_columns)
            )

            return None

        # Clean Amount
        df["Amount"] = (
            df["Amount"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("AED", "", regex=False)
            .str.strip()
        )

        df["Amount"] = pd.to_numeric(
            df["Amount"],
            errors="coerce"
        )

        # Clean Date
        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce",
            format="mixed"
        )

        # Remove invalid rows
        df = df.dropna(
            subset=[
                "Date",
                "Amount"
            ]
        )

        # Clean Debit/Credit
        df["Debit/Credit"] = (
            df["Debit/Credit"]
            .astype(str)
            .str.strip()
            .str.title()
        )

        # Automatic categories
        df = categorize_transactions(df)

        return df

    except Exception as e:

        st.error(
            f"Error processing file: {e}"
        )

        return None


# =========================================================
# KEYWORD MANAGEMENT
# =========================================================

def add_keyword_to_category(
    category,
    keyword
):

    keyword = str(keyword).strip()

    if not keyword:
        return False

    if category not in st.session_state.categories:
        st.session_state.categories[category] = []

    if keyword not in st.session_state.categories[category]:

        st.session_state.categories[
            category
        ].append(keyword)

        save_categories()

        return True

    return False


# =========================================================
# DASHBOARD
# =========================================================

def show_dashboard(df):

    st.title("💰 Personal Finance Dashboard")

    st.caption(
        "Track income, expenses and spending categories"
    )

    # -----------------------------------------------------
    # Separate Debit / Credit
    # -----------------------------------------------------

    expenses_df = df[
        df["Debit/Credit"] == "Debit"
    ].copy()

    income_df = df[
        df["Debit/Credit"] == "Credit"
    ].copy()

    total_expense = expenses_df["Amount"].sum()
    total_income = income_df["Amount"].sum()
    balance = total_income - total_expense

    transaction_count = len(df)

    # -----------------------------------------------------
    # KPI CARDS
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💵 Total Income",
        f"AED {total_income:,.2f}"
    )

    col2.metric(
        "💸 Total Expense",
        f"AED {total_expense:,.2f}"
    )

    col3.metric(
        "💰 Balance",
        f"AED {balance:,.2f}"
    )

    col4.metric(
        "📋 Transactions",
        f"{transaction_count:,}"
    )

    st.divider()

    # =====================================================
    # FILTERS
    # =====================================================

    st.subheader("🔎 Filters")

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:

        min_date = df["Date"].min().date()
        max_date = df["Date"].max().date()

        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

    with filter_col2:

        transaction_type = st.multiselect(
            "Transaction Type",
            options=[
                "Debit",
                "Credit"
            ],
            default=[
                "Debit",
                "Credit"
            ]
        )

    with filter_col3:

        category_options = sorted(
            df["Category"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_categories = st.multiselect(
            "Category",
            options=category_options,
            default=category_options
        )

    # -----------------------------------------------------
    # Apply filters
    # -----------------------------------------------------

    filtered_df = df.copy()

    if len(date_range) == 2:

        start_date = pd.Timestamp(
            date_range[0]
        )

        end_date = pd.Timestamp(
            date_range[1]
        ) + pd.Timedelta(days=1)

        filtered_df = filtered_df[
            (filtered_df["Date"] >= start_date)
            & (filtered_df["Date"] < end_date)
        ]

    if transaction_type:

        filtered_df = filtered_df[
            filtered_df["Debit/Credit"].isin(
                transaction_type
            )
        ]

    if selected_categories:

        filtered_df = filtered_df[
            filtered_df["Category"].isin(
                selected_categories
            )
        ]

    st.write(
        f"Showing **{len(filtered_df)}** transactions"
    )

    # =====================================================
    # CHARTS
    # =====================================================

    chart_col1, chart_col2 = st.columns(2)

    # -----------------------------------------------------
    # Category Expense Chart
    # -----------------------------------------------------

    with chart_col1:

        st.subheader("📊 Expenses by Category")

        category_expenses = (
            filtered_df[
                filtered_df["Debit/Credit"] == "Debit"
            ]
            .groupby("Category")["Amount"]
            .sum()
            .reset_index()
        )

        if not category_expenses.empty:

            fig_category = px.pie(
                category_expenses,
                names="Category",
                values="Amount",
                hole=0.4,
                title="Expense Distribution"
            )

            st.plotly_chart(
                fig_category,
                use_container_width=True
            )

        else:

            st.info(
                "No expense data available."
            )

    # -----------------------------------------------------
    # Monthly Income / Expense
    # -----------------------------------------------------

    with chart_col2:

        st.subheader("📈 Monthly Cash Flow")

        monthly_df = filtered_df.copy()

        monthly_df["Month"] = (
            monthly_df["Date"]
            .dt.to_period("M")
            .astype(str)
        )

        monthly_summary = (
            monthly_df
            .groupby(
                ["Month", "Debit/Credit"]
            )["Amount"]
            .sum()
            .reset_index()
        )

        if not monthly_summary.empty:

            fig_monthly = px.bar(
                monthly_summary,
                x="Month",
                y="Amount",
                color="Debit/Credit",
                barmode="group",
                title="Monthly Income vs Expense"
            )

            st.plotly_chart(
                fig_monthly,
                use_container_width=True
            )

        else:

            st.info(
                "No monthly data available."
            )

    # =====================================================
    # TRANSACTION TABLE
    # =====================================================

    st.divider()

    st.subheader("📋 Transactions")

    display_columns = [
        "Date",
        "Details",
        "Amount",
        "Debit/Credit",
        "Category"
    ]

    available_columns = [
        col
        for col in display_columns
        if col in filtered_df.columns
    ]

    st.dataframe(
        filtered_df[
            available_columns
        ].sort_values(
            "Date",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# CATEGORY MANAGEMENT
# =========================================================

def category_management():

    st.subheader("🗂️ Category Management")

    col1, col2 = st.columns(2)

    with col1:

        st.write("### Add New Category")

        new_category = st.text_input(
            "Category Name",
            key="new_category"
        )

        if st.button(
            "➕ Add Category"
        ):

            new_category = new_category.strip()

            if not new_category:

                st.warning(
                    "Please enter a category name."
                )

            elif new_category in st.session_state.categories:

                st.warning(
                    "Category already exists."
                )

            else:

                st.session_state.categories[
                    new_category
                ] = []

                save_categories()

                st.success(
                    f"Category '{new_category}' added."
                )

                st.rerun()

    with col2:

        st.write("### Existing Categories")

        for category, keywords in (
            st.session_state.categories.items()
        ):

            st.write(
                f"**{category}** → "
                f"{len(keywords)} keywords"
            )


# =========================================================
# EXPENSE EDITOR
# =========================================================

def expense_editor():

    if (
        "debits_df"
        not in st.session_state
    ):
        return

    st.subheader(
        "✏️ Edit Expense Categories"
    )

    expenses = (
        st.session_state.debits_df
        .copy()
    )

    if "Category" not in expenses.columns:

        expenses["Category"] = (
            "uncategorized"
        )

    edited_df = st.data_editor(

        expenses[
            [
                "Date",
                "Details",
                "Amount",
                "Category"
            ]
        ],

        column_config={

            "Date":
                st.column_config.DateColumn(
                    "Date",
                    format="DD/MM/YYYY"
                ),

            "Amount":
                st.column_config.NumberColumn(
                    "Amount",
                    format="%.2f AED"
                ),

            "Category":
                st.column_config.SelectboxColumn(
                    "Category",
                    options=list(
                        st.session_state
                        .categories
                        .keys()
                    ),
                    required=True
                )
        },

        hide_index=True,

        use_container_width=True,

        key="category_editor"
    )

    if st.button(
        "💾 Apply Changes",
        type="primary"
    ):

        changes = 0

        for idx, row in edited_df.iterrows():

            new_category = row["Category"]

            old_category = (
                st.session_state
                .debits_df
                .at[idx, "Category"]
            )

            if new_category != old_category:

                details = str(
                    row["Details"]
                )

                st.session_state.debits_df.at[
                    idx,
                    "Category"
                ] = new_category

                add_keyword_to_category(
                    new_category,
                    details
                )

                changes += 1

        st.success(
            f"{changes} category changes applied."
        )


# =========================================================
# MAIN
# =========================================================

def main():

    # Initialize categories
    if "categories" not in st.session_state:

        st.session_state.categories = (
            load_categories()
        )

    # File uploader
    uploaded_file = st.file_uploader(
        "📁 Upload Bank Statement CSV",
        type=["csv"]
    )

    if uploaded_file is None:

        st.info(
            "👆 Upload your bank statement CSV "
            "to start the dashboard."
        )

        st.markdown(
            """
            ### Expected CSV columns

            Your CSV should contain:

            - `Date`
            - `Details`
            - `Amount`
            - `Debit/Credit`
            """
        )

        return

    # -----------------------------------------------------
    # Load file only when new file is uploaded
    # -----------------------------------------------------

    file_id = (
        uploaded_file.name,
        uploaded_file.size
    )

    if (
        "file_id" not in st.session_state
        or st.session_state.file_id != file_id
    ):

        df = load_transactions(
            uploaded_file
        )

        if df is None:
            return

        st.session_state.file_id = file_id
        st.session_state.df = df

    else:

        df = st.session_state.df

    # -----------------------------------------------------
    # Store debit dataframe
    # -----------------------------------------------------

    if (
        "debits_df"
        not in st.session_state
        or st.session_state.file_id == file_id
    ):

        if "debits_df" not in st.session_state:

            st.session_state.debits_df = (
                df[
                    df["Debit/Credit"] == "Debit"
                ].copy()
            )

    # =====================================================
    # TABS
    # =====================================================

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📊 Dashboard",
            "💸 Expenses",
            "💵 Payments",
            "🗂️ Categories"
        ]
    )

    # =====================================================
    # DASHBOARD TAB
    # =====================================================

    with tab1:

        show_dashboard(df)

    # =====================================================
    # EXPENSE TAB
    # =====================================================

    with tab2:

        expense_editor()

    # =====================================================
    # PAYMENT TAB
    # =====================================================

    with tab3:

        st.subheader(
            "💵 Payments / Income"
        )

        credits_df = df[
            df["Debit/Credit"] == "Credit"
        ].copy()

        if credits_df.empty:

            st.info(
                "No credit transactions found."
            )

        else:

            st.dataframe(
                credits_df[
                    [
                        "Date",
                        "Details",
                        "Amount",
                        "Category"
                    ]
                ].sort_values(
                    "Date",
                    ascending=False
                ),
                use_container_width=True,
                hide_index=True
            )

    # =====================================================
    # CATEGORY TAB
    # =====================================================

    with tab4:

        category_management()


# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":
    main()