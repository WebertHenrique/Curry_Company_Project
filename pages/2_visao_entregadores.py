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

st.set_page_config( page_title="Visão Entregadores", layout="wide" )

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

def top_delivers ( df1, top_asc ):
    """ Esta função tem a responsabilidade de plotar um data frame
        
        Data frame contém: Informações sobre os entregadores mais rápidos e lentos por cidade
        
        Input: Dataframe
        Output: Dataframe filtrado
    """    
    #Na coluna Time_taken(min), temos um problema, pois a informação está ''suja'' com a informação (min)
    #Aqui, vamos usar o .apply, é um comando que permite que a gente aplique outro comando linha a linha, ou seja:
    #então quando eu uso o df1["Time_taken(min)"].apply, eu to dizendo assim: eu quero aplicar um comando em todas as linhas dessa coluna.
    #mas qual a função? a função lambda ela é como uma função matemática:
    #x=10
    #f(x) = 1*10 + 2*10 + 2*10 = 50
    #f(x=10) = 50
    #Então nesse caso meu lambda é o meu f(x)
    #Quando eu uso o lambda x: x.split eu tenho acesso ao x e quando eu uso .apply, meu x do x.split é exatamente meu valor de linha.
    #e a cada linha eu estou dando um split("(min)")[1]).
    #df1["Time_taken(min)"] = df1["Time_taken(min)"].apply( lambda x: x.split("(min)")[1])
    #df1["Time_taken(min)"] = df1["Time_taken(min)"].astype(int)
    #fiz a limpeza la em cima na área de limpeza, então o código acima está la naquela área.

    df2 = ( df1.loc[:, ["Delivery_person_ID", "Time_taken(min)", "City"]]
               .groupby(["Delivery_person_ID", "City"])
               .min()
               .sort_values(["City", "Time_taken(min)"], ascending=top_asc)
               .reset_index())

    df_aux01 = df2.loc[df2["City"] == "Metropolitian", :].head(10)
    df_aux02 = df2.loc[df2["City"] == "Urban", :].head(10)
    df_aux03 = df2.loc[df2["City"] == "Semi-Urban", :].head(10)

    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    
    return df3
  
#-------------------------------------- Início da estrutura lógica do código -------------------------------------------
#Import dataset
df = pd.read_csv("train.csv")

#--------------------------
#Limpando os dados
#--------------------------
df1 = clean_code( df )




# ============================================================================
# Barra Lateral no StreamLit
# ============================================================================
st.header( "Market Place - Visão Entregadores" )

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

tab1, tab2, tab3 = st.tabs( ["Visão Gerencial", "--", "--"] )

with tab1:
    with st.container():
        st.title( "Overall Metrics" )
        
        col1, col2, col3, col4 = st.columns ( 4, gap="large" )
        with col1:
#maior idade dos entregadores            
            maior_idade = df1.loc[:, "Delivery_person_Age"].max()
            col1.metric( "Maior idade", maior_idade )               

            
        with col2:
#menor idade dos entregadores
            menor_idade = df1.loc[:, "Delivery_person_Age"].min()
            col2.metric( "Menor idade", menor_idade )
           
        with col3:
#melhor condicao de veiculos
            melhor_condicao = df1.loc[:, "Vehicle_condition"].max()
            col3.metric( "Melhor condição", melhor_condicao ) 
            
        with col4:
#pior condicao de veiculos
            pior_condicao = df1.loc[:, "Vehicle_condition"].min()
            col4.metric( "Pior condição", pior_condicao )
            
    with st.container():
        st.markdown( """---""" )
        st.title( "Avaliações" )
        
        col1, col2 = st.columns ( 2 )
        with col1:
            st.markdown( "##### Avaliação média por entregador" )
            av_media_entregador = round (df1[["Delivery_person_ID", "Delivery_person_Ratings"]]
                                            .groupby("Delivery_person_ID")
                                            .mean()
                                            .reset_index(), 2 )
            st.dataframe( av_media_entregador )

        with col2:
#Aqui, vamos aprender a usar a função .agg, onde vamos agregar a média e o desvio padrão em uma linha de código só.
#Dentro do .agg, a primeira informação é a coluna que vai sofrer a operação, no caso a coluna referente a avaliação
#A segunda informação é quais dados eu quero saber, no caso quero saber a média e o desvio padrão
#Observe que eu alterei o nome dos index pra ficar visualmente mais bonito
            st.markdown( "#### Avaliação média por trânsito" )
            av_mean_std_traffic = round (df1[["Delivery_person_Ratings", "Road_traffic_density"]]
                                            .groupby(["Road_traffic_density"])
                                            .agg({"Delivery_person_Ratings": ["mean", "std"]}), 2 )
            #Mudança nome das colunas
            av_mean_std_traffic.columns = ["delivery_mean", "delivery_std"]
            #reset index
            av_mean_std_traffic.reset_index()
            st.dataframe( av_mean_std_traffic )
            
            st.markdown( "#### Avaliação média por clima" )
            av_mean_std_weather = round (df1[["Delivery_person_Ratings", "Weatherconditions"]]
                                            .groupby(["Weatherconditions"])
                                            .agg({"Delivery_person_Ratings": ["mean", "std"]}), 2)
            #Mudança nome das colunas
            av_mean_std_weather.columns = ["delivery_mean", "delivery_std"]
            #reset index
            av_mean_std_weather.reset_index()
            st.dataframe( av_mean_std_weather )
            
    with st.container():
        st.markdown( """---""" )
        st.title ( "Velocidade de entrega" )
        
        col1, col2 = st.columns ( 2 )
        with col1:
            st.markdown( "#### Entregadores mais rápidos" )
            df3 = top_delivers( df1, top_asc=True )
            st.dataframe( df3 )
            

        with col2:
            st.markdown( "#### Entregadores mais lentos" )
            df3 = top_delivers( df1, top_asc=False )
            st.dataframe( df3 )
