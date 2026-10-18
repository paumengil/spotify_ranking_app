import streamlit as st
import ranking

@st.cache_data #Usamos este decorador que solo afecta a la función que tiene debajo para que a pesar de movamos el slider no haya que cargar los mismos datos luego
def preparar_todo(contenidos): 
    df = ranking.cargar_datos(contenidos)
    songs = ranking.preparar_canciones(df)
    sstats = ranking.calcular_sstats(songs)
    
    return songs, sstats

st.title("Mi ranking de Spotify")
subidos = st.file_uploader("sube tus JSON de Spotify", type="json", accept_multiple_files=True)
if not subidos:
    st.info("Sube tus archivos para empezar")
    st.stop()

contenidos = [archivo.getvalue() for archivo in subidos]


songs, sstats = preparar_todo(contenidos)

col1, col2, col3, col4 =st.columns(4)
col1.metric("Reproducciones",len(songs["ts"]),border=True) # Esto sería más interesante si son minutos de escuchas
col2.metric("canciones", len(sstats["cancion"]))
col3.metric("Inicio",str(sstats["fecha_inicio"].min().date())) #convertimos la fecha a string porque no lee fechas
col4.metric("Fin",str(sstats["fecha_max"].max().date())) #convertimos la fecha a string porque no lee fechas
st.dataframe(sstats)
st.subheader("Ranking de Spotify")
st.dataframe(ranking.ranking_reproducidas(songs))
st.subheader("Ranking Reproducciones de canciones hasta el final")
st.text("En este ranking las reproducciones que aparecen son solo en las que hemos escuchado la canción entera.")
st.dataframe(ranking.ranking_trackdone(songs))
st.subheader("Ranking de repeticiones de las canciones clicadas conscientemente")
st.text("Este es un ranking de reproducciones, al igual que los otros pero lo que muestra son las canciones que hemos clicado nosotros para escuchar. Si no tienes Spotify premium, creo que este ranking no tiene mucho sentido, lo siento")
st.dataframe(ranking.ranking_clickrow(songs))
st.subheader("Ranking canciones en Loop")
st.text("Este ranking, nuevamente cuenta las reproducciones, pero esta vez solo cuentas las que han estado en bucle. ¿A ver qué canción es la que más has tenido en bucle?")
st.dataframe(ranking.ranking_loop(songs))
st.subheader("Ranking densidad")
st.text("Este ranking es el motivo de que se hiciera este proyecto. Cuando salió el ranking de Spotify me pareció muy injusto porque claramente una canción que conozco de hace más años, es más probable que tenga más reproducciones. Por eso creamos el rankind de densidad, este ranking mide cuando fue la primera vez que escuchaste una cación y la última vez, y apartir de ahí cuantas veces la hemos escuchado para todo el tiempo que llevamos conociendola. Sin embargo este ranking hace que las canciones que las conoces de un día o solo las has escuchado muchas veces en un periodo corto de tu vida suban mucho en el ranking, por eso, para que se ajuste mejor hemos hecho que el número de reproducciones mínimas que tenga que tener una cación para que se la incluya en el ranking sea un valor variable. Prueba a moverlo para ver como cambia tu ranking")
max_rep = sstats["rep"].max()
min_rep = st.slider("Ajusta el mínimo de reproducciones que tiene que tener una canción para aparecer en el ranking",1, max_rep,50)
st.dataframe(ranking.ranking_densidad(sstats, min_rep))
