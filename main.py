import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from trade_analysis import TradeAnalysis


trade_analysis_obj = TradeAnalysis()
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server
app.layout = html.Div([html.H1('Trade analysis - Toy example'),\
                       dcc.Dropdown(options={info:info for info in ['price_execution','order_qty','side_dist']},\
                                    value='price_execution',id='info',multi=False),\
                       dcc.Graph(id='info_plot')],style={'paddingBottom': 10, 'paddingTop': 15,\
                                                         'paddingRight': 10, 'paddingLeft': 10})


@app.callback(
  Output(component_id='info_plot',component_property='figure'),\
  Input(component_id='info', component_property='value')
)
def plot(value):
    if value == 'price_execution':
        # Silence warning as this is a false positive for self.buy_df and self.sell_df
        pd.set_option('mode.chained_assignment', None)
        quartile25, quartile75 = np.percentile(trade_analysis_obj.df['price'], 25),\
                                 np.percentile(trade_analysis_obj.df['price'], 75)
        interquartile = quartile75 - quartile25
        lower_bound = quartile25 - interquartile * 1.5
        upper_bound = quartile75 + interquartile * 1.5
        less_lower_bound_s = trade_analysis_obj.df.price < lower_bound
        more_upper_bound_s = trade_analysis_obj.df.price > upper_bound
        temp_df = trade_analysis_obj.df[['price']]
        temp_df.loc[:,'filtered_price'] = temp_df.loc[:,'price']
        temp_df.loc[less_lower_bound_s, 'filtered_price'] = lower_bound
        temp_df.loc[more_upper_bound_s, 'filtered_price'] = upper_bound
        fig = px.line(temp_df)
        fig.add_hline(y=lower_bound,line_dash='dash', annotation_text='upper bound',\
                      annotation_position='top right')
        fig.add_hline(y=upper_bound,line_dash='dash', annotation_text='lower bound',\
                      annotation_position='bottom left')
        fig.add_vrect(x0='2017-06-01 11:30', x1='2017-06-01 12:30', line_dash='dash', \
                      fillcolor='green', annotation_text='mid day', opacity=0.75, annotation_position='bottom right')
    elif value == 'order_qty':
        order_qty_s = (trade_analysis_obj.df.groupby('taker_side').count()['quantity'] / \
        trade_analysis_obj.df.groupby('taker_side').count()['quantity'].sum()).round(4)
        order_qty_df = pd.DataFrame(order_qty_s)
        order_qty_df.loc[:,'side'] = order_qty_df.index.tolist()
        fig = px.pie(order_qty_df, values='quantity', names='side', title='Percentage of BUY vs SELL orders',\
                     hole=.4)

    elif value == 'side_dist':
        fig = px.histogram(trade_analysis_obj.df, x='quantity', color='taker_side', \
                           title='Distribution of trades - Direction', text_auto=True)
        fig.show()

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)