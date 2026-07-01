
import pandas as pd


 # ---> Schema validation <---
def validate_schema(required_columns, df_silver):
    df = df_silver
    missing_cols = [ 
        column for column in required_columns 
        if column not in df.columns
    ]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

 # ---> Range validation <---
def validate_range(df_silver, column, max_value = None, min_value = None):
    df = df_silver
    mask = pd.Series(True,index=df.index)

    if min_value is not None:
        mask &= df[column] >= min_value
    if max_value is not None:
        mask &= df[column] <= max_value
    mask &= df[column].notna()
    return mask

# ---> Reject rows missing required not-null fields <---
def validate_not_null(df_silver,column):
    df = df_silver
    return df[column].notna()


def validate_fk(df_silver, column, valid_id ):
    df = df_silver
    return df[column].isin(valid_id) 

def validate_no_future_date(df_silver,column):
    df = df_silver
    today = pd.Timestamp.now().normalize()
    return df[column] < today

def validate_outliers_iqr(df_silver,column, multiplier = 1.5):
    df = df_silver
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr

    return df[column].between(lower,upper ) 