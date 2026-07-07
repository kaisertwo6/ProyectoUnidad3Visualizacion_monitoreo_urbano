import os
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash import html
import logging

logger = logging.getLogger("monitoreo")

# Determinar URL del Backend
# Si corre dentro de Docker Compose se comunica por la red interna: http://backend:8000
# Si corre de forma local se comunica por localhost: http://localhost:8000
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

def register_callbacks(app):
    
    # --- HELPER: Aplicar Estilo Oscuro Premium a los Gráficos ---
    def aplicar_tema_oscuro(fig, titulo, x_title="", y_title=""):
        fig.update_layout(
            title={
                'text': titulo,
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 15, 'color': '#ffffff', 'family': 'Outfit, sans-serif'}
            },
            font=dict(family="Inter, sans-serif", color="#d1d5db"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title=x_title,
                gridcolor="rgba(255, 255, 255, 0.05)",
                zerolinecolor="rgba(255, 255, 255, 0.1)",
                tickfont=dict(color="#9ca3af"),
                titlefont=dict(color="#9ca3af")
            ),
            yaxis=dict(
                title=y_title,
                gridcolor="rgba(255, 255, 255, 0.05)",
                zerolinecolor="rgba(255, 255, 255, 0.1)",
                tickfont=dict(color="#9ca3af"),
                titlefont=dict(color="#9ca3af")
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(255, 255, 255, 0.05)"
            ),
            margin=dict(l=50, r=50, t=55, b=50),
            hovermode="closest"
        )
        return fig

    # --- HELPER: Crear Gráfico de Error/Vacio ---
    def crear_grafico_vacio(mensaje):
        fig = go.Figure()
        fig.update_layout(
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[{
                "text": mensaje,
                "font": {"size": 14, "color": "#9ca3af", "family": "Inter, sans-serif"},
                "showarrow": False,
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 0.5
            }],
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10)
        )
        return fig

    # --- HELPER: Crear Tarjeta de Alerta ---
    def generar_div_alerta(nivel, titulo, mensaje):
        icon_map = {
            "CRITICA": "fa-circle-xmark text-danger",
            "ADVERTENCIA": "fa-triangle-exclamation text-warning",
            "PRECAUCION": "fa-circle-exclamation text-info",
            "NORMAL": "fa-circle-check text-success"
        }
        class_map = {
            "CRITICA": "alert-item alert-critica",
            "ADVERTENCIA": "alert-item alert-advertencia",
            "PRECAUCION": "alert-item alert-precaucion",
            "NORMAL": "alert-item alert-normal"
        }
        icon_class = icon_map.get(nivel, "fa-bell")
        div_class = class_map.get(nivel, "alert-item")
        
        return html.Div(
            className=div_class,
            children=[
                html.I(className=f"fa-solid {icon_class} alert-item-icon"),
                html.Div(
                    className="alert-item-content",
                    children=[
                        html.Strong(f"{titulo}: ", className="alert-item-title"),
                        html.Span(mensaje, className="alert-item-message")
                    ]
                )
            ]
        )

    # ==========================================
    # CALLBACK 1: VISIBILIDAD DYNAMIC TABS
    # ==========================================
    @app.callback(
        [
            Output("kpi-temp-card", "style"),
            Output("kpi-humidity-card", "style"),
            Output("kpi-wind-card", "style"),
            Output("kpi-traffic-card", "style"),
            Output("kpi-aqi-card", "style"),
            Output("traffic-graph-container", "style"),
            Output("pollution-graph-container", "style"),
            Output("temp-traffic-graph-container", "style")
        ],
        [Input("metric-tabs", "value")]
    )
    def filtrar_visibilidad_metricas(tab_seleccionado):
        show_flex = {"display": "flex"}
        show_block = {"display": "block"}
        hide = {"display": "none"}
        
        if tab_seleccionado == "todos":
            return show_flex, show_flex, show_flex, show_flex, show_flex, show_block, show_block, show_block
        elif tab_seleccionado == "trafico":
            return hide, hide, hide, show_flex, hide, show_block, show_block, show_block
        elif tab_seleccionado == "aire":
            return hide, hide, hide, hide, show_flex, hide, show_block, hide
        elif tab_seleccionado == "clima":
            return show_flex, show_flex, show_flex, hide, hide, hide, hide, show_block
        
        return show_flex, show_flex, show_flex, show_flex, show_flex, show_block, show_block, show_block


    # ==========================================
    # CALLBACK 2: ACTUALIZACIÓN DE KPIS Y ALERTAS
    # ==========================================
    @app.callback(
        [
            Output("kpi-temp-value", "children"),
            Output("kpi-humidity-value", "children"),
            Output("kpi-wind-value", "children"),
            Output("kpi-traffic-value", "children"),
            Output("kpi-traffic-helper", "children"),
            Output("kpi-aqi-value", "children"),
            Output("kpi-aqi-helper", "children"),
            Output("alerts-list", "children")
        ],
        [
            Input("refresh-interval", "n_intervals"),
            Input("zone-dropdown", "value")
        ]
    )
    def actualizar_kpis_y_alertas(n, zona_seleccionada):
        url = f"{BACKEND_URL}/api/monitoreo/actual"
        alertas = []
        
        try:
            logger.info(f"Petición API para KPIs en {url}")
            response = requests.get(url, timeout=3)
            
            if response.status_code != 200:
                raise Exception(f"Código de respuesta HTTP {response.status_code}")
            
            data = response.json()
            
            # --- 1. Clima (Global) ---
            clima = data.get("clima", {})
            temp = f"{clima.get('temperatura', 0.0):.1f} °C"
            humedad = f"{clima.get('humedad', 0.0):.0f}%"
            viento = f"{clima.get('viento', 0.0):.1f} km/h"
            
            # --- 2. Tráfico (Dependiente de Zona) ---
            trafico_data = data.get("trafico", {})
            
            if zona_seleccionada == "Todas":
                total_vehiculos = sum(z.get("vehiculos", 0) for z in trafico_data.values())
                conteo_zonas = len(trafico_data)
                avg_vel = sum(z.get("velocidad_promedio", 0.0) for z in trafico_data.values()) / (conteo_zonas if conteo_zonas > 0 else 1)
                
                vehiculos_val = f"{total_vehiculos} veh"
                vehiculos_helper = f"Total Santiago — Vel. Promedio: {avg_vel:.1f} km/h"
            else:
                zona_t = trafico_data.get(zona_seleccionada, {})
                vehiculos_val = f"{zona_t.get('vehiculos', 0)} veh"
                vel = zona_t.get('velocidad_promedio', 0.0)
                cong = zona_t.get('congestion_level', 'bajo').upper()
                vehiculos_helper = f"Vel. Promedio: {vel:.1f} km/h — {cong}"
            
            # --- 3. Calidad del Aire (Dependiente de Zona) ---
            aire_data = data.get("calidad_aire", {})
            
            if zona_seleccionada == "Todas":
                conteo_zonas = len(aire_data)
                avg_aqi = sum(z.get("aqi", 0.0) for z in aire_data.values()) / (conteo_zonas if conteo_zonas > 0 else 1)
                avg_pm25 = sum(z.get("pm25", 0.0) for z in aire_data.values()) / (conteo_zonas if conteo_zonas > 0 else 1)
                
                aqi_val = f"{avg_aqi:.1f}"
                aqi_helper = f"Promedio ciudad — PM2.5: {avg_pm25:.1f} µg/m³"
            else:
                zona_a = aire_data.get(zona_seleccionada, {})
                aqi = zona_a.get('aqi', 0.0)
                pm25 = zona_a.get('pm25', 0.0)
                
                # Clasificación de calidad local
                estado = "Bueno"
                if aqi > 50:
                    estado = "Crítico"
                elif aqi > 30:
                    estado = "Regular"
                    
                aqi_val = f"{aqi:.1f}"
                aqi_helper = f"PM2.5: {pm25:.1f} µg/m³ — {estado}"

            # --- 4. Evaluación de Alertas Inteligentes ---
            humedad_raw = clima.get('humedad', 0.0)
            viento_raw = clima.get('viento', 0.0)
            
            # Lógica para Niebla + Congestión
            if zona_seleccionada == "Todas":
                zonas_peligrosas = [z for z, val in trafico_data.items() if val.get("vehiculos", 0) >= 280]
                if humedad_raw > 80.0 and len(zonas_peligrosas) > 0:
                    alertas.append(generar_div_alerta(
                        "CRITICA", 
                        "RIESGO DE COLISIÓN POR NIEBLA", 
                        f"Humedad del {humedad_raw:.1f}% y tráfico pesado en {', '.join(zonas_peligrosas)}. Reduzca la velocidad."
                    ))
            else:
                veh_zona = trafico_data.get(zona_seleccionada, {}).get("vehiculos", 0)
                if humedad_raw > 80.0 and veh_zona >= 280:
                    alertas.append(generar_div_alerta(
                        "CRITICA", 
                        "RIESGO DE COLISIÓN POR NIEBLA", 
                        f"Visibilidad reducida (humedad {humedad_raw:.1f}%) y tránsito denso ({veh_zona} veh) en la zona. Precaución extrema."
                    ))
                    
            # Lógica para Restricción Vehicular Ambiental
            if zona_seleccionada == "Todas":
                zonas_criticas = [z for z, val in aire_data.items() if val.get("aqi", 0.0) >= 45.0]
                if len(zonas_criticas) > 0:
                    alertas.append(generar_div_alerta(
                        "ADVERTENCIA", 
                        "ALERTA AMBIENTAL - RESTRICCIÓN SUGERIDA", 
                        f"Nivel de AQI crítico detectado en {', '.join(zonas_criticas)}. Se sugiere restringir circulación a no catalíticos."
                    ))
            else:
                aqi_zona = aire_data.get(zona_seleccionada, {}).get("aqi", 0.0)
                if aqi_zona >= 45.0:
                    alertas.append(generar_div_alerta(
                        "ADVERTENCIA", 
                        "ALERTA AMBIENTAL - RESTRICCIÓN SUGERIDA", 
                        f"AQI de {aqi_zona:.1f} en la zona {zona_seleccionada} supera umbral saludable. Evite deportes al aire libre."
                    ))
                    
            # Lógica para Viento Fuerte
            if viento_raw > 25.0:
                alertas.append(generar_div_alerta(
                    "PRECAUCION", 
                    "VIENTOS FUERTES DETECTADOS", 
                    f"Vientos continuos de {viento_raw:.1f} km/h en la ciudad. Posible desprendimiento de ramas, maneje con cuidado."
                ))
                
            # Si no hay alertas acumuladas
            if not alertas:
                alertas.append(generar_div_alerta(
                    "NORMAL", 
                    "CONDICIONES ÓPTIMAS", 
                    "No se registran situaciones viales ni ambientales críticas en este momento."
                ))
                
            return temp, humedad, viento, vehiculos_val, vehiculos_helper, aqi_val, aqi_helper, alertas
            
        except Exception as e:
            logger.error(f"Error consultando estado actual: {e}")
            # Fallback en caso de desconexión
            alertas_fallo = [generar_div_alerta(
                "CRITICA", 
                "SERVICIO DE DATOS DESCONECTADO", 
                "No se pudo establecer comunicación con el Backend. Verifique que los contenedores estén levantados."
            )]
            return "--", "--", "--", "--", "API no disponible", "--", "API no disponible", alertas_fallo


    # ==========================================
    # CALLBACK 3: ACTUALIZACIÓN DE GRÁFICOS
    # ==========================================
    @app.callback(
        [
            Output("traffic-graph", "figure"),
            Output("pollution-graph", "figure"),
            Output("temp-traffic-graph", "figure")
        ],
        [
            Input("refresh-interval", "n_intervals"),
            Input("zone-dropdown", "value"),
            Input("time-dropdown", "value")
        ]
    )
    def actualizar_graficos(n, zona_seleccionada, rango_tiempo):
        # Generar URLs correspondientes
        query_params = f"?rango={rango_tiempo}"
        if zona_seleccionada != "Todas":
            query_params += f"&zona={zona_seleccionada}"
            
        url_trafico = f"{BACKEND_URL}/api/monitoreo/historico/trafico{query_params}"
        url_aire = f"{BACKEND_URL}/api/monitoreo/historico/calidad-aire{query_params}"
        url_clima = f"{BACKEND_URL}/api/monitoreo/historico/clima?rango={rango_tiempo}" # Clima no usa filtro de zona
        
        try:
            logger.info(f"Peticiones históricas: {url_trafico} | {url_aire} | {url_clima}")
            
            # Realizar peticiones
            resp_trafico = requests.get(url_trafico, timeout=4)
            resp_aire = requests.get(url_aire, timeout=4)
            resp_clima = requests.get(url_clima, timeout=4)
            
            if resp_trafico.status_code != 200 or resp_aire.status_code != 200 or resp_clima.status_code != 200:
                raise Exception("Alguna de las peticiones históricas falló.")
                
            data_trafico = resp_trafico.json()
            data_aire = resp_aire.json()
            data_clima = resp_clima.json()
            
            if not data_trafico or not data_aire or not data_clima:
                mensaje_vacio = "Esperando que el ingest cargue datos en la base de datos..."
                return crear_grafico_vacio(mensaje_vacio), crear_grafico_vacio(mensaje_vacio), crear_grafico_vacio(mensaje_vacio)
                
            # Convertir a DataFrames de Pandas
            df_trafico = pd.DataFrame(data_trafico)
            df_aire = pd.DataFrame(data_aire)
            df_clima = pd.DataFrame(data_clima)
            
            df_trafico['timestamp'] = pd.to_datetime(df_trafico['timestamp'])
            df_aire['timestamp'] = pd.to_datetime(df_aire['timestamp'])
            df_clima['timestamp'] = pd.to_datetime(df_clima['timestamp'])
            
            # ----------------------------------------------------
            # GRÁFICO 1: Historial de Tránsito (Línea Temporal)
            # ----------------------------------------------------
            if zona_seleccionada == "Todas":
                # Graficar una línea por cada zona para comparación
                fig1 = px.line(
                    df_trafico,
                    x="timestamp",
                    y="vehiculos",
                    color="zona",
                    color_discrete_map={"Centro": "#FF5252", "Norte": "#4CAF50", "Sur": "#2196F3"},
                    labels={"timestamp": "Hora de Registro", "vehiculos": "Cantidad de Vehículos", "zona": "Zona"},
                    markers=True
                )
            else:
                # Filtrado o ya viene filtrado de la API
                fig1 = px.line(
                    df_trafico,
                    x="timestamp",
                    y="vehiculos",
                    color_discrete_sequence=["#FF9F43"],
                    labels={"timestamp": "Hora de Registro", "vehiculos": "Vehículos"},
                    markers=True
                )
                
            fig1.update_traces(line=dict(width=2.5), marker=dict(size=5))
            fig1 = aplicar_tema_oscuro(fig1, "Carga Vehicular en el Tiempo", "", "Número de Vehículos")
            
            # ----------------------------------------------------
            # GRÁFICO 2: Correlación PM2.5 vs Vehículos (Dispersión)
            # ----------------------------------------------------
            # Unir tráfico y calidad de aire en base a timestamp y zona
            df_merged = pd.merge(df_trafico, df_aire, on=["timestamp", "zona"])
            
            if df_merged.empty:
                fig2 = crear_grafico_vacio("No hay datos coincidentes para la correlación.")
            else:
                if zona_seleccionada == "Todas":
                    fig2 = px.scatter(
                        df_merged,
                        x="vehiculos",
                        y="pm25",
                        color="zona",
                        color_discrete_map={"Centro": "#FF5252", "Norte": "#4CAF50", "Sur": "#2196F3"},
                        labels={"vehiculos": "Vehículos registrados", "pm25": "Material Particulado PM2.5 (µg/m³)", "zona": "Zona"}
                    )
                else:
                    fig2 = px.scatter(
                        df_merged,
                        x="vehiculos",
                        y="pm25",
                        color_discrete_sequence=["#00D2C4"],
                        labels={"vehiculos": "Vehículos registrados", "pm25": "PM2.5 (µg/m³)"}
                    )
                fig2.update_traces(marker=dict(size=10, opacity=0.75, line=dict(width=1, color="rgba(255,255,255,0.15)")))
                fig2 = aplicar_tema_oscuro(fig2, "Correlación: Impacto del Tránsito en la Polución (PM2.5)", "Cantidad de Vehículos", "PM2.5 (µg/m³)")
            
            # ----------------------------------------------------
            # GRÁFICO 3: Temperatura vs Cantidad de Vehículos
            # ----------------------------------------------------
            # Unir tráfico y clima en base a timestamp
            df_merged_clima = pd.merge(df_trafico, df_clima, on="timestamp")
            
            if df_merged_clima.empty:
                fig3 = crear_grafico_vacio("No hay datos para comparar clima y tránsito.")
            else:
                # Agrupar clima por timestamp para evitar duplicar por zonas si es "Todas"
                if zona_seleccionada == "Todas":
                    df_grouped = df_merged_clima.groupby("timestamp").agg({
                        "vehiculos": "sum",
                        "temperatura": "first"
                    }).reset_index()
                else:
                    df_grouped = df_merged_clima
                
                # Ordenar cronológicamente
                df_grouped = df_grouped.sort_values("timestamp")
                
                # Crear gráfico con doble eje Y usando graph_objects
                fig3 = go.Figure()
                
                # Añadir vehículos en eje Y izquierdo
                fig3.add_trace(go.Scatter(
                    x=df_grouped['timestamp'],
                    y=df_grouped['vehiculos'],
                    name="Vehículos",
                    mode="lines+markers",
                    line=dict(color="#FF9F43", width=2.5),
                    marker=dict(size=5),
                    yaxis="y1"
                ))
                
                # Añadir temperatura en eje Y derecho
                fig3.add_trace(go.Scatter(
                    x=df_grouped['timestamp'],
                    y=df_grouped['temperatura'],
                    name="Temperatura (°C)",
                    mode="lines",
                    line=dict(color="#9b5de5", width=2, dash="dash"),
                    yaxis="y2"
                ))
                
                # Configurar el diseño del doble eje
                fig3.update_layout(
                    yaxis=dict(
                        title="Vehículos",
                        titlefont=dict(color="#FF9F43"),
                        tickfont=dict(color="#FF9F43"),
                        gridcolor="rgba(255, 255, 255, 0.05)"
                    ),
                    yaxis2=dict(
                        title="Temperatura (°C)",
                        titlefont=dict(color="#9b5de5"),
                        tickfont=dict(color="#9b5de5"),
                        anchor="x",
                        overlaying="y",
                        side="right"
                    )
                )
                fig3 = aplicar_tema_oscuro(fig3, "Efecto de la Temperatura sobre el Flujo Vial (Doble Eje)", "", "")
                
            return fig1, fig2, fig3
            
        except Exception as e:
            logger.error(f"Error generando gráficos históricos: {e}")
            msg_error = "Error al conectar con la API para cargar históricos."
            return crear_grafico_vacio(msg_error), crear_grafico_vacio(msg_error), crear_grafico_vacio(msg_error)
