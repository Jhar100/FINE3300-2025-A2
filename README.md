# FINE3300-2025-A2

This repository contains Jonathan Hargitai’s solutions for FINE3300 (Fall 2025) Assignment 2.

Includes:

Part A – Loan Amortization Schedules

Extends Assignment 1 by generating detailed amortization schedules for multiple payment frequencies.

Prompts the user for:

-Principal amount

-Quoted annual interest rate (percent)

-Amortization period (years)

-Term (years)

Calculates periodic payments (monthly, semi-monthly, bi-weekly, weekly, and rapid options).

Exports an Excel file with six worksheets (one per payment type).

Creates a PNG figure showing the decline of loan balances over time.

Uses Canadian semi-annual compounding and the standard present-value-of-annuity formula.

Part B – Consumer Price Index (CPI) Analysis

Reads CPI data for 2024 from Statistics Canada (Canada + 10 provinces).

Combines all 11 CSV files into one dataset and computes:

-Average month-to-month CPI changes

-Provinces with the highest inflation rates

-Equivalent salary comparisons across provinces

-Nominal and real minimum wages (CPI-adjusted)

-Annual change in services inflation (Jan–Dec 2024)

Outputs all results clearly labeled in the terminal.

Example Output (Part A):

Input: Principal: $500,000 Quoted Rate: 5.5% Amortization: 25 years, Mortgage TERM: 30 years

Output: Monthly Payment: $3051.96 Semi-monthly Payment: $1524.25 Bi-weekly Payment: $1406.88 Weekly Payment: $703.07 Rapid Bi-weekly Payment: $1525.98 Rapid Weekly Payment: $762.99, A2_PartA_Schedules.xlsx, A2_PartA_BalanceDecline.png

Summary of Approach:

-Organized both parts into separate Python programs.

-Used pandas for data handling and numerical analysis.

-Uploaded all project files to this GitHub repository for submission.





