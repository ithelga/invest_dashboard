import pandas as pd


def load_data():
    df_operations = pd.read_csv('data/operations.csv')
    df_operations['date'] = pd.to_datetime(df_operations['date'], errors='coerce')
    df_operations['year'] = df_operations['date'].dt.year
    df_operations = df_operations[df_operations['year'].isin([2020, 2021, 2022, 2023, 2024])]
    df_portfolio = pd.read_csv('data/portfolio.csv')
    return df_operations, df_portfolio


def process_operations_data(df, portfolio_name=None):
    if portfolio_name:
        df = df[df['portfolio_name'] == portfolio_name]  # Фильтрация по брокерскому счёту

    tax_types = [
        'Удержание налога по дивидендам',
        'Удержание налога',
        'Корректировка налога',
        'Удержание НДФЛ по купонам'
    ]
    commission_types = ['Удержание комиссии за операцию']

    total_taxes = df[df['type'].isin(tax_types)]['amount'].sum()
    total_commissions = df[df['type'].isin(commission_types)]['amount'].sum()

    payments_df = df[df['type'].isin(['Выплата дивидендов', 'Выплата купонов'])]
    payments_analytics = payments_df.groupby(['year', 'type'])['amount'].sum().reset_index()

    input_output_df = df[df['type'].isin(['Пополнение брокерского счёта', 'Вывод денежных средств'])]
    input_output_df['amount'] = input_output_df.apply(
        lambda row: row['amount'] if row['type'] == 'Пополнение брокерского счёта' else -row['amount'], axis=1
    )
    input_output_yearly = input_output_df.groupby(['year', 'type', 'portfolio_name'])['amount'].sum().reset_index()
    input_output_yearly['account'] = input_output_yearly['portfolio_name']

    operations_summary = {
        'total_coupons': payments_df[payments_df['type'] == 'Выплата купонов']['amount'].sum(),
        'total_dividends': payments_df[payments_df['type'] == 'Выплата дивидендов']['amount'].sum(),
        'total_deposits': input_output_df[input_output_df['type'] == 'Пополнение брокерского счёта']['amount'].sum(),
        'total_withdrawals': -1 * input_output_df[input_output_df['type'] == 'Вывод денежных средств']['amount'].sum(),
    }

    return total_taxes, total_commissions, payments_analytics, input_output_yearly, operations_summary



def process_portfolio_data(df, portfolio_name=None):
    if portfolio_name:
        df = df[df['portfolio_name'] == portfolio_name]  # Фильтрация по брокерскому счёту

    df['current_value'] = df['quantity'] * df['current_price']
    df['investment_value'] = df['quantity'] * df['average_price']

    total_portfolio_value = df['current_value'].sum()
    total_profitability = ((df['current_value'].sum() - df['investment_value'].sum()) / df[
        'investment_value'].sum()) * 100 if df['investment_value'].sum() > 0 else 0

    detailed_data = df.groupby('type').agg(
        total_value=('current_value', 'sum')
    ).reset_index()

    sunburst_data = df.groupby(['type', 'portfolio_name']).agg(
        total_value=('current_value', 'sum')
    ).reset_index()

    treemap_data = df.groupby(['sector', 'name']).agg(
        total_quantity=('quantity', 'sum'),
        total_value=('current_value', 'sum')
    ).reset_index()

    grouped_data = df.groupby(['ticker', 'name', 'type']).agg(
        total_quantity=('quantity', 'sum'),
        average_price=('average_price', 'mean'),
        current_price=('current_price', 'mean')
    ).reset_index()

    return detailed_data, sunburst_data, treemap_data, total_portfolio_value, total_profitability, grouped_data

