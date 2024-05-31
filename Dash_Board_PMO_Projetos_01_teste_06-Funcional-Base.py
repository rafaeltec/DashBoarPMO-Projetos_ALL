import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import base64
import io

# Inicializar o aplicativo Dash
# Define o nome do aplicativo como __name__ e usa o tema BOOTSTRAP do dash_bootstrap_components
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Função para processar o arquivo uploadado
# Recebe o conteúdo do arquivo e o nome do arquivo como entrada
def parse_contents(contents, filename):
    # Divide o conteúdo em tipo de conteúdo e string de conteúdo
    content_type, content_string = contents.split(',')
    # Decodifica a string de conteúdo usando base64
    decoded = base64.b64decode(content_string)
    # Tenta ler o arquivo com base na extensão
    try:
        if 'csv' in filename:
            # Se for um arquivo CSV, lê usando pd.read_csv
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename or 'xlsx':
            # Se for um arquivo Excel, lê usando pd.read_excel
            df = pd.read_excel(io.BytesIO(decoded))
        # Retorna o DataFrame
        return df
    except Exception as e:
        # Imprime a exceção se ocorrer algum erro
        print(e)
        # Retorna None se houver um erro ao ler o arquivo
        return None

# Função para filtrar dados
# Recebe o DataFrame e os valores dos filtros como entrada
def filter_data(df, project, department, manager):
    # Cria uma cópia do DataFrame para evitar a modificação do DataFrame original
    filtered_df = df.copy()
    # Aplica os filtros um por um
    if project and project != 'Todos':
        # Filtra por projeto se o projeto não for 'Todos'
        filtered_df = filtered_df[filtered_df['Nome do Projeto'] == project]
    if department and department != 'Todos':
        # Filtra por departamento se o departamento não for 'Todos'
        filtered_df = filtered_df[filtered_df['Departamento'] == department]
    if manager and manager != 'Todos':
        # Filtra por gerente se o gerente não for 'Todos'
        filtered_df = filtered_df[filtered_df['Gerente do Projeto'] == manager]
    # Retorna o DataFrame filtrado
    return filtered_df

# Layout do aplicativo
# Define o layout do aplicativo Dash usando componentes dash_bootstrap_components
app.layout = dbc.Container([
    # Primeira linha: Título do aplicativo
    dbc.Row([
        # Uma coluna abrangendo 12 colunas de largura com o título "Dashboard de Projetos"
        dbc.Col(html.H1("Dashboard de Projetos"), width=12)
    ]),

    # Segunda linha: Upload de arquivo
    dbc.Row([
        # Uma coluna abrangendo 12 colunas de largura para o componente de upload de arquivo
        dbc.Col([
            # Componente de upload de arquivo com estilo personalizado
            dcc.Upload(
                id='upload-data',  # ID do componente
                children=html.Div(['Arraste e solte ou ', html.A('selecione um arquivo')]),  # Texto e link para upload de arquivo
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False  # Permite o upload de apenas um arquivo por vez
            ),
            # Div para exibir a saída do upload de dados
            html.Div(id='output-data-upload')
        ], width=12)
    ]),

    # Terceira linha: Filtros
    dbc.Row([
        # Três colunas, cada uma abrangendo 4 colunas de largura, para os filtros de projeto, departamento e gerente
        dbc.Col([
            html.Label('Projeto:'),  # Rótulo para o filtro de projeto
            dcc.Dropdown(id='project-filter', value='Todos')  # Menu suspenso para o filtro de projeto
        ], width=4),
        dbc.Col([
            html.Label('Departamento:'),  # Rótulo para o filtro de departamento
            dcc.Dropdown(id='department-filter', value='Todos')  # Menu suspenso para o filtro de departamento
        ], width=4),
        dbc.Col([
            html.Label('Gerente do Projeto:'),  # Rótulo para o filtro de gerente
            dcc.Dropdown(id='manager-filter', value='Todos')  # Menu suspenso para o filtro de gerente
        ], width=4)
    ]),

    # Quarta linha: Gráficos de pizza para status de prazo, trabalho e custo
    dbc.Row([
        # Três colunas, cada uma abrangendo 4 colunas de largura, para os gráficos de pizza
        dbc.Col(dcc.Graph(id='status-prazo-pie'), width=4),  # Gráfico de pizza para status de prazo
        dbc.Col(dcc.Graph(id='status-trabalho-pie'), width=4),  # Gráfico de pizza para status de trabalho
        dbc.Col(dcc.Graph(id='status-custo-pie'), width=4)  # Gráfico de pizza para status de custo
    ]),

    # Quinta linha: Gráficos de barras para status de prazo, trabalho e custo
    dbc.Row([
        # Três colunas, cada uma abrangendo 4 colunas de largura, para os gráficos de barras
        dbc.Col(dcc.Graph(id='status-de-prazo'), width=4),  # Gráfico de barras para status de prazo
        dbc.Col(dcc.Graph(id='status-de-trabalho'), width=4),  # Gráfico de barras para status de trabalho
        dbc.Col(dcc.Graph(id='status-de-custo'), width=4)  # Gráfico de barras para status de custo
    ]),

    # Sexta linha: Tabela de projetos
    dbc.Row([
        # Uma coluna abrangendo 12 colunas de largura para a tabela de projetos
        dbc.Col(dcc.Graph(id='project-table'), width=12)  # Tabela de projetos
    ])
], fluid=True)  # Define o contêiner como fluido para ocupar toda a largura da página

# Callback para atualizar os filtros e os gráficos com base no upload do arquivo
# Define um callback que é acionado quando o conteúdo do componente 'upload-data' é alterado
@app.callback(
    # Saídas do callback: opções para os filtros de projeto, departamento e gerente e os filhos do componente 'output-data-upload'
    [
        Output('project-filter', 'options'),  # Opções para o filtro de projeto
        Output('department-filter', 'options'),  # Opções para o filtro de departamento
        Output('manager-filter', 'options'),  # Opções para o filtro de gerente
        Output('output-data-upload', 'children')  # Filhos do componente 'output-data-upload'
    ],
    # Entradas do callback: conteúdo e nome do arquivo do componente 'upload-data'
    [Input('upload-data', 'contents')],  # Conteúdo do arquivo
    [State('upload-data', 'filename')]  # Nome do arquivo
)
def update_dropdowns(contents, filename):
    # Se o conteúdo for None, não faz nada
    if contents is None:
        raise dash.exceptions.PreventUpdate
    # Analisa o conteúdo do arquivo usando a função parse_contents
    df = parse_contents(contents, filename)
    # Se o DataFrame for None, retorna uma mensagem de erro
    if df is None:
        return [[], [], [], "Falha ao processar o arquivo."]
    # Cria as opções para os menus suspensos dos filtros
    project_options = [{'label': proj, 'value': proj} for proj in ['Todos'] + df['Nome do Projeto'].unique().tolist()]
    department_options = [{'label': dept, 'value': dept} for dept in ['Todos'] + df['Departamento'].unique().tolist()]
    manager_options = [{'label': mgr, 'value': mgr} for mgr in ['Todos'] + df['Gerente do Projeto'].unique().tolist()]
    # Retorna as opções dos filtros e uma mensagem de sucesso
    return project_options, department_options, manager_options, f"Arquivo {filename} carregado com sucesso."

# Callback para atualizar os gráficos com base nos filtros
# Define um callback que é acionado quando os valores dos filtros ou o conteúdo do componente 'upload-data' são alterados
@app.callback(
    # Saídas do callback: figuras para os gráficos de status de prazo, trabalho e custo, tabela de projetos e gráficos de pizza
    [
        Output('status-de-prazo', 'figure'),  # Figura para o gráfico de barras de status de prazo
        Output('status-de-trabalho', 'figure'),  # Figura para o gráfico de barras de status de trabalho
        Output('status-de-custo', 'figure'),  # Figura para o gráfico de barras de status de custo
        Output('project-table', 'figure'),  # Figura para a tabela de projetos
        Output('status-prazo-pie', 'figure'),  # Figura para o gráfico de pizza de status de prazo
        Output('status-trabalho-pie', 'figure'),  # Figura para o gráfico de pizza de status de trabalho
        Output('status-custo-pie', 'figure')  # Figura para o gráfico de pizza de status de custo
    ],
    # Entradas do callback: valores dos filtros de projeto, departamento e gerente e conteúdo do componente 'upload-data'
    [
        Input('project-filter', 'value'),  # Valor do filtro de projeto
        Input('department-filter', 'value'),  # Valor do filtro de departamento
        Input('manager-filter', 'value'),  # Valor do filtro de gerente
        Input('upload-data', 'contents')  # Conteúdo do arquivo
    ],
    # Estados do callback: nome do arquivo do componente 'upload-data'
    [State('upload-data', 'filename')]  # Nome do arquivo
)
def update_dashboard(project, department, manager, contents, filename):
    # Se o conteúdo for None, não faz nada
    if contents is None:
        raise dash.exceptions.PreventUpdate
    # Analisa o conteúdo do arquivo usando a função parse_contents
    df = parse_contents(contents, filename)
    # Se o DataFrame for None, não faz nada
    if df is None:
        raise dash.exceptions.PreventUpdate
    # Filtra os dados usando a função filter_data
    filtered_df = filter_data(df, project, department, manager)

    # Cria as figuras para os gráficos e a tabela
    # Status de Prazo
    status_prazo = filtered_df['Status de Prazo'].value_counts()
    status_de_prazo_fig = go.Figure(go.Bar(
        x=status_prazo.index,
        y=status_prazo.values,
        name='Status de Prazo'
    ))
    status_de_prazo_fig.update_layout(
        title="Status de Prazo",
        xaxis_title="Status",
        yaxis_title="Quantidade",
        legend_title="Legenda"
    )

    # Status de Trabalho
    status_trabalho = filtered_df['Status de Trabalho'].value_counts()
    status_de_trabalho_fig = go.Figure(go.Bar(
        x=status_trabalho.index,
        y=status_trabalho.values,
        name='Status de Trabalho'
    ))
    status_de_trabalho_fig.update_layout(
        title="Status de Trabalho",
        xaxis_title="Status",
        yaxis_title="Quantidade",
        legend_title="Legenda"
    )

    # Status de Custo
    status_custo = filtered_df['Status de Custo'].value_counts()
    status_de_custo_fig = go.Figure(go.Bar(
        x=status_custo.index,
        y=status_custo.values,
        name='Status de Custo'
    ))
    status_de_custo_fig.update_layout(
        title="Status de Custo",
        xaxis_title="Status",
        yaxis_title="Quantidade",
        legend_title="Legenda"
    )

    # Tabela de Projetos
    project_table_fig = go.Figure(data=[go.Table(
        header=dict(values=list(filtered_df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[filtered_df[col] for col in filtered_df.columns],
                   fill_color='lavender',
                   align='left'))
    ])
    project_table_fig.update_layout(
        title="Tabela de Projetos"
    )

    # Gráfico de pizza - Status de Prazo
    status_prazo_pie_fig = go.Figure(go.Pie(
        labels=status_prazo.index,
        values=status_prazo.values,
        name='Status de Prazo'
    ))
    status_prazo_pie_fig.update_layout(
        title="Distribuição do Status de Prazo"
    )

    # Gráfico de pizza - Status de Trabalho
    status_trabalho_pie_fig = go.Figure(go.Pie(
        labels=status_trabalho.index,
        values=status_trabalho.values,
        name='Status de Trabalho'
    ))
    status_trabalho_pie_fig.update_layout(
        title="Distribuição do Status de Trabalho"
    )

    # Gráfico de pizza - Status de Custo
    status_custo_pie_fig = go.Figure(go.Pie(
        labels=status_custo.index,
        values=status_custo.values,
        name='Status de Custo'
    ))
    status_custo_pie_fig.update_layout(
        title="Distribuição do Status de Custo"
    )
    # Retorna as figuras para os gráficos e a tabela
    return (
        status_de_prazo_fig, 
        status_de_trabalho_fig, 
        status_de_custo_fig, 
        project_table_fig,
        status_prazo_pie_fig,
        status_trabalho_pie_fig,
        status_custo_pie_fig
    )

# Executa o aplicativo se o script for executado diretamente
if __name__ == '__main__':
    app.run_server(debug=True)