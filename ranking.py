import json
import pandas as pd

def cargar_datos(contenidos):
    """ Recibe una lista de archivos JSON de Spotify( ya abiertos porque no es una ruta lo que se pega en la web sino el archivo, es equivalente a abrirlo) y devuelve un Data Frame """
    parametros = []
    for contenido in contenidos:
        parametros.extend(json.loads(contenido))
    
    return pd.DataFrame(parametros)

def preparar_canciones(df: pd.DataFrame): #Los dos puntos del paréntersis sirve para decir qué tipo de dato es df, no es obligatorio, pero es una buena praxis
    """Recibe un Data Frame y devuelve otro pero con la fila de las fecha y minutos pasada a formato legible para pandas y quita por si las hubiera las filas sin información"""
    
    df = df.copy()  # Estamos creando una copia de la tabla que nos llega porque en la siguiente linea la vamos a alterar, así no alteramos los datos que se meten en la función sino la copia
    df["ts"] = pd.to_datetime(df["ts"]) 
    songs = df[df["master_metadata_track_name"].notna()].rename(columns={
        "master_metadata_track_name": "cancion",
        "master_metadata_album_artist_name": "artista"
    }
    )
    return songs

def calcular_sstats(songs: pd.DataFrame):
    """Función que recoge el data frame de songs y crea una fila por canción, añadiendo el número de reproducciones, la fecha de primera y última reproducción de esa canción """

    sstats = (songs.groupby(["cancion", "artista"]).agg(
        rep = ('ts', 'size'),
        fecha_inicio = ('ts', 'min'),
        fecha_max = ('ts', 'max')
    ).reset_index())
    return sstats

def ranking_reproducidas(songs, min_played = 30000):
    """Ranking de canciones ordenadas por reproducciones pero teniendo en cuenta las reproducciones a partir de un minimo de milisegundos de escucha (min_played)"""
    reproducidas = songs[songs["ms_played"]> min_played]
    ranking = reproducidas.groupby(["cancion", "artista"]).size().reset_index(name = "rep").sort_values(by = "rep", ascending = False)
    return ranking

def ranking_trackdone(songs, min_played = 30000):
    """Ranking de canciones pero las repeticiones solo cuentan si he escuchado la canción hasta el final"""
    ranking_trackdone = songs[(songs["reason_end"]== "trackdone") & (songs["ms_played"]>min_played)]
    ranking_trackdone = ranking_trackdone.groupby(["cancion", "artista"]).size().reset_index(name="rep").sort_values(by="rep", ascending=False)
    return ranking_trackdone

def ranking_clickrow(songs, min_played = 30000):
    """Ranking de canciones que le he dado yo a reproducir activamente, es decir; no me las ha puesto Spotify, las he buscado yo y las he puesto yo"""
    ranking_clickrow = songs[songs["reason_start"] == "clickrow"]
    ranking_clickrow = ranking_clickrow.groupby(["cancion","artista"]).size().reset_index(name = "rep").sort_values(by="rep", ascending = False)
    return ranking_clickrow

def ranking_loop(songs):
    """Ranking de repeticiones pero solo cuenta las canciones que has puesto en bucle"""
    ranking_loop = songs[(songs["cancion"]==songs["cancion"].shift(1)) & (songs["artista"]==songs["artista"].shift(1))]
    ranking_loop = ranking_loop.groupby(["cancion","artista"]).size().reset_index(name = "rep").sort_values(by="rep", ascending = False)
    return ranking_loop

def ranking_densidad(sstats, min_rep = 50):
    sstats = sstats.copy()
    fecha_fin = sstats['fecha_max'].max() # Última fecha registrada en el estudio
    # Intervalo entre la primera escucha y el final del estudio pasado a días (mínimo 1 día para no dividir por 0)
    sstats['delta_dias'] = ((fecha_fin - sstats['fecha_inicio']).dt.total_seconds() / 86400).clip(lower=1)
    sstats['densidad'] = sstats['rep'] / sstats['delta_dias'] # Reproducciones por día

    # Nos quedamos con las canciones con un mínimo de escuchas, si no ganan las que se escucharon 2 o 3 veces el mismo día
    
    ranking_densidad = sstats[sstats['rep'] >= min_rep].sort_values(by='densidad', ascending=False)
    return ranking_densidad