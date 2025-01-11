import plotly.graph_objects as go

def create_gauge(value, min_val, max_val, threshold_1, threshold_2, colors):
    """
    Erstellt eine Gauge mit benutzerdefinierten Farben.

    Parameters:
        value (float): Der aktuelle Wert.
        min_val (float): Der minimale Wert.
        max_val (float): Der maximale Wert.
        threshold_1 (float): Schwellenwert für den ersten Bereich.
        threshold_2 (float): Schwellenwert für den zweiten Bereich.
        colors (list): Liste von 4 Farben [Bereich 1, Bereich 2, Bereich 3, Balkenfarbe].

    Returns:
        go.Figure: Die Gauge-Plotly-Figur.
    """
    gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': 'PnL (%)'},
        delta={'reference': 0},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': colors[3]},  # Balkenfarbe
            'steps': [
                {'range': [min_val, threshold_1], 'color': colors[0]},  # Bereich 1
                {'range': [threshold_1, threshold_2], 'color': colors[1]},  # Bereich 2
                {'range': [threshold_2, max_val], 'color': colors[2]},  # Bereich 3
            ],
        },
    ))
    return gauge