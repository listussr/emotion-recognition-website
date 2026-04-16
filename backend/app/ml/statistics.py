import base64
from collections import Counter
from typing import List, Dict

import cv2
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio


EMOTIONS = ['anger', 'contempt', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']


EMOTION_COLORS: Dict[str, str] = {
    'anger':    '#ff3b30',
    'contempt': '#af52de',
    'disgust':  '#34c759',
    'fear':     '#a5a500',
    'happy':    '#ffcc00',
    'neutral':  '#8e8e93',
    'sad':      '#007aff',
    'surprise': '#ff9500',
}

EMOTION_LABELS: Dict[str, str] = {
    'anger':    'Гнев',
    'contempt': 'Презрение',
    'disgust':  'Отвращение',
    'fear':     'Страх',
    'happy':    'Радость',
    'neutral':  'Нейтральность',
    'sad':      'Грусть',
    'surprise': 'Удивление',
}


_BASE_LAYOUT = dict(
    template='plotly_white',
    margin=dict(l=48, r=24, t=48, b=40),
    font=dict(family='Inter, -apple-system, Segoe UI, Roboto, sans-serif', size=12, color='#1f2937'),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend=dict(orientation='h', yanchor='bottom', y=-0.28, xanchor='center', x=0.5),
)

_PLOTLY_CONFIG = {'displayModeBar': False, 'responsive': True}


def _encode_face_img(face_img: np.ndarray) -> str:
    """
    Кодирует лицо (BGR) в base64 JPEG для вставки в HTML через data-URI.
    """
    if face_img is None or face_img.size == 0:
        return ''
    ok, buffer = cv2.imencode('.jpg', face_img, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    if not ok:
        return ''
    return base64.b64encode(buffer).decode('utf-8')


def _track_metrics(history: List[dict], emotion_traces: Dict[str, List[float]]) -> Dict[str, object]:
    """
    Сводные показатели трека.
    ---

    Возвращает:
      * duration_sec — длительность присутствия в кадре,
      * dominant — эмоция с максимальной средней вероятностью,
      * dominant_share — какую долю времени эта эмоция была доминирующей,
      * switches — сколько раз доминирующая эмоция менялась.
    """
    if not history:
        return {
            'duration_sec': 0.0,
            'dominant': 'neutral',
            'dominant_share': 0.0,
            'switches': 0,
            'first_ts': 0.0,
            'last_ts': 0.0,
        }

    first_ts = float(history[0]['timestamp'])
    last_ts = float(history[-1]['timestamp'])
    duration = max(0.0, last_ts - first_ts)

    per_frame_dom = [h['emotion'].get('label') or 'neutral' for h in history]
    counts = Counter(per_frame_dom)

    dominant, dom_count = counts.most_common(1)[0]
    dominant_share = dom_count / max(len(per_frame_dom), 1)

    switches = sum(1 for i in range(1, len(per_frame_dom)) if per_frame_dom[i] != per_frame_dom[i - 1])

    return {
        'duration_sec': duration,
        'dominant': dominant,
        'dominant_share': dominant_share,
        'switches': switches,
        'first_ts': first_ts,
        'last_ts': last_ts,
        'per_frame_dom': per_frame_dom,
    }


def _fig_to_div(fig: go.Figure) -> str:
    """Рендер фигуры в HTML-div без повторной инжекции plotly.js."""
    return pio.to_html(fig, include_plotlyjs=False, full_html=False, config=_PLOTLY_CONFIG)


def _build_line_plot(time_stamps: List[float], emotion_traces: Dict[str, List[float]]) -> go.Figure:
    """График вероятностей каждой эмоции во времени."""
    traces = []
    for emo in EMOTIONS:
        traces.append(go.Scatter(
            x=time_stamps,
            y=emotion_traces[emo],
            mode='lines',
            line=dict(color=EMOTION_COLORS[emo], width=2),
            name=emo,
            hovertemplate=f'<b>{emo}</b><br>t=%{{x:.2f}}с<br>p=%{{y:.2f}}<extra></extra>',
        ))
    fig = go.Figure(data=traces)
    fig.update_layout(
        title=dict(text='Вероятности во времени', x=0, font=dict(size=14, color='#111827')),
        xaxis=dict(title='Время, с', gridcolor='#eef0f3'),
        yaxis=dict(title='Вероятность', range=[0, 1], gridcolor='#eef0f3'),
        height=340,
        **_BASE_LAYOUT,
    )
    return fig


def _build_area_plot(time_stamps: List[float], emotion_traces: Dict[str, List[float]]) -> go.Figure:
    """Стек площадей — видно, как «состав» эмоций меняется во времени."""
    traces = []
    for emo in EMOTIONS:
        color = EMOTION_COLORS[emo]
        traces.append(go.Scatter(
            x=time_stamps,
            y=emotion_traces[emo],
            mode='none',
            fill='tonexty',
            stackgroup='one',
            name=emo,
            fillcolor=color,
            line=dict(width=0, color=color),
            hovertemplate=f'<b>{emo}</b><br>t=%{{x:.2f}}с<br>p=%{{y:.2f}}<extra></extra>',
        ))
    fig = go.Figure(data=traces)
    fig.update_layout(
        title=dict(text='Стек площадей', x=0, font=dict(size=14, color='#111827')),
        xaxis=dict(title='Время, с', gridcolor='#eef0f3'),
        yaxis=dict(title='Площадь', range=[0, 1], gridcolor='#eef0f3'),
        height=340,
        **_BASE_LAYOUT,
    )
    return fig


def _build_dominant_bar(per_frame_dom: List[str], duration_sec: float) -> go.Figure:
    """Сколько секунд трек провёл с каждой доминирующей эмоцией."""
    if not per_frame_dom:
        return go.Figure()
    counts = Counter(per_frame_dom)
    frame_share = {emo: counts.get(emo, 0) / len(per_frame_dom) for emo in EMOTIONS}
    seconds = [frame_share[emo] * max(duration_sec, 0.001) for emo in EMOTIONS]

    fig = go.Figure(data=[go.Bar(
        x=EMOTIONS,
        y=seconds,
        marker=dict(color=[EMOTION_COLORS[e] for e in EMOTIONS], line=dict(width=0)),
        text=[f'{s:.1f}с' for s in seconds],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>%{y:.2f} с<extra></extra>',
    )])
    fig.update_layout(
        title=dict(text='Время проявления эмоций', x=0, font=dict(size=14, color='#111827')),
        xaxis=dict(title='', gridcolor='#eef0f3'),
        yaxis=dict(title='Секунд', gridcolor='#eef0f3'),
        height=340,
        showlegend=False,
        **{k: v for k, v in _BASE_LAYOUT.items() if k != 'legend'},
    )
    return fig


def _build_radar(emotion_traces: Dict[str, List[float]]) -> go.Figure:
    """
    Радар (polar) средней вероятности по каждой эмоции.
    ---
    Для 8 осей радар читается лучше, чем pie.
    """
    avg = [float(np.mean(emotion_traces[emo])) if emotion_traces[emo] else 0.0 for emo in EMOTIONS]
    theta = EMOTIONS + [EMOTIONS[0]]
    r = avg + [avg[0]]

    fig = go.Figure(data=[go.Scatterpolar(
        r=r,
        theta=theta,
        fill='toself',
        name='Среднее',
        line=dict(color='#6366f1', width=2),
        fillcolor='rgba(99,102,241,0.22)',
        hovertemplate='<b>%{theta}</b><br>среднее=%{r:.2f}<extra></extra>',
    )])
    fig.update_layout(
        title=dict(text='Средний профиль эмоции', x=0, font=dict(size=14, color='#111827')),
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0, max(0.5, max(avg) * 1.1)], gridcolor='#eef0f3'),
            angularaxis=dict(gridcolor='#eef0f3'),
        ),
        height=340,
        showlegend=False,
        **{k: v for k, v in _BASE_LAYOUT.items() if k != 'legend'},
    )
    return fig


def _metric_tiles(metrics: Dict[str, object]) -> str:
    """Три маленькие «плитки» со сводной статистикой трека."""
    dominant = str(metrics['dominant'])
    dom_color = EMOTION_COLORS.get(dominant, '#111827')
    dom_share_pct = float(metrics['dominant_share']) * 100.0
    duration = float(metrics['duration_sec'])
    switches = int(metrics['switches'])

    return f"""
    <div class="tiles">
      <div class="tile">
        <div class="tile-label">Длительность</div>
        <div class="tile-value">{duration:.2f}<span class="tile-unit">с</span></div>
      </div>
      <div class="tile">
        <div class="tile-label">Доминант</div>
        <div class="tile-value" style="color:{dom_color}">{EMOTION_LABELS.get(dominant, dominant)}</div>
        <div class="tile-sub">{dom_share_pct:.0f}% кадров</div>
      </div>
      <div class="tile">
        <div class="tile-label">Количество смен эмоций</div>
        <div class="tile-value">{switches}</div>
      </div>
    </div>
    """


def _session_summary(tracks: List) -> str:
    """Верхний блок «сводка по всему видео»."""
    n_tracks = len(tracks)
    if n_tracks == 0:
        return '<div class="session-summary"><p class="subtle">Лица не обнаружены.</p></div>'

    total_duration = 0.0
    all_dominants: List[str] = []
    for t in tracks:
        if t.history:
            total_duration = max(total_duration, float(t.history[-1]['timestamp']))
            for h in t.history:
                lbl = h['emotion'].get('label')
                if lbl:
                    all_dominants.append(lbl)

    top_emotion = Counter(all_dominants).most_common(1)[0][0] if all_dominants else 'neutral'
    top_color = EMOTION_COLORS.get(top_emotion, '#111827')

    return f"""
    <div class="session-summary">
      <div class="session-item">
        <div class="session-label">Лиц обнаружено</div>
        <div class="session-value">{n_tracks}</div>
      </div>
      <div class="session-item">
        <div class="session-label">Длительность видео</div>
        <div class="session-value">{total_duration:.2f}<span class="tile-unit">с</span></div>
      </div>
      <div class="session-item">
        <div class="session-label">Самая частая эмоция</div>
        <div class="session-value" style="color:{top_color}">{EMOTION_LABELS.get(top_emotion, top_emotion)}</div>
      </div>
    </div>
    """


def _build_track_block(track) -> str:
    """HTML-блок одного трека: фото + сводка + 2x2 сетка графиков."""
    img_b64 = _encode_face_img(track.image)
    img_tag = (
        f'<img src="data:image/jpeg;base64,{img_b64}" alt="лицо {track.id}" class="face-photo" />'
        if img_b64 else '<div class="face-photo face-photo-empty">нет изображения</div>'
    )

    time_stamps: List[float] = []
    emotion_traces: Dict[str, List[float]] = {emo: [] for emo in EMOTIONS}
    for h in track.history:
        time_stamps.append(float(h['timestamp']))
        probs = h['emotion'].get('probabilities', {})
        for emo in EMOTIONS:
            emotion_traces[emo].append(float(probs.get(emo, 0.0)))

    metrics = _track_metrics(track.history, emotion_traces)
    per_frame_dom = metrics.get('per_frame_dom') or []

    line_div = _fig_to_div(_build_line_plot(time_stamps, emotion_traces))
    area_div = _fig_to_div(_build_area_plot(time_stamps, emotion_traces))
    bar_div = _fig_to_div(_build_dominant_bar(per_frame_dom, float(metrics['duration_sec'])))
    radar_div = _fig_to_div(_build_radar(emotion_traces))

    return f"""
    <section class="track-card">
      <header class="track-head">
        <div class="track-ident">
          {img_tag}
          <div class="track-title">
            <div class="track-id">Лицо №{track.id}</div>
            <div class="track-sub">записано кадров: {len(track.history)}</div>
          </div>
        </div>
        {_metric_tiles(metrics)}
      </header>
      <div class="plot-grid">
        <div class="plot-cell">{line_div}</div>
        <div class="plot-cell">{area_div}</div>
        <div class="plot-cell">{bar_div}</div>
        <div class="plot-cell">{radar_div}</div>
      </div>
    </section>
    """


_CSS = """
:root {
  --bg: #f5f6f8;
  --card: #ffffff;
  --text: #111827;
  --text-sub: #6b7280;
  --border: #e5e7eb;
  --accent: #6366f1;
  --shadow: 0 1px 2px rgba(17, 24, 39, 0.04), 0 4px 12px rgba(17, 24, 39, 0.06);
}
* { box-sizing: border-box; }
html, body {
  margin: 0; padding: 0;
  background: var(--bg); color: var(--text);
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 14px; line-height: 1.5;
}
.page {
  max-width: 1240px; margin: 0 auto; padding: 32px 24px 64px;
}
.page-header {
  display: flex; align-items: baseline; justify-content: space-between; gap: 16px;
  margin-bottom: 24px;
}
.page-title { font-size: 28px; font-weight: 700; letter-spacing: -0.01em; margin: 0; }
.page-subtitle { color: var(--text-sub); font-size: 13px; margin: 0; }
.session-summary {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;
  background: var(--card); border: 1px solid var(--border); border-radius: 14px;
  padding: 20px 24px; box-shadow: var(--shadow); margin-bottom: 28px;
}
.session-item { display: flex; flex-direction: column; gap: 4px; }
.session-label { color: var(--text-sub); font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; }
.session-value { font-size: 22px; font-weight: 600; color: var(--text); }
.session-value .tile-unit { font-size: 14px; color: var(--text-sub); margin-left: 2px; font-weight: 500; }
.track-card {
  background: var(--card); border: 1px solid var(--border); border-radius: 16px;
  box-shadow: var(--shadow); padding: 24px; margin-bottom: 24px;
}
.track-head {
  display: grid; grid-template-columns: minmax(260px, 0.9fr) 2fr; gap: 24px; align-items: center;
  padding-bottom: 20px; margin-bottom: 20px; border-bottom: 1px solid var(--border);
}
.track-ident { display: flex; align-items: center; gap: 16px; }
.face-photo {
  width: 96px; height: 96px; object-fit: cover;
  border-radius: 14px; border: 1px solid var(--border);
  box-shadow: var(--shadow);
}
.face-photo-empty {
  display: flex; align-items: center; justify-content: center;
  color: var(--text-sub); font-size: 12px; background: var(--bg);
}
.track-title .track-id { font-size: 20px; font-weight: 700; letter-spacing: -0.01em; }
.track-title .track-sub { color: var(--text-sub); font-size: 12px; }
.tiles { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.tile {
  background: var(--bg); border: 1px solid var(--border); border-radius: 12px;
  padding: 12px 14px;
}
.tile-label { color: var(--text-sub); font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; }
.tile-value { font-size: 18px; font-weight: 600; margin-top: 2px; }
.tile-value .tile-unit { font-size: 12px; color: var(--text-sub); margin-left: 2px; font-weight: 500; }
.tile-sub { color: var(--text-sub); font-size: 12px; margin-top: 2px; }
.plot-grid {
  display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px;
}
.plot-cell {
  background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 8px 6px 4px;
}
.subtle { color: var(--text-sub); }
@media (max-width: 920px) {
  .track-head { grid-template-columns: 1fr; }
  .plot-grid { grid-template-columns: 1fr; }
  .session-summary { grid-template-columns: 1fr; }
  .tiles { grid-template-columns: 1fr 1fr; }
}
"""


def build_emotion_html(tracks: List) -> str:
    """
    Генерация HTML-отчёта со статистикой по каждому треку.
    ---

    Возвращает единый HTML-документ (самодостаточный, без внешних CSS): встроены
    стили, Plotly-скрипт подгружается из CDN один раз на весь отчёт.

    На каждый трек рендерятся 4 графика: линейный, стек-площади, bar (время как
    доминирующая эмоция) и polar-radar (средний профиль). Во всех графиках
    используется единая цветовая палитра, чтобы эмоции узнавались с первого взгляда.
    """
    blocks = [_build_track_block(t) for t in tracks]
    body = ''.join(blocks) if blocks else '<p class="subtle">Нет треков для отображения.</p>'

    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Отчёт о распознавании эмоций</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>{_CSS}</style>
</head>
<body>
<div class="page">
  <div class="page-header">
    <div>
      <h1 class="page-title">Отчёт о распознавании эмоций</h1>
      <p class="page-subtitle">Подробная статистика по каждому лицу: динамика во времени, композиция, распределение и средний профиль.</p>
    </div>
  </div>
  {_session_summary(tracks)}
  {body}
</div>
</body>
</html>
"""
