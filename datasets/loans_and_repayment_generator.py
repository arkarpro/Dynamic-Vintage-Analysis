import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Settings
np.random.seed(42)  # For reproducibility
months = 24  # 24 months of data
regions = ["Yangon", "Mandalay", "Shan", "Ayeyarwaddy"]
products = ["Personal Loan", "SME Loan", "Agriculture Loan"]

# Interest rates by product
interest_rates = {
    "Personal Loan": 0.02,  # 2% monthly
    "SME Loan": 0.015,      # 1.5% monthly
    "Agriculture Loan": 0.025  # 2.5% monthly
}

# --- Generate Loan Disbursements ---
disbursement_data = []
start_date = datetime(2024, 1, 1)

for month in range(months):
    current_date = start_date + timedelta(days=30 * month)
    month_year = current_date.strftime("%b-%y")
    
    for region in regions:
        for product in products:
            # Base borrowers (scaled by region/product)
            base_borrowers = {
                "Yangon": {"Personal Loan": 200, "SME Loan": 50, "Agriculture Loan": 30},
                "Mandalay": {"Personal Loan": 100, "SME Loan": 120, "Agriculture Loan": 40},
                "Shan": {"Personal Loan": 80, "SME Loan": 100, "Agriculture Loan": 60},
                "Ayeyarwaddy": {"Personal Loan": 50, "SME Loan": 30, "Agriculture Loan": 150}
            }
            
            # Seasonal adjustments for Agriculture Loans
            if product == "Agriculture Loan" and current_date.month in [1, 5, 6, 12]:
                borrowers = int(base_borrowers[region][product] * 1.5)  # +50% in peak months
            else:
                borrowers = base_borrowers[region][product]
            
            # SME Loan growth (10-20% from Q2 2024)
            if product == "SME Loan" and current_date >= datetime(2024, 4, 1):
                borrowers = int(borrowers * (1 + np.random.uniform(0.1, 0.2)))
            
            # Loan amount (USD)
            loan_amount = {
                "Personal Loan": borrowers * 350,
                "SME Loan": borrowers * 2000,
                "Agriculture Loan": borrowers * 300
            }[product]
            
            # Loan term (3-24 months)
            loan_term = {
                "Personal Loan": np.random.choice([3, 6, 12]),
                "SME Loan": np.random.choice([12, 18, 24]),
                "Agriculture Loan": 12  # Fixed term for agriculture
            }[product]
            
            # Scheduled repayments
            principal = loan_amount / loan_term
            interest = loan_amount * interest_rates[product]
            total_repayment = principal + interest
            
            disbursement_data.append([
                month_year, product, region, borrowers, loan_amount, loan_term,
                round(principal, 2), round(interest, 2), round(total_repayment, 2),
                round(total_repayment * loan_term, 2)
            ])

# Create Disbursement DataFrame
disbursement_df = pd.DataFrame(
    disbursement_data,
    columns=[
        "Disbursed Month", "Loan Product", "Region", "Total Borrowers",
        "Loan Amount (USD)", "Loan Term (Months)", "Principal Repayment Scheduled",
        "Interest Repayment Scheduled", "Total Repayment Scheduled",
        "Total Repayment for Loan Term"
    ]
)

# --- Generate Repayment Data (with Disbursed Month) ---
repayment_data = []

for _, row in disbursement_df.iterrows():
    disbursement_date = datetime.strptime(row["Disbursed Month"], "%b-%y")
    
    for month_num in range(1, row["Loan Term (Months)"] + 1):
        repayment_date = disbursement_date + timedelta(days=30 * month_num)
        repayment_month_year = repayment_date.strftime("%b-%y")
        
        # Simulate repayments (90% on-time, 10% overdue)
        principal_paid = row["Principal Repayment Scheduled"]
        interest_paid = row["Interest Repayment Scheduled"]
        
        if np.random.random() < 0.9:  # 90% on-time
            overdue = 0
        else:
            overdue = principal_paid * np.random.uniform(0.1, 0.3)  # 10-30% overdue
        
        outstanding = max(0, row["Loan Amount (USD)"] - (principal_paid * month_num))
        
        repayment_data.append([
            row["Disbursed Month"],  # Added to link repayments to disbursements
            repayment_month_year, 
            row["Region"], 
            row["Loan Product"],
            round(principal_paid - overdue, 2),
            round(interest_paid, 2),
            round(interest_paid * 0.8, 2),  # Profit = 80% of interest
            round(overdue, 2),
            round(outstanding, 2)
        ])

# Create Repayment DataFrame
repayment_df = pd.DataFrame(
    repayment_data,
    columns=[
        "Disbursed Month",  # New column
        "Repayment Month", 
        "Region", 
        "Product", 
        "Principal Repayment",
        "Interest Repayment", 
        "Average Profit", 
        "Overdue Amount",
        "Outstanding Balance"
    ]
)

# --- Save to CSV ---
disbursement_df.to_csv("loan_disbursements.csv", index=False)
repayment_df.to_csv("loan_repayments.csv", index=False)

print("Data generated: loan_disbursements.csv & loan_repayments.csv")
print(f"Disbursement records: {len(disbursement_df)}")
print(f"Repayment records: {len(repayment_df)}")