import streamlit as st
import ranking
import altair as alt

@st.cache_data #Usamos este decorador que solo afecta a la función que tiene debajo para que a pesar de movamos el slider no haya que cargar los mismos datos luego
def preparar_todo(contenidos): 
    df = ranking.cargar_datos(contenidos)
    songs = ranking.preparar_canciones(df)
    sstats = ranking.calcular_sstats(songs)
    
    return songs, sstats

st.set_page_config(page_title="Mi ranking de Spotify", page_icon="🎧", layout="wide")
st.title("Mi ranking de Spotify")
subidos = st.file_uploader("sube tus JSON de Spotify", type="json", accept_multiple_files=True)
if not subidos:
    st.info("Sube tus archivos para empezar")
    st.stop()

contenidos = [archivo.getvalue() for archivo in subidos]

# Creamos un traductos para las columnas de las tablas tengan un nombre concreto y no el de la variable
traductor = {
    "cancion": "Canción",
    "artista": "Artista",
    "fecha_inicio": st.column_config.DateColumn("Primera escucha", format="DD-MM-YYYY"),
    "fecha_max":st.column_config.DateColumn("Última escucha", format="DD-MM-YYYY"),
    "rep": "Nº Escuchas",
    "rep_ventana": "Nº Escuchas",
    "densidad": "Media de escuchas por día",
    "delta_dias": None

    
}


songs, sstats = preparar_todo(contenidos)

col1, col2, col3, col4 =st.columns(4)
col1.metric("Minutos totales",round(ranking.calcular_minutos_escuchas(songs)),border=True) 
col2.metric("canciones", len(sstats["cancion"]), border=True)
col3.metric("Inicio",str(sstats["fecha_inicio"].min().date()), border=True) #convertimos la fecha a string porque no lee fechas
col4.metric("Fin",str(sstats["fecha_max"].max().date()),border=True) #convertimos la fecha a string porque no lee fechas
with st.expander("Ver todos mis datos"):
    st.dataframe(sstats, hide_index=True, column_config=traductor)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Spotify", "Trackdone", "Clickrow","Loop", "Densidad", "Intervalo", "Mi historia con una canción"])


with tab1:
    st.subheader("Ranking de Spotify")
    top10 = ranking.calcular_ranking_reproducidas(songs).head(10)
    grafico = (
            alt.Chart(top10)
            .mark_bar(cornerRadiusEnd=4) # con mark_bar estamos creando un gráfico de barras
            .encode(
                x = alt.X("rep:Q", title="Escuchas"), # la columna rep va en el eje horizontal. Q significa cuantitativa
                y=alt.Y("cancion:N", sort="-x", title=None), # La columna canción va en el eje vertical, la N significa nominal
                tooltip=["cancion","artista", "rep"],# Las cosas que salen cuando pongo el cursor encima
            )
        )
    st.altair_chart(grafico)
    st.dataframe(ranking.calcular_ranking_reproducidas(songs), hide_index=True, column_config=traductor)
   
with tab2:
    st.subheader("Ranking Reproducciones de canciones hasta el final")
    with st.expander("Explicación"):
        st.text("En este ranking las reproducciones que aparecen son solo en las que hemos escuchado la canción entera.")
    
    top10 = ranking.calcular_ranking_trackdone(songs).head(10)
    grafico = (
                alt.Chart(top10)
                .mark_bar(cornerRadiusEnd=4) # con mark_bar estamos creando un gráfico de barras
                .encode(
                    x = alt.X("rep:Q", title="Escuchas"), # la columna rep va en el eje horizontal. Q significa cuantitativa
                    y=alt.Y("cancion:N", sort="-x", title=None), # La columna canción va en el eje vertical, la N significa nominal
                    tooltip=["cancion","artista", "rep"],# Las cosas que salen cuando pongo el cursor encima
                )
            )
    st.altair_chart(grafico)
    st.dataframe(ranking.ranking_trackdone(songs), hide_index=True, column_config=traductor)

with tab3:
    st.subheader("Ranking de repeticiones de las canciones clicadas conscientemente")
    with st.expander("Explicación"):
        st.markdown("Este es un ranking de reproducciones, al igual que los otros pero lo que muestra son las canciones que hemos clicado nosotros para escuchar. Si no tienes Spotify premium, creo que este ranking no tiene mucho sentido, lo siento")
    top10 = ranking.calcular_ranking_clickrow(songs).head(10)
    grafico = (
                alt.Chart(top10)
                .mark_bar(cornerRadiusEnd=4) # con mark_bar estamos creando un gráfico de barras
                .encode(
                    x = alt.X("rep:Q", title="Escuchas"), # la columna rep va en el eje horizontal. Q significa cuantitativa
                    y=alt.Y("cancion:N", sort="-x", title=None), # La columna canción va en el eje vertical, la N significa nominal
                    tooltip=["cancion","artista", "rep"],# Las cosas que salen cuando pongo el cursor encima
                )
            )
    st.altair_chart(grafico)
    st.dataframe(ranking.calcular_ranking_clickrow(songs), hide_index=True, column_config=traductor)

with tab4:
    st.subheader("Ranking canciones en Loop")
    with st.expander("Explicación"):    
        st.text("Este ranking, nuevamente cuenta las reproducciones, pero esta vez solo cuentas las que han estado en bucle. ¿A ver qué canción es la que más has tenido en bucle?")
    top10 = ranking.calcular_ranking_loop(songs).head(10)
    grafico = (
                alt.Chart(top10)
                .mark_bar(cornerRadiusEnd=4) # con mark_bar estamos creando un gráfico de barras
                .encode(
                        x = alt.X("rep:Q", title="Escuchas"), # la columna rep va en el eje horizontal. Q significa cuantitativa
                        y=alt.Y("cancion:N", sort="-x", title=None), # La columna canción va en el eje vertical, la N significa nominal
                        tooltip=["cancion","artista", "rep"],# Las cosas que salen cuando pongo el cursor encima
                    )
                )
    st.altair_chart(grafico)
    st.dataframe(ranking.calcular_ranking_loop(songs), hide_index=True, column_config=traductor)

with tab5:
    st.subheader("Ranking densidad")
    with st.expander("Explicación"):
        st.text("Este ranking es el motivo de que se hiciera este proyecto. Cuando salió el ranking de Spotify me pareció muy injusto porque claramente una canción que conozco de hace más años, es más probable que tenga más reproducciones. Por eso creamos el rankind de densidad, este ranking mide cuando fue la primera vez que escuchaste una cación y la última vez, y apartir de ahí cuantas veces la hemos escuchado para todo el tiempo que llevamos conociendola. Sin embargo este ranking hace que las canciones que las conoces de un día o solo las has escuchado muchas veces en un periodo corto de tu vida suban mucho en el ranking, por eso, para que se ajuste mejor hemos hecho que el número de reproducciones mínimas que tenga que tener una cación para que se la incluya en el ranking sea un valor variable. Prueba a moverlo para ver como cambia tu ranking")
    max_rep = sstats["rep"].max()
    min_rep = st.slider("Ajusta el mínimo de reproducciones que tiene que tener una canción para aparecer en el ranking",1, max_rep,50)
    top10 = ranking.calcular_ranking_densidad(sstats, min_rep).head(10)
    grafico = (
                alt.Chart(top10)
                .mark_bar(cornerRadiusEnd=4) # con mark_bar estamos creando un gráfico de barras
                .encode(
                    x = alt.X("densidad:Q", title="Escuchas al día desde que la escuchamos por primera vez"), # la columna rep va en el eje horizontal. Q significa cuantitativa
                    y=alt.Y("cancion:N", sort="-x", title=None), # La columna canción va en el eje vertical, la N significa nominal
                    tooltip=["cancion","artista", "densidad"],# Las cosas que salen cuando pongo el cursor encima
                )
            )
    st.altair_chart(grafico)
    st.dataframe(ranking.calcular_ranking_densidad(sstats, min_rep), hide_index=True, column_config=traductor)

with tab6:
    st.subheader("Ranking ventana")
    with st.expander("Explicación"):
        st.text("El anterior ranking mete una desigualdad y es que las canciones que hemos conocido hace poco tiempo, tienen ventaja frente a las que conocemos desde hace menos, por ello creamos este ranking donde vamos a calcular para todas las canciones, desde el momento que las conocimos hasta un tiempo limitado, cuanto las hemos escuchado")
    intervalo_mes = st.slider("Ajustas el número de meses que quieres que cuente las reproducciones", 1, int((sstats["fecha_max"].max()-sstats["fecha_inicio"].min()).days/30), 12)
    top10 = ranking.calcular_ranking_intervalo(sstats,songs,intervalo_mes).head(10)
    grafico = (
                alt.Chart(top10)
                .mark_bar(cornerRadiusEnd=4) # con mark_bar estamos creando un gráfico de barras
                .encode(
                    x = alt.X("rep_ventana:Q", title="Reproducciones en ese intervalo"), # la columna rep va en el eje horizontal. Q significa cuantitativa
                    y=alt.Y("cancion:N", sort="-x", title=None), # La columna canción va en el eje vertical, la N significa nominal
                    tooltip=["cancion","artista", "rep_ventana"],# Las cosas que salen cuando pongo el cursor encima
                )
            )
    st.altair_chart(grafico)
    st.dataframe(ranking.calcular_ranking_intervalo(sstats,songs,intervalo_mes), hide_index=True, column_config=traductor)

with tab7:
    
    opciones = sstats[sstats["rep"]>=20]
    opciones = opciones.sort_values(by="rep", ascending= False)
    opciones["etiqueta"] = opciones["cancion"] + " - " +opciones["artista"] 
    elegida = st.selectbox("Elige una canción", opciones["etiqueta"])

    fila =opciones[opciones["etiqueta"]==elegida].iloc[0]
    cancion = fila["cancion"]
    artista = fila["artista"]

    escuchas_elegida = ranking.calcular_escuchas_por_mes(songs, cancion, artista)
    grafico = (
        alt.Chart(escuchas_elegida)
        .mark_line()
        .encode(
            x = alt.X("mes:T"), # T para que altair sepa que es algo temporal y ordene bien
            y = alt.Y("escuchas:Q")
        )
        .mark_line(point=True)
    )

    st.altair_chart(grafico)
