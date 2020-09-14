from flask import Flask
import os
import dash
import pandas as pd
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import numpy as np
import dash_leaflet as dl


basedir=os.path.abspath(os.path.dirname(__file__))
server=Flask(__name__)
server.config['SECRET_KEY'] = 'hvewydbh643hvcjhv@#ycvdagc*874g'
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']



app = dash.Dash(__name__, server=server, url_base_pathname='/', external_stylesheets=external_stylesheets)
path=os.path.join(basedir,'data\\Transactions.csv')
df=pd.read_csv(path,low_memory=False)
df.area_name_en.fillna("None",inplace=True)
df['instance_date'] = df['instance_date'].astype('datetime64[ns]')
path1=os.path.join(basedir,'data\\Past10YearPiePlot.csv')
df1=pd.read_csv(path1,index_col ="Unnamed: 0")
names=df1.index
df['year']=df.instance_date.dt.year
years=[str(i) for i in range(1995,2021)]
table = pd.pivot_table(df,values=['instance_date'], index=['area_name_en', 'year'],columns=['procedure_name_en'],fill_value=0, aggfunc='count')
grouped_df = df.groupby(df.area_name_en)
path2=os.path.join(basedir,'data\\latslons.csv')
df2=pd.read_csv(path2,index_col="area_name_en")
path3=os.path.join(basedir,'data\\amenities_new.csv')
df3=pd.read_csv(path3)
has_amenity=df3["area_name_en"].unique()
path4=os.path.join(basedir,'data\\new1_dubai_reduced.csv')
df4=pd.read_csv(path4)
df4['instance_date'] = df4['instance_date'].astype('datetime64[ns]')



app.layout = html.Div(children=[
	dcc.Tabs([
		dcc.Tab(label="Home",children=[
			html.Div([
			dcc.Dropdown(
				id='dropdown',
				options=[
					{'label': city, 'value': city} for city in df2.index
				],
				value="Al Barsha")
			],style={'marginBottom': 15, 'marginTop': 15}),

			html.Div([
						dl.Map(children=[dl.TileLayer(), dl.Marker(id="marker",position=[25.099479,55.203292])],
							   style={'width': "100%", 'height': "100%"}, center=[25.05, 54.25],zoom=8, id="map"),
					], style={'height': '500px'}),

			html.Div([
				html.Div([
							html.H4('  Sales by Year'),
							dcc.Graph(id='barchart',
							  config={'displayModeBar': False},
							  animate=True)],className="six columns"),
				html.Div([
							html.H4('Mortgages by Year'),
							dcc.Graph(id='barchart2',
							  config={'displayModeBar': False},
							  animate=True)],className="six columns"),
			],style={'marginBottom': 15, 'marginTop': 15},className="row"),

			html.Div([
						html.H4('Average transactional sale price procedure_name_en'),
						dcc.Graph(id='bubblechart',
						  config={'displayModeBar': False},
						  animate=True)],style={'marginBottom': 15, 'marginTop': 15}),
			html.Div([
						html.H4('Average transactional sale price by property_sub_type'),
						dcc.Graph(id='bubblechart2',
						  config={'displayModeBar': False},
						  animate=True)],style={'marginBottom': 15, 'marginTop': 15}),
			html.Div([
				html.Div([
					html.Div([html.H4('No. of transactions By Category')],className="four columns"),
					html.Div([
						dcc.Graph(id='piechart',
						  config={'displayModeBar': False},
						  animate=True)],style={'marginBottom': 15, 'marginTop': 15},className="eight columns"),
				],className="row"),
					html.Div([
						dcc.RangeSlider(
							id='my-range-slider',
							min=0,
							max=25,
							step=None,
							marks={0: '1995', 1: '1996', 2: '1997', 3: '1998', 4: '1999', 5: '2000', 6: '2001', 7: '2002', 8: '2003', 9: '2004', 10: '2005', 11: '2006', 12: '2007', 13: '2008', 14: '2009', 15: '2010', 16: '2011', 17: '2012', 18: '2013', 19: '2014', 20: '2015', 21: '2016', 22: '2017', 23: '2018', 24: '2019', 25: '2020'},
							value=[0, 3]
						)]),
			],style={'marginBottom': 15, 'marginTop': 15}),

			html.Div([
						html.H4('Local Amenities'),
						dcc.Graph(id='barlocal',
						  config={'displayModeBar': False},
						  animate=True)],style={'marginBottom': 15, 'marginTop': 15})
		]),

		dcc.Tab(label="Sales Data",children=[
			html.Div([
			dcc.Dropdown(
				id='dropdown-2',
				options=[
					{'label': city, 'value': city} for city in df2.index
				],
				value="Al Barsha")
			],style={'marginBottom': 15, 'marginTop': 15}),

			html.Div([
			dl.Map(children=[dl.TileLayer(), dl.LayerGroup(id="markers")],
				   style={'width': "100%", 'height': "100%"}, center=[25.05, 54.25],zoom=8, id="map2"),
			], style={'height': '500px', 'marginBottom': 15}),

			html.Div([
			dcc.RangeSlider(
				id='my-range-slider-2',
				min=0,
				max=3,
				step=None,
				marks={0:'2017',1:'2018',2:'2019',3:'2020'},
				value=[0, 3]
			)]),

			html.Div(id='dd-output-container')
		])
	])
])

@app.callback(
	dash.dependencies.Output('piechart', 'figure'),
	[dash.dependencies.Input('my-range-slider', 'value')])
def update_output(value):
	values=[]
	for i in names:
		values.append(np.sum(df1.loc[i][value[0]:value[1]+1]))
	pieplot=px.pie(df,names=names,values=values,hole=.4,width=480,height=480).update_traces(textposition='inside',textinfo='label+percent')
	return (pieplot)


@app.callback(
	dash.dependencies.Output('barchart', 'figure'),
	[dash.dependencies.Input('dropdown', 'value')])
def update_output(value):
	SalesOfYear=list(table.loc[value].index)
	sales=[]
	for i in SalesOfYear:
		sales.append(table.loc[value].loc[i][2])
	if sum(sales)>0:
		fig = px.bar(x=SalesOfYear, y=sales)
		fig.update_layout(xaxis_title="Year",yaxis_title="Sales")
		return (fig)
	else:
		fig=px.bar()
		fig.update_layout({
				"xaxis":{
					"visible": False
				},
				"yaxis":{
					"visible": False
				},
				"annotations": [
					{
						"text": "No Sales data found",
						"xref": "paper",
						"yref": "paper",
						"showarrow": False,
						"font": {
							"size": 28
						}
					}
				]
			})
		return fig



@app.callback(
	dash.dependencies.Output('barchart2', 'figure'),
	[dash.dependencies.Input('dropdown', 'value')])
def update_output(value):
	MortgagesOfYear=list(table.loc[value].index)
	mortgages=[]
	for i in MortgagesOfYear:
		mortgages.append(table.loc[value].loc[i][1])
	if sum(mortgages)>0:
		fig = px.bar(x=MortgagesOfYear, y=mortgages)
		fig.update_layout(xaxis_title="Year",yaxis_title="Mortgages")
		return (fig)
	else:
		fig=px.bar()
		fig.update_layout({
				"xaxis":{
					"visible": False
				},
				"yaxis":{
					"visible": False
				},
				"annotations": [
					{
						"text": "No Mortgages data found",
						"xref": "paper",
						"yref": "paper",
						"showarrow": False,
						"font": {
							"size": 28
						}
					}
				]
			})
		return fig


@app.callback(
	dash.dependencies.Output('bubblechart', 'figure'),
	[dash.dependencies.Input('dropdown', 'value')])
def update_output(value):
	data=grouped_df.get_group(value)
	fig = px.scatter(data, x="procedure_area", y="meter_sale_price",
			 size="actual_worth", color="procedure_name_en",log_x=True, size_max=100)
	return (fig)


@app.callback(
	dash.dependencies.Output('bubblechart2', 'figure'),
	[dash.dependencies.Input('dropdown', 'value')])
def update_output(value):
	data=grouped_df.get_group(value)
	fig = px.scatter(data, x="procedure_area", y="meter_sale_price",
			 size="actual_worth", color="property_sub_type_en",log_x=True, size_max=100)
	return (fig)

@app.callback(
	dash.dependencies.Output('marker', 'position'),
	[dash.dependencies.Input('dropdown', 'value')])
def update_output(value):
	return [df2.loc[value].latitude,df2.loc[value].longitude]

@app.callback(
	dash.dependencies.Output('barlocal', 'figure'),
	[dash.dependencies.Input('dropdown', 'value')])
def update_output(value):
	if value in has_amenity:
		grouped=df3.groupby("area_name_en")
		data=grouped.get_group(value).amenity.value_counts().to_dict()
		new_df2=pd.DataFrame.from_dict(data,orient="index")
		new_df2.reset_index(inplace=True)
		new_df2.columns=["Amenity","Count"]
		fig = px.bar(new_df2, x="Count", y="Amenity", orientation='h')
		return fig
	else:
		fig=px.bar()
		fig.update_layout({
				"xaxis":{
					"visible": False
				},
				"yaxis":{
					"visible": False
				},
				"annotations": [
					{
						"text": "No Local Amenities data found",
						"xref": "paper",
						"yref": "paper",
						"showarrow": False,
						"font": {
							"size": 28
						}
					}
				]
			})
		return fig


@app.callback(
	dash.dependencies.Output('markers', 'children'),
	[dash.dependencies.Input('dropdown-2', 'value'),
	dash.dependencies.Input('my-range-slider-2', 'value')])
def update_output(value1,value2):
	if value2==[0,3]:
		data=df4.loc[(df4["area_name_en"]==value1) & (df4["instance_date"].dt.year>=2017.0)]
		if len(data)>0:
			data=data[["lat","lon"]]
			data.drop_duplicates(inplace=True)
			marker_data = [dl.Marker(position=[row["lat"], row["lon"]]) for i, row in data.iterrows()]
			return(marker_data)


	elif value2==[1,3]:
		data=df4.loc[(df4["area_name_en"]==value1) & (df4["instance_date"].dt.year>=2018.0)]
		if len(data)>0:
			data=data[["lat","lon"]]
			data.drop_duplicates(inplace=True)
			marker_data = [dl.Marker(position=[row["lat"], row["lon"]]) for i, row in data.iterrows()]
			return(marker_data)

	elif value2==[2,3]:
		data=df4.loc[(df4["area_name_en"]==value1) & (df4["instance_date"].dt.year>=2019.0)]
		if len(data)>0:
			data=data[["lat","lon"]]
			data.drop_duplicates(inplace=True)
			marker_data = [dl.Marker(position=[row["lat"], row["lon"]]) for i, row in data.iterrows()]
			return(marker_data)

	elif value2==[3,3]:
		data=df4.loc[(df4["area_name_en"]==value1) & (df4["instance_date"].dt.year==2020.0)]
		if len(data)>0:
			data=data[["lat","lon"]]
			data.drop_duplicates(inplace=True)
			marker_data = [dl.Marker(position=[row["lat"], row["lon"]]) for i, row in data.iterrows()]
			return(marker_data)

	elif value2==[0,2]:
		data=df4.loc[(df4["area_name_en"]==value1) & ((df4["instance_date"].dt.year>=2017.0) & (df4["instance_date"].dt.year<=2019.0))]
		if len(data)>0:
			data=data[["lat","lon"]]
			data.drop_duplicates(inplace=True)
			marker_data = [dl.Marker(position=[row["lat"], row["lon"]]) for i, row in data.iterrows()]
			return(marker_data)

	elif value2==[1,2]:
		data=df4.loc[(df4["area_name_en"]==value1) & ((df4["instance_date"].dt.year>=2018.0) & (df4["instance_date"].dt.year<=2019.0))]
		if len(data)>0:
			data=data[["lat","lon"]]
			data.drop_duplicates(inplace=True)
			marker_data = [dl.Marker(position=[row["lat"], row["lon"]]) for i, row in data.iterrows()]
			return(marker_data)

	elif value2==[2,2]:
		data=df4.loc[(df4["area_name_en"]==value1) & (df4["instance_date"].dt.year==2019.0)]
		if len(data)>0:
			data=data[["lat","lon"]]
			data.drop_duplicates(inplace=True)
			marker_data = [dl.Marker(position=[row["lat"], row["lon"]]) for i, row in data.iterrows()]
			return(marker_data)

	elif value2==[0,1]:
		data=df4.loc[(df4["area_name_en"]==value1) & ((df4["instance_date"].dt.year>=2017.0) & (df4["instance_date"].dt.year<=2018.0))]
		if len(data)>0:
			data=data[["lat","lon"]]
			data.drop_duplicates(inplace=True)
			marker_data = [dl.Marker(position=[row["lat"], row["lon"]]) for i, row in data.iterrows()]
			return(marker_data)

	elif value2==[1,1]:
		data=df4.loc[(df4["area_name_en"]==value1) & (df4["instance_date"].dt.year==2018.0)]
		if len(data)>0:
			data=data[["lat","lon"]]
			data.drop_duplicates(inplace=True)
			marker_data = [dl.Marker(position=[row["lat"], row["lon"]]) for i, row in data.iterrows()]
			return(marker_data)

	elif value2==[0,0]:
		data=df4.loc[(df4["area_name_en"]==value1) & (df4["instance_date"].dt.year==2017.0)]
		if len(data)>0:
			data=data[["lat","lon"]]
			data.drop_duplicates(inplace=True)
			marker_data = [dl.Marker(position=[row["lat"], row["lon"]]) for i, row in data.iterrows()]
			return(marker_data)

