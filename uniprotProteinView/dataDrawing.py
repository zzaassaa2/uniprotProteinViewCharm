import dataRetrieval
import dataParse
import plotly.graph_objects as go
import pandas as pd


def drawProtein():
    None


xml = dataRetrieval.getProtein(["../Q04206.xml", "../Q04207.xml"])
featuresDataFrame = dataParse.getFeaturesDataFrame(xml, ['chain'])

#
# df = pd.DataFrame([
#     dict(Name="p65", Start=0, Finish=300, yStart=0, color="red"),
#     dict(Name="     p65_domain", Start=80, Finish=210, yStart=0, color="purple"),
#     dict(Name="p67", Start=0, Finish=170, yStart=1, color="green"),
# ])
#
# fig = go.Figure()
#
# for index, row in df.iterrows():
#     name = row['Name']
#     xi = row['Start']
#     xf = row['Finish']
#     y = row['yStart']
#     clr = row['color']
#     fig.add_trace(go.Scatter(x=[xi, xi, xf, xf],
#                              y=[y, y+1, y+1, y],
#                              fill='toself',
#                              fillcolor=clr,
#                              hoveron='fills',
#                              line=dict(color ="rgba(1,1,1,0.0)"),
#                              name=name,
#                              text=name,
#                              hoverinfo='text+x+y'
#                              ))
#
#
# fig.update_layout(
#     title="hover on <i>points</i> or <i>fill</i>",
#     xaxis=dict(showgrid=False, title='Protein Size', dtick=50),
#     yaxis=dict(showgrid=False, tickvals=[])
# )
#
# fig.show()
