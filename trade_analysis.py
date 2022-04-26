import pandas as pd
import sqlite3

class TradeAnalysis:

    def __init__(self):
        df = pd.read_sql(sql='SELECT * FROM trades',\
                                     con=sqlite3.connect('sample_data.db'),index_col='time_exchange')
        df = df.drop(['time_coinapi','guid'],axis=1).rename(columns={'quantity':'base_amount'})
        df.index = pd.to_datetime(df.index,format='%Y-%m-%d %H:%M:%S.%f')
        df[['price','quantity']] = df[['price','quantity']].astype(float)
        self.df = df

    @property
    def df(self):
        return self.__df

    @df.setter
    def df(self, df):
        self.__df = df