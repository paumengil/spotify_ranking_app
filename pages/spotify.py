import streamlit as st
import ranking
import altair as alt
import comun

## Nos traemos los datos para no guardarlos fuera de la caché

contenidos = [archivo.getvalue() for archivo in st.session_state["subidos"]]
# Calculamos las tablas
songs, sstats = comun.preparar_todo(contenidos)

#calculamos el ranking
rk_spotify = ranking.calcular_ranking_reproducidas(songs)

# Maquetamos la visualización
st.subheader(":green[Ranking de Spotify]")

# Explicación del ranking
with st.expander("Explicación"):
    st.markdown("""Este ranking simula el ranking creado por Spotify por su veinte aniversario para la playlist *Tu top de canciones más escuchadas*. Tras muchas pruebas se consiguió replicar este ranking contando las repeticiones de las canciones con más de 30 segundos de reproducción.¡Compruebalo tú mismo en tu playlist de Spotify!\\\n Ojo: Hay que tener en cuenta que el ranking de Spotify se hizo con los datos recopilados hasta mayo de 2026 y el tuyo depende de cuando pediste el histórico, por lo que pueden no coincidir""")

# Creamos el top10 para pintalo en el gráfico
top10 = rk_spotify.head(10)

# Gráfico
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

# Tabla con todos los datos del ranking
st.dataframe(rk_spotify, hide_index=True, column_config=comun.traductor)
