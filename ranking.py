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
    songs =  songs[songs["ms_played"]> 30000]
    return songs

def calcular_minutos_escuchas(songs):
    """Función que le das una data table de canciones y te da los minutos totales que se ha escuchado en toda esa tabla"""
    ms_total = songs["ms_played"].sum()
    min_escuchas = ms_total/(6*10**4)
    return min_escuchas

def calcular_escuchas_por_mes(songs, cancion, artista):
    """ Calcula las escuchas por mes de una cación y artista concreto para una tabla de datos dada"""
    songs = songs.copy()
    songs = songs[(songs["cancion"]==cancion) & (songs["artista"]==artista)]
    songs["mes"] = songs["ts"].dt.to_period("M").dt.to_timestamp()
    escuchas_por_mes = songs.groupby("mes").size().reset_index(name = "escuchas")
    return escuchas_por_mes

def calcular_sstats(songs: pd.DataFrame):
    """Función que recoge el data frame de songs y crea una fila por canción, añadiendo el número de reproducciones, la fecha de primera y última reproducción de esa canción """

    sstats = (songs.groupby(["cancion", "artista"]).agg(
        rep = ('ts', 'size'),
        fecha_inicio = ('ts', 'min'),
        fecha_max = ('ts', 'max')
    ).reset_index())
    return sstats

def calcular_ranking_reproducidas(songs, min_played = 30000):
    """Ranking de canciones ordenadas por reproducciones pero teniendo en cuenta las reproducciones a partir de un minimo de milisegundos de escucha (min_played)"""
    reproducidas = songs[songs["ms_played"]> min_played]
    ranking = reproducidas.groupby(["cancion", "artista"]).size().reset_index(name = "rep").sort_values(by = "rep", ascending = False)
    ranking.insert(0, "Puesto", range(1, len(ranking) + 1))

    return ranking

def calcular_ranking_trackdone(songs, min_played = 30000):
    """Ranking de canciones pero las repeticiones solo cuentan si he escuchado la canción hasta el final"""
    ranking_trackdone = songs[(songs["reason_end"]== "trackdone") & (songs["ms_played"]>min_played)]
    ranking_trackdone = ranking_trackdone.groupby(["cancion", "artista"]).size().reset_index(name="rep_trackdone").sort_values(by="rep_trackdone", ascending=False)
    ranking_trackdone.insert(0, "Puesto", range(1, len(ranking_trackdone) + 1))

    return ranking_trackdone

def calcular_ranking_clickrow(songs, min_played = 30000):
    """Ranking de canciones que le he dado yo a reproducir activamente, es decir; no me las ha puesto Spotify, las he buscado yo y las he puesto yo"""
    ranking_clickrow = songs[songs["reason_start"] == "clickrow"]
    ranking_clickrow = ranking_clickrow.groupby(["cancion","artista"]).size().reset_index(name = "rep_clickrow").sort_values(by="rep_clickrow", ascending = False)
    ranking_clickrow.insert(0, "Puesto", range(1, len(ranking_clickrow) + 1))

    return ranking_clickrow

def calcular_ranking_loop(songs):
    """Ranking de repeticiones pero solo cuenta las canciones que has puesto en bucle"""
    ranking_loop = songs[(songs["cancion"]==songs["cancion"].shift(1)) & (songs["artista"]==songs["artista"].shift(1))]
    ranking_loop = ranking_loop.groupby(["cancion","artista"]).size().reset_index(name = "rep_loop").sort_values(by="rep_loop", ascending = False)
    ranking_loop.insert(0, "Puesto", range(1, len(ranking_loop) + 1))

    return ranking_loop

def calcular_ranking_densidad(sstats, min_rep = 50):

    """Calcula para una tabla dada de canciones, las media de las escuchas desde la primera escucha hasta la última para cada canción, además añade un minimo de reproducciones para no favorecer a las canciones que se han escuchado un solo día"""    
    sstats = sstats.copy()
    fecha_fin = sstats['fecha_max'].max() # Última fecha registrada en el estudio
    # Intervalo entre la primera escucha y el final del estudio pasado a días (mínimo 1 día para no dividir por 0)
    sstats['delta_dias'] = ((fecha_fin - sstats['fecha_inicio']).dt.total_seconds() / 86400).clip(lower=1)
    sstats['densidad'] = sstats['rep'] / sstats['delta_dias'] # Reproducciones por día

    # Nos quedamos con las canciones con un mínimo de escuchas, si no ganan las que se escucharon 2 o 3 veces el mismo día
    
    ranking_densidad = sstats[sstats['rep'] >= min_rep].sort_values(by='densidad', ascending=False)
    ranking_densidad.insert(0, "Puesto", range(1, len(ranking_densidad) + 1))

    return ranking_densidad

def calcular_ranking_intervalo(sstats, songs, intervalo_mes=3):
    """Función que para un intervalo de tiempo fijo calcula desde la primera reproducción las escuchas en ese intervalo de tiempo. No tiene en cuenta canciones que no tienen todo el intervalo de tiempo, por lo tanto si la canción la has conocido hace menos que tu intervalo de tiempo, no va a salir"""

    ranking_intervalo = songs.merge(
    sstats,
    on= ['cancion', 'artista'] )
    fecha_fin = sstats['fecha_max'].max() 
# A continuación queremos hacer un slicing de toda la table para que coja las reproducciones concretas en un intervalo de tiempo desde la primera vez que la escuchamos
    ranking_intervalo = ranking_intervalo[(ranking_intervalo['fecha_inicio'] + pd.DateOffset(months=intervalo_mes) > ranking_intervalo['ts'])&(fecha_fin > ranking_intervalo['fecha_inicio'] + pd.DateOffset(months=intervalo_mes))]

# Una vez hecho la selección y que todas las reproducciones son de un mismo intervalo de tiempo, agrupamos por nombre como siemmpre
    ranking_intervalo = ranking_intervalo.groupby(['cancion','artista']).agg(
    rep_ventana = ('ts', 'size')
    ).reset_index()

# Calculamos la densidad
    ranking_intervalo['densidad'] = ranking_intervalo['rep_ventana']/(intervalo_mes*30)

# Recortamos un poco la tabla para que no sea tan grande.
    ranking_intervalo = ranking_intervalo[['cancion', 'artista', 'rep_ventana','densidad']].sort_values(by='densidad', ascending=False)
    ranking_intervalo.insert(0, "Puesto", range(1, len(ranking_intervalo) + 1))

    return ranking_intervalo

#valor por defecto que usamos al final del código
PESOS_RANKINGS_DEFAULT = {
        "rep_ventana":1,
        "pct_trackdone": 1,
        "pct_clickrow":1,
        "pct_loop":1
    }

def calcular_ranking_percentile(sstats, min_rep, intervalo_mes,songs, ranking_trackdone, ranking_clickrow, ranking_loop, pesos_rankings = PESOS_RANKINGS_DEFAULT):


    
    # Definimos la matriz base a la que le vamos a añadir todos los percentiles
    fecha_fin = sstats["fecha_max"].max()
    base = sstats[(sstats['rep'] >= min_rep) & (sstats['fecha_inicio'] + pd.DateOffset(months=intervalo_mes) <= fecha_fin)]
    base = base[['cancion', 'artista', 'rep']]

    # Calculamos el ind del trackdone
    ind_trackdone = ranking_trackdone.merge(
        sstats,
        on = ['cancion', 'artista']
        )
    ind_trackdone['pct_trackdone'] = (ind_trackdone['rep_trackdone'] / ind_trackdone['rep'])
    ind_trackdone = ind_trackdone[['cancion', 'artista', 'pct_trackdone']] 
    # lo unimos a la base
    base = base.merge(ind_trackdone,
        on = ['cancion', 'artista'],
        how = 'left'
        )
    
    # Calculamos el indicador de clickrow
    ind_clickrow = ranking_clickrow.merge(
        sstats,
        on = ['cancion', 'artista'] 
        )
    ind_clickrow['pct_clickrow'] = (ind_clickrow['rep_clickrow'] / ind_clickrow['rep'])
    ind_clickrow = ind_clickrow[['cancion', 'artista', 'pct_clickrow']]
    # Lo unimos a la base
    base = base.merge(ind_clickrow,
                  on = ['cancion', 'artista'],
                  how = 'left')

    # Calculamos el indicador de loop
    ind_loop = ranking_loop.merge(
        sstats,
        on = ['cancion', 'artista'] 
        )
    ind_loop['pct_loop'] = (ind_loop['rep_loop'] / ind_loop['rep'])
    ind_loop = ind_loop[['cancion', 'artista', 'pct_loop']]
    # Lo unimos a la base
    base = base.merge(ind_loop,
                  on = ['cancion', 'artista'],
                  how = 'left')

    # Calculamos el indicador del intervalo
    ranking_intervalo = calcular_ranking_intervalo(sstats,songs,intervalo_mes)
    ind_intensidad = ranking_intervalo[['cancion', 'artista', 'rep_ventana']]
    base = base.merge(ind_intensidad, on=['cancion', 'artista'], how='left')
    base = base.fillna(0)

    # Creamos la tabla con los percentiles de cada indicador
    indicadores = ['rep_ventana', 'pct_trackdone', 'pct_clickrow', 'pct_loop']
    
    base['nota'] = 0
    suma_pesos = sum(pesos_rankings.values())
    for col in indicadores:
        base['p_' + col] = base[col].rank(pct=True) # Creamos la columna de los percentiles para cada indicador
        base['nota'] += base['p_' + col ]*pesos_rankings[col]* 10/suma_pesos  # nota sobre 10, base += numero es igual que hacer base = numero + base
    ranking_final = base.sort_values(by='nota', ascending=False)
    return ranking_final
    