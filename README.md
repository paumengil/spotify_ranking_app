# Mi ranking de Spotify
Mi ranking de Spotify es una aplicación que te permite crear distintos rankings con los datos proporcionados por el historial de escuchas de Spotify. 

Este proyecto nace debido a que en 2025 por el 20 aniversario Spotify crea un ranking de reproducciones para cada usuario. A raiz de esto pensé en cuál sería mi canción favorita  y si sería la de más reproducciones. Sin embargo descarté la idea debido a que, de ser así, las canciones que conozco de hace más tiempo tienen mayor posibilidad de acumular más escuchas y no por ello ser la que más me gustan. 

Con este problema en mente solicité mis datos y empecé a crear distintos tipos de rankings para ver cuál sería mi canción favorita y cree esta interfaz para que todo el mundo pueda saber cuál es la suya.

## Rankings
 
 - ** Ranking enteras**: Muestra un ranking de reproducciones pero solo cuenta una reproducción si la canción se ha escuchado hasta el final
 - ** Ranking elegidas ** :  Muestra un ranking de reproducciones pero solo cuenta una reproducción si la canción se ha seleccionado haciendo click en ella. 
 - ** Ranking en bucle **: Muestra un ranking de reproducciones pero solo cuenta una reproducción si la canción anterior es exactamente la misma que esa. 
 - ** Ranking densidad **: Muestra un ranking de densidad de reproducciones. calcula las reproducciones que se han dado desde que se conoció la canción hasta la última vez que se escuchó y las divide entre el número de días que hay desde que se conoció la canción hasta la última escuchado. Para no beneficiar a las canciones que solo hemos escuchado un par de veces un día, el número de reproducciones mínimas para entrar en el ranking es editable.
 - ** Ranking ventana **: Muestra un ranking de reproducciones pero solo cuenta las reproducciones que ocurrieron para un mismo intervalo temporal editable. Solo cuentan las reproducciones que se han dado desde la primera vez que escuchaste la canción hasta el número de meses que digas, así todas las canciones se miden en el mismo intervalo de tiempo. Si pones de intervalo de tiempo 3 meses y la canción la escuchaste por primera vez hace un mes, no aparece en el ranking porque no tenemos suficientes datos de ella.
 - ** Ranking definitivo **: Muestra un ranking de notas. Estas notas se calculan según los percentiles de cada ranking anterior y el peso, variable, que se le de a cada uno. 

 ## Uso

Para usarla con tus datos tienes que solicitarlos en la app oficial de Spotify, en la aplicación explico como. Si solo quieres investigar la aplicación, pueds descargar un fichero de ejemplo con mis datos de 2025 que encontrarás en la app. 

Puedes usar la app de dos formas:

    - online : https://spotify-ranking-app.streamlit.app/
    - local : 
        1. Clonar repositorio 
        2. Hacer pip install - r requirements.txt
        3. Ejecutar: streamlit run app.py

## Estructura
- ** app.py ** : contiene el frontend de la aplicación
- ** ranking.py** : En esta función se calculan todos los rankings, datos y métricas necesarios. 
- ** ejemplo_2025.JSON ** : archivo de ejemplo con mis datos.
- ** .streamlit/congi.toml ** : contiene el estilo que usa la aplicación
- **requirements.txt** : contiene los requisitios necesarios para correr la aplicación en local

## Declaración de uso de IA
Este proyecto se ha hecho por dos motivos: por curiosidad y por querer aprender. Por ello, se ha usado claude para consultar dudas y entender el funcionamiento de streamlit. Todo el código ha sido idea y escrito por mi a excepción de: 
    - Docstrings de las funciones de ranking.py una vez ya creadas las funciones.
    -  Aviso de privadicad

    