def remove_outliers_iqr(df, col='amount'):
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1

    return df[
        (df[col] >= q1 - 1.5 * iqr) &
        (df[col] <= q3 + 1.5 * iqr)
    ].copy()