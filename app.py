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
st.markdown("""Esta aplicación sirve para analizar tus gustos musicales según la información recopilada por Spotify.
Spotify guarda todos tus datos y puedes pedírselos en dos sencillos pasos: 

1. En el icono de tu perfil, pulsa **cuenta**. Esto te redirigirá a una página con todos los datos de tu cuenta de Spotify 
2. En el apartado de **Seguridad y Privacidad** selecciona **Privacidad de la cuenta* 
3. Desliza hasta el final y marca **Historial de reproducción ampliado** y pulsa **solicitar datos**

En unos días te llegarán al correo una carpeta comprimida con unos archivos en formato .json con todo tu historial, para poder ver tu análisis, simplemente cárgalos aquí""")

with st.expander("Sube tus JSONs de Spotify"):
    subidos = st.file_uploader(label="Sube tus JSONs de Spotify", type="json", accept_multiple_files=True, label_visibility="hidden")
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


songs, sstats = preparar_todo(contenidos)

col1, col2, col3, col4 =st.columns(4)
col1.metric("Minutos totales",round(ranking.calcular_minutos_escuchas(songs)),border=True) 
col2.metric("canciones", len(sstats["cancion"]), border=True)
col3.metric("Inicio",str(sstats["fecha_inicio"].min().date()), border=True) #convertimos la fecha a string porque no lee fechas
col4.metric("Fin",str(sstats["fecha_max"].max().date()),border=True) #convertimos la fecha a string porque no lee fechas
with st.expander("Ver todos mis datos"):
    st.dataframe(sstats, hide_index=True, column_config=traductor)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["Spotify", "Trackdone", "Clickrow","Loop", "Densidad", "Intervalo", "Ranking definitivo", "Mi historia con una canción" ])


with tab1:
    st.subheader("Ranking de Spotify")
    with st.expander("Explicación"):
        st.markdown("Este ranking pretende simular el creado por Spotify por su veinte aniversario para la playlist *Tu top de canciones más escuchadas*. Tras muchas pruebas se detectectó que este se había creado contando las repeticiones de las canciones con más de 30 segundos de reproducción.¡Comprueba tu mismo que se corresponde con este ranking revisando tu playlist de Spotify! Hay que tener en cuenta que el ranking se hizo con los datos recopilados hasta mayo de 2026 y el tuyo depende de cuando pediste el histórico")
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
        st.text("Este es un ranking de reproducciones, al igual que el de Spotify, sin embargo, aquí solo cuenta como reproducción si has escuchado la canción entera.")
    
    top10 = ranking.calcular_ranking_trackdone(songs).head(10)
    grafico = (
                alt.Chart(top10)
                .mark_bar(cornerRadiusEnd=4) # con mark_bar estamos creando un gráfico de barras
                .encode(
                    x = alt.X("rep_trackdone:Q", title="Escuchas"), # la columna rep va en el eje horizontal. Q significa cuantitativa
                    y=alt.Y("cancion:N", sort="-x", title=None), # La columna canción va en el eje vertical, la N significa nominal
                    tooltip=["cancion","artista", "rep_trackdone"],# Las cosas que salen cuando pongo el cursor encima
                )
            )
    st.altair_chart(grafico)
    st.dataframe(ranking.calcular_ranking_trackdone(songs), hide_index=True, column_config=traductor)

with tab3:
    st.subheader("Ranking de repeticiones de las canciones clicadas conscientemente")
    with st.expander("Explicación"):
        st.markdown("Este es un ranking de reproducciones, al igual que los otros pero aquí solo cuentan las reproducciones de las canciones que hemos seleccionado nosotros mismos. Es decir, solo cuenta si la hemos buscado y clicado. Si no tienes Spotify premium, creo que este ranking no tiene mucho sentido, lo siento")
    top10 = ranking.calcular_ranking_clickrow(songs).head(10)
    grafico = (
                alt.Chart(top10)
                .mark_bar(cornerRadiusEnd=4) # con mark_bar estamos creando un gráfico de barras
                .encode(
                    x = alt.X("rep_clickrow:Q", title="Escuchas"), # la columna rep va en el eje horizontal. Q significa cuantitativa
                    y=alt.Y("cancion:N", sort="-x", title=None), # La columna canción va en el eje vertical, la N significa nominal
                    tooltip=["cancion","artista", "rep_clickrow"],# Las cosas que salen cuando pongo el cursor encima
                )
            )
    st.altair_chart(grafico)
    st.dataframe(ranking.calcular_ranking_clickrow(songs), hide_index=True, column_config=traductor)

with tab4:
    st.subheader("Ranking canciones en Loop")
    with st.expander("Explicación"):    
        st.text("Este ranking, nuevamente cuenta las reproducciones, pero esta vez solo cuentan las que han estado en bucle. ¿A ver qué canción es la que más has tenido en bucle?")
    top10 = ranking.calcular_ranking_loop(songs).head(10)
    grafico = (
                alt.Chart(top10)
                .mark_bar(cornerRadiusEnd=4) # con mark_bar estamos creando un gráfico de barras
                .encode(
                        x = alt.X("rep_loop:Q", title="Escuchas"), # la columna rep va en el eje horizontal. Q significa cuantitativa
                        y=alt.Y("cancion:N", sort="-x", title=None), # La columna canción va en el eje vertical, la N significa nominal
                        tooltip=["cancion","artista", "rep_loop"],# Las cosas que salen cuando pongo el cursor encima
                    )
                )
    st.altair_chart(grafico)
    st.dataframe(ranking.calcular_ranking_loop(songs), hide_index=True, column_config=traductor)

with tab5:
    st.subheader("Ranking densidad")
    with st.expander("Explicación"):
        st.text("Este ranking es el motivo de que se hiciera este proyecto. El ranking de Spotify beneficia a las canciones que conocemos desde hace más años proque tienen más probabilidad de haber sido escuchadas más veces. Sin embargo, este ranking mide cuantos las reproducciones totales de una canción y lo divide por el tiempo hemos estado escuchando esa canción; es decir, desde que la conocemos hasta que la hemos escuchado por última vez. Sin embargo, este ranking hace que las canciones que solo has escuchado unos pocos días, tengan mucha puntuación, sin implicar eso que sea tu canción favorita. Por eso, para que sea más justo hemos hecho que el número de reproducciones mínimas que tenga que tener una canción para que se la incluya en el ranking sea un valor variable. Prueba a moverlo para ver cómo cambia tu ranking")
    max_rep = sstats["rep"].max()
    min_rep_densidad = st.slider("Ajusta el mínimo de reproducciones que tiene que tener una canción para aparecer en el ranking",1, max_rep,50, key="min_rep_densidad")
    top10 = ranking.calcular_ranking_densidad(sstats, min_rep_densidad).head(10)
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
    st.dataframe(ranking.calcular_ranking_densidad(sstats, min_rep_densidad), hide_index=True, column_config=traductor)

with tab6:
    st.subheader("Ranking ventana")
    with st.expander("Explicación"):
        st.text("El anterior ranking mete una desigualdad y es que las canciones que hemos conocido hace poco tiempo, tienen ventaja frente a las que conocemos desde hace más, por ello creamos este ranking donde vamos a calcular para todas las canciones, desde el momento que las conocimos hasta un tiempo limitado (ventana), cuanto las hemos escuchado")
    intervalo_mes_ventana = st.slider("Ajustas el número de meses que quieres que cuente las reproducciones", 1, int((sstats["fecha_max"].max()-sstats["fecha_inicio"].min()).days/30), 12, key="intervalo_mes_ventana")
    top10 = ranking.calcular_ranking_intervalo(sstats,songs,intervalo_mes_ventana).head(10)
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
    st.dataframe(ranking.calcular_ranking_intervalo(sstats,songs,intervalo_mes_ventana), hide_index=True, column_config=traductor)

with tab7:
    st.subheader("Ranking Definitivo")
    with st.expander("Explicación"):
        st.text("Este ranking fusiona todos los anteriores: Calcula los porcentajes de las reproducciones totales que han sido clicadas, en bucle o reproducidas hasta el final y las reproducciones que se han tenido en cada canción para una ventana temporal. De cada canción se tiene en cuenta el percentil de su ranking, pero como sabemos que cada persona es un mundo, este ranking te permite decidir a cuál de los rankings anteriores le das más peso, además de editar los dos parámetros que hemos visto en el resto de rankings:" \
        "La ventana temporal que estamos observando de una canción para el ranking de intensidad y el número de reproducciones mínimas que tienen que tener las canciones para aparecer en el ranking ")
    min_rep_definitivo = st.slider(" Ajusta el mínimo de reproducciones para salir en el top",1, max_rep,50, key="min_rep_definitivo")
    intervalo_mes_definitivo = st.slider("Ajustas el número de meses que quieres que cuente las reproducciones", 1, int((sstats["fecha_max"].max()-sstats["fecha_inicio"].min()).days/30), 12, key="intervalo_mes_definitivo")
    st.markdown("**Cuánto pesa cada indicador**")
    c1, c2, c3, c4 = st.columns(4)
    pesos_rankings = {
        "rep_ventana":   c1.slider("ventana (meses)", 1, 10, 1),
        "pct_trackdone": c2.slider("Escuchas enteras", 1, 10, 1),
        "pct_clickrow":  c3.slider("Elegida por mí", 1, 10, 1),
        "pct_loop":      c4.slider("En bucle", 1, 10, 1),
    }

    rk_trackdone = ranking.calcular_ranking_trackdone(songs)
    rk_clickrow = ranking.calcular_ranking_clickrow(songs)
    rk_loop = ranking.calcular_ranking_loop(songs)

    final = ranking.calcular_ranking_percentile(sstats, songs, min_rep_definitivo, intervalo_mes_definitivo,
                                                rk_trackdone, rk_clickrow, rk_loop, pesos_rankings)
    st.dataframe(final[["Puesto","cancion","artista","rep","rep_ventana", "pct_trackdone", "pct_clickrow", "pct_loop", "nota" ]], hide_index=True, column_config=traductor)
            


with tab8:
    st.subheader("Trayectoria de una canción")
    with st.expander("Explicación"):
        st.text("Este gráfico muestra la historia de una canción que busques, en una línea temporal frente a las reproducciones que ha tenido para cada intervalo")
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

