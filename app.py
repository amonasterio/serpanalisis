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
                try:
                    resultado={"keyword":keyword,"position":dictionary["position"],"url":dictionary['link'],'question':rq['question'],'snippet':rq['snippet']}
                except Exception as e:
                    st.error("Error related_questions consulta '"+keyword+"': "+e.args[0])
                else:
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
            try:
                query=dictionary["query"]
                resultado={"keyword":keyword,"query":query}
            except Exception as e:
                st.error("Error related_searches consulta '"+keyword+"': "+e.args[0])
            else:
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
            try:
                question=dictionary["question"]
                link=dictionary['link']
                snippet=''
                if "snippet" in dictionary:
                    snippet=dictionary["snippet"]
                resultado={"keyword":keyword,"question":question,"url":link,"snippet":snippet}
            except Exception as e:
                st.error("Error people_also_ask consulta '"+keyword+"': "+e.args[0])
            else:
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
            if 'source' in dictionary:
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
            try:
                title=answer['title']
                if 'link' in answer:
                    link=answer['link']
                snippet=''
                if "snippet" in answer:
                    snippet=answer['snippet']
                elif 'answer' in answer:
                    snippet=answer['answer']
                resultado={"keyword":keyword,'url':link,'title':title,'snippet':snippet}        
                df=pd.DataFrame([resultado])
            except Exception as e:
                st.error("Error answer_box consulta '"+keyword+"': "+e.args[0])
    return df

#Devuelve los resultados orgánicos
def getOrganicResults(search):
    keyword=getQuery(search)
    resultados=[]
    resultado={}
    results = search.get_dict()
    df=None
    if 'organic_results' in results:
        res= results['organic_results']
        for dictionary in res:
            extensiones=[]
            postion=dictionary["position"]
            link=dictionary["link"]
            title=dictionary["title"]
            if 'snippet' in dictionary:
                snippet=dictionary["snippet"]
            if 'rich_snippet' in dictionary:
                rich=dictionary["rich_snippet"]
                if 'top' in rich:
                    top=rich['top']
                    extensiones=top['extensions']
                elif 'bottom' in rich:
                    bottom=rich['bottom']
                    extensiones=bottom['extensions']
            resultado={"Query":keyword,"Position":postion,"Link":link,"Title":title,"Snippet":snippet}
            i=1
            for item in extensiones:
                resultado["Extension_"+str(i)]=item
                i+=1
            resultados.append(resultado)
    df=pd.DataFrame(resultados)
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

#Elimina los duplicados de una lista
def eliminaDuplicadosLista(lista):
    if len(lista)>0:
        lista=list(dict.fromkeys(lista))
    return lista

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

lista_consultas=st.text_area("Introduzca las consultas que desea analizar o cárguelas en un CSV",'')
csv=st.file_uploader('CSV con keywords a analizar', type='csv')
consultas=[]

#Si no hay CSV miramos el textArea
if csv is  None:
    if len(lista_consultas)>0:
        consultas=lista_consultas.split('\n')
else: 
    df_entrada=pd.read_csv(csv,header=None)
    st.write(df_entrada)
    consultas = df_entrada[0].tolist()
if len(consultas)>0:
    #Eliminamos posibles duplicados
    lista=eliminaDuplicadosLista(consultas)
    total_count=0
    bar = st.progress(0.0)
    longitud=len(lista)
    appended_data = []
    df_paa = pd.DataFrame(appended_data)
    df_img = pd.DataFrame(appended_data)
    df_faq = pd.DataFrame(appended_data)
    df_ab = pd.DataFrame(appended_data)
    df_rs = pd.DataFrame(appended_data)
    for kw in lista:
        total_count+=1
        percent_complete=total_count/longitud 
        keyword=kw
        params['q'] =keyword
        search = GoogleSearch(params)
        if search is not None:
            df=getPeopleAlsoAsk(search)
            df_paa=pd.concat([df_paa, df]) 
              
            df=getOrganicResults(search)
            df_img=pd.concat([df_img,df])

            df=getRelatedQuestions(search)
            df_faq=pd.concat([df_faq,df])

            df=getAnswerBox(search)
            df_ab=pd.concat([df_ab,df])

            df=getRelatedSearches(search)
            df_rs=pd.concat([df_rs,df])
        bar.progress(percent_complete)
    st.subheader("Otras preguntas de los usuarios")
    st.dataframe(df_paa)
    st.download_button(
        label="Descargar como CSV",
        data=df_paa.to_csv(index=False).encode('utf-8'),
        file_name='people_also_ask.csv',
        mime='text/csv'
        )

    st.subheader("FAQs en resultados")
    st.dataframe(df_faq)
    st.download_button(
        label="Descargar como CSV",
        data= df_faq.to_csv(index=False).encode('utf-8'),
        file_name='faqs.csv',
        mime='text/csv'
        )
    
    st.subheader("Answer box (posición 0)")
    st.dataframe(df_ab)
    st.download_button(
        label="Descargar como CSV",
        data= df_ab.to_csv(index=False).encode('utf-8'),
        file_name='answer_box.csv',
        mime='text/csv'
        )
    
    st.subheader("Búsquedas relacionadas")  
    st.dataframe(df_rs)
    st.download_button(
        label="Descargar como CSV",
        data= df_rs.to_csv(index=False).encode('utf-8'),
        file_name='related_searches.csv',
        mime='text/csv'
        )

    st.subheader("Resultados orgánicos")
    st.dataframe(df_img)
    st.download_button(
        label="Descargar como CSV",
        data= df_img.to_csv(index=False).encode('utf-8'),
        file_name='organicos.csv',
        mime='text/csv'
        )
    st.subheader("Créditos restantes en SerpApi: "+str(getTotalSearchesLeft(api_key)))
else:
    st.warning("No ha introducido ninguna consulta") 