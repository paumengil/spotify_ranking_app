import streamlit as st
import ranking
import altair as alt

@st.cache_data(ttl=7200, max_entries=5) #Usamos este decorador que solo afecta a la función que tiene debajo para que a pesar de movamos el slider no haya que cargar los mismos datos luego
def preparar_todo(contenidos): 
    df = ranking.cargar_datos(contenidos)
    songs = ranking.preparar_canciones(df)
    sstats = ranking.calcular_sstats(songs)
    
    return songs, sstats


st.set_page_config(page_title="Mi ranking de Spotify", page_icon="🎧", layout="wide")
st.title(":green[Mi ranking de Spotify]")
st.markdown("""Esta aplicación sirve para analizar tus gustos musicales según la información recopilada por Spotify""")

with st.expander("¿Cómo pedir tus datos?"):
    st.markdown("""Spotify guarda todos tus datos y puedes pedírselos en tres sencillos pasos:\n\n1. En el icono de tu perfil, pulsa **cuenta**. Esto te redirigirá a una página con todos los datos de tu cuenta de Spotify\n2. En el apartado de **Seguridad y Privacidad** selecciona **Privacidad de la cuenta**\n3. Desliza hasta el final y marca **Historial de reproducción ampliado** y pulsa **solicitar datos**\n\nEn unos días te llegarán al correo una carpeta comprimida con unos archivos en formato .json con todo tu historial, para poder ver tu análisis, simplemente cárgalos aquí""")

with st.expander("Sube tus datos de Spotify"):
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

#Calculamos las tablas
songs, sstats = preparar_todo(contenidos)

# Calculamos los rankings que usaremos más adelante, algunos los calculamos abajo porque requieren de un parámetro que está en el slider
rk_spotify = ranking.calcular_ranking_reproducidas(songs)
rk_trackdone = ranking.calcular_ranking_trackdone(songs)
rk_clickrow = ranking.calcular_ranking_clickrow(songs)
rk_loop = ranking.calcular_ranking_loop(songs)

col1, col2, col3, col4 =st.columns(4)
col1.metric("Minutos totales",round(ranking.calcular_minutos_escuchas(songs)),border=True) 
col2.metric("canciones", len(sstats["cancion"]), border=True)
col3.metric("Inicio",str(sstats["fecha_inicio"].min().date()), border=True) #convertimos la fecha a string porque no lee fechas
col4.metric("Fin",str(sstats["fecha_max"].max().date()),border=True) #convertimos la fecha a string porque no lee fechas
with st.expander("Ver todos mis datos"):
    st.dataframe(sstats, hide_index=True, column_config=traductor)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["Spotify", "Enteras", "Seleccionadas","En bucle", "Al día", "En un tiempo", "Definitivo", "Mi historia con una canción" ])


with tab1:
    st.subheader(":green[Ranking de Spotify]")
    with st.expander("Explicación"):
        st.markdown("""Este ranking simula el ranking creado por Spotify por su veinte aniversario para la playlist *Tu top de canciones más escuchadas*. Tras muchas pruebas se consiguió replicar este ranking contando las repeticiones de las canciones con más de 30 segundos de reproducción.¡Compruebalo tú mismo en tu playlist de Spotify!\\\n Ojo: Hay que tener en cuenta que el ranking de Spotify se hizo con los datos recopilados hasta mayo de 2026 y el tuyo depende de cuando pediste el histórico, por lo que pueden no coincidir""")
    top10 = rk_spotify.head(10)
    grafico = (
            alt.Chart(top10)
            .mark_bar(cornerRadiusEnd=4) # con mark_bar estamos creando un gráfico de barras
            .encode(
                x = alt.X("rep:Q", title="Escuchas"), # la columna rep va en el eje horizontal. Q significa cuantitativa
                y=alt.Y("cancion:N", sort="-x", title=None,axis=alt.Axis(labelColor="#191414", labelFontWeight="bold", labelFontSize=15, labelLimit=600)), # La columna canción va en el eje vertical, la N significa nominal
                tooltip=["cancion","artista", "rep"],# Las cosas que salen cuando pongo el cursor encima
            ).properties(height=400)
        )
    st.altair_chart(grafico)
    st.dataframe(rk_spotify, hide_index=True, column_config=traductor)
   
with tab2:
    st.subheader(":green[Ranking canciones terminadas]")
    with st.expander("Explicación"):
        st.markdown("Este es un ranking de reproducciones, al igual que el de Spotify. Sin embargo, aquí solo cuenta como reproducción si has escuchado la canción hasta el final, sin saltártela. Así le damos verdadera importancia a las canciones que te gustan en su completitud, no solo el estribillo de TikTok.")
    
    top10 = rk_trackdone.head(10)
    grafico = (
                alt.Chart(top10)
                .mark_bar(cornerRadiusEnd=4) # con mark_bar estamos creando un gráfico de barras
                .encode(
                    x = alt.X("rep_trackdone:Q", title="Escuchas"), # la columna rep va en el eje horizontal. Q significa cuantitativa
                    y=alt.Y("cancion:N", sort="-x", title=None,axis=alt.Axis(labelColor="#191414", labelFontWeight="bold", labelFontSize=15, labelLimit=600)), # La columna canción va en el eje vertical, la N significa nominal
                    tooltip=["cancion","artista", "rep_trackdone"],# Las cosas que salen cuando pongo el cursor encima
                ).properties(height=400) # Ajusta la altura del gráfico a una fija
            )
    st.altair_chart(grafico)
    st.dataframe(rk_trackdone, hide_index=True, column_config=traductor)

with tab3:
    st.subheader(":green[Ranking de canciones elegidas]")
    with st.expander("Explicación"):
        st.markdown("""Este es un ranking de reproducciones, al igual que los otros pero aquí solo cuentan las reproducciones de las canciones que has seleccionado tú. Es decir, solo cuenta si la hemos buscado y clicado. Con este ranking valoramos esas canciones que te vienen a la mente escuchar, no las que están en tu playlist favorita ni la que te ha puesto DJ Livi.\\\n Ojo: En la versión gratuita de Spotify las opciones para elegir canciones concretas son limitadas, sobre todo en el móvil, así que tal vez tengas pocos datos aquí""")
    top10 = rk_clickrow.head(10)
    grafico = (
                alt.Chart(top10)
                .mark_bar(cornerRadiusEnd=4) # con mark_bar estamos creando un gráfico de barras
                .encode(
                    x = alt.X("rep_clickrow:Q", title="Escuchas"), # la columna rep va en el eje horizontal. Q significa cuantitativa
                    y=alt.Y("cancion:N", sort="-x", title=None,axis=alt.Axis(labelColor="#191414", labelFontWeight="bold", labelFontSize=15, labelLimit=600)), # La columna canción va en el eje vertical, la N significa nominal
                    tooltip=["cancion","artista", "rep_clickrow"],# Las cosas que salen cuando pongo el cursor encima
                ).properties(height=400)
            )
    st.altair_chart(grafico)
    st.dataframe(rk_clickrow, hide_index=True, column_config=traductor)

with tab4:
    st.subheader(":green[Ranking canciones en bucle]")
    with st.expander("Explicación"):    
        st.markdown("Este ranking, nuevamente cuenta las reproducciones, pero esta vez solo cuentan las que han estado en bucle. Aquí contamos como reproducción solo si la anterior era la misma canción, da igual si has puesto literalmente el bucle o simplemente le has dado hacia atrás. Este ranking pretende valorar esas canciones que nos obsesionan y que con una escucha no es suficiente. ¿A ver qué canción es la que más has tenido en bucle?")
    top10 = rk_loop.head(10)
    grafico = (
                alt.Chart(top10)
                .mark_bar(cornerRadiusEnd=4) # con mark_bar estamos creando un gráfico de barras
                .encode(
                        x = alt.X("rep_loop:Q", title="Escuchas"), # la columna rep va en el eje horizontal. Q significa cuantitativa
                        y=alt.Y("cancion:N", sort="-x", title=None,axis=alt.Axis(labelColor="#191414", labelFontWeight="bold", labelFontSize=15, labelLimit=600)), # La columna canción va en el eje vertical, la N significa nominal
                        tooltip=["cancion","artista", "rep_loop"],# Las cosas que salen cuando pongo el cursor encima
                    ).properties(height=400)
                )
    st.altair_chart(grafico)
    st.dataframe(rk_loop, hide_index=True, column_config=traductor)

with tab5:
    st.subheader(":green[Ranking de más escuchas en un día]")
    with st.expander("Explicación"):
        st.markdown("""Este ranking es el motivo de que se hiciera este proyecto. El ranking de Spotify beneficia a las canciones que conoces desde hace más años, porque han tenido más tiempo para acumular escuchas. Para compensarlo, este ranking divide las escuchas totales de cada canción entre los días que han pasado desde que la escuchaste por primera vez hasta la fecha más reciente de tu historial. Así, 100 escuchas en un año pesan más que 200 en diez años, y las canciones que siguen contigo salen mejor paradas que las que dejaste de escuchar.\\\n El problema es que las canciones que acabas de descubrir llevan muy pocos días contigo, así que con pocas escuchas ya consiguen mucha puntuación, sin que eso signifique que sean tus favoritas. Por eso puedes elegir cuántas escuchas necesita una canción como mínimo para entrar en el ranking. Prueba a moverlo para ver cómo cambia tu ranking.
        """)
    max_rep = sstats["rep"].max()
    min_rep_densidad = st.slider("Nº mínimo de reproducciones para entrar",1, max_rep,max_rep//2, key="min_rep_densidad")
    #calculamos el ranking con el valor del slider
    rk_densidad = ranking.calcular_ranking_densidad(sstats, min_rep_densidad)
    
    top10 = rk_densidad.head(10)
    grafico = (
                alt.Chart(top10)
                .mark_bar(cornerRadiusEnd=4) # con mark_bar estamos creando un gráfico de barras
                .encode(
                    x = alt.X("densidad:Q", title="Escuchas al día desde que la escuchamos por primera vez"), # la columna rep va en el eje horizontal. Q significa cuantitativa
                    y=alt.Y("cancion:N", sort="-x", title=None,axis=alt.Axis(labelColor="#191414", labelFontWeight="bold", labelFontSize=15, labelLimit=600)), # La columna canción va en el eje vertical, la N significa nominal
                    tooltip=["cancion","artista", "densidad"],# Las cosas que salen cuando pongo el cursor encima
                ).properties(height=400)
            )
    st.altair_chart(grafico)
    st.dataframe(rk_densidad, hide_index=True, column_config=traductor)

with tab6:
    st.subheader(":green[Ranking intervalo fijo]")
    with st.expander("Explicación"):
        st.markdown("""El anterior ranking mete una desigualdad y es que, las canciones que hemos conocido hace poco tiempo, tienen ventaja frente a las que conocemos desde hace más, por ello creamos este ranking donde vamos a calcular para todas las canciones, desde el momento que las conocimos hasta un tiempo limitado (ventana), cuanto las hemos escuchado. Este ranking valora lo enganchado que te tuvieron las canciones cuando las conociste.\\\n Ojo: Las canciones que conoces desde hace menos mesos de los puestos en el slider, no aparecerán en el ranking, ya que no contaríamos con todos los datos y no sería justo""")
    valor_inicial_ventana = min(12, int((sstats["fecha_max"].max()-sstats["fecha_inicio"].min()).days/30))
    intervalo_mes_ventana = st.slider("Nº de meses del estudio", 1, int((sstats["fecha_max"].max()-sstats["fecha_inicio"].min()).days/30), valor_inicial_ventana, key="intervalo_mes_ventana")
    rk_intervalo = ranking.calcular_ranking_intervalo(sstats,songs,intervalo_mes_ventana)
    top10 = rk_intervalo.head(10)
    grafico = (
                alt.Chart(top10)
                .mark_bar(cornerRadiusEnd=4) # con mark_bar estamos creando un gráfico de barras
                .encode(
                    x = alt.X("rep_ventana:Q", title="Reproducciones en ese intervalo"), # la columna rep va en el eje horizontal. Q significa cuantitativa
                    y=alt.Y("cancion:N", sort="-x", title=None,axis=alt.Axis(labelColor="#191414", labelFontWeight="bold", labelFontSize=15, labelLimit=600)), # La columna canción va en el eje vertical, la N significa nominal
                    tooltip=["cancion","artista", "rep_ventana"],# Las cosas que salen cuando pongo el cursor encima
                ).properties(height=400)
            )
    st.altair_chart(grafico)
    st.dataframe(rk_intervalo, hide_index=True, column_config=traductor)

with tab7:
    st.subheader(":green[Ranking Definitivo]")
    with st.expander("Explicación"):
        st.markdown("""Este ranking fusiona todos los anteriores: Calcula los porcentajes de las reproducciones totales que han sido clicadas, en bucle o reproducidas hasta el final y las reproducciones que se han tenido en cada canción para una ventana temporal. De cada canción se tiene en cuenta el percentil de su ranking, pero como cada persona es un mundo, este ranking te permite decidir a cuál de los rankings anteriores le das más peso, además de editar los dos parámetros que hemos visto en el resto de rankings:\\\n La ventana temporal que estamos observando de una canción para el ranking de intensidad y el número de reproducciones mínimas que tienen que tener las canciones para aparecer en el ranking """)
    min_rep_definitivo = st.slider("Nº mínimo de reproducciones para entrar",1, max_rep, max_rep//2, key="min_rep_definitivo")
    intervalo_mes_definitivo = st.slider("Nº de meses del estudio", 1, int((sstats["fecha_max"].max()-sstats["fecha_inicio"].min()).days/30),valor_inicial_ventana, key="intervalo_mes_definitivo")
    st.markdown("**Cuánto pesa cada indicador**")
    c1, c2, c3, c4 = st.columns(4)
    pesos_rankings = {
        "rep_ventana":   c1.slider("Intervalo fijo", 1, 10, 1),
        "pct_trackdone": c2.slider("Enteras", 1, 10, 1),
        "pct_clickrow":  c3.slider("Elegida por mí", 1, 10, 1),
        "pct_loop":      c4.slider("En bucle", 1, 10, 1),
    }

   

    rk_final = ranking.calcular_ranking_percentile(sstats, songs, min_rep_definitivo, intervalo_mes_definitivo, rk_trackdone, rk_clickrow, rk_loop, pesos_rankings)
    
    top10 = rk_final.head(10)
    grafico = (
                alt.Chart(top10)
                .mark_bar(cornerRadiusEnd=4) # con mark_bar estamos creando un gráfico de barras
                .encode(
                    x = alt.X("nota:Q", title="Nota"), # la columna rep va en el eje horizontal. Q significa cuantitativa
                    y=alt.Y("cancion:N", sort="-x", title=None,axis=alt.Axis(labelColor="#191414", labelFontWeight="bold", labelFontSize=15, labelLimit=600)), # La columna canción va en el eje vertical, la N significa nominal
                    tooltip=["cancion","artista", "nota"],# Las cosas que salen cuando pongo el cursor encima
                ).properties(height=400)
            )
    st.altair_chart(grafico)
    st.dataframe(rk_final[["Puesto","cancion","artista","rep","rep_ventana", "pct_trackdone", "pct_clickrow", "pct_loop", "nota" ]], hide_index=True, column_config=traductor)
            


with tab8:
    st.subheader(":green[Trayectoria de una canción]")
    with st.expander("Explicación"):
        st.markdown("Este gráfico muestra la historia de una canción que busques, en una línea temporal frente a las reproducciones que ha tenido para cada intervalo")
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
        .encode(
            x = alt.X("mes:T", title="Tiempo"), # T para que altair sepa que es algo temporal y ordene bien
            y = alt.Y("escuchas:Q", title="Escuchas")
        )
        .mark_line(point=True)
    )

    st.altair_chart(grafico)

