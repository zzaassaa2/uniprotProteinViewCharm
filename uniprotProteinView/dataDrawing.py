import dataParse
import plotly.graph_objects as go


def drawProtein(proteins, types=None, descriptionSearch=None, offsetSearch=None, title=None, showProgress=True):
    types = [] if types is None else types
    dess = [] if descriptionSearch is None else descriptionSearch
    offset = [] if offsetSearch is None else offsetSearch
    featuresDataFrame = dataParse.getFeaturesDataFrame(proteins, types, dess, offset, showProgress)

    fig = go.Figure()

    protName = None
    for index, row in featuresDataFrame.iterrows():
        name = row['Name']
        xi = row['Start']
        xf = row['Finish']
        yi = row['yStart']
        yf = row['yStop']
        clr = row['Color']
        fig.add_trace(go.Scatter(x=[xi, xi, xf, xf],
                                 y=[yi, yf, yf, yi],
                                 fill='toself',
                                 fillcolor=clr,
                                 hoveron='fills',
                                 line=dict(color="rgba(1,1,1,0.0)"),
                                 name=name,
                                 text=name,
                                 hoverinfo='text+x+y'
                                 ))
        newName = row['ProtName']
        if protName != newName:
            fig.add_annotation(x=-0.01,
                               y=yi + 0.5,
                               text=newName,
                               showarrow=False,
                               xanchor="right",
                               font=dict(size=8)
                               )
            protName = newName

    fig.update_layout(
        title=title,
        xaxis=dict(showgrid=False, title='Protein Size', dtick=50),
        yaxis=dict(showgrid=False, tickvals=[])
    )

    fig.show()
