import streamlit as st
from pytube import YouTube
import os
import re
from io import BytesIO
import datetime
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
from youtubesearchpython import VideosSearch

# Get the current date and time
now = datetime.datetime.now()
parsed_now = now.strftime("%d-%m-%Y %H:%M:%S")


@st.cache_resource()
def get_info(url):
    yt = YouTube(url)
    streams= yt.streams.filter(progressive= True, type= 'video')
    details= {}
    details["image"]= yt.thumbnail_url
    details["streams"]= streams
    details["title"]= yt.title
    details["length"]= yt.length
    itag, resolutions, vformat, frate = ([] for i in range(4))
    for i in streams:
        res= re.search(r'(\d+)p', str(i))
        typ= re.search(r'video/(\w+)', str(i))
        fps= re.search(r'(\d+)fps', str(i))
        tag= re.search(r'(\d+)',str(i))
        itag.append(str(i)[tag.start():tag.end()])
        resolutions.append(str(i)[res.start():res.end()])
        vformat.append(str(i)[typ.start():typ.end()])
        frate.append(str(i)[fps.start():fps.end()])
    details["resolutions"]= resolutions
    details["itag"]= itag
    details["fps"]= frate
    details["format"]= vformat
    return details
#st.sidebar.title(f"Welcome {name}")
st.title("YouTube Downloader ⬇️")
url = st.text_input("Colar Link aqui 👇", placeholder='https://www.youtube.com/')
buffer = BytesIO()
mime = ""



if url:
    media_format = st.selectbox('__Escolha o Formato__', ("","MP3","MP4"))

    v_info= get_info(url)
    col1, col2= st.columns([1,1.5], gap="small")
    with st.container():
        with col1:            
            st.image(v_info["image"])   
        with col2:
            st.subheader("Video Details ⚙️")
            res_inp = st.selectbox('__Escolha a Resolução__',v_info["resolutions"])
            id = v_info["resolutions"].index(res_inp)            
            st.write(f"__Title:__ {v_info['title']}")
            st.write(f"__Length:__ {v_info['length']} sec")
            st.write(f"__Resolution:__ {v_info['resolutions'][id]}")
            st.write(f"__Frame Rate:__ {v_info['fps'][id]}")
            st.write(f"__Format:__ {v_info['format'][id]}")
            file_name = st.text_input('__Save as 🎯__', placeholder = v_info['title'])

            ds = v_info["streams"].get_by_itag(v_info['itag'][id])
            if media_format == "MP3":
                
                mime = "audio/mp3"
                

                if file_name:        
                    if file_name != v_info['title']:
                        file_name+=".mp3"

                else:
                    file_name = v_info['title'] + ".mp3" 

                try:
                    yt = YouTube(url)
                    # extract only audio 
                    audio = yt.streams.filter(only_audio=True).first()
                    with st.spinner('Convertendo arquivo de áudio aguarde ...'):
                        audio.stream_to_buffer(buffer)
                    if st.download_button("Salvar ⚡️", buffer ,file_name,mime):
                        st.success('Download Completo', icon="✅") 
                        print("%s - Downloaded File: %s" %(parsed_now, file_name))  
                        st.balloons()

                except:
                    st.error('Error: Save with a different name!', icon="🚨")  
    
            elif media_format == "MP4":
                mime = "video/mp4"
                print(mime)
                if file_name:        
                    if file_name != v_info['title']:
                        file_name+=".mp4"
                else:
                    file_name = v_info['title'] + ".mp4"
                try:
                    with st.spinner('Convertendo arquivo de vídeo aguarde ...'):
                        ds.stream_to_buffer(buffer)
                    st.download_button("Salvar ⚡️", buffer ,file_name,mime) 
                    st.success('Download Completo', icon="✅")   
                    print("%s - Downloaded File: %s" %(parsed_now, file_name))         
                    st.balloons()
                        
                except:
                    st.error('Error: Save with a different name!', icon="🚨")  
            

itens = 20
@st.cache_resource()
def query_youtube(query):
    videosSearch = VideosSearch(query, limit = itens)
    video_list = {}
    query_result = videosSearch.result()["result"]

    for item in range(len(query_result)):
        video_list.update([(f"item_{item}", [query_result[item]["thumbnails"][0], query_result[item]["title"], "https://www.youtube.com/watch?v=%s" %(query_result[item]["id"])])])
    
    return video_list


#@st.experimental_dialog("Cast your vote")
with st.container(height=500):
    with st.expander("Youtube Player 🎵"):
        #st.sidebar.title(f"Welcome {name}")
        st.title("YouTube Player ")
        with st.container():
            url = st.text_input("Pesquise seus videos 👇", placeholder='')

        if url:
            with st.spinner('Buscando vídeos aguarde ...'):
                video_list = query_youtube(url)

            
            col1, col2= st.columns([1,1.5], gap="small")

            lists = []

            
            with st.container():
                for i in video_list.items():
                            
                            st.subheader(i[1][1])
                            st.video(i[1][2])
                            st.write(i[1][2])
