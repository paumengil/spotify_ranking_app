import streamlit as st

st.title("Mi ranking de Spotify")
st.write("Hola, esto es mi primera app de Streamlit")
st.write( "a ver que pasa")
import random
numero = st.slider("Elige un número", 0, 100, 50)
st.write("Has elegido:", numero)
st.write("Número aleatorio:", random.randint(1, 1000))
