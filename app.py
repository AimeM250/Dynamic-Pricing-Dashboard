import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Function to calculate the impact of price changes based on elasticity
def analyze_price_change_by_channel(merged_data, price_change):
    # Calculate the new price
    merged_data['New Price'] = merged_data['Original Price'] + price_change

    # Calculate the change in sales using the elasticity
    merged_data['Sales Change'] = merged_data['% change in sales for every $ change from original price'] * price_change

    # Calculate the new sales
    merged_data['New Sales'] = merged_data['Sales'] * (1 + merged_data['Sales Change'])

    # Calculate the new revenue
    merged_data['New Revenue'] = merged_data['New Sales'] * merged_data['New Price']

    # Summarize the impact on sales and revenue for each business channel and plan type
    summary = merged_data.groupby(['Business Channel', 'Plan Type - StonePoint']).agg(
        Total_Original_Sales=('Sales', 'sum'),
        Total_New_Sales=('New Sales', 'sum'),
        Total_Original_Revenue=('Sales', lambda x: sum(x * merged_data.loc[x.index, 'Original Price'])),
        Total_New_Revenue=('New Revenue', 'sum')
    ).reset_index()

    # Calculate overall sales and revenue impact
    summary['Sales_Impact'] = summary['Total_New_Sales'] - summary['Total_Original_Sales']
    summary['Revenue_Impact'] = summary['Total_New_Revenue'] - summary['Total_Original_Revenue']

    return summary

# Load the sheets into dataframes
sales_data = pd.read_excel('Jr Data Scientist Project - Data Set.xlsx', sheet_name = 'Sales Data')
plan_prices = pd.read_excel('Jr Data Scientist Project - Data Set.xlsx', sheet_name = 'Plan Prices')

# Clean the plan prices data
plan_prices_cleaned = plan_prices.dropna(subset=['% change in sales for every $ change from original price'])
plan_prices_cleaned['price_elasticity'] = plan_prices_cleaned['% change in sales for every $ change from original price']

# Merge the dataframes
merged_data = pd.merge(sales_data, plan_prices_cleaned, on=['Business Channel', 'Plan Type - StonePoint'])

# Streamlit App
price_change = st.slider("Select the price change ($):", min_value=-20.0, max_value=20.0, value=5.0, step=0.5)

st.title(f"Price Change Impact Analysis ($ {price_change})")

# Analyze the price change
summary_impact_by_channel = analyze_price_change_by_channel(merged_data, price_change)

# Display results as a table
st.subheader("Summary Impact of Price Change by Channel")
st.dataframe(summary_impact_by_channel)

# Plot changes using Plotly
st.subheader("Change in Sales and Revenue")

summary_impact_by_channel['Channel_Plan'] = summary_impact_by_channel['Business Channel'] + " - " + summary_impact_by_channel['Plan Type - StonePoint']

fig = go.Figure()

# Add traces for original and new sales
fig.add_trace(go.Bar(
    x=summary_impact_by_channel['Channel_Plan'],
    y=summary_impact_by_channel['Total_Original_Sales'],
    name='Original Sales',
    marker_color='indianred'
))

fig.add_trace(go.Bar(
    x=summary_impact_by_channel['Channel_Plan'],
    y=summary_impact_by_channel['Sales_Impact'],
    name='Sales Impact',
    marker_color='lightsalmon'
))

# Add traces for original and new revenue
fig.add_trace(go.Bar(
    x=summary_impact_by_channel['Channel_Plan'],
    y=summary_impact_by_channel['Total_Original_Revenue'],
    name='Original Revenue',
    marker_color='lightblue'
))

fig.add_trace(go.Bar(
    x=summary_impact_by_channel['Channel_Plan'],
    y=summary_impact_by_channel['Revenue_Impact'],
    name='Revenue Impact',
    marker_color='blue'
))

fig.update_layout(
    barmode='stack',
    xaxis_tickangle=-45,
    title='Impact of Price Change on Sales and Revenue',
    xaxis_title='Business Channel - Plan Type',
    
    yaxis_title='Impact',
    legend_title='Legend',
    plot_bgcolor='rgba(0,0,0,0)',
)

st.plotly_chart(fig)


# Explanations
st.subheader(f"Analysis of Sample Data for a Price Change of $ {price_change}")
for index, row in summary_impact_by_channel.iterrows():
    business_channel = row['Business Channel']
    plan_type = row['Plan Type - StonePoint']
    elasticity = plan_prices_cleaned[(plan_prices_cleaned['Business Channel'] == business_channel) & 
                                     (plan_prices_cleaned['Plan Type - StonePoint'] == plan_type)]['price_elasticity'].values[0]
    sales_impact = row['Sales_Impact']
    revenue_impact = row['Revenue_Impact']
    
    st.markdown(f"**{business_channel} - {plan_type}:**")
    if elasticity > 0:
        st.markdown(f"- **Elasticity**: Positive ({elasticity:.4f}), indicating a {elasticity*100:.2f}% increase in sales for each $1 increase in price.")
    else:
        st.markdown(f"- **Elasticity**: Negative ({elasticity:.4f}), indicating a {abs(elasticity*100):.2f}% decrease in sales for each $1 increase in price.")
    st.markdown(f"- **Impact**: Sales changed by {sales_impact:.2f} units, and revenue changed by ${revenue_impact:.2f}.")
    
    