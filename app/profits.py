# import pandas as pd
# from app.models import Car



# # Assuming you have a function to calculate the profit margins
# def get_profit_data(start_date, end_date):
    
#     # Calculate the profit data for the given period
#     profit_data = Car.query.filter(Car.date_added >= start_date, Car.date_added <= end_date).with_entities(Car.SP- Car.BP)

#     # Convert the result to a data frame
#     profit_data = pd.read_sql(profit_data.statement, profit_data.session.bind).set_index(0).cumsum()

#     return profit_data.rename(columns={0: 'Profit'})
