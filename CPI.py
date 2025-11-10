# This program processes CPI data for Assignment #2 (Part B)
# Outputs for Assignment #2 (Part B):
#   Printed answers for Questions 1–8, each labeled in the terminal.
#   Uses pandas library for data loading and calculations.
#
# Data inputs:
#   - 11 CSV files from Statistics Canada (Canada + 10 provinces) located in 'A2 Data' folder.
#   - Each file contains CPI values by item (All-items, Food, Shelter, etc.) for 2024.
#   - 'MinimumWages.csv' file with provincial minimum wages.
#
# Calculations performed (Q1–Q8):
#   Q1 & Q2: Combine CPI data and show first 12 rows.
#   Q3: Compute average month-to-month CPI change for All-items excl. food & energy.
#   Q4: Identify province with highest average CPI change per category.
#   Q5: Calculate equivalent salary in each province for $100,000 Ontario income using Dec-24 CPI.
#   Q6: Find provinces with highest/lowest nominal and real minimum wages (Dec-24 CPI adjusted).
#   Q7: Compute annual change (Jan–Dec 2024) in Services CPI.
#   Q8: Identify province with highest Services inflation.
#
# Input to program: None required (reads directly from CSV files in 'A2 Data').
# Output from program: Printed formatted tables and answers in the terminal.

import pandas as pd

# Function used to print section headers for output formatting
def header(title):
    print("\n" + "=" * 70)  # Print separator line for readability
    print(title)

# Function to format numeric values as percentages
def percent_fmt(x):
    try:
        return f"{float(x):.1f}%"  # Convert to float and format with one decimal, including '%'
    except Exception:
        return ""  # Return a empty string if the conversion fails

# Function to load and normalize the CPI data from multiple CSV files
def load_cpi(files):
    out = []  # Using this list to store all the processed dataframes
    for name, path in files.items():  # Loop through each province and its file path
        try:
            df = pd.read_csv(path)  # Read the CSV file
        except Exception as e:
            print("Could not read", path, "-", e)  # Print an error message if file read fails
            continue  # Skip to next file

        # First type of CSV structure 'Item' column
        if 'Item' in df.columns:
            # Convert wide format to long format, meaning that columns become 'Month' and values become 'CPI'
            long_df = df.melt(id_vars='Item', var_name='Month', value_name='CPI')
            # turning month in two possible formats (Jan-24 or 24-Jan)
            a = pd.to_datetime(long_df['Month'], format='%b-%y', errors='coerce')
            b = pd.to_datetime(long_df['Month'], format='%y-%b', errors='coerce')
            m = a.fillna(b)  # Use whichever format succeeded
            long_df['Month'] = m.dt.strftime('%b-%y')  # Reformat month back to string
            long_df['Jurisdiction'] = name  # Add province/country name
            out.append(long_df[['Item','Month','CPI','Jurisdiction']])  # Keep relevant columns

        # Second type of CSV structure, uses 'Products and product groups'
        elif 'Products and product groups' in df.columns:
            # Rename columns to standard names
            df = df.rename(columns={'Products and product groups':'Item','VALUE':'CPI','REF_DATE':'Month'})
            try:
                dt = pd.to_datetime(df['Month'], errors='coerce')  # Parse dates if possible
                df['Month'] = dt.dt.strftime('%b-%y')  # Reformat
            except Exception:
                pass  # Ignore errors
            df['Jurisdiction'] = name  # Tag data with province name
            out.append(df[['Item','Month','CPI','Jurisdiction']])  # Keep standard columns

    # Return empty dataframe if no files were loaded successfully
    if len(out) == 0:
        return pd.DataFrame(columns=['Item','Month','CPI','Jurisdiction'])

    # Concatenate all provincial dataframes into one combined dataframe
    res = pd.concat(out, ignore_index=True)
    res['CPI'] = pd.to_numeric(res['CPI'], errors='coerce').round(1)  # Convert CPI to numeric and round
    res = res.dropna(subset=['CPI'])  # Remove rows where CPI could not be parsed
    return res  # Return cleaned combined dataset

# Function to calculate average month-to-month CPI percentage change for selected items
def month_change(df, items):
    # Define months to ensure correct ordering
    months = ['Jan-24','Feb-24','Mar-24','Apr-24','May-24','Jun-24','Jul-24','Aug-24','Sep-24','Oct-24','Nov-24','Dec-24']
    d = df[df['Month'].isin(months)].copy()  # Keep only relevant months
    d['Month'] = pd.Categorical(d['Month'], categories=months, ordered=True)  # Keep month order

    rows = []  # Store results
    for prov in d['Jurisdiction'].unique():  # Loop through provinces
        for it in items:  # Loop through requested CPI item types
            tmp = d[(d['Jurisdiction']==prov) & (d['Item']==it)].sort_values('Month')  # Sort by time
            if tmp.empty:
                continue  # Skip if no data
            pct = tmp['CPI'].pct_change() * 100  # Calculate month-to-month percent change
            avg = round(pct[1:].mean(), 1)  # Compute average change
            if not pd.isna(avg):
                rows.append({'Jurisdiction': prov, 'Item': it, 'Change': avg})  # Store result
    return pd.DataFrame(rows, columns=['Jurisdiction','Item','Change'])  # Return summary dataframe

# Function to compute equivalent salaries across provinces using CPI
def salary_equiv(df_all, base_region, base_amount):
    dec = df_all[df_all['Month']=='Dec-24']  # Use December data
    base_cpi = float(dec[dec['Jurisdiction']==base_region]['CPI'].iloc[0])  # Get base region CPI
    out = []  # Store results
    for prov in dec['Jurisdiction'].unique():  # Loop through each province
        cpi_p = float(dec[dec['Jurisdiction']==prov]['CPI'].iloc[0])  # Get province CPI
        eq = base_amount * (cpi_p / base_cpi)  # Adjust salary by CPI ratio
        out.append({'Jurisdiction': prov, 'Salary': round(eq, 1)})  # Store equivalent salary
    return pd.DataFrame(out)  # Return table

# Function to compute CPI-adjusted real minimum wages
def real_wage(dec_all, mw):
    # Merge December CPI with nominal minimum wage table
    m = pd.merge(mw, dec_all[["Jurisdiction","CPI"]], on="Jurisdiction", how="inner")
    if m.empty:
        return pd.DataFrame(columns=["Jurisdiction","Real"]), None  # Return empty if no match
    m["Real"] = (m["MinimumWage"] / (m["CPI"] / 100.0)).round(1)  # Adjust nominal wage for inflation
    if m["Real"].notna().any():
        top = m.loc[m["Real"].idxmax()]  # Find province with highest real wage
    else:
        top = None
    return m[["Jurisdiction","MinimumWage","Real"]], top  # Return table and best province

# Function to calculate annual percentage change in Services CPI
def service_change(df_services):
    # Take January and December values for comparison
    jan = df_services[df_services['Month']=='Jan-24'][['Jurisdiction','CPI']].rename(columns={'CPI':'Jan'})
    dec = df_services[df_services['Month']=='Dec-24'][['Jurisdiction','CPI']].rename(columns={'CPI':'Dec'})
    # Merge January and December data
    m = pd.merge(dec, jan, on='Jurisdiction', how='inner')
    # Compute percentage change over the year
    m['Change'] = (((m['Dec'] - m['Jan']) / m['Jan']) * 100.0).round(1)
    return m[['Jurisdiction','Change']]  # Return province and change

# Main program block
if __name__ == '__main__':
    print("\nPART B: Consumer Price Index (CPI)\n")  # Initial header

    # File paths for each region’s CPI data
    files = {
        'Canada':'A2 Data/Canada.CPI.1810000401.csv',
        'Ontario':'A2 Data/ON.CPI.1810000401.csv',
        'Quebec':'A2 Data/QC.CPI.1810000401.csv',
        'British Columbia':'A2 Data/BC.CPI.1810000401.csv',
        'Alberta':'A2 Data/AB.CPI.1810000401.csv',
        'Manitoba':'A2 Data/MB.CPI.1810000401.csv',
        'Saskatchewan':'A2 Data/SK.CPI.1810000401.csv',
        'Nova Scotia':'A2 Data/NS.CPI.1810000401.csv',
        'New Brunswick':'A2 Data/NB.CPI.1810000401.csv',
        'Prince Edward Island':'A2 Data/PEI.CPI.1810000401.csv',
        'Newfoundland and Labrador':'A2 Data/NL.CPI.1810000401.csv'
    }

    # Q1 & Q2: Load and display combined CPI data
    header('Q1 & Q2: Combine CPI files and show first 12 rows')
    cpi = load_cpi(files)  # Load and merge all CPI data
    print(cpi.head(12).to_string(index=False))  # Display first 12 rows

    # Q3: Average month-to-month CPI change
    header('Q3: Average month-to-month change (Food, Shelter, All-items excl. food & energy)')
    items = ['Food', 'Shelter', 'All-items excluding food and energy']  # Items of interest
    chg = month_change(cpi, items)  # Calculate average monthly changes
    if not chg.empty:
        chg_print = chg.copy()
        chg_print['Change'] = chg_print['Change'].apply(percent_fmt)  # Format as percentage
        print(chg_print.to_string(index=False))  # Print formatted result
    else:
        print('No valid data for the requested item.')

    # Q4: Identify province with highest average CPI change
    header('Q4: Highest average change by category')
    if not chg.empty:
        # Sort by Item and Change, take top record per Item
        top = chg.sort_values(['Item','Change'], ascending=[True, False]).groupby('Item', as_index=False).head(1)
        top_print = top.copy()
        top_print['Change'] = top_print['Change'].apply(percent_fmt)
        print(top_print[['Jurisdiction','Item','Change']].to_string(index=False))
    else:
        print('No data to rank.')

    # Q5: Equivalent salary comparison
    header('Q5: Equivalent salary to $100,000 in Ontario (Dec-24 All-items CPI)')
    all_items = cpi[cpi['Item']=='All-items']  # Filter “All-items” CPI
    eq = salary_equiv(all_items, 'Ontario', 100000)  # Compute equivalent salaries
    eq['Salary'] = eq['Salary'].map(lambda x: f"${x:,.1f}")  # Format salary
    print(eq.to_string(index=False))  # Print table

    # Q6: Minimum wage analysis
    header('Q6: Minimum wages nominal & real (Dec-24 CPI)')
    try:
        mw = pd.read_csv('A2 Data/MinimumWages.csv')  # Load minimum wages
        # Ensure required columns exist, or rename first two columns
        if set(['Jurisdiction','MinimumWage']).issubset(set(mw.columns)):
            mw = mw[['Jurisdiction','MinimumWage']].copy()
        else:
            cols2 = list(mw.columns)[:2]
            mw = mw[cols2].copy()
            mw.columns = ['Jurisdiction','MinimumWage']
        # Mapping abbreviations to full province names
        name_map = {
            'AB':'Alberta','BC':'British Columbia','MB':'Manitoba','NB':'New Brunswick',
            'NL':'Newfoundland and Labrador','NS':'Nova Scotia','ON':'Ontario',
            'PE':'Prince Edward Island','PEI':'Prince Edward Island','QC':'Quebec',
            'SK':'Saskatchewan','CANADA':'Canada'
        }
        # Function to normalize province names
        def norm_j(x):
            s = str(x).strip()
            up = s.upper()
            if up in name_map:
                return name_map[up]
            if up.startswith('PRINCE EDWARD'):
                return 'Prince Edward Island'
            if up.startswith('NEWFOUNDLAND'):
                return 'Newfoundland and Labrador'
            return s
        mw['Jurisdiction'] = mw['Jurisdiction'].apply(norm_j)  # Apply normalization
        mw['MinimumWage'] = mw['MinimumWage'].astype(str).str.replace(r'[^0-9.]','', regex=True)  # Keep only numbers
        mw['MinimumWage'] = pd.to_numeric(mw['MinimumWage'], errors='coerce').round(1)  # Convert to float
        mw = mw.dropna(subset=['MinimumWage'])  # Remove invalid rows
        dec_all = all_items[all_items['Month']=='Dec-24']  # Get Dec CPI
        if dec_all.empty:
            print('Missing Dec-24 All-items CPI; cannot compute real wages.')
        elif mw.empty:
            print('MinimumWages.csv has no numeric wage values after cleaning.')
        else:
            real_tbl, top_real = real_wage(dec_all, mw)  # Compute real wages
            if real_tbl.empty:
                print('No matching provinces between wages and CPI after name normalization.')
                print('CPI jurisdictions:', sorted(dec_all['Jurisdiction'].unique()))
                print('Wage jurisdictions:', sorted(mw['Jurisdiction'].unique()))
            else:
                print("Nominal Minimum Wages ($):")
                nom_tbl = mw.sort_values('MinimumWage', ascending=False)
                for _, r in nom_tbl.iterrows():
                    print(f"  {r['Jurisdiction']:<25} ${r['MinimumWage']:.1f}")
                # Identify highest and lowest nominal wages
                nom_high = nom_tbl.iloc[0]
                nom_low  = nom_tbl.iloc[-1]
                print(f"\nNominal highest: {nom_high['Jurisdiction']} (${nom_high['MinimumWage']:.1f})")
                print(f"Nominal lowest : {nom_low['Jurisdiction']} (${nom_low['MinimumWage']:.1f})")

                print("\nReal Minimum Wages (CPI-adjusted):")
                real_tbl = real_tbl.sort_values('Real', ascending=False)
                for _, r in real_tbl.iterrows():
                    print(f"  {r['Jurisdiction']:<25} ${r['Real']:.1f}")
                if top_real is not None:
                    print(f"\nHighest real min wage: {top_real['Jurisdiction']} (${top_real['Real']:.1f})")
                else:
                    print('Could not determine highest real wage (all values missing).')
    except Exception as e:
        print('Could not process MinimumWages.csv', e)

    # Q7: Annual Services CPI change
    header('Q7: Annual percentage change in Services (Jan-Dec 2024)')
    services = cpi[cpi['Item']=='Services']  # Select 'Services' data
    serv = service_change(services)  # Calculate annual change
    if not serv.empty:
        serv_print = serv.copy()
        serv_print['Change'] = serv_print['Change'].apply(percent_fmt)  # Format as percent
        print(serv_print.to_string(index=False))  # Print results
    else:
        print('No Services data found.')

    # Q8: Identify region with highest Services inflation
    header('Q8: Region with highest inflation in Services (Jan-Dec 2024)')
    if not serv.empty:
        best = serv.sort_values('Change', ascending=False).iloc[0]  # Province with highest inflation
        print(best['Jurisdiction'], '->', percent_fmt(best['Change']))  # Print result
    else:
        print('No data found')