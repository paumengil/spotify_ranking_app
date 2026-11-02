import json
import pandas as pd

def cargar_datos(contenidos):
    """Une el contenido de varios JSON de Spotify en un único DataFrame.

    Parameters
    ----------
    contenidos : list of bytes or str
        Contenido de cada archivo JSON del historial extendido de Spotify
        (por ejemplo, ``archivo.getvalue()`` de ``st.file_uploader``). No son
        rutas, sino el texto ya leído de cada archivo.

    Returns
    -------
    pd.DataFrame
        Una fila por reproducción, con las columnas originales de Spotify
        (``ts``, ``ms_played``, ``master_metadata_track_name``...). Las filas
        quedan en el orden en que vienen los archivos.
"""
    parametros = []
    for contenido in contenidos:
        parametros.extend(json.loads(contenido))
    
    return pd.DataFrame(parametros)

def preparar_canciones(df: pd.DataFrame): #Los dos puntos del paréntersis sirve para decir qué tipo de dato es df, no es obligatorio, pero es una buena praxis
    """Limpia el historial y se queda solo con las escuchas de canciones.

    Convierte ``ts`` a fecha, descarta las filas sin nombre de canción
    (podcasts y audiolibros), renombra las columnas de canción y artista y
    elimina las reproducciones de 30 segundos o menos.

    Parameters
    ----------
    df : pd.DataFrame
        Historial tal como lo devuelve ``cargar_datos``. No se modifica.

    Returns
    -------
    pd.DataFrame
        Copia filtrada con ``ts`` en formato fecha y las columnas
        ``cancion`` y ``artista`` en lugar de los nombres originales.
"""
    
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
    """Calcula los minutos totales escuchados.

    Parameters
    ----------
    songs : pd.DataFrame
        Tabla de escuchas con la columna ``ms_played``.

    Returns
    -------
    float
        Suma de ``ms_played`` convertida a minutos.
"""
    ms_total = songs["ms_played"].sum()
    min_escuchas = ms_total/(6*10**4)
    return min_escuchas

def calcular_escuchas_por_mes(songs, cancion, artista):
    """Cuenta las escuchas por mes de una canción concreta.

    Parameters
    ----------
    songs : pd.DataFrame
        Tabla de escuchas devuelta por ``preparar_canciones``.
    cancion : str
        Nombre de la canción.
    artista : str
        Artista de la canción. Se usa junto con ``cancion`` para no mezclar
        canciones distintas con el mismo título.

    Returns
    -------
    pd.DataFrame
        Columnas ``mes`` (primer día de cada mes) y ``escuchas``. Los meses
        sin ninguna escucha no aparecen.
"""
    songs = songs.copy()
    songs = songs[(songs["cancion"]==cancion) & (songs["artista"]==artista)]
    songs["mes"] = songs["ts"].dt.to_period("M").dt.to_timestamp()
    escuchas_por_mes = songs.groupby("mes").size().reset_index(name = "escuchas")
    return escuchas_por_mes

def calcular_sstats(songs: pd.DataFrame):
    """Resume las escuchas en una fila por canción.

    Parameters
    ----------
    songs : pd.DataFrame
        Tabla de escuchas devuelta por ``preparar_canciones``.

    Returns
    -------
    pd.DataFrame
        Una fila por cada par (``cancion``, ``artista``) con:

        - ``rep``: número de escuchas.
        - ``fecha_inicio``: fecha de la primera escucha.
        - ``fecha_max``: fecha de la última escucha.
"""

    sstats = (songs.groupby(["cancion", "artista"]).agg(
        rep = ('ts', 'size'),
        fecha_inicio = ('ts', 'min'),
        fecha_max = ('ts', 'max')
    ).reset_index())
    return sstats

def calcular_ranking_reproducidas(songs, min_played = 30000):
    """Ranking por número total de escuchas, como el de Spotify.

    Parameters
    ----------
    songs : pd.DataFrame
        Tabla de escuchas devuelta por ``preparar_canciones``.
    min_played : int, default 30000
        Milisegundos mínimos para que una reproducción cuente. Como
        ``preparar_canciones`` ya descarta las de 30 s o menos, valores
        inferiores a 30000 no tienen efecto.

    Returns
    -------
    pd.DataFrame
        Columnas ``Puesto``, ``cancion``, ``artista`` y ``rep``, ordenadas
        de más a menos escuchas.
"""
    reproducidas = songs[songs["ms_played"]> min_played]
    ranking = reproducidas.groupby(["cancion", "artista"]).size().reset_index(name = "rep").sort_values(by = "rep", ascending = False)
    ranking.insert(0, "Puesto", range(1, len(ranking) + 1))

    return ranking

def calcular_ranking_trackdone(songs, min_played = 30000):
    """Ranking que solo cuenta las escuchas completas.

    Una escucha cuenta si la canción terminó sola
    (``reason_end == "trackdone"``), sin saltarla ni pararla.

    Parameters
    ----------
    songs : pd.DataFrame
        Tabla de escuchas devuelta por ``preparar_canciones``.
    min_played : int, default 30000
        Milisegundos mínimos para que una reproducción cuente.

    Returns
    -------
    pd.DataFrame
        Columnas ``Puesto``, ``cancion``, ``artista`` y ``rep_trackdone``,
        ordenadas de más a menos escuchas completas.
"""
    ranking_trackdone = songs[(songs["reason_end"]== "trackdone") & (songs["ms_played"]>min_played)]
    ranking_trackdone = ranking_trackdone.groupby(["cancion", "artista"]).size().reset_index(name="rep_trackdone").sort_values(by="rep_trackdone", ascending=False)
    ranking_trackdone.insert(0, "Puesto", range(1, len(ranking_trackdone) + 1))

    return ranking_trackdone

def calcular_ranking_clickrow(songs, min_played = 30000):
    """Ranking que solo cuenta las escuchas elegidas activamente.

    Una escucha cuenta si empezó porque se pulsó la canción
    (``reason_start == "clickrow"``), no porque Spotify la pusiera
    automáticamente. Sin Spotify Premium este dato es poco fiable.

    Parameters
    ----------
    songs : pd.DataFrame
        Tabla de escuchas devuelta por ``preparar_canciones``.
    min_played : int, default 30000
        Se acepta por coherencia con las demás funciones, pero actualmente
        no se usa.

    Returns
    -------
    pd.DataFrame
        Columnas ``Puesto``, ``cancion``, ``artista`` y ``rep_clickrow``,
        ordenadas de más a menos escuchas elegidas.
"""
    ranking_clickrow = songs[songs["reason_start"] == "clickrow"]
    ranking_clickrow = ranking_clickrow.groupby(["cancion","artista"]).size().reset_index(name = "rep_clickrow").sort_values(by="rep_clickrow", ascending = False)
    ranking_clickrow.insert(0, "Puesto", range(1, len(ranking_clickrow) + 1))

    return ranking_clickrow

def calcular_ranking_loop(songs):
    """Ranking que solo cuenta las escuchas en bucle.

    Una escucha cuenta como bucle si la fila anterior de ``songs`` es la
    misma canción del mismo artista. En una racha de N escuchas seguidas se
    cuentan N - 1, porque la primera no es una repetición.

    Parameters
    ----------
    songs : pd.DataFrame
        Tabla de escuchas devuelta por ``preparar_canciones``.

    Returns
    -------
    pd.DataFrame
        Columnas ``Puesto``, ``cancion``, ``artista`` y ``rep_loop``,
        ordenadas de más a menos repeticiones.

"""
    songs = songs.sort_values(by="ts")
    ranking_loop = songs[(songs["cancion"]==songs["cancion"].shift(1)) & (songs["artista"]==songs["artista"].shift(1))]
    ranking_loop = ranking_loop.groupby(["cancion","artista"]).size().reset_index(name = "rep_loop").sort_values(by="rep_loop", ascending = False)
    ranking_loop.insert(0, "Puesto", range(1, len(ranking_loop) + 1))

    return ranking_loop

def calcular_ranking_densidad(sstats, min_rep = 50):

    """Ranking por escuchas al día desde que se conoce la canción.

    Para cada canción divide sus escuchas totales entre los días que van
    desde su primera escucha hasta la última fecha de todo el historial.
    Así se compensa la ventaja de las canciones que se conocen desde hace
    más tiempo.

    Parameters
    ----------
    sstats : pd.DataFrame
        Resumen por canción devuelto por ``calcular_sstats``. No se
        modifica.
    min_rep : int, default 50
        Escuchas mínimas para entrar en el ranking. Evita que ganen las
        canciones que se escucharon unas pocas veces hace muy poco.

    Returns
    -------
    pd.DataFrame
        Las columnas de ``sstats`` más ``Puesto``, ``delta_dias`` (días
        desde la primera escucha, mínimo 1) y ``densidad`` (escuchas por
        día), ordenadas de mayor a menor densidad.
"""
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
    """Ranking por escuchas en los primeros meses de cada canción.

    Para cada canción cuenta las escuchas que tuvo en los ``intervalo_mes``
    meses siguientes a su primera escucha. Así todas las canciones se
    comparan con el mismo tiempo, sin ventaja por antigüedad.

    Parameters
    ----------
    sstats : pd.DataFrame
        Resumen por canción devuelto por ``calcular_sstats``.
    songs : pd.DataFrame
        Tabla de escuchas devuelta por ``preparar_canciones``.
    intervalo_mes : int, default 3
        Duración de la ventana en meses.

    Returns
    -------
    pd.DataFrame
        Columnas ``Puesto``, ``cancion``, ``artista``, ``rep_ventana``
        (escuchas dentro de la ventana) y ``densidad`` (escuchas por día,
        tomando meses de 30 días), ordenadas de mayor a menor densidad.

    Notes
    -----
    Las canciones cuya ventana no ha terminado todavía (primera escucha
    hace menos de ``intervalo_mes`` meses respecto a la última fecha del
    historial) quedan fuera, porque no han tenido el tiempo completo.
"""

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

def calcular_ranking_percentile(sstats, songs, min_rep, intervalo_mes, ranking_trackdone, ranking_clickrow, ranking_loop, pesos_rankings = PESOS_RANKINGS_DEFAULT):

    """Ranking definitivo: nota sobre 10 que combina cuatro indicadores.

    El cálculo tiene tres pasos:

    1. Para cada canción se calculan cuatro indicadores:

       - ``rep_ventana``: escuchas en los primeros ``intervalo_mes`` meses
         (volumen).
       - ``pct_trackdone``: proporción de escuchas completas.
       - ``pct_clickrow``: proporción de escuchas elegidas activamente.
       - ``pct_loop``: proporción de escuchas en bucle.

       Las tres proporciones se calculan sobre todas las escuchas de la
       canción (``rep``) para que midan cómo se escucha, no cuánto.
    2. Cada indicador se convierte en percentil (de 0 a 1) respecto al
       resto de canciones del ranking.
    3. La nota es la media ponderada de los cuatro percentiles,
       multiplicada por 10.

    Solo entran las canciones con al menos ``min_rep`` escuchas, para que
    las proporciones no salgan de muy pocos datos, y las que se conocen
    desde hace al menos ``intervalo_mes`` meses, porque si no ``rep_ventana``
    no sería comparable.

    Parameters
    ----------
    sstats : pd.DataFrame
        Resumen por canción devuelto por ``calcular_sstats``.
    songs : pd.DataFrame
        Tabla de escuchas devuelta por ``preparar_canciones``.
    min_rep : int
        Escuchas totales mínimas para entrar en el ranking.
    intervalo_mes : int
        Duración en meses de la ventana de ``rep_ventana``.
    ranking_trackdone : pd.DataFrame
        Resultado de ``calcular_ranking_trackdone`` (necesita la columna
        ``rep_trackdone``).
    ranking_clickrow : pd.DataFrame
        Resultado de ``calcular_ranking_clickrow`` (necesita la columna
        ``rep_clickrow``).
    ranking_loop : pd.DataFrame
        Resultado de ``calcular_ranking_loop`` (necesita la columna
        ``rep_loop``).
    pesos_rankings : dict, default PESOS_RANKINGS_DEFAULT
        Peso de cada indicador. Debe tener exactamente las claves
        ``"rep_ventana"``, ``"pct_trackdone"``, ``"pct_clickrow"`` y
        ``"pct_loop"``; si falta alguna se produce un ``KeyError``. Solo
        importan las proporciones entre pesos ({1, 1, 1, 1} equivale a
        {5, 5, 5, 5}) y la suma no puede ser 0.

    Returns
    -------
    pd.DataFrame
        Una fila por canción, ordenada de mayor a menor ``nota``, con las
        columnas ``Puesto``, ``cancion``, ``artista``, ``rep``, los cuatro
        indicadores, ``nota`` y los percentiles ``p_<indicador>``.

    Notes
    -----
    Si una canción no aparece en alguno de los rankings de entrada (por
    ejemplo, nunca se puso en bucle), su indicador vale 0.
"""
    
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
    ranking_final.insert(0, "Puesto", range(1, len(ranking_final) + 1))
    return ranking_final
    