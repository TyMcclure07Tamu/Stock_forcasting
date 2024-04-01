
import os
import pandas as pd

# Define paths
current_directory = os.getcwd()
input_file_path = os.path.join(current_directory, 'FinalDatabase.csv')  # Input file location
output_file_path = os.path.join(current_directory, 'SentimentDispersion.csv')  # Output file location

# Load the dataset
df = pd.read_csv(input_file_path)

# Convert date columns to datetime format, correcting the format to match your data
df['date'] = pd.to_datetime(df['date'], format='%d%b%Y')  # Corrected format here
df['rdq'] = pd.to_datetime(df['rdq'], format='%d%b%Y')    # Corrected format here

# Define the period before the earnings announcement date (e.g., B0 = 10 days, B1 = 5 days before)
B0 = 10  # Start of the period (10 days before)
B1 = 5   # End of the period (5 days before)

# Prepare a list to collect results
results = []

# Iterate over each firm
for firm_id in df['firm_id'].unique():
    firm_data = df[df['firm_id'] == firm_id]
    
    # Iterate over each earnings announcement date for the firm
    for rdq in firm_data['rdq'].dropna().unique():  # Ensure rdq is not NaT
        # Select the data from B0 to B1 days before the announcement
        period_start = rdq - pd.Timedelta(days=B0)
        period_end = rdq - pd.Timedelta(days=B1)
        period_data = firm_data[(firm_data['date'] >= period_start) & (firm_data['date'] < period_end)]
        
        # Calculate sentiment range and standard deviation, ignoring NaN values
        if not period_data.empty:
            max_sentiment = period_data['sentiment'].max(skipna=True)
            min_sentiment = period_data['sentiment'].min(skipna=True)
            avg_sentiment = period_data['sentiment'].mean(skipna = True)
            sentiment_range = max_sentiment - min_sentiment if pd.notnull(max_sentiment) and pd.notnull(min_sentiment) else None
            sentiment_std = period_data['sentiment'].std(skipna=True)
            sentiment_avg = period_data['sentiment'].mean(skipna = True)
        else:
            sentiment_range = None
            sentiment_std = None
            sentiment_avg = None
        
        
        # Collect results
        results.append({
            'firm_id': firm_id,
            'rdq': rdq,
            'sentiment_range': sentiment_range,
            'sentiment_std': sentiment_std,
            'sentiment_avg': sentiment_avg
        })

# Convert results to a DataFrame
results_df = pd.DataFrame(results)

# Save the results to a CSV file
results_df.to_csv(output_file_path, index=False)

print(f"Sentiment dispersion data saved to {output_file_path}")


# Load both datasets
sentiment_df = pd.read_csv('SentimentDispersion.csv')
returns_df = pd.read_csv('AdjustedDailyReturns.csv')

# Merge the datasets on 'firm_id' and 'rdq'
merged_df = pd.merge(sentiment_df, returns_df, on=['firm_id', 'rdq'])

# Drop rows with missing values
cleaned_df = merged_df.dropna()

# Optionally, inspect the cleaned data
print(cleaned_df.head())

# Save the cleaned dataframe to a new CSV file
cleaned_df.to_csv('Portfolio.csv', index=False)

import pandas as pd

def separate_firms(csv_file):
    # Read data from CSV file
    df = pd.read_csv(csv_file)

    # Calculating the percentiles for sentiment_range and sentiment_std
    percentile_80_range = df['sentiment_range'].quantile(0.80)
    percentile_20_range = df['sentiment_range'].quantile(0.20)
    percentile_80_std = df['sentiment_std'].quantile(0.80)
    percentile_20_std = df['sentiment_std'].quantile(0.20)

    # Identifying firms in the top 80% for both sentiment_range and sentiment_std
    top_80_df = df[(df['sentiment_range'] >= percentile_80_range) & (df['sentiment_std'] >= percentile_80_std)]

    # Identifying firms in the bottom 20% for both sentiment_range and sentiment_std
    bottom_20_df = df[(df['sentiment_range'] <= percentile_20_range) & (df['sentiment_std'] <= percentile_20_std)]

    # Saving the separated data into new CSV files
    top_80_df.to_csv('top_80_percent.csv', index=False)
    bottom_20_df.to_csv('bottom_20_percent.csv', index=False)

    print("Data separated and saved into 'top_80_percent.csv' and 'bottom_20_percent.csv'")

    # Calculate average daily_return for top 80% and bottom 20%
    sum_top_80 = top_80_df['daily_return'].sum()
    sum_bottom_20 = bottom_20_df['daily_return'].sum()

    # Calculate the difference
    difference = sum_top_80 + sum_bottom_20

    # Print the results
    print(f"Average Daily Return for Top 80%: {sum_top_80}")
    print(f"Average Daily Return for Bottom 20%: {sum_bottom_20}")
    print(f"Difference (Top 80% - Bottom 20%): {difference}")

# Using the script with your CSV file
separate_firms('Portfolio.csv')

