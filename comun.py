import streamlit as st
import ranking
import altair as alt

# Extraemos de los json las tablas songs y sstats con la información que vamos a necesitar
@st.cache_data(ttl=7200, max_entries=5) #Usamos este decorador que solo afecta a la función que tiene debajo para que a pesar de movamos el slider no haya que cargar los mismos datos luego
def preparar_todo(contenidos): 
    df = ranking.cargar_datos(contenidos)
    songs = ranking.preparar_canciones(df)
    sstats = ranking.calcular_sstats(songs)
    
    return songs, sstats

# Creamos un traductos para las columnas de las tablas tengan un nombre concreto y no el de la variable
traductor = {
    "cancion": "Canción",
    "artista": "Artista",
    "fecha_inicio": st.column_config.DateColumn("Primera escucha", format="DD-MM-YYYY"),
    "fecha_max":st.column_config.DateColumn("Última escucha", format="DD-MM-YYYY"),
    "rep": "Nº Escuchas",
    "rep_clickrow": "Nº Escuchas",
    "rep_trackdone":"Nº Escuchas",
    "rep_loop":"Nº Escuchas",
    "rep_ventana": "Nº Escuchas en ventana",
    "densidad": "Media de escuchas por día",
    "delta_dias": None,
    "pct_trackdone": st.column_config.NumberColumn(" % de repeticiones acabadas", format="percent"),
    "pct_clickrow": st.column_config.NumberColumn(" % de repeticiones seleccionadas", format="percent"),
    "pct_loop": st.column_config.NumberColumn(" % de repeticiones en bucle", format="percent"),
    "nota": st.column_config.NumberColumn("Nota", format="%.2f")
}
