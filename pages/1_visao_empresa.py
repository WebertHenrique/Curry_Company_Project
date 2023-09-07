#Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

#Bibliotecas necessárias
import pandas as pd
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config( page_title="Visão Empresa", layout="wide" )

#-------------------
#Funções
#-------------------
def clean_code( df1 ):
    """ Esta função tem a responsabilidade de limpar o data frame
        
        Tipos de limpeza:
        1. Removação dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Removação dos espaços das variáveis de texto
        4. Formação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica )
        
        Input: Dataframe
        Output: Dataframe
    """    
    
    #1. Convertendo a coluna AGE de texto para número
    linhas_selecionadas = (df1["Delivery_person_Age"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1["Delivery_person_Age"]=df1["Delivery_person_Age"].astype(int)

    #2. Convertendo a coluna Ratings de texto para número decimal (float)
    df1["Delivery_person_Ratings"] = df1["Delivery_person_Ratings"].astype(float)

    #3. Convertendo a coluna Order_Date de texto para data
    df1["Order_Date"] = pd.to_datetime( df1["Order_Date"], format= "%d-%m-%Y")

    #4. Convertendo multiple_deliveries de texto para número inteiro (int)
    linhas_selecionadas = (df1["multiple_deliveries"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1["multiple_deliveries"] = df1["multiple_deliveries"].astype(int)

    #5. Vamos limpar a coluna Road tirando a linha NaN
    linhas_selecionadas = (df1["Road_traffic_density"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #6. Vamos limpar a coluna City tirando a linha NaN
    linhas_selecionadas = (df1["City"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #7. Removendo os espacos dentro de strings/texto/object
    df1.loc[:, "ID"] = df1.loc[:, "ID"].str.strip()
    df1.loc[:, "Road_traffic_density"] = df1.loc[:, "Road_traffic_density"].str.strip()
    df1.loc[:, "Delivery_person_ID"] = df1.loc[:, "Delivery_person_ID"].str.strip()
    df1.loc[:, "Type_of_order"] = df1.loc[:, "Type_of_order"].str.strip()
    df1.loc[:, "Type_of_vehicle"] = df1.loc[:, "Type_of_vehicle"].str.strip()
    df1.loc[:, "Festival"] = df1.loc[:, "Festival"].str.strip()
    df1.loc[:, "City"] = df1.loc[:, "City"].str.strip()

    #8. Limpando a coluna Time_taken
    df1["Time_taken(min)"] = df1["Time_taken(min)"].apply( lambda x: x.split("(min)")[1])
    df1["Time_taken(min)"] = df1["Time_taken(min)"].astype(int)
    
    return df1


def order_metric( df1 ):
    """ Esta função tem a responsabilidade de plotar um gráfico
        
        Tipo de gráfico: De barras
        Informação do gráfico: Número de pedidos por dia.
        
        Input: Dataframe
        Output: Gráfico
    """    
    #Colunas
    cols = ["ID", "Order_Date"]

    #Seleção de linhas
    df_aux = df1.loc[:, cols].groupby(["Order_Date"]).count().reset_index()

    #Desenhar gráficos linhas
    fig = px.bar(df_aux, x="Order_Date", y="ID")
            
    return fig


def traffic_order_share( df1 ):
    """ Esta função tem a responsabilidade de plotar um gráfico
        
        Tipo de gráfico: De barras
        Informação do gráfico: Distribuição de pedidos por tipo de tráfego.
        
        Input: Dataframe
        Output: Gráfico
    """
    
    df_aux = df1[["ID", "Road_traffic_density"]].groupby(["Road_traffic_density"]).count().reset_index()

    #vou transformar a coluna ID em porcentagem criando uma nova coluna
    df_aux["entregas_perc"] = df_aux["ID"] / df_aux["ID"].sum()

    fig = px.pie(df_aux, values="entregas_perc", names="Road_traffic_density")
                
    return fig


def traffic_order_city( df1 ):
    """ Esta função tem a responsabilidade de plotar um gráfico
        
        Tipo de gráfico: De barras
        Informação do gráfico: Comparação do volume de pedidos por cidade e tipo de tráfego.
        
        Input: Dataframe
        Output: Gráfico
    """
    
    df_aux = (df1[["ID", "City", "Road_traffic_density"]]
                 .groupby(["City", "Road_traffic_density"])
                 .count()
                 .reset_index())

    fig = px.scatter (df_aux, x="City", y="Road_traffic_density", size="ID", color="City")
                
    return fig


def order_by_week( df1 ):
    """ Esta função tem a responsabilidade de plotar um gráfico
        
        Tipo de gráfico: De barras
        Informação do gráfico: Quantidade de pedidos por semana.
        
        Input: Dataframe
        Output: Gráfico
    """
    
    #Criar as colunas da semana
    df1["week_of_year"] = df1["Order_Date"].dt.strftime("%U")
    df_aux = df1.loc[: ,["ID", "week_of_year"]].groupby(["week_of_year"]).count().reset_index()
    fig = px.line(df_aux, x="week_of_year", y="ID")
    
    return fig


def order_share_by_week( df1 ):
    """ Esta função tem a responsabilidade de plotar um gráfico
        
        Tipo de gráfico: De barras
        Informação do gráfico: Quantidade de pedidos por entregador e por semana.
        
        Input: Dataframe
        Output: Gráfico
    """
    
    # Quantidade de pedidos por semana / Quantidade de entregadores unicos por semana
    df_aux1 = df1.loc[:, ["ID", "week_of_year"]].groupby(["week_of_year"]).count().reset_index()
    df_aux2 = df1.loc[:, ["Delivery_person_ID", "week_of_year"]].groupby(["week_of_year"]).nunique().reset_index()

    #aqui vamos juntar os dois date frames
    df_aux = pd.merge(df_aux1, df_aux2, how="inner")
            
    #agora vamos criar uma nova coluna, e essa coluna será usada pra fazer o gráfico
    df_aux["order_by_deliver"] = df_aux["ID"] / df_aux["Delivery_person_ID"]

    fig = px.line(df_aux, x="week_of_year", y="order_by_deliver")
            
    return fig


def country_maps ( df1 ):
    """ Esta função tem a responsabilidade de plotar um gráfico
        
        Tipo de gráfico: De barras
        Informação do gráfico: A localização central de cada cidade por tipo de tráfego.
        
        Input: Dataframe
        Output: Mapa Gráfico
    """
    
    #A biblioteca folium irá me ajudar a fazer um mapa com pinos, por isso importei ela.

    df_aux = (df1.loc[:, ["City", "Road_traffic_density", "Delivery_location_latitude", "Delivery_location_longitude"]]
                 .groupby(["City", "Road_traffic_density"])
                 .median()
                 .reset_index())
    #Se você observar o código, eu utilizei a MEDIANA e não a MÉDIA, porque? A média altera o valor, por exemplo, se tivermos 2 + 3 = 5, a média disso é 2,5
    #ou seja, ele alterou para um número que não existia, a Mediana não altera o valor, ela seleciona o número que esta literalmente no meio.
    #ex: uma lista com [1,2,3,4,5], a mediana irá selecionar o 3, pois é o numero do "meio", caso fosse a média, ela iria somar tudo e dividir por 5.
            
    map = folium.Map()
    #Agora vamos "desenhar" o mapa
    #As únicas diferenças pra um loop for normal é que, eu preciso por o .iterrows e o INDEX
    #E NÃO preciso utilizar o LOC e porque? Porque quem criou o folium quis assim.
            
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info["Delivery_location_latitude"],
                       location_info["Delivery_location_longitude"]],
                       popup = location_info[["City", "Road_traffic_density"]]).add_to(map)
        
    folium_static( map, width=800, height=600 )
            
#-------------------------------------- Início da estrutura lógica do código -------------------------------------------

#--------------------------
#Import dataset
#--------------------------
df=pd.read_csv("train.csv")

#--------------------------
#Limpando os dados
#--------------------------
df1 = clean_code( df )



# ============================================================================
# Barra Lateral no StreamLit
# ============================================================================
st.header( "Market Place - Visão Restaurantes" )

#image_path = "LogoFlecha.jpg"
image = Image.open( "LogoFlecha.jpg" )
st.sidebar.image( image, width=150 )

st.sidebar.markdown ( "# Cury Company" )
st.sidebar.markdown ( "## Fastest Delivery in Town" )
st.sidebar.markdown ( """---""" )

st.sidebar.markdown ( "## Selecione uma data limite" )

date_slider = st.sidebar.slider ( 
    "Até qual valor?",
    value=pd.datetime( 2022, 4, 13 ),
    min_value=pd.datetime( 2022, 2, 11),
    max_value=pd.datetime( 2022, 4, 6),
    format="DD-MM-YYYY" )

st.sidebar.markdown ( """---""" )

traffic_options = st.sidebar.multiselect(
    "Quais as condições de trânsito?",
    ["Low", "Medium", "High", "Jam"],
    default=["Low", "Medium", "High", "Jam"] )

st.sidebar.markdown ( """---""" )

weather_conditions = st.sidebar.multiselect(
    "Quais as condições climáticas?",
    ["conditions Cloudy", "conditions Fog", "conditions Sandstorms", "conditions Stormy", "conditions Sunny", "conditions Windy"],
    default=["conditions Cloudy", "conditions Fog", "conditions Sandstorms", "conditions Stormy", "conditions Sunny", "conditions Windy"] )

st.sidebar.markdown ( """---""" )

City = st.sidebar.multiselect(
    "Quais as regiões?",
    ["Metropolitian", "Urban", "Semi-Urban"],
    default=["Metropolitian", "Urban", "Semi-Urban"] )

st.sidebar.markdown ( """---""" )
st.sidebar.markdown ( "### Powered by Webert Bortolotti" )

#Filtro de data
linhas_selecionadas = df1[ "Order_Date" ] < date_slider
df1 = df1.loc[ linhas_selecionadas, : ]

#Filtro de trânsito
linhas_selecionadas = df1[ "Road_traffic_density"].isin ( traffic_options )
df1 = df1.loc[ linhas_selecionadas, : ]

#Filtro de condição climática.
linhas_selecionadas = df1[ "Weatherconditions"].isin ( weather_conditions )
df1 = df1.loc[ linhas_selecionadas, : ]

#Filtro de cidade.
linhas_selecionadas = df1[ "City"].isin ( City )
df1 = df1.loc[ linhas_selecionadas, : ]

# ============================================================================
# Layout no StreamLit
# ============================================================================

tab1, tab2, tab3 = st.tabs( ["Visão Gerencial", "Visão Tática", "Visão Geográfica"] )

with tab1:
    with st.container ():
        st.markdown( "# Orders by Day" )
        fig = order_metric( df1 )
        st.plotly_chart( fig, use_container_width=True )
        
        
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header( "Traffic Order Share" )
            fig = traffic_order_share( df1 )
            st.plotly_chart( fig, use_container_width=True )
            
                
        with col2:
            st.header( "Traffic Order City" )
            fig = traffic_order_city( df1 )
            st.plotly_chart( fig, use_container_width=True )

            


with tab2:
    with st.container ():
        st.markdown( "# Order by Week" )
        fig = order_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True )
        
        

    with st.container ():
        st.markdown( "# Order Share by Week" )
        fig = order_share_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True )
        
        

with tab3:
    with st.container ():
        #Observando o gráfico abaixo, podemos ver que na semana 06, tivemos praticamente quase 3 entregas por entregador
        #Já na semana 11, podemos observar que tivemos quase 10 entregas por entregador
        #Com isso, podemos observar que, OU tivemos um aumento de pedidos, OU tivemos uma diminuição de entregadores.
        #Claro que devemos observar demais fatores, porém, já é uma métrica que conseguimos utilizar pra corrigir um possível gap
        st.markdown( "# Country Maps" )
        country_maps ( df1 )
        
        
        
    


        





