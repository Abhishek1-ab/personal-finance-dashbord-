💰 Personal Finance Dashboard

An interactive Personal Finance Dashboard built using Python, Pandas, Plotly, and Streamlit. The application allows users to upload bank transaction data in CSV format and analyze their income, expenses, balance, spending categories, and monthly cash flow.

🚀 Features

- 📁 Upload bank statement CSV
- 💵 Calculate total income and expenses
- 💰 Calculate overall and filtered balance
- 🔎 Filter transactions by date, type, and category
- 🔍 Search transactions by details
- 🥧 Expense analysis by category
- 📈 Monthly income vs expense analysis
- 🏆 Top 5 spending categories
- ✏️ Edit and manage expense categories
- 🗂️ Create custom categories and keywords
- 📋 View transactions in an interactive table
- ⬇️ Download filtered transactions as CSV

🛠️ Technologies Used

- Python
- Pandas – Data cleaning and analysis
- Plotly – Interactive data visualization
- Streamlit – Dashboard and web application
- JSON – Category and keyword management

📂 Project Structure

personal-finance-dashboard/
│
├── app.py
├── categories.json
├── requirements.txt
├── README.md
├── .gitignore
└── sample_data.csv

📊 Required CSV Columns

The uploaded CSV file should contain:

- "Date"
- "Details"
- "Amount"
- "Debit/Credit"

Example:

Date| Details| Amount| Debit/Credit
01/01/2026| Salary| 5000| Credit
02/01/2026| Grocery Store| 250| Debit
03/01/2026| Electricity Bill| 180| Debit

▶️ How to Run

Install the required libraries:

pip install -r requirements.txt

Run the Streamlit application:

streamlit run app.py

The dashboard will open in your browser.

🎯 Project Purpose

This project demonstrates practical skills in:

- Data cleaning
- Data analysis
- Data filtering
- Data visualization
- Python programming
- Pandas
- Streamlit dashboard development
- Building an interactive data analytics application
