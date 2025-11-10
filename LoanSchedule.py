# This program extends Assignment #1 to generate loan amortization schedules
# Outputs for Assignment #2 (Part A):
#   One Excel file with six worksheets (one per payment option)
#   One PNG figure showing loan balance decline for all six options
#
# Attributes of MortgagePayment remain: quoted_rate, amortization_years
# New input: term_years (mortgage term in years)
#
# Public methods:
#   payments(principal):
#       returns a tuple with six payment amounts (same order as from Assignment #1)

#   build_payment_schedule(principal, frequency_name):
#       returns a pandas DataFrame with columns:
#           period, starting_balance, interest, payment, ending_balance
#
# Input to program (via input()):
#   Principal amount (float)
#   Quoted interest rate in percent (float)
#   Amortization period in years (int)
#   Term in years (int)
#
# Output from program:
#   Printed six payment amounts rounded to 2 decimals
#   Excel file with six worksheets saved as: A2_PartA_Schedules.xlsx
#   PNG figure saved as: A2_PartA_BalanceDecline.png

import pandas as pd
import matplotlib.pyplot as plt

class MortgagePayment:
    def __init__(self, quoted_rate, amortization_years):
        # Quoted rate is the annual interest rate
        # Amortization is the number of years the loan will be paid off
        self.__quoted_rate = quoted_rate
        self.__amortization_years = amortization_years

    def payments(self, principal):
        # Convert quoted rate to effective annual rate (EAR)
        # In Canada, mortgage rates are quoted as semi-annually compounded
        # So first convert the semi-annual rate to an effective annual rate
        EAR = (1 + self.__quoted_rate / 200) ** 2 - 1

        # MONTHLY PAYMENT
        # Calculate the monthly periodic rate based on EAR
        r_monthly = (1 + EAR) ** (1 / 12) - 1
        # Total number of monthly payments (years * 12 months)
        n_months = self.__amortization_years * 12
        # Apply annuity formula: P = principal * [r / (1 - (1 + r)^-n)]
        monthly = principal * (r_monthly / (1 - (1 + r_monthly) ** -n_months))

        # SEMI-MONTHLY PAYMENT (24 per year)
        # There are 24 semi-monthly payments per year (2 per month)
        r_semi_monthly = (1 + EAR) ** (1 / 24) - 1
        n_semi_monthly = self.__amortization_years * 24
        semi_monthly = principal * (r_semi_monthly / (1 - (1 + r_semi_monthly) ** -n_semi_monthly))

        # BI-WEEKLY PAYMENT (26 per year)
        # There are 26 bi-weekly payments in a year (every two weeks)
        r_bi_weekly = (1 + EAR) ** (1 / 26) - 1
        n_bi_weekly = self.__amortization_years * 26
        bi_weekly = principal * (r_bi_weekly / (1 - (1 + r_bi_weekly) ** -n_bi_weekly))

        # WEEKLY PAYMENT (52 per year)
        # There are 52 weekly payments per year
        r_weekly = (1 + EAR) ** (1 / 52) - 1
        n_weekly = self.__amortization_years * 52
        weekly = principal * (r_weekly / (1 - (1 + r_weekly) ** -n_weekly))

        # RAPID PAYMENTS
        # Rapid payments are based on dividing the monthly payment:
        #   Rapid bi-weekly = half of monthly
        #   Rapid weekly = one-quarter of monthly
        rapid_bi_weekly = monthly / 2
        rapid_weekly = monthly / 4

        # Return all payment values as a tuple in order
        return (monthly, semi_monthly, bi_weekly, weekly, rapid_bi_weekly, rapid_weekly)

    def build_payment_schedule(self, principal, frequency_name):
        # Build a schedule for the selected payment frequency
        # Returns a pandas DataFrame with the required columns
        EAR = (1 + self.__quoted_rate / 200) ** 2 - 1

        # Mapping frequency to periods per year and periodic rate
        if frequency_name == "Monthly":
            periods_per_year = 12
            r = (1 + EAR) ** (1 / 12) - 1
            n = self.__amortization_years * periods_per_year
            payment = principal * (r / (1 - (1 + r) ** -n))
        elif frequency_name == "Semi-monthly":
            periods_per_year = 24
            r = (1 + EAR) ** (1 / 24) - 1
            n = self.__amortization_years * periods_per_year
            payment = principal * (r / (1 - (1 + r) ** -n))
        elif frequency_name == "Bi-weekly":
            periods_per_year = 26
            r = (1 + EAR) ** (1 / 26) - 1
            n = self.__amortization_years * periods_per_year
            payment = principal * (r / (1 - (1 + r) ** -n))
        elif frequency_name == "Weekly":
            periods_per_year = 52
            r = (1 + EAR) ** (1 / 52) - 1
            n = self.__amortization_years * periods_per_year
            payment = principal * (r / (1 - (1 + r) ** -n))
        elif frequency_name == "Rapid Bi-weekly":
            periods_per_year = 26
            r = (1 + EAR) ** (1 / 26) - 1
            n = self.__amortization_years * periods_per_year
            # rapid amount is half of monthly amount
            r_monthly = (1 + EAR) ** (1 / 12) - 1
            n_months = self.__amortization_years * 12
            monthly_amt = principal * (r_monthly / (1 - (1 + r_monthly) ** -n_months))
            payment = monthly_amt / 2
        elif frequency_name == "Rapid Weekly":
            periods_per_year = 52
            r = (1 + EAR) ** (1 / 52) - 1
            n = self.__amortization_years * periods_per_year
            # rapid amount is one-quarter of monthly amount
            r_monthly = (1 + EAR) ** (1 / 12) - 1
            n_months = self.__amortization_years * 12
            monthly_amt = principal * (r_monthly / (1 - (1 + r_monthly) ** -n_months))
            payment = monthly_amt / 4
        else:
            # If there is an unknown name provided
            raise ValueError("Unknown name")

        # Building rows until the balance reaches zero (protect against rounding)
        rows = []
        balance = float(principal)
        period = 1
        while balance > 0 and period <= n + 1:
            starting_balance = balance
            interest = starting_balance * r
            principal_component = payment - interest
            # Adjusting the final payment to avoid a negative balance due to rounding
            if principal_component > balance:
                principal_component = balance
                payment_effective = interest + principal_component
            else:
                payment_effective = payment
            ending_balance = starting_balance - principal_component

            rows.append({
                "period": period,
                "starting_balance": round(starting_balance, 2),
                "interest": round(interest, 2),
                "payment": round(payment_effective, 2),
                "ending_balance": round(ending_balance, 2)
            })

            balance = ending_balance
            period += 1

        # Creating DataFrame with specified column order
        df = pd.DataFrame(rows, columns=["period", "starting_balance", "interest", "payment", "ending_balance"])
        return df

if __name__ == "__main__":
    # Asking the user to enter mortgage details
    principal = float(input("Enter the mortgage principal amount: "))
    rate = float(input("Enter the quoted interest rate (percent): "))
    years = int(input("Enter the amortization period (years): "))
    term_years = int(input("Enter the mortgage term (years): "))

    # Creating an object from the MortgagePayment class using the user input
    mortgage = MortgagePayment(rate, years)

    # Calling the payments method to calculate the 6 payment options
    result = mortgage.payments(principal)

    # Displaying results with 2 decimal places
    # Each print line corresponds to one payment type
    print("Monthly Payment: ${:.2f}".format(result[0]))
    print("Semi-monthly Payment: ${:.2f}".format(result[1]))
    print("Bi-weekly Payment: ${:.2f}".format(result[2]))
    print("Weekly Payment: ${:.2f}".format(result[3]))
    print("Rapid Bi-weekly Payment: ${:.2f}".format(result[4]))
    print("Rapid Weekly Payment: ${:.2f}".format(result[5]))

    # Building six schedules and save to one Excel with multiple worksheets
    # Sheet names match the frequency labels used in the printout
    frequencies = [
        "Monthly",
        "Semi-monthly",
        "Bi-weekly",
        "Weekly",
        "Rapid Bi-weekly",
        "Rapid Weekly"
    ]

    # Creating schedules and collect balance series for plotting
    schedules = {}
    balances = {}

    with pd.ExcelWriter("A2_PartA_Schedules.xlsx", engine="xlsxwriter") as writer:
        for name in frequencies:
            df_sched = mortgage.build_payment_schedule(principal, name)
            schedules[name] = df_sched
            balances[name] = df_sched["ending_balance"].values
            # Replace spaces with underscore for sheet name; ensure <=31 chars
            sheet_name = name.replace(" ", "_")[:31]
            df_sched.to_excel(writer, sheet_name=sheet_name, index=False)

    # Ploting the balance decline for all six options on one figure
    plt.figure()
    for name in frequencies:
        plt.plot(balances[name], label=name)
    plt.title("Loan Balance Decline by Payment Frequency")
    plt.xlabel("Period")
    plt.ylabel("Ending Balance ($)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("A2_PartA_BalanceDecline.png", dpi=200)
    plt.close()