from dash import dcc, html
import plotly.graph_objects as go
import plotly.express as px


def create_graph(data, asset_type):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data['ticker'],
        y=data['average_price'],
        name='Средняя цена',
        mode='lines+markers',
        line=dict(color='#D8D8D8', width=1, dash='dash'),
        text=data['name'],
        textposition='top center',
        showlegend=False
    ))

    colors = ['#396534' if curr > avg else '#C51C33' for curr, avg in zip(data['current_price'], data['average_price'])]
    fig.add_trace(go.Bar(
        x=data['ticker'],
        y=data['current_price'],
        name='Текущая цена',
        marker_color=colors,
        text=data['name'],
        texttemplate='%{text}',
        textposition='auto',
        showlegend=False
    ))

    fig.update_layout(
        title=f'Текущая и средняя цены для {asset_type}',
        xaxis_title='Тикер',
        yaxis_title='Цена',
        barmode='overlay',
        template='plotly_dark',
        font=dict(color='#D8D8D8'),
        plot_bgcolor='#2A2A2A',
        paper_bgcolor='#2A2A2A'
    )

    return fig


def dashboard_layout(total_portfolio_value, total_profitability, operations_summary,
                     total_taxes, total_commissions, payments_analytics,
                     input_output_yearly, sunburst_data, treemap_data, grouped_data):
    return html.Div([
        html.H1("Анализ инвестиционного портфеля", style={
            'textAlign': 'center',
            'color': 'white'
        }),

        # Плашки с метриками
        html.Div([
            html.Div([
                html.H4("Текущая стоимость портфеля", style={'textAlign': 'center', 'color': '#FFFFFF'}),
                html.Div(f"{total_portfolio_value:.2f} руб.",
                         style={'fontSize': 20, 'fontWeight': 'bold', 'textAlign': 'center', 'color': '#FFFFFF'}),
                html.Div(f"Доходность: {total_profitability:.2f}%",
                         style={'fontSize': 16, 'textAlign': 'center', 'color': '#D8D8D8'})
            ], style={'border': '1px solid #444', 'padding': 10, 'margin': 10, 'width': '18%',
                      'display': 'inline-block',
                      'backgroundColor': '#2A2A2A', 'borderRadius': '10px',
                      'boxShadow': '0px 4px 10px rgba(0, 0, 0, 0.5)'}),

            html.Div([
                html.H4("Получено", style={'textAlign': 'center', 'color': '#FFFFFF'}),
                html.Div(f"Купоны: {operations_summary['total_coupons']:.2f} руб.",
                         style={'fontSize': 16, 'textAlign': 'center', 'color': '#D8D8D8'}),
                html.Div(f"Дивиденды: {operations_summary['total_dividends']:.2f} руб.",
                         style={'fontSize': 16, 'TextAlign': 'center', 'color': '#D8D8D8'})
            ], style={'border': '1px solid #444', 'padding': 10, 'margin': 10, 'width': '18%',
                      'display': 'inline-block',
                      'backgroundColor': '#2A2A2A', 'borderRadius': '10px',
                      'boxShadow': '0px 4px 10px rgba(0, 0, 0, 0.5)'}),

            html.Div([
                html.H4("Средства", style={'textAlign': 'center', 'color': '#FFFFFF'}),
                html.Div(f"Введено: {operations_summary['total_deposits']:.2f} руб.",
                         style={'fontSize': 16, 'textAlign': 'center', 'color': '#D8D8D8'}),
                html.Div(f"Выведено: {operations_summary['total_withdrawals']:.2f} руб.",
                         style={'fontSize': 16, 'textAlign': 'center', 'color': '#D8D8D8'})
            ], style={'border': '1px solid #444', 'padding': 10, 'margin': 10, 'width': '18%',
                      'display': 'inline-block',
                      'backgroundColor': '#2A2A2A', 'borderRadius': '10px',
                      'boxShadow': '0px 4px 10px rgba(0, 0, 0, 0.5)'}),

            html.Div([
                html.H4("Всего уплачено", style={'textAlign': 'center', 'color': '#FFFFFF'}),
                html.Div(f"Налоги: {total_taxes:.2f} руб.",
                         style={'fontSize': 16, 'textAlign': 'center', 'color': '#D8D8D8'}),
                html.Div(f"Комиссии: {total_commissions:.2f} руб.",
                         style={'fontSize': 16, 'textAlign': 'center', 'color': '#D8D8D8'})
            ], style={'border': '1px solid #444', 'padding': 10, 'margin': 10, 'width': '18%',
                      'display': 'inline-block',
                      'backgroundColor': '#2A2A2A', 'borderRadius': '10px',
                      'boxShadow': '0px 4px 10px rgba(0, 0, 0, 0.5)'}),
        ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),

        html.Div([
            html.Div([
                dcc.Graph(
                    figure=px.sunburst(
                        sunburst_data,
                        path=['type', 'portfolio_name'],
                        values='total_value',
                        title='Детализация по типам активов и счетам',
                        template='plotly_dark',
                        color_discrete_sequence=["#396534", "#C51C33", "#EBC641", "#AEC76B"]
                    ).update_layout(
                        plot_bgcolor='#2A2A2A',
                        paper_bgcolor='#2A2A2A'
                    ),
                    style={
                        'padding': '20px',
                        'margin': '10px',
                        'height': '800px'
                    }
                )
            ], style={
                'width': '48%',
                'backgroundColor': '#2A2A2A',
                'borderRadius': '10px',
                'boxShadow': '0px 4px 10px rgba(0, 0, 0, 0.5)',
                'padding': '20px',
                'marginRight': '2%'
            }
            ),

            html.Div([
                dcc.Graph(
                    figure=px.bar(
                        input_output_yearly,
                        x='year',
                        y='amount',
                        color='account',
                        title='Пополнение и вывод средств',
                        labels={'amount': 'Сумма', 'year': 'Год'},
                        barmode='group',
                        hover_data={'type': True, 'portfolio_name': True, 'amount': ':.2f', 'account': False},
                        template='plotly_dark',
                        color_discrete_sequence=["#396534", "#C51C33", "#EBC641"]
                    ).update_layout(
                        plot_bgcolor='#2A2A2A',
                        paper_bgcolor='#2A2A2A'
                    ),
                    style={
                        'padding': '20px',
                        'marginBottom': '20px',
                        'height': '390px'
                    }
                ),
                dcc.Graph(
                    figure=px.bar(
                        payments_analytics,
                        x='year',
                        y='amount',
                        color='type',
                        title='Выплаты по годам',
                        labels={'amount': 'Сумма', 'year': 'Год'},
                        barmode='group',
                        template='plotly_dark',
                        color_discrete_sequence=["#C51C33", "#396534"]
                    ).update_layout(
                        plot_bgcolor='#2A2A2A',
                        paper_bgcolor='#2A2A2A'
                    ),
                    style={
                        'padding': '20px',
                        'height': '390px'
                    }
                )
            ], style={
                'width': '48%',
                'backgroundColor': '#2A2A2A',
                'borderRadius': '10px',
                'boxShadow': '0px 4px 10px rgba(0, 0, 0, 0.5)',
                'padding': '20px',
                'display': 'flex',
                'flexDirection': 'column'
            })
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

        dcc.Graph(
            figure=px.treemap(
                treemap_data,
                path=['sector', 'name'],
                values='total_value',
                title='Состав портфеля',
                template='plotly_dark',
                color_discrete_sequence=["#396534", "#C51C33", "#EBC641", "#A20132", "#5B002B", "#A01913", "#4C1B16",
                                         "#DE451C", "#D66626", "#66600F", "#AEC76B", "#FFFFFF", "#C0C0C0", "#516D45",
                                         "#7C991E"]
            ).update_layout(
                plot_bgcolor='#2A2A2A',
                paper_bgcolor='#2A2A2A'
            ),
            style={'backgroundColor': '#2A2A2A', 'height': '800px', 'padding': '20px', 'marginTop': '20px',
                   'borderRadius': '10px',
                   'boxShadow': '0px 4px 10px rgba(0, 0, 0, 0.5)'}
        ),

        html.Div([
            html.H4("Сравнение текущих и средних цен активов", style={'textAlign': 'center', 'color': '#FFFFFF'}),
            html.Div([
                dcc.Graph(
                    figure=create_graph(grouped_data[grouped_data['type'] == 'share'], 'акций')
                ),
                dcc.Graph(
                    figure=create_graph(grouped_data[grouped_data['type'] == 'bond'], 'облигаций')
                ),
                dcc.Graph(
                    figure=create_graph(grouped_data[grouped_data['type'] == 'etf'], 'ETF')
                )
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '20px'}),

            html.Div([
                html.Div([
                    html.Span(style={
                        'display': 'inline-block',
                        'width': '20px',
                        'height': '20px',
                        'backgroundColor': '#C51C33',
                        'marginRight': '10px'
                    }),
                    "Текущая цена ниже средней"
                ], style={'marginBottom': '10px'}),
                html.Div([
                    html.Span(style={
                        'display': 'inline-block',
                        'width': '20px',
                        'height': '20px',
                        'backgroundColor': '#396534',
                        'marginRight': '10px'
                    }),
                    "Текущая цена выше средней"
                ], style={'marginBottom': '10px'}),
                html.Div([
                    html.Span(style={
                        'display': 'inline-block',
                        'width': '20px',
                        'height': '20px',
                        'backgroundColor': '#D8D8D8',
                        'marginRight': '10px'
                    }),
                    "Средняя цена покупки"
                ])
            ], style={'textAlign': 'center', 'color': '#D8D8D8', 'marginTop': '20px'})
        ], style={'backgroundColor': '#2A2A2A', 'padding': '20px', 'marginTop': '20px', 'borderRadius': '10px',
                  'boxShadow': '0px 4px 10px rgba(0, 0, 0, 0.5)'})
    ], style={'backgroundColor': '#222222', 'padding': '20px'})
