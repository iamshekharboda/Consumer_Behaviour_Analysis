from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine


# Searches entire  home folder for 'customer_shopping_behavior.csv'
matching_files = list(Path.home().rglob('customer_shopping_behavior.csv'))

if not matching_files:
    raise FileNotFoundError("Could not find 'customer_shopping_behavior.csv' anywhere on your Mac. Please make sure the file exists.")

file_path = matching_files[0]
print(f"Found file at: {file_path}")

# Load the dataset
df = pd.read_csv(file_path)

# ==========================================
# 2. DATA CLEANING & TRANSFORMATION
# ==========================================

# Impute missing values in Review Rating column with the median rating of the product category
df['Review Rating'] = df.groupby('Category')['Review Rating'].transform(lambda x: x.fillna(x.median()))

# Rename columns according to snake casing
df.columns = df.columns.str.lower()
df.columns = df.columns.str.replace(' ', '_')
df = df.rename(columns={'purchase_amount_(usd)': 'purchase_amount'})

# Create new column age_group
labels = ['Young Adult', 'Adult', 'Middle-aged', 'Senior']
df['age_group'] = pd.qcut(df['age'], q=4, labels=labels)

# Create new column purchase_frequency_days
frequency_mapping = {
    'Fortnightly': 14,
    'Weekly': 7,
    'Monthly': 30,
    'Quarterly': 90,
    'Bi-Weekly': 14,
    'Annually': 365,
    'Every 3 Months': 90
}
df['purchase_frequency_days'] = df['frequency_of_purchases'].map(frequency_mapping)

# Drop redundant promo_code_used column
df = df.drop('promo_code_used', axis=1)


# ==========================================
# 3. MYSQL DATABASE CONFIGURATION
# ==========================================

username = "root"
password = "F05dpmbuyz"
host = "localhost"
port = "3306"
database = "customero_behavior"
table_name = "customer"

# MySQL SQLAlchemy engine
engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")


# ==========================================
# 4. EXPORT TO SQL DATABASE
# ==========================================
try:
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"Data successfully cleaned and loaded into table '{table_name}' in database '{database}'.")
except Exception as e:
    print(f"Error connecting or loading data: {e}")