from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly
import json

app = Flask(__name__)
df = pd.read_csv('data/supermarket_sales.csv')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sales_trends')
def sales_trends():
    # Convert date column to datetime format, allowing for automatic format inference
    df['Date'] = pd.to_datetime(df['Date'], infer_datetime_format=True, errors='coerce')

    # Drop any rows where the date couldn't be parsed
    df.dropna(subset=['Date'], inplace=True)

    # Extract month-year and aggregate sales by month
    df['Month'] = df['Date'].dt.to_period('M').astype(str)  # Convert Period to string
    sales_by_month = df.groupby('Month')['Total'].sum().reset_index()

    # Generate Plotly graph
    fig = px.line(sales_by_month, x='Month', y='Total', title='Sales Trends Over Time')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('sales_trends.html', graphJSON=graphJSON)



@app.route('/similar_product', methods=['GET'])
def similar_product():
    # Get query parameters for filtering
    product_line = request.args.get('product_line', default='Electronic accessories', type=str)
    city = request.args.get('city', default='Yangon', type=str)
    gender = request.args.get('gender', default='Male', type=str)

    # Filter the dataset based on selected criteria
    filtered_df = df[(df['Product line'] == product_line) & (df['City'] == city)]
    if gender != 'None':
        filtered_df = filtered_df[filtered_df['Gender'] == gender]

    # Check if the filtered dataframe is empty
    if filtered_df.empty:
        print("Filtered dataframe is empty.")  # Debugging print
        return render_template('similar_product.html', product_line=product_line, city=city, gender=gender, product_details=[], graph_JSON='')

    # Aggregate gross income and ratings data
    gross_income_data = filtered_df[['Product line', 'gross income']].groupby('Product line').sum().reset_index()
    ratings_data = filtered_df[['Product line', 'Rating']].groupby('Product line').mean().reset_index()

    # Check if gross_income_data and ratings_data are empty
    print("Gross Income Data:\n", gross_income_data)  # Debugging print
    print("Ratings Data:\n", ratings_data)  # Debugging print

    # Generate Plotly graphs
    fig = px.bar(gross_income_data, x='Product line', y='gross income', title=f'Gross Income for {product_line} in {city}')
    fig.add_trace(px.bar(ratings_data, x='Product line', y='Rating').data[0])
    fig.update_layout(barmode='group')

    graph_JSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Prepare product details for display
    product_details = filtered_df[['Product line', 'City', 'gross income', 'Rating']].to_dict(orient='records')

    return render_template('similar_product.html', product_line=product_line, city=city, gender=gender, product_details=product_details, graph_JSON=graph_JSON)

@app.route('/category_performance')
def category_performance():
    # Aggregate sales by product line
    sales_by_category = df.groupby('Product line')['Total'].sum().reset_index()

    # Generate Plotly graph
    fig = px.bar(sales_by_category, x='Product line', y='Total', title='Sales by Product Line')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('category_performance.html', graphJSON=graphJSON)

@app.route('/customer_insights')
def customer_insights():
    # Aggregate count of transactions by gender
    gender_count = df['Gender'].value_counts().reset_index()
    gender_count.columns = ['Gender', 'Count']

    # Generate Plotly graph
    fig = px.pie(gender_count, values='Count', names='Gender', title='Customer Gender Distribution')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('customer_insights.html', graphJSON=graphJSON)

@app.route('/revenue_by_branch')
def revenue_by_branch():
    # Aggregate sales by branch
    revenue_by_branch = df.groupby('Branch')['Total'].sum().reset_index()

    # Generate Plotly graph
    fig = px.bar(revenue_by_branch, x='Branch', y='Total', title='Revenue by Branch')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('revenue_by_branch.html', graphJSON=graphJSON)



@app.route('/display')
def display():
    # Aggregate average rating by product line
    ratings_by_category = df.groupby('Product line')['Rating'].mean().reset_index()

    # Generate Plotly graph
    fig = px.bar(ratings_by_category, x='Product line', y='Rating', title='Average Rating by Product Line')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('display.html', graphJSON=graphJSON)

if __name__ == '__main__':
    app.run(debug=True)
