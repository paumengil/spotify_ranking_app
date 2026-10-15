import json
import pandas as pd

def cargar_datos(archivos):
    """ Recibe una lista de archivos JSON de Spotify( ya abiertos porque no es una ruta lo que se pega en la web sino el archivo, es equivalente a abrirlo) y devuelve un Data Frame """
    parametros = []
    for archivo in archivos:
        parametros.extend(json.load(archivo))
    return pd.DataFrame(parametros)

def preparar_canciones(df: pd.DataFrame): #Los dos puntos del paréntersis sirve para decir qué tipo de dato es df, no es obligatorio, pero es una buena praxis
    """Recibe un Data Frame y devuelve otro pero con la fila de las fecha y minutos pasada a formato legible para pandas y quita por si las hubiera las filas sin información"""
    
    df = df.copy()  # Estamos creando una copia de la tabla que nos llega porque en la siguiente linea la vamos a alterar, así no alteramos los datos que se meten en la función sino la copia
    df["ts"] = pd.to_datetime(df["ts"]) 
    songs = df[df["master_metadata_track_name"].notna()]
    return songs

def calcular_sstats(songs: pd.DataFrame):
    """Función que recoge el data frame de songs y crea una fila por canción, añadiendo el número de reproducciones, la fecha de primera y última reproducción de esa canción """

    sstats = (songs.groupby(["master_metadata_track_name", "master_metadata_album_artist_name"]).agg(
        rep = ('ts', 'size'),
        fecha_inicio = ('ts', 'min'),
        fecha_max = ('ts', 'max')
    ).reset_index().rename(columns={
        "master_metadata_track_name": "cancion",
        "master_metadata_album_artist_name": "artista"
    }
    ))
    return sstats

def ranking_reproducidas(songs, min_played = 30000):
    """Ranking de canciones ordenadas por reproducciones pero teniendo en cuenta las reproducciones a partir de un minimo de milisegundos de escucha (min_played)"""
    reproducidas = songs[songs["ms_played"]> min_played]
    ranking = reproducidas.groupby(["master_metadata_track_name", "master_metadata_album_artist_name"]).size().reset_index(name = "rep").sort_values(by = "rep", ascending = False).rename(columns = {
        "master_metadata_track_name": "cancion",
        "master_metadata_album_artist_name": "artista"
    })
    return ranking