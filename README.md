# Mi ranking de Spotify
 
Mi ranking de Spotify es una aplicación que te permite crear distintos rankings a partir de tu historial de escuchas de Spotify.
 
Este proyecto nace en 2025, cuando Spotify, con motivo de su 20.º aniversario, creó un ranking de reproducciones para cada usuario. A raíz de esto me pregunté cuál sería mi canción favorita y si coincidiría con la más reproducida. Pronto vi que no tenía por qué ya que las canciones que conozco desde hace más tiempo han tenido más oportunidades de acumular escuchas, y eso no significa que sean las que más me gustan.
 
Con este problema en mente, solicité mis datos y empecé a crear distintos tipos de rankings para descubrir cuál era mi canción favorita. Después creé esta interfaz para que cualquiera pueda descubrir la suya.
 
## Rankings
 
 - **Ranking enteras**: Muestra un ranking de reproducciones pero solo cuenta una reproducción si la canción se ha escuchado hasta el final.
 - **Ranking elegidas**: Muestra un ranking de reproducciones pero solo cuenta una reproducción si la canción se ha seleccionado haciendo clic en ella. 
 - **Ranking en bucle**: Muestra un ranking de reproducciones pero solo cuenta una reproducción si la canción anterior es exactamente la misma que esa. 
 - **Ranking densidad**: Muestra un ranking de densidad de reproducciones. Calcula las reproducciones que se han dado desde que se conoció la canción hasta la última vez que se escuchó y las divide entre el número de días que hay desde que se conoció la canción hasta la última escucha. Para no beneficiar a las canciones que solo hemos escuchado un par de veces un día, el número de reproducciones mínimas para entrar en el ranking es editable.
 - **Ranking ventana**: Muestra un ranking de reproducciones pero solo cuenta las reproducciones que ocurrieron para un mismo intervalo temporal editable. Solo cuentan las reproducciones que se han dado desde la primera vez que escuchaste la canción hasta el número de meses que digas, así todas las canciones se miden en el mismo intervalo de tiempo. Si pones de intervalo de tiempo 3 meses y la canción la escuchaste por primera vez hace un mes, no aparece en el ranking porque no tenemos suficientes datos de ella.
 - **Ranking definitivo**: Muestra un ranking de notas. Estas notas se calculan según los percentiles de cada ranking anterior y el peso, variable, que se le dé a cada uno. 
 ## Uso
 
Para usarla con tus datos tienes que solicitarlos en la app oficial de Spotify, en la aplicación explico cómo. Si solo quieres investigar la aplicación, puedes descargar un fichero de ejemplo con mis datos de 2025 que encontrarás en la app. 
 
Puedes usar la app de dos formas:
 
- online: https://spotify-ranking-app.streamlit.app/
- local (necesitas Python 3.11 o superior):
```bash
  git clone https://github.com/paumengil/spotify_ranking_app.git
  cd spotify_ranking_app
  python -m venv venv
  venv\Scripts\activate          # Windows. En macOS/Linux: source venv/bin/activate
  pip install -r requirements.txt
  streamlit run app.py
```
 
## Estructura
- **app.py**: contiene el frontend de la aplicación
- **ranking.py**: En este archivo se calculan todos los rankings, datos y métricas necesarios. 
- **ejemplo_2025.JSON**: archivo de ejemplo con mis datos.
- **.streamlit/config.toml**: contiene el estilo que usa la aplicación
- **requirements.txt**: contiene los requisitos necesarios para correr la aplicación en local
## Declaración de uso de IA
Este proyecto se ha hecho por dos motivos: por curiosidad y por querer aprender. Por ello, se ha usado Claude para consultar dudas y entender el funcionamiento de Streamlit. Todo el código ha sido ideado y escrito por mí a excepción de: 
 - Docstrings de las funciones de ranking.py una vez ya creadas las funciones.
 - Aviso de privacidad
