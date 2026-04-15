import plotly.graph_objs as go
import plotly.io as pio
import base64
import cv2
import numpy as np
from typing import List

EMOTIONS = ['anger', 'contempt', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

def build_emotion_html(tracks: List):
    """
    Генерация html файла со статистикой по каждому треку.
    ---
    """
    html_blocks = []

    for track in tracks:
        face_img = track.image
        _, buffer = cv2.imencode('.jpg', face_img)
        img_b64 = base64.b64encode(buffer).decode('utf-8')
        img_tag = f'<img src="data:image/jpeg;base64,{img_b64}" width="128" style="border:1px solid #ccc;">'

        time_stamps = []
        emotion_traces = {emo: [] for emo in EMOTIONS}

        for h in track.history:
            t = h['timestamp']
            probs = h['emotion']['probabilities']
            time_stamps.append(t)
            for emo in EMOTIONS:
                emotion_traces[emo].append(float(probs.get(emo, 0.0)))

        lines = []
        for emo in EMOTIONS:
            lines.append(go.Scatter(
                x=time_stamps,
                y=emotion_traces[emo],
                mode='lines+markers',
                name=emo
            ))

        layout_line = go.Layout(
            title=f"Track {track.id} - Emotion over time",
            xaxis=dict(title="Time (s)"),
            yaxis=dict(title="Probability", range=[0, 1]),
            height=400,
            width=700
        )
        fig_line = go.Figure(data=lines, layout=layout_line)
        line_div = pio.to_html(fig_line, include_plotlyjs=False, full_html=False)

        avg_probs = [np.mean(emotion_traces[emo]) for emo in EMOTIONS]
        fig_pie = go.Figure(
            data=[go.Pie(labels=EMOTIONS, values=avg_probs, hole=0.3)]
        )
        fig_pie.update_layout(title=f"Track {track.id} - Average emotions")
        pie_div = pio.to_html(fig_pie, include_plotlyjs=False, full_html=False)

        block = f"""
        <div style="border:1px solid #999; padding:10px; margin-bottom:20px;">
            <h2>Track {track.id}</h2>
            {img_tag}
            <div>{line_div}</div>
            <div>{pie_div}</div>
        </div>
        """
        html_blocks.append(block)

    full_html = f"""
    <html>
    <head>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <title>Emotion Report</title>
    </head>
    <body>
        <h1>Emotion Recognition Report</h1>
        {''.join(html_blocks)}
    </body>
    </html>
    """
    return full_html
