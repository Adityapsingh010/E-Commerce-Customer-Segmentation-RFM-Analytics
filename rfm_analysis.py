import pandas as pd

file_path  = "C:/Users/neela/Desktop/Project/ecommerce_dataset_v2.csv"
df = pd.read_csv(file_path)

print("Dates validation check")
print(df[["InvoiceNo","InvoiceDate","CustomerID","Quantity"]].head(10))

print("\n ----Dataset Info ---")
print(df.info())

# Converting 'InvoiceDate' column to datetime format 

df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# Revenue Calculation

df['TotalPrice'] = df['Quantity'] * df['UnitPrice']

# Checking Missing Values
print("---- Missing values in Column ----")
print(df.isnull().sum())

print("\n--- Processed Data sample ---")
print(df[['InvoiceNo', 'InvoiceDate', 'Quantity', 'UnitPrice', 'TotalPrice']].head())

# Total Description (average )
print("\n --- Statistical summary of Numeric Columns ---")
print(df.describe())

# Calculate Base RFM VALUES

snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days = 1)
print(f"Snapshot Date (For Calculation): {snapshot_date.strftime('%Y-%m-%d')}\n")

# Customers 
df['DaysSincePurchase'] = (snapshot_date - df['InvoiceDate']).dt.days

#RFM 
rfm = df.groupby('CustomerID').agg({
    'DaysSincePurchase':'min',
    'InvoiceNo':'nunique',
    'TotalPrice':'sum'
}).rename(columns={
    'DaysSincePurchase':'Recency',
    'InvoiceNo': 'Frequency',
    'TotalPrice':'Monetary'
})

#4. RFM table check karein

print("--- Base RFM Values for Customers (No Lambda) ---")
print(rfm.head())

print(f"\n Total Unique Customers: {len(rfm)}")


#RFM Scoring

#R_Score
rfm['R_Score'] = pd.qcut(rfm['Recency'],5, labels = [5,4,3,2,1]).astype(int)

#F_Score
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method = 'first'),5,labels = [1,2,3,4,5]).astype(int)

#M_Score
rfm['M_Score'] = pd.qcut(rfm['Monetary'],5,labels = [1,2,3,4,5]).astype(int)

#2.
rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

print("--- RFM Scores Table (First 5 Customers) ---")
print(rfm[['Recency','R_Score','Frequency','F_Score','Monetary','M_Score','RFM_Score']].head())

#Category Allotment

def get_segment_name(row):
    r = row['R_Score']
    f = row['F_Score']
    m = row['M_Score']
    
    #Champions: Best Point Customer
    if r >= 4 and f >= 4 and m >=4:
        return 'Champions'
    
    #Good: Good Frequecy Customer
    elif r >= 3 and f >=4 and m >= 3:
        return 'Loyal Customers'
    
    # Recent and New Customers 
    
    elif r >= 4 and f <=2:
        return 'Recent/New Customers'
    
    #At Risk/Cant Loose Them
    elif r <= 2 and f >=3 and m >=3:
        return 'At Risk/ Can\'t Lose Them'
    
    # Lost Customers: 
    elif r <= 2 and f <=2:
        return 'Lost Customers/ Hibernating'
    
    else:
        return 'Need Attention / Average'
    
# Applying Function on to the Customers
rfm['Segment'] = rfm.apply(get_segment_name, axis = 1)

# Checking How many Customers in each Category
print("\n--- Final Customer Segmentation Distrubution--- ")
print(rfm['Segment'].value_counts())



output_file = "C:/Users/neela/Desktop/Project/rfm_customer_segments.csv"
rfm.to_csv(output_file)

print(f"{output_file}")