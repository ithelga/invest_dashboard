import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from data_processing import load_data, process_operations_data, process_portfolio_data
from dashboard import dashboard_layout

app = dash.Dash(__name__, suppress_callback_exceptions=True)

df_operations, df_portfolio = load_data()
(total_taxes, total_commissions, payments_analytics, input_output_yearly, operations_summary) = process_operations_data(df_operations)
(detailed_data, sunburst_data, treemap_data, total_portfolio_value, total_profitability,
 grouped_data) = process_portfolio_data(df_portfolio)

broker_accounts = df_portfolio['portfolio_name'].unique()


app.index_string = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
</head>
<body>
    {%app_entry%}
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>
'''


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', children=dashboard_layout(
        total_portfolio_value, total_profitability, operations_summary,
        total_taxes, total_commissions, payments_analytics,
        input_output_yearly, sunburst_data, treemap_data, grouped_data,
        broker_accounts, broker_accounts[0]
    ))
])


@app.callback(
    Output('page-content', 'children'),
    [Input('broker-filter-dashboard', 'value')]
)
def update_dashboard(selected_accounts):
    if not selected_accounts:
        selected_accounts = [broker_accounts[0]]
    filtered_portfolio = df_portfolio[df_portfolio['portfolio_name'].isin(selected_accounts)]
    filtered_operations = df_operations[df_operations['portfolio_name'].isin(selected_accounts)]

    (total_taxes, total_commissions, payments_analytics, input_output_yearly,
     operations_summary) = process_operations_data(filtered_operations)
    (detailed_data, sunburst_data, treemap_data, total_portfolio_value, total_profitability,
     grouped_data) = process_portfolio_data(filtered_portfolio)

    return dashboard_layout(
        total_portfolio_value,
        total_profitability,
        operations_summary,
        total_taxes,
        total_commissions,
        payments_analytics,
        input_output_yearly,
        sunburst_data,
        treemap_data,
        grouped_data,
        broker_accounts,
        selected_accounts
    )


if __name__ == '__main__':
    app.run_server(debug=False)
