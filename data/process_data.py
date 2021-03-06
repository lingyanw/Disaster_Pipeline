import sys
import pandas as pd
import numpy as np
import sqlite3
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    '''
    load data from given files and combine them to a dataframe
    parameters:
    messages_filepath: message datafile path
    categories_filepath: category datafile path
    returns:
    df: dataframe containing messages and categories 
    '''
    #read data
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    # combine messages and categories data
    df = messages.merge(categories,how = 'inner', on = ['id'])
    return df


def clean_data(df):
    '''
    clean data, remove duplicates and properly format data
    parameters:
    df: dataframe containing messages and categories 
    returns:
    df: cleanedd dataframe containing messages and categories 
    '''
    #1. create a dataframe of the 36 individual category columns
    categories = df['categories'].str.split(';',expand=True)
    
    #2. rename the columns of categories
    #separate the first row and cut the name string
    row = categories.loc[0]
    s = lambda x: x[:-2]
    category_colnames = []
    for x in row:
        category_colnames.append(s(x))
    # rename the columns 
    categories.columns = category_colnames
   
    #3. convert the categories values to binary values 
    for column in categories:
    # set each value to be the last character of the string
        categories[column] =  categories[column].str[-1]
    # convert column from string to numeric
        categories[column] =  categories[column].astype(int)
    # convert all '2' in 'related' category to 1 
    categories.related[categories.related==2]=1
    
    #4. replace df category columns with new cleaned ones 
    df = df.drop(['categories'],axis = 1)
    df = pd.concat([df,categories],axis = 1)
    
    #5. remove duplicates 
    df = df.drop_duplicates()
    return df


def save_data(df, database_filename):
    '''
    save cleaned dataset to database
    parameters:
    df: cleaned dataframe containing messages and categories 
    database_filename: database name you want to use
    '''
    engine = create_engine('sqlite:///'+ database_filename)
    df.to_sql('data', engine, index=False, if_exists = 'replace')  


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
