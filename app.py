import streamlit as st
import pandas as pd
from serpapi import GoogleSearch
import requests


st.set_page_config(
   page_title="Análisis de competidores en SERP",
   layout="wide"
)

st.title("Análisis de competidores en SERP")

#related questions dentro de un resultado
def getRelatedQuestions(query):
    keyword=getQuery(search)
    resultados=[]
    resultado={}
    results = search.get_dict()
    organic= results['organic_results']
    for dictionary in organic:
        if "related_questions" in dictionary:
            l_rq=dictionary["related_questions"]
            for rq in l_rq:
                resultado={"keyword":keyword,"position":dictionary["position"],"url":dictionary['link'],'question':rq['question'],'snippet':rq['snippet']}
                resultados.append(resultado)
    df=pd.DataFrame(resultados)
    return df
    
def getRelatedSearches(search):
    keyword=getQuery(search)
    resultados=[]
    resultado={}
    results = search.get_dict()
    if 'related_searches' in results:
        related= results['related_searches']
        for dictionary in related:
            query=dictionary["query"]
            resultado={"keyword":keyword,"query":query}
            resultados.append(resultado)
    df=pd.DataFrame(resultados)
    return df


def getQuery(search):
    dict = search.get_dict()
    parameters=dict["search_parameters"]
    query=parameters['q']
    return query

def getPeopleAlsoAsk(search):
    keyword=getQuery(search)
    resultados=[]
    resultado={}
    results = search.get_dict()
    if 'related_questions' in results:
        paa= results['related_questions']
        for dictionary in paa:
            question=dictionary["question"]
            link=dictionary['link']
            snippet=''
            if "snippet" in dictionary:
                snippet=dictionary["snippet"]
            resultado={"keyword":keyword,"question":question,"url":link,"snippet":snippet}
            resultados.append(resultado)
    df=pd.DataFrame(resultados)
    return df


def getInlineImages(search):
    keyword=getQuery(search)
    resultados=[]
    resultado={}
    results = search.get_dict()
    link=''
    if 'inline_images' in results:
        imgs= results['inline_images']
        for dictionary in imgs:
            link=dictionary["source"]
            resultado={"keyword":keyword,"img_link_url":link}
            resultados.append(resultado)
    df=pd.DataFrame(resultados)
    return df



def getAnswerBox(search):
    keyword=getQuery(search)
    resultado={}
    results = search.get_dict()
    df=None
    if 'answer_box' in results:
        answer= results['answer_box']
        if answer['type']=='organic_result':
            title=answer['title']
            link=answer['link']
            snippet=''
            if "snippet" in answer:
                snippet=answer['snippet']
            resultado={"keyword":keyword,'link':link,'title':title,'snippet':snippet}        
            df=pd.DataFrame([resultado])
    return df

#para conocer los créditos restantes para hacer consultas en SerpAPI
def getTotalSearchesLeft(apikey):
    response = requests.get('https://serpapi.com/account?api_key='+apikey)
    json=response.json()
    restantes=0
    if json is not None:
        if 'total_searches_left' in json:
            restantes=json['total_searches_left']
    else:
        restantes=-1
    return restantes

api_key= st.text_input('API key de SERPAPI', '')
if api_key !='':
    st.text("Créditos restantes en SerpApi: "+str(getTotalSearchesLeft(api_key)))
google_domain=st.text_input('Dominio de Google a utilizar (https://serpapi.com/google-domains)', 'google.es')
gl= st.text_input('País de la búsqueda (https://serpapi.com/google-countries)', 'es')
hl= st.text_input('Idioma de la búsqueda (https://serpapi.com/google-languages)', 'es')
location=st.text_input('Geolocalización de la búsqueda', 'Spain')
device= st.radio(
     "Dispositivo de la búsqueda",
     ('desktop', 'mobile', 'tablet'))
num_resultados= st.slider('Número de resultados a analizar', value=50, min_value=10, max_value=100)

params = {
  "google_domain": google_domain,
  "hl": hl,
  "gl": gl,
  "location_requested": location,
  "location_used": location,
  "api_key": api_key,
  "device": device,
  "num": num_resultados
}


f_keywords=st.file_uploader('CSV con keywords a analizar', type='csv')


if f_keywords is not None:
    df_entrada=pd.read_csv(f_keywords,header=None)
    lista_kws=df_entrada[0].to_list()
    appended_data = []
    df_paa = pd.DataFrame(appended_data)
    df_img = pd.DataFrame(appended_data)
    df_faq = pd.DataFrame(appended_data)
    df_ab = pd.DataFrame(appended_data)
    df_rs = pd.DataFrame(appended_data)
    for kw in lista_kws:
        keyword=kw
        params['q'] =keyword
        search = GoogleSearch(params)
        if search is not None:
            df=getPeopleAlsoAsk(search)
            df_paa=pd.concat([df_paa, df]) 
            
        
            df=getInlineImages(search)
            df_img=pd.concat([df_img,df])

            df=getRelatedQuestions(search)
            df_faq=pd.concat([df_faq,df])

            df=getAnswerBox(search)
            df_ab=pd.concat([df_ab,df])

            df=getRelatedSearches(search)
            df_rs=pd.concat([df_rs,df])
        
    st.subheader("Otras preguntas de los usuarios")
    st.download_button(
        label="Descargar como CSV",
        data=df_paa.to_csv(index=False).encode('utf-8'),
        file_name='people_also_ask.csv',
        mime='text/csv'
        )

    st.subheader("FAQs en resultados")
    st.download_button(
        label="Descargar como CSV",
        data= df_faq.to_csv(index=False).encode('utf-8'),
        file_name='faqs.csv',
        mime='text/csv'
        )
    
    st.subheader("Answer box (posición 0)")
    st.download_button(
        label="Descargar como CSV",
        data= df_ab.to_csv(index=False).encode('utf-8'),
        file_name='answer_box.csv',
        mime='text/csv'
        )
    
    st.subheader("Consultas relacionadas")  
    st.download_button(
        label="Descargar como CSV",
        data= df_rs.to_csv(index=False).encode('utf-8'),
        file_name='related_searches.csv',
        mime='text/csv'
        )

    st.subheader("Imágenes")
    st.download_button(
        label="Descargar como CSV",
        data= df_img.to_csv(index=False).encode('utf-8'),
        file_name='images.csv',
        mime='text/csv'
        )
    st.subheader("Créditos restantes en SerpApi: "+str(getTotalSearchesLeft(api_key)))