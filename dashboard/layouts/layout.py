from dash import html, dcc

# Cabecera del Dashboard
header = html.Div(
    className="dashboard-header",
    children=[
        html.Div(
            className="header-brand",
            children=[
                html.I(className="fa-solid fa-city header-icon"),
                html.Div(
                    children=[
                        html.H1("SISTEMA DE MONITOREO URBANO", className="header-title"),
                        html.P("Movilidad Urbana, Calidad del Aire y Clima en Tiempo Real", className="header-subtitle")
                    ]
                )
            ]
        ),
        html.Div(
            className="header-status",
            children=[
                html.Div(className="status-indicator-pulse"),
                html.Span("SANTIAGO — EN VIVO", className="status-text")
            ]
        )
    ]
)

# Barra de Filtros
filter_bar = html.Div(
    className="filter-bar",
    children=[
        html.Div(
            className="filter-group",
            children=[
                html.Label("Zona Urbana", className="filter-label"),
                dcc.Dropdown(
                    id="zone-dropdown",
                    options=[
                        {"label": "Todas las Zonas", "value": "Todas"},
                        {"label": "Centro", "value": "Centro"},
                        {"label": "Norte", "value": "Norte"},
                        {"label": "Sur", "value": "Sur"}
                    ],
                    value="Todas",
                    clearable=False,
                    searchable=False,
                    className="custom-dropdown"
                )
            ]
        ),
        html.Div(
            className="filter-group",
            children=[
                html.Label("Rango de Tiempo", className="filter-label"),
                dcc.Dropdown(
                    id="time-dropdown",
                    options=[
                        {"label": "Últimos 5 Minutos", "value": "5m"},
                        {"label": "Última 1 Hora", "value": "1h"},
                        {"label": "Últimas 24 Horas", "value": "24h"}
                    ],
                    value="24h",
                    clearable=False,
                    searchable=False,
                    className="custom-dropdown"
                )
            ]
        ),
        html.Div(
            className="filter-group metric-selector-group",
            children=[
                html.Label("Enfoque de Métrica", className="filter-label"),
                dcc.Tabs(
                    id="metric-tabs",
                    value="todos",
                    children=[
                        dcc.Tab(label="General", value="todos", className="custom-tab", selected_className="custom-tab--selected"),
                        dcc.Tab(label="Tráfico", value="trafico", className="custom-tab", selected_className="custom-tab--selected"),
                        dcc.Tab(label="Aire", value="aire", className="custom-tab", selected_className="custom-tab--selected"),
                        dcc.Tab(label="Clima", value="clima", className="custom-tab", selected_className="custom-tab--selected")
                    ],
                    className="custom-tabs"
                )
            ]
        )
    ]
)

# Cuadrícula de KPIs
kpi_section = html.Div(
    id="kpi-grid",
    className="kpi-grid",
    children=[
        # Tarjeta 1: Temperatura
        html.Div(
            id="kpi-temp-card",
            className="kpi-card clima-card",
            children=[
                html.Div(
                    className="kpi-icon-container",
                    children=[html.I(className="fa-solid fa-temperature-half")]
                ),
                html.Div(
                    className="kpi-content",
                    children=[
                        html.P("Temperatura", className="kpi-title"),
                        html.H3("...", id="kpi-temp-value", className="kpi-value"),
                        html.P("Clima Global (Santiago)", className="kpi-helper")
                    ]
                )
            ]
        ),
        # Tarjeta 2: Humedad
        html.Div(
            id="kpi-humidity-card",
            className="kpi-card clima-card",
            children=[
                html.Div(
                    className="kpi-icon-container",
                    children=[html.I(className="fa-solid fa-droplet")]
                ),
                html.Div(
                    className="kpi-content",
                    children=[
                        html.P("Humedad", className="kpi-title"),
                        html.H3("...", id="kpi-humidity-value", className="kpi-value"),
                        html.P("Humedad relativa actual", className="kpi-helper")
                    ]
                )
            ]
        ),
        # Tarjeta 3: Viento
        html.Div(
            id="kpi-wind-card",
            className="kpi-card clima-card",
            children=[
                html.Div(
                    className="kpi-icon-container",
                    children=[html.I(className="fa-solid fa-wind")]
                ),
                html.Div(
                    className="kpi-content",
                    children=[
                        html.P("Viento", className="kpi-title"),
                        html.H3("...", id="kpi-wind-value", className="kpi-value"),
                        html.P("Velocidad del viento", className="kpi-helper")
                    ]
                )
            ]
        ),
        # Tarjeta 4: Tráfico (vehículos)
        html.Div(
            id="kpi-traffic-card",
            className="kpi-card trafico-card",
            children=[
                html.Div(
                    className="kpi-icon-container",
                    children=[html.I(className="fa-solid fa-car")]
                ),
                html.Div(
                    className="kpi-content",
                    children=[
                        html.P("Tránsito Vehicular", className="kpi-title"),
                        html.H3("...", id="kpi-traffic-value", className="kpi-value"),
                        html.P("Carga de vehículos actual", id="kpi-traffic-helper", className="kpi-helper")
                    ]
                )
            ]
        ),
        # Tarjeta 5: Calidad del aire
        html.Div(
            id="kpi-aqi-card",
            className="kpi-card aire-card",
            children=[
                html.Div(
                    className="kpi-icon-container",
                    children=[html.I(className="fa-solid fa-lungs")]
                ),
                html.Div(
                    className="kpi-content",
                    children=[
                        html.P("Calidad del Aire (AQI)", className="kpi-title"),
                        html.H3("...", id="kpi-aqi-value", className="kpi-value"),
                        html.P("Índice de calidad e impacto", id="kpi-aqi-helper", className="kpi-helper")
                    ]
                )
            ]
        )
    ]
)

# Consola de Alertas Inteligentes
alerts_section = html.Div(
    className="alerts-section",
    children=[
        html.Div(
            className="alerts-card",
            children=[
                html.Div(
                    className="alerts-card-header",
                    children=[
                        html.I(className="fa-solid fa-triangle-exclamation alerts-header-icon"),
                        html.H2("CONSOLA DE ALERTAS INTELIGENTES Y RECOMENDACIONES", className="alerts-title")
                    ]
                ),
                html.Div(
                    id="alerts-list",
                    className="alerts-list",
                    children=[
                        html.Div("Inicializando alertas y análisis correlativo...", className="alert-placeholder-text")
                    ]
                )
            ]
        )
    ]
)

# Cuadrícula de Gráficos
charts_section = html.Div(
    className="charts-grid",
    children=[
        # Gráfico 1: Tráfico
        html.Div(
            id="traffic-graph-container",
            className="chart-card",
            children=[
                html.Div(
                    className="chart-card-header",
                    children=[
                        html.I(className="fa-solid fa-chart-line chart-icon"),
                        html.H3("Historial de Tránsito Vehicular (Vehículos vs Tiempo)", className="chart-title")
                    ]
                ),
                dcc.Graph(
                    id="traffic-graph",
                    config={"displayModeBar": False},
                    className="plotly-graph"
                )
            ]
        ),
        # Gráfico 2: Dispersión PM2.5 vs Vehículos
        html.Div(
            id="pollution-graph-container",
            className="chart-card",
            children=[
                html.Div(
                    className="chart-card-header",
                    children=[
                        html.I(className="fa-solid fa-chart-scatter chart-icon"),
                        html.H3("Correlación: Contaminación PM2.5 vs. Cantidad de Vehículos", className="chart-title")
                    ]
                ),
                dcc.Graph(
                    id="pollution-graph",
                    config={"displayModeBar": False},
                    className="plotly-graph"
                )
            ]
        ),
        # Gráfico 3: Clima vs Tráfico
        html.Div(
            id="temp-traffic-graph-container",
            className="chart-card",
            children=[
                html.Div(
                    className="chart-card-header",
                    children=[
                        html.I(className="fa-solid fa-chart-bar chart-icon"),
                        html.H3("Comparativo: Temperatura vs. Carga de Tráfico", className="chart-title")
                    ]
                ),
                dcc.Graph(
                    id="temp-traffic-graph",
                    config={"displayModeBar": False},
                    className="plotly-graph"
                )
            ]
        )
    ]
)

# Contenedor principal unificado
main_layout = html.Div(
    className="dashboard-container",
    children=[
        header,
        filter_bar,
        kpi_section,
        alerts_section,
        charts_section,
        # Intervalo para actualizar cada 10 segundos
        dcc.Interval(
            id="refresh-interval",
            interval=10000,  # 10 segundos
            n_intervals=0
        )
    ]
)
