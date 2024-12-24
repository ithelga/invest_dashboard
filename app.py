import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from data_processing import load_data, process_operations_data, process_portfolio_data
from dashboard import dashboard_layout

app = dash.Dash(__name__, suppress_callback_exceptions=True)

df_operations, df_portfolio = load_data()
(total_taxes, total_commissions, payments_analytics, input_output_yearly, operations_summary) = process_operations_data(
    df_operations)
(detailed_data, sunburst_data, treemap_data, total_portfolio_value, total_profitability,
 grouped_data) = process_portfolio_data(df_portfolio)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
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
        grouped_data
    )


if __name__ == '__main__':
    app.run_server(debug=True)
