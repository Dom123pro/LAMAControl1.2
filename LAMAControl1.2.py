# -*- coding: utf-8 -*-

import os
import sqlite3
import hashlib
import threading
import time
import random
import secrets
import socket
import csv
import io
import json
import shutil
import zipfile
import webbrowser
import signal
import sys
import subprocess
import traceback
import urllib.request
import urllib.error
from threading import Timer
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timedelta
from io import BytesIO
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from flask import (
    Flask, request, redirect, session,
    render_template_string, url_for,
    flash, get_flashed_messages,
    send_file, abort, jsonify
)
from werkzeug.utils import secure_filename

# Importar requests si está disponible (para keep-alive)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests no disponible - usando urllib para keep-alive")


# —— Evitar reposo en Windows ——
import sys
if sys.platform == "win32":
    import ctypes

from flask import Flask
app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Cambia esto por una clave segura en producción
DB_PATH = 'lama_control.db'  # Cambia esto por la ruta real de tu base de datos si es necesario

# —— Definiciones de estilos y rutas de carpetas ——
BASE_STYLES = """
<style>
body {
  font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
  background: #f4f6fb;
  margin: 0;
  color: #23272f;
  font-size: 16px;
  letter-spacing: 0.01em;
}
.layout-container {
  display: flex;
  min-height: 100vh;
}
.sidebar {
  width: 200px;
  background: #23272f;
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  box-shadow: 2px 0 16px #0001;
  z-index: 2;
}
.sidebar-header {
  padding: 32px 0 18px 0;
  text-align: center;
  border-bottom: 1px solid #23272f;
}
.sidebar-logo {
  width: 64px;
  height: 64px;
  object-fit: contain;
  border-radius: 12px;
  margin: 0 auto 10px auto;
  display: block;
  box-shadow: 0 2px 8px #0002;
}
.sidebar-nav {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
}
.sidebar-nav li {
  border-bottom: 1px solid #23272f;
}
.sidebar-nav a {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #cfd8dc;
  text-decoration: none;
  padding: 14px 24px;
  font-weight: 500;
  font-size: 1.05em;
  transition: background 0.18s, color 0.18s;
  border-left: 3px solid transparent;
}
.sidebar-nav a.active, .sidebar-nav a:hover {
  background: #2d323c;
  color: #fff;
  border-left: 3px solid #4f8cff;
}
.main-content {
  flex: 1;
  background: #f4f6fb;
  padding: 0;
  min-width: 0;
}
.content-header {
  background: #fff;
  padding: 32px 36px 12px 36px;
  border-bottom: 1px solid #e3e7ef;
  position: sticky;
  top: 0;
  z-index: 1;
}
.content-header h1 {
  margin: 0;
  font-size: 2em;
  color: #23272f;
  font-weight: 700;
  letter-spacing: 0.01em;
}
.breadcrumb {
  color: #7b8ca7;
  font-size: 0.98em;
  margin-top: 8px;
}
.content-body {
  padding: 36px;
  max-width: 1200px;
  margin: 0 auto;
}
.card {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 2px 16px #0001;
  margin-bottom: 28px;
  padding: 28px 24px;
  border: 1px solid #e3e7ef;
}
.card-header {
  border-bottom: 1px solid #e3e7ef;
  margin-bottom: 16px;
  padding-bottom: 8px;
}
.card-title {
  font-size: 1.18em;
  color: #23272f;
  font-weight: 600;
  margin: 0;
}
/* Tablas */
table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin-top: 10px;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 8px #0001;
}
th, td {
  padding: 12px 10px;
  border-bottom: 1px solid #e3e7ef;
  text-align: left;
  font-size: 1em;
  transition: background 0.15s;
}
th {
  background: #f0f4fa;
  font-weight: 700;
  color: #23272f;
  letter-spacing: 0.01em;
  border-bottom: 2px solid #e3e7ef;
}
tr:last-child td {
  border-bottom: none;
}
tr:hover td {
  background: #f7fafd;
}
/* Botones */
.btn {
  background: linear-gradient(90deg, #4f8cff 0%, #3e6edb 100%);
  color: #fff;
  border: none;
  border-radius: 7px;
  padding: 10px 22px;
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.18s, box-shadow 0.18s, color 0.18s;
  box-shadow: 0 2px 8px #4f8cff22;
  outline: none;
  margin: 2px 0;
  display: inline-block;
}
.btn:hover, .btn:focus {
  background: linear-gradient(90deg, #3e6edb 0%, #4f8cff 100%);
  box-shadow: 0 4px 16px #4f8cff33;
  color: #fff;
}
.btn.btn-secondary {
  background: #e3e7ef;
  color: #23272f;
  box-shadow: none;
}
.btn.btn-secondary:hover {
  background: #cfd8dc;
}
.btn.btn-danger {
  background: linear-gradient(90deg, #e74c3c 0%, #c0392b 100%);
  color: #fff;
}
.btn.btn-danger:hover {
  background: linear-gradient(90deg, #c0392b 0%, #e74c3c 100%);
}
.btn.btn-success {
  background: linear-gradient(90deg, #27ae60 0%, #2ecc71 100%);
  color: #fff;
}
.btn.btn-success:hover {
  background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%);
}
/* Formularios */
input[type="text"], input[type="password"], input[type="number"], input[type="date"], select, textarea {
  width: 100%;
  padding: 12px 14px;
  margin: 8px 0 18px 0;
  border: 1px solid #cfd8dc;
  border-radius: 7px;
  font-size: 1em;
  background: #f7fafd;
  transition: border 0.18s, box-shadow 0.18s;
  box-sizing: border-box;
  outline: none;
}
input:focus, select:focus, textarea:focus {
  border-color: #4f8cff;
  box-shadow: 0 0 0 2px #4f8cff22;
}
label {
  font-weight: 500;
  color: #23272f;
  margin-bottom: 4px;
  display: block;
}
/* Alertas y mensajes */
.alert, .flash {
  padding: 14px 18px;
  border-radius: 7px;
  margin-bottom: 18px;
  font-size: 1em;
  font-weight: 500;
  background: #f0f4fa;
  color: #1565c0;
  border-left: 5px solid #4f8cff;
  box-shadow: 0 1px 6px #4f8cff11;
}
.alert-success {
  background: #eafaf1;
  color: #218838;
  border-left-color: #27ae60;
}
.alert-danger, .flash-error {
  background: #fdecea;
  color: #c0392b;
  border-left-color: #e74c3c;
}
.alert-warning {
  background: #fff8e1;
  color: #b26a00;
  border-left-color: #f39c12;
}
/* Íconos y títulos */
.card-title i, .sidebar-nav i {
  font-style: normal;
  margin-right: 6px;
  opacity: 0.85;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
}
/* Utilidades */
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-muted { color: #7b8ca7; }
.mt-2 { margin-top: 12px; }
.mb-2 { margin-bottom: 12px; }
.mt-4 { margin-top: 24px; }
.mb-4 { margin-bottom: 24px; }
.rounded { border-radius: 12px; }
.shadow { box-shadow: 0 2px 8px #0001; }
/* Responsive */
@media (max-width: 900px) {
  .content-body { padding: 10px; }
  .main-content { padding: 0; }
  .sidebar { width: 60px; }
  .sidebar-nav a { padding: 12px 10px; font-size: 0.95em; }
  .sidebar-header { padding: 18px 0 8px 0; }
  .sidebar-logo { width: 36px; height: 36px; }
}
@media (max-width: 600px) {
  .content-header { padding: 18px 8px 8px 8px; }
  .content-body { padding: 4px; }
  .card { padding: 12px 4px; }
  table, th, td { font-size: 0.95em; }
}
/* Panel de acciones rápidas */
.quick-actions-panel {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  background: #f0f4fa;
  border-radius: 14px;
  box-shadow: 0 2px 12px #4f8cff11;
  padding: 22px 18px;
  margin-bottom: 32px;
  align-items: center;
  justify-content: flex-start;
}
.quick-action-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(90deg, #4f8cff 0%, #3e6edb 100%);
  color: #fff;
  border: none;
  border-radius: 9px;
  padding: 16px 28px;
  font-size: 1.08em;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px #4f8cff22;
  transition: background 0.18s, box-shadow 0.18s, transform 0.12s;
  text-decoration: none;
  outline: none;
}
.quick-action-btn i {
  font-size: 1.3em;
  margin-right: 6px;
  opacity: 0.92;
}
.quick-action-btn:hover, .quick-action-btn:focus {
  background: linear-gradient(90deg, #3e6edb 0%, #4f8cff 100%);
  box-shadow: 0 4px 16px #4f8cff33;
  transform: translateY(-2px) scale(1.03);
}
.quick-action-btn.success {
  background: linear-gradient(90deg, #27ae60 0%, #2ecc71 100%);
}
.quick-action-btn.success:hover {
  background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%);
}
.quick-action-btn.danger {
  background: linear-gradient(90deg, #e74c3c 0%, #c0392b 100%);
}
.quick-action-btn.danger:hover {
  background: linear-gradient(90deg, #c0392b 0%, #e74c3c 100%);
}
.quick-action-btn.secondary {
  background: #e3e7ef;
  color: #23272f;
  box-shadow: none;
}
.quick-action-btn.secondary:hover {
  background: #cfd8dc;
}
@media (max-width: 700px) {
  .quick-actions-panel {
    flex-direction: column;
    gap: 12px;
    padding: 12px 6px;
  }
  .quick-action-btn {
    width: 100%;
    justify-content: center;
    font-size: 1em;
    padding: 14px 0;
  }
}
</style>
"""

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FOTOS_FOLDER = os.path.join(BASE_DIR, 'static', 'fotos')
LOGO_FOLDER = os.path.join(BASE_DIR, 'static', 'logo')
BANNER_FOLDER = os.path.join(BASE_DIR, 'static', 'banner')
app.config["FOTOS_FOLDER"] = FOTOS_FOLDER
app.config["LOGO_FOLDER"] = LOGO_FOLDER
app.config["BANNER_FOLDER"] = BANNER_FOLDER

""", retencion_labels=retencion_labels, retencion_activos=retencion_activos, retencion_vencidos=retencion_vencidos,
     frecuencia_asistencia=frecuencia_asistencia, proximas_renovaciones=proximas_renovaciones,
     semana_labels=semana_labels, semana_asistencias=semana_asistencias,
     crecimiento_labels=crecimiento_labels, crecimiento_miembros=crecimiento_miembros, 
     crecimiento_asistencias=crecimiento_asistencias, BASE_STYLES=BASE_STYLES, logo_fn=logo_fn, asistencias=asistencias)
      height: auto;
    }
    .content-body {
      padding: 20px;
    }
    .stats-grid {
      grid-template-columns: 1fr;
    }
  }
</style>"""

def encriptar(texto):
    return hashlib.sha256(texto.encode()).hexdigest()

def conectar():
    return sqlite3.connect(DB_PATH)

def calcular_vigencia(modalidad, fecha_inicio=None):
    """
    Calcula la fecha de vigencia basada en la modalidad y fecha de inicio.
    Si no se proporciona fecha_inicio, usa la fecha actual.
    """
    if modalidad == "semanal":
        dias = 7
    elif modalidad == "mensual":
        dias = 30
    elif modalidad == "trimestre":
        dias = 90
    elif modalidad == "semestre":
        dias = 180
    elif modalidad == "anualidad":
        dias = 365
    elif modalidad == "plan_familiar":
        dias = 30
    elif modalidad == "plan_grupal":
        dias = 30
    else:
        dias = 30
    
    # Si se proporciona fecha_inicio, usarla; si no, usar fecha actual
    if fecha_inicio:
        try:
            fecha_base = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        except (ValueError, TypeError):
            fecha_base = datetime.now()
    else:
        fecha_base = datetime.now()
    
    return (fecha_base + timedelta(days=dias)).strftime("%Y-%m-%d")

def dias_restantes(fecha_str):
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    return (fecha - datetime.now().date()).days

def generar_nip_unico():
    con = conectar()
    while True:
        nip = str(random.randint(1000, 9999))
        existe = con.execute("SELECT 1 FROM usuarios WHERE nip_visible=?", (nip,)).fetchone()
        if not existe:
            con.close()
            return nip

def crear_db():
    con = conectar()
    
    # Actualizar tabla planes_familiares si no tiene responsable_id
    try:
        con.execute("ALTER TABLE planes_familiares ADD COLUMN responsable_id INTEGER")
        print("✅ Columna responsable_id agregada a planes_familiares")
    except sqlite3.OperationalError:
        # La columna ya existe
        pass
    
    # Actualizar tabla miembros_familia para agregar columnas faltantes
    try:
        con.execute("ALTER TABLE miembros_familia ADD COLUMN activo INTEGER DEFAULT 1")
        print("✅ Columna activo agregada a miembros_familia")
    except sqlite3.OperationalError:
        # La columna ya existe
        pass
    
    try:
        con.execute("ALTER TABLE miembros_familia ADD COLUMN fecha_desvinculacion TEXT")
        print("✅ Columna fecha_desvinculacion agregada a miembros_familia")
    except sqlite3.OperationalError:
        # La columna ya existe
        pass
    
    con.execute("""
      CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        usuario TEXT UNIQUE,
        pin TEXT UNIQUE,
        nip_visible TEXT,
        modalidad TEXT,
        vigencia TEXT,
        foto TEXT,
        rol TEXT DEFAULT 'miembro',
        permisos TEXT,
        correo TEXT,
        telefono_emergencia TEXT,
        datos_medicos TEXT
      )
    """)
    con.execute("""
      CREATE TABLE IF NOT EXISTS historial_miembros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        fecha TEXT
      )
    """)
    con.execute("""
      CREATE TABLE IF NOT EXISTS historial_admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        fecha TEXT
      )
    """)
    con.execute("CREATE TABLE IF NOT EXISTS banner (id INTEGER PRIMARY KEY CHECK(id=1), filename TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS logo   (id INTEGER PRIMARY KEY CHECK(id=1), filename TEXT)")
    con.execute("""
      CREATE TABLE IF NOT EXISTS pagos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        monto REAL,
        fecha TEXT,
        concepto TEXT
      )
    """)
    con.execute("""
      CREATE TABLE IF NOT EXISTS facturacion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT,
        monto REAL,
        fecha TEXT,
        folio TEXT
      )
    """)
    con.execute("""
      CREATE TABLE IF NOT EXISTS asistencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        fecha TEXT,
        hora_entrada TEXT,
        hora_salida TEXT,
        FOREIGN KEY (usuario) REFERENCES usuarios(usuario)
      )
    """)
    
    # Tabla para planes familiares
    con.execute("""
      CREATE TABLE IF NOT EXISTS planes_familiares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_plan TEXT,
        responsable_id INTEGER,
        fecha_creacion TEXT,
        vigencia TEXT,
        activo INTEGER DEFAULT 1,
        FOREIGN KEY (responsable_id) REFERENCES usuarios(id)
      )
    """)
    
    # Tabla para vincular miembros a planes familiares
    con.execute("""
      CREATE TABLE IF NOT EXISTS miembros_familia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_familiar_id INTEGER,
        miembro_id INTEGER,
        fecha_vinculacion TEXT,
        activo INTEGER DEFAULT 1,
        fecha_desvinculacion TEXT,
        FOREIGN KEY (plan_familiar_id) REFERENCES planes_familiares(id),
        FOREIGN KEY (miembro_id) REFERENCES usuarios(id)
      )
    """)
    
    # Tabla para sugerencias de vinculación familiar
    con.execute("""
      CREATE TABLE IF NOT EXISTS sugerencias_familia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        miembro1_id INTEGER,
        miembro2_id INTEGER,
        razon TEXT,
        estado TEXT DEFAULT 'pendiente',
        fecha_sugerencia TEXT,
        fecha_decision TEXT,
        decidido_por TEXT,
        FOREIGN KEY (miembro1_id) REFERENCES usuarios(id),
        FOREIGN KEY (miembro2_id) REFERENCES usuarios(id)
      )
    """)
    
    # Tabla para planes grupales
    con.execute("""
      CREATE TABLE IF NOT EXISTS planes_grupales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_grupo TEXT,
        responsable_id INTEGER,
        fecha_creacion TEXT,
        vigencia TEXT,
        activo INTEGER DEFAULT 1,
        descripcion TEXT,
        max_miembros INTEGER DEFAULT 10,
        FOREIGN KEY (responsable_id) REFERENCES usuarios(id)
      )
    """)
    
    # Tabla para vincular miembros a planes grupales
    con.execute("""
      CREATE TABLE IF NOT EXISTS miembros_grupo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_grupal_id INTEGER,
        miembro_id INTEGER,
        fecha_vinculacion TEXT,
        activo INTEGER DEFAULT 1,
        FOREIGN KEY (plan_grupal_id) REFERENCES planes_grupales(id),
        FOREIGN KEY (miembro_id) REFERENCES usuarios(id)
      )
    """)
    
    cur = con.execute("SELECT COUNT(*) FROM usuarios WHERE usuario='alfredo'")
    if cur.fetchone()[0] == 0:
        con.execute("""
          INSERT INTO usuarios (nombre,usuario,pin,nip_visible,modalidad,vigencia,rol)
          VALUES (?,?,?,?,?,?,?)
        """, (
          "Alfredo Luna", "alfredo", encriptar("2121"), "2121",
          "mensual", calcular_vigencia("mensual"), "admin"
        ))
    for tbl in ("banner","logo"):
        cur = con.execute(f"SELECT COUNT(*) FROM {tbl}")
        if cur.fetchone()[0] == 0:
            con.execute(f"INSERT INTO {tbl} (id,filename) VALUES (1,'')")
    con.commit()
    con.close()

def registrar_historial(usuario, rol):
    tabla = "historial_admin" if rol in ("admin","moderador") else "historial_miembros"
    con = conectar()
    con.execute(f"""
      INSERT INTO {tabla} (usuario,fecha) VALUES (?,?)
    """, (usuario, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    con.commit()
    con.close()

# —— CSRF Protection ——
def generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_urlsafe(32)
    return session["_csrf_token"]

def validate_csrf():
    token = session.get("_csrf_token", None)
    form_token = request.form.get("_csrf_token", None)
    if not token or not form_token or token != form_token:
        abort(400, "CSRF token inválido o ausente.")

app.jinja_env.globals["csrf_token"] = generate_csrf_token

# Filtro personalizado para calcular días restantes
@app.template_filter('dias_restantes')
def filter_dias_restantes(fecha_str):
    return dias_restantes(fecha_str)

# —— Inicializar BD ——
crear_db()

# —— Headers de seguridad ——
@app.after_request
def set_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: https://cdn.jsdelivr.net;"
    return response

# ——— Rutas de Keep-Alive y Monitoreo ———

@app.route('/keep_alive')
def keep_alive():
    """Ruta simple para mantener el servidor activo"""
    return {
        'status': 'alive',
        'timestamp': datetime.now().isoformat(),
        'uptime': time.time() - app.config.get('START_TIME', time.time()),
        'message': 'Servidor LAMA Control activo',
        'service': 'LAMAControl'
    }

@app.route('/ping')
def ping():
    """Ruta ultra simple para verificar conectividad"""
    return 'pong'

@app.route('/health')
def health_check():
    """Health check completo del servidor"""
    try:
        # Verificar base de datos
        con = conectar()
        con.execute('SELECT 1').fetchone()
        con.close()
        db_status = 'ok'
    except:
        db_status = 'error'
    
    return {
        'status': 'healthy' if db_status == 'ok' else 'degraded',
        'database': db_status,
        'timestamp': datetime.now().isoformat(),
        'uptime': time.time() - app.config.get('START_TIME', time.time()),
        'service': 'LAMAControl'
    }

@app.route('/server_status')
def server_status():
    """Estado detallado del servidor"""
    try:
        con = conectar()
        miembros_count = con.execute("SELECT COUNT(*) FROM usuarios WHERE tipo='Miembro'").fetchone()[0]
        admins_count = con.execute("SELECT COUNT(*) FROM usuarios WHERE tipo='Administrador'").fetchone()[0]
        moderadores_count = con.execute("SELECT COUNT(*) FROM usuarios WHERE tipo='Moderador'").fetchone()[0]
        con.close()
        
        status = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'server_info': {
                'service': 'LAMAControl',
                'process_id': os.getpid(),
                'threads_count': threading.active_count(),
            },
            'database_stats': {
                'miembros_count': miembros_count,
                'admins_count': admins_count,
                'moderadores_count': moderadores_count,
                'total_usuarios': miembros_count + admins_count + moderadores_count
            },
            'request_info': {
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'Unknown')[:100],
                'host': request.host,
                'method': request.method
            }
        }
        
        return f"""
        <h2>Estado del Servidor LAMA Control</h2>
        <pre>{json.dumps(status, indent=2)}</pre>
        <hr>
        <p><a href="/keep_alive">Keep Alive</a></p>
        <p><a href="/ping">Ping</a></p>
        <p><a href="/health">Health Check</a></p>
        <p><a href="/login">Ir al Login</a></p>
        """
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/")
def home():
    return redirect("/login")

# —— Funciones para Planes Familiares ——

def detectar_apellidos_similares():
    """Detecta miembros con apellidos similares para sugerir vinculación familiar"""
    con = conectar()
    miembros = con.execute("""
        SELECT id, nombre, usuario FROM usuarios 
        WHERE rol='miembro' AND modalidad != 'plan_familiar'
    """).fetchall()
    
    sugerencias = []
    apellidos_procesados = set()
    
    # Agrupar miembros por apellido
    grupos_apellidos = {}
    for miembro in miembros:
        id_miembro, nombre, usuario = miembro
        if nombre:
            apellido = nombre.split()[-1].lower().strip()
            if apellido and len(apellido) > 1:  # Evitar apellidos de una sola letra
                if apellido not in grupos_apellidos:
                    grupos_apellidos[apellido] = []
                grupos_apellidos[apellido].append((id_miembro, nombre, usuario))
    
    # Crear sugerencias para grupos con más de un miembro
    for apellido, miembros_grupo in grupos_apellidos.items():
        if len(miembros_grupo) > 1 and apellido not in apellidos_procesados:
            # Crear sugerencias entre todos los miembros del mismo apellido
            for i, miembro1 in enumerate(miembros_grupo):
                for miembro2 in miembros_grupo[i+1:]:
                    id1, nombre1, usuario1 = miembro1
                    id2, nombre2, usuario2 = miembro2
                    
                    # Verificar si ya existe una sugerencia para estos miembros
                    existe = con.execute("""
                        SELECT id FROM sugerencias_familia 
                        WHERE (miembro1_id=? AND miembro2_id=?) OR (miembro1_id=? AND miembro2_id=?)
                        AND estado = 'pendiente'
                    """, (id1, id2, id2, id1)).fetchone()
                    
                    if not existe:
                        # Agregar nueva sugerencia
                        con.execute("""
                            INSERT INTO sugerencias_familia 
                            (miembro1_id, miembro2_id, razon, fecha_sugerencia, estado)
                            VALUES (?, ?, ?, ?, 'pendiente')
                        """, (id1, id2, f"Apellido compartido: {apellido.title()}", 
                              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        
                        sugerencias.append((id1, id2, apellido))
            
            apellidos_procesados.add(apellido)
    
    con.commit()
    con.close()
    return sugerencias

def crear_plan_familiar(nombre_plan, miembro_ids, responsable_id=None):
    """Crea un nuevo plan familiar y vincula los miembros del mismo apellido"""
    con = conectar()
    
    try:
        print(f"Debug crear_plan_familiar:")
        print(f"  Nombre plan: {nombre_plan}")
        print(f"  Miembros: {miembro_ids}")
        print(f"  Responsable: {responsable_id}")
        
        # Verificar que todos los miembros tengan el mismo apellido
        apellidos = []
        for miembro_id in miembro_ids:
            miembro = con.execute("SELECT nombre, modalidad FROM usuarios WHERE id=? AND rol='miembro'", (miembro_id,)).fetchone()
            if not miembro:
                raise Exception(f"Miembro con ID {miembro_id} no encontrado")
            if miembro[1] in ['plan_familiar', 'plan_grupal']:
                raise Exception(f"Miembro {miembro[0]} ya está en un plan ({miembro[1]})")
            
            apellido = miembro[0].split()[-1].lower() if miembro[0] else ""
            apellidos.append(apellido)
            print(f"  Miembro verificado: {miembro[0]} (apellido: {apellido})")
        
        # Verificar que todos tengan el mismo apellido
        apellido_principal = apellidos[0] if apellidos else ""
        if not all(apellido == apellido_principal for apellido in apellidos):
            raise ValueError("Todos los miembros deben tener el mismo apellido para formar un plan familiar")
        
        # Crear el plan familiar
        vigencia = calcular_vigencia("plan_familiar")
        print(f"  Vigencia calculada: {vigencia}")
        
        cursor = con.execute("""
            INSERT INTO planes_familiares (nombre_plan, responsable_id, fecha_creacion, vigencia, activo)
            VALUES (?, ?, ?, ?, 1)
        """, (nombre_plan, responsable_id, datetime.now().strftime("%Y-%m-%d"), vigencia))
        
        plan_id = cursor.lastrowid
        print(f"  Plan ID creado: {plan_id}")
        
        if not plan_id:
            raise Exception("No se pudo crear el plan familiar")
        
        # Vincular miembros al plan
        for miembro_id in miembro_ids:
            print(f"  Vinculando miembro: {miembro_id}")
            cursor = con.execute("""
                INSERT INTO miembros_familia (plan_familiar_id, miembro_id, fecha_vinculacion, activo)
                VALUES (?, ?, ?, 1)
            """, (plan_id, miembro_id, datetime.now().strftime("%Y-%m-%d")))
            
            # Actualizar modalidad del miembro a plan_familiar
            cursor = con.execute("""
                UPDATE usuarios SET modalidad='plan_familiar', vigencia=? WHERE id=?
            """, (vigencia, miembro_id))
            print(f"  Modalidad actualizada para miembro: {miembro_id}")
        
        con.commit()
        
        # Verificar que el plan se creó correctamente
        verificacion = con.execute("SELECT COUNT(*) FROM planes_familiares WHERE id=?", (plan_id,)).fetchone()
        if verificacion[0] == 0:
            raise Exception("El plan no se guardó correctamente en la base de datos")
        
        print(f"  Plan familiar creado exitosamente")
        
    except Exception as e:
        print(f"Error en crear_plan_familiar: {e}")
        import traceback
        traceback.print_exc()
        con.rollback()
        raise e
    finally:
        con.close()
    
    return plan_id

def crear_plan_grupal(nombre_grupo, miembro_ids, responsable_id=None, descripcion="", max_miembros=10):
    """Crea un nuevo plan grupal y vincula los miembros"""
    con = conectar()
    
    print(f"Debug crear_plan_grupal:")
    print(f"  Nombre: {nombre_grupo}")
    print(f"  Miembros: {miembro_ids}")
    print(f"  Responsable: {responsable_id}")
    
    try:
        # Verificar que los miembros existen y están disponibles
        for miembro_id in miembro_ids:
            miembro = con.execute("SELECT id, nombre, modalidad FROM usuarios WHERE id=? AND rol='miembro'", (miembro_id,)).fetchone()
            if not miembro:
                raise Exception(f"Miembro con ID {miembro_id} no encontrado")
            if miembro[2] in ['plan_familiar', 'plan_grupal']:
                raise Exception(f"Miembro {miembro[1]} ya está en un plan ({miembro[2]})")
            print(f"  Miembro verificado: {miembro[1]} (ID: {miembro_id})")
        
        # Crear el plan grupal
        vigencia = calcular_vigencia("plan_grupal")
        print(f"  Vigencia calculada: {vigencia}")
        
        cursor = con.execute("""
            INSERT INTO planes_grupales (nombre_grupo, responsable_id, fecha_creacion, vigencia, descripcion, max_miembros, activo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (nombre_grupo, responsable_id, datetime.now().strftime("%Y-%m-%d"), vigencia, descripcion, max_miembros))
        
        plan_id = cursor.lastrowid
        print(f"  Plan ID creado: {plan_id}")
        
        if not plan_id:
            raise Exception("No se pudo crear el plan grupal")
        
        # Vincular miembros al plan
        for miembro_id in miembro_ids:
            print(f"  Vinculando miembro: {miembro_id}")
            cursor = con.execute("""
                INSERT INTO miembros_grupo (plan_grupal_id, miembro_id, fecha_vinculacion, activo)
                VALUES (?, ?, ?, 1)
            """, (plan_id, miembro_id, datetime.now().strftime("%Y-%m-%d")))
            
            # Actualizar modalidad del miembro a plan_grupal
            cursor = con.execute("""
                UPDATE usuarios SET modalidad='plan_grupal', vigencia=? WHERE id=?
            """, (vigencia, miembro_id))
            print(f"  Modalidad actualizada para miembro: {miembro_id}")
        
        con.commit()
        print(f"  Plan grupal creado exitosamente")
        
        # Verificar que el plan se creó correctamente
        verificacion = con.execute("SELECT COUNT(*) FROM planes_grupales WHERE id=?", (plan_id,)).fetchone()
        if verificacion[0] == 0:
            raise Exception("El plan no se guardó correctamente en la base de datos")
        
        print(f"  Verificación exitosa: Plan {plan_id} guardado correctamente")
        
    except Exception as e:
        print(f"Error en crear_plan_grupal: {e}")
        import traceback
        traceback.print_exc()
        con.rollback()
        raise e
    finally:
        con.close()
    
    return plan_id

def obtener_sugerencias_pendientes():
    """Obtiene todas las sugerencias de vinculación familiar pendientes"""
    con = conectar()
    sugerencias = con.execute("""
        SELECT s.id, u1.nombre, u2.nombre, s.razon, s.fecha_sugerencia, s.miembro1_id, s.miembro2_id
        FROM sugerencias_familia s
        JOIN usuarios u1 ON s.miembro1_id = u1.id
        JOIN usuarios u2 ON s.miembro2_id = u2.id
        WHERE s.estado = 'pendiente'
        ORDER BY s.fecha_sugerencia DESC
    """).fetchall()
    con.close()
    return sugerencias

@app.route("/login", methods=["GET", "POST"])
def login():
    con = conectar()
    banner_row = con.execute("SELECT filename FROM banner WHERE id=1").fetchone()
    banner_fn = banner_row[0] if banner_row else ""
    logo_row = con.execute("SELECT filename FROM logo WHERE id=1").fetchone()
    logo_fn = logo_row[0] if logo_row else ""
    con.close()
    if request.method == "POST":
        nip = request.form["nip"]
        con = conectar()
        user = con.execute("SELECT id, nombre, usuario, rol, vigencia FROM usuarios WHERE nip_visible=?", (nip,)).fetchone()
        con.close()
        if user:
            uid, nombre, usuario, rol, vigencia = user
            
            # Verificar vigencia para miembros
            if rol == "miembro":
                dias_rest = dias_restantes(vigencia)
                if dias_rest < 0:
                    flash("Tu membresía ha vencido. Contacta a recepción para renovar.")
                    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Acceso Denegado</title>
  <style>
    body {
      background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
      font-family: 'Segoe UI', Arial, sans-serif;
      min-height: 100vh;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .error-box {
      max-width: 400px;
      background: #fff;
      border-radius: 14px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
      padding: 40px 32px;
      text-align: center;
    }
    .error-icon {
      font-size: 4em;
      color: #e74c3c;
      margin-bottom: 20px;
    }
    h2 { color: #e74c3c; margin-bottom: 20px; }
    .btn {
      background: #e74c3c;
      color: #fff;
      padding: 12px 24px;
      border: none;
      border-radius: 6px;
      text-decoration: none;
      display: inline-block;
      margin-top: 20px;
    }
  </style>
</head>
<body>
  <div class="error-box">
    <div class="error-icon">⚠️</div>
    <h2>Membresía Vencida</h2>
    <p>Tu membresía venció el <strong>{{ vigencia }}</strong></p>
    <p>Por favor contacta a recepción para renovar tu membresía.</p>
    <a href="/login" class="btn">Volver</a>
  </div>
</body>
</html>
""", vigencia=vigencia)
                elif dias_rest <= 7:
                    # Registrar asistencia automáticamente para miembros
                    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
                    hora_actual = datetime.now().strftime("%H:%M")
                    
                    con = conectar()
                    # Verificar si ya existe asistencia hoy
                    existe = con.execute("SELECT id FROM asistencias WHERE usuario=? AND fecha=?", (usuario, fecha_hoy)).fetchone()
                    
                    if existe:
                        # Actualizar hora de salida
                        con.execute("UPDATE asistencias SET hora_salida=? WHERE usuario=? AND fecha=?", (hora_actual, usuario, fecha_hoy))
                    else:
                        # Registrar entrada
                        con.execute("INSERT INTO asistencias (usuario, fecha, hora_entrada, hora_salida) VALUES (?, ?, ?, ?)",
                                   (usuario, fecha_hoy, hora_actual, ""))
                    con.commit()
                    con.close()
                    
                    # Mostrar aviso de membresía próxima a vencer
                    session["uid"] = uid
                    session["nombre"] = nombre
                    session["usuario"] = usuario
                    session["rol"] = rol
                    registrar_historial(usuario, rol)
                    
                    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Aviso de Vencimiento</title>
  <meta http-equiv="refresh" content="5;url=/panel_miembro">
  <style>
    body {
      background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
      font-family: 'Segoe UI', Arial, sans-serif;
      min-height: 100vh;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .warning-box {
      max-width: 450px;
      background: #fff;
      border-radius: 14px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
      padding: 40px 32px;
      text-align: center;
    }
    .warning-icon {
      font-size: 4em;
      color: #f39c12;
      margin-bottom: 20px;
    }
    h2 { color: #e67e22; margin-bottom: 20px; }
    .countdown {
      background: #fff3cd;
      padding: 15px;
      border-radius: 8px;
      margin: 20px 0;
      color: #856404;
      font-weight: 600;
    }
    .btn {
      background: #f39c12;
      color: #fff;
      padding: 12px 24px;
      border: none;
      border-radius: 6px;
      text-decoration: none;
      display: inline-block;
      margin-top: 10px;
    }
  </style>
</head>
<body>
  <div class="warning-box">
    <div class="warning-icon">⚠️</div>
    <h2>¡Atención!</h2>
    <p>Tu membresía vence en <strong>{{ dias_rest }} días</strong></p>
    <p>Fecha de vencimiento: <strong>{{ vigencia }}</strong></p>
    <p>Te recomendamos renovar pronto para evitar interrupciones.</p>
    
    <div class="countdown">
      ⏱️ Serás redirigido a tu panel en <span id="countdown">5</span> segundos
    </div>
    
    <a href="/panel_miembro" class="btn">Ir al Panel</a>
  </div>

  <script>
    let seconds = 5;
    const countdownElement = document.getElementById('countdown');
    
    const timer = setInterval(() => {
      seconds--;
      countdownElement.textContent = seconds;
      
      if (seconds <= 0) {
        clearInterval(timer);
        window.location.href = '/panel_miembro';
      }
    }, 1000);
  </script>
</body>
</html>
""", dias_rest=dias_rest, vigencia=vigencia)
                else:
                    # Registrar asistencia automáticamente para miembros con vigencia válida
                    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
                    hora_actual = datetime.now().strftime("%H:%M")
                    
                    con = conectar()
                    # Verificar si ya existe asistencia hoy
                    existe = con.execute("SELECT id FROM asistencias WHERE usuario=? AND fecha=?", (usuario, fecha_hoy)).fetchone()
                    
                    if existe:
                        # Actualizar hora de salida
                        con.execute("UPDATE asistencias SET hora_salida=? WHERE usuario=? AND fecha=?", (hora_actual, usuario, fecha_hoy))
                    else:
                        # Registrar entrada
                        con.execute("INSERT INTO asistencias (usuario, fecha, hora_entrada, hora_salida) VALUES (?, ?, ?, ?)",
                                   (usuario, fecha_hoy, hora_actual, ""))
                    con.commit()
                    con.close()
            
            session["uid"] = uid
            session["nombre"] = nombre
            session["usuario"] = usuario
            session["rol"] = rol
            registrar_historial(usuario, rol)
            
            if rol == "admin":
                return redirect("/admin")
            elif rol == "moderador":
                return redirect("/moderador")
            else:
                return redirect("/panel_miembro")
        else:
            flash("NIP incorrecto.")
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Acceso LAMA</title>
  <style>
    body {
      background: linear-gradient(135deg, #2980b9 0%, #6dd5fa 100%);
      font-family: 'Segoe UI', Arial, sans-serif;
      min-height: 100vh;
      margin: 0;
    }
    .banner-header {
      width: 100%;
      max-height: 140px;
      object-fit: cover;
      border-bottom-left-radius: 18px;
      border-bottom-right-radius: 18px;
      box-shadow: 0 4px 24px #0002;
      margin-bottom: 0;
      display: block;
    }
    .login-box {
      max-width: 370px;
      margin: 40px auto 0 auto;
      background: #fff;
      border-radius: 14px;
      box-shadow: 0 8px 32px #0003;
      padding: 40px 32px 32px 32px;
      text-align: center;
      position: relative;
      top: -40px;
    }
    .login-logo {
      width: 80px;
      margin-bottom: 18px;
      filter: drop-shadow(0 2px 6px #2980b9);
      display: block;
      margin-left: auto;
      margin-right: auto;
    }
    h2 {
      color: #2980b9;
      margin-bottom: 24px;
      font-weight: 700;
      letter-spacing: 1px;
    }
    input[type="text"], input[type="password"], input[type="number"] {
      width: 100%;
      padding: 12px;
      margin: 16px 0 22px 0;
      border: 1px solid #b2bec3;
      border-radius: 6px;
      font-size: 1.1em;
      background: #f7fafd;
      transition: border 0.2s;
    }
    input:focus {
      border-color: #2980b9;
      outline: none;
    }
    .btn {
      background: #2980b9;
      color: #fff;
      padding: 14px 0;
      border: none;
      border-radius: 6px;
      width: 100%;
      font-size: 1.1em;
      font-weight: bold;
      cursor: pointer;
      transition: background 0.2s;
      box-shadow: 0 2px 8px #2980b933;
    }
    .btn:hover {
      background: #1f6391;
    }
    .flash {
      background: #fce4e4;
      color: #c0392b;
      padding: 10px;
      border: 1px solid #e0b4b4;
      border-radius: 6px;
      margin-bottom: 20px;
      font-size: 1em;
    }
    @media (max-width: 500px) {
      .login-box { padding: 24px 8px; }
      .banner-header { max-height: 80px; }
    }
  </style>
</head>
<body>
  {% if banner_fn %}
    <img src="{{ url_for('static', filename='banner/' + banner_fn) }}" class="banner-header">
  {% endif %}
  <div class="login-box">
    {% if logo_fn %}
      <img src="{{ url_for('static', filename='logo/' + logo_fn) }}" class="login-logo">
    {% endif %}
    <h2>Acceso LAMA</h2>
    {% for msg in get_flashed_messages() %}
      <div class="flash">{{ msg }}</div>
    {% endfor %}
    <form method="POST">
      <input name="nip" maxlength="4" placeholder="Ingresa tu NIP" required autofocus>
      <button type="submit" class="btn">Entrar</button>
    </form>
  </div>
</body>
</html>
""", banner_fn=banner_fn, logo_fn=logo_fn)

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.")
    return redirect("/login")

@app.route("/buscar_familia")
def buscar_familia():
    """Endpoint para buscar miembros con apellidos similares para vinculación familiar"""
    if session.get("rol") not in ("admin", "moderador"):
        return jsonify({"error": "No autorizado"}), 403
    
    apellido = request.args.get("apellido", "").strip().lower()
    if not apellido:
        return jsonify({"miembros": []})
    
    try:
        con = conectar()
        # Buscar miembros que tengan apellidos similares
        miembros = con.execute("""
            SELECT id, nombre, modalidad, vigencia, fecha_registro
            FROM usuarios 
            WHERE rol = 'miembro' 
            AND modalidad != 'plan_familiar'
            AND LOWER(nombre) LIKE ?
            ORDER BY id DESC
        """, (f'%{apellido}%',)).fetchall()
        
        # Filtrar por apellido específico (última palabra del nombre)
        miembros_filtrados = []
        for miembro in miembros:
            nombre_completo = miembro[1]  # nombre
            apellido_miembro = nombre_completo.split()[-1].lower() if nombre_completo else ""
            
            # Verificar si el apellido coincide exactamente o es similar
            if apellido_miembro == apellido or apellido in apellido_miembro or apellido_miembro in apellido:
                miembros_filtrados.append({
                    "id": miembro[0],
                    "nombre": miembro[1],
                    "modalidad": miembro[2],
                    "vigencia": miembro[3],
                    "fecha_registro": miembro[4] if miembro[4] else "Sin fecha"
                })
        
        con.close()
        return jsonify({"miembros": miembros_filtrados})
        
    except Exception as e:
        print(f"Error al buscar familia: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route("/buscar_miembros_familia")
def buscar_miembros_familia():
    """Endpoint para buscar miembros disponibles para agregar a un plan familiar"""
    if session.get("rol") not in ("admin", "moderador"):
        return jsonify({"error": "No autorizado"}), 403
    
    try:
        busqueda = request.args.get("busqueda", "").strip()
        plan_id = request.args.get("plan_id", "").strip()
        
        if not busqueda or len(busqueda) < 2:
            return jsonify({"miembros": []})
        
        con = sqlite3.connect(DB_PATH)
        cursor = con.cursor()
        
        # Obtener el apellido del plan familiar
        cursor.execute("SELECT nombre FROM planes_familiares WHERE id = ?", (plan_id,))
        plan = cursor.fetchone()
        if not plan:
            return jsonify({"miembros": []})
        
        apellido_plan = plan[0].split(' - ')[0]  # Extraer apellido del nombre del plan
        
        # Buscar miembros que NO estén ya en la familia y tengan el mismo apellido
        cursor.execute("""
            SELECT m.id, m.nombre 
            FROM miembros m 
            WHERE (m.nombre LIKE ? OR CAST(m.id AS TEXT) LIKE ?)
            AND m.activo = 1
            AND m.id NOT IN (
                SELECT miembro_id FROM miembros_familia 
                WHERE plan_familiar_id = ? AND activo = 1
            )
            ORDER BY m.nombre
            LIMIT 10
        """, (f"%{busqueda}%", f"%{busqueda}%", plan_id))
        
        miembros = cursor.fetchall()
        miembros_filtrados = []
        
        # Filtrar por apellido
        for miembro in miembros:
            nombre_completo = miembro[1]
            apellido_miembro = nombre_completo.split()[-1] if ' ' in nombre_completo else nombre_completo
            
            # Verificar que el apellido coincida
            if apellido_miembro.lower() == apellido_plan.lower():
                miembros_filtrados.append({
                    "id": miembro[0],
                    "nombre": miembro[1]
                })
        
        con.close()
        return jsonify({"miembros": miembros_filtrados})
        
    except Exception as e:
        print(f"Error al buscar miembros para familia: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route("/buscar_familiares", methods=["POST"])
def buscar_familiares():
    """Endpoint para buscar miembros familiares basado en nombre completo"""
    if session.get("rol") not in ("admin", "moderador"):
        return jsonify({"error": "No autorizado"}), 403
    
    nombre_completo = request.form.get("nombre", "").strip()
    if len(nombre_completo) < 3:
        return jsonify({"miembros": []})
    
    try:
        # Extraer apellidos del nombre (asumimos que las últimas palabras son apellidos)
        palabras = nombre_completo.split()
        if len(palabras) < 2:
            return jsonify({"miembros": []})
        
        # Tomar el apellido principal (última palabra)
        apellido_principal = palabras[-1].lower()
        
        con = conectar()
        # Buscar miembros que tengan apellidos similares
        miembros = con.execute("""
            SELECT id, nombre, modalidad, vigencia
            FROM usuarios 
            WHERE rol = 'miembro' 
            AND modalidad NOT IN ('plan_familiar', 'plan_grupal')
            AND LOWER(nombre) LIKE ?
            ORDER BY nombre
        """, (f'%{apellido_principal}%',)).fetchall()
        
        # Filtrar por apellido específico
        miembros_filtrados = []
        for miembro in miembros:
            id_miembro, nombre_miembro, modalidad, vigencia = miembro
            apellido_miembro = nombre_miembro.split()[-1].lower() if nombre_miembro else ""
            
            # Verificar si coincide el apellido y no es el mismo nombre
            if (apellido_miembro == apellido_principal and 
                nombre_miembro.lower() != nombre_completo.lower()):
                miembros_filtrados.append({
                    "id": id_miembro,
                    "nombre": nombre_miembro,
                    "usuario": con.execute("SELECT usuario FROM usuarios WHERE id=?", (id_miembro,)).fetchone()[0],
                    "modalidad": modalidad,
                    "vigencia": vigencia
                })
        
        con.close()
        return jsonify({"miembros": miembros_filtrados})
        
    except Exception as e:
        print(f"Error al buscar familiares: {e}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

@app.route("/buscar_miembros_grupo", methods=["GET", "POST"])
def buscar_miembros_grupo():
    """Endpoint para buscar miembros para agregar a un plan grupal y listar planes"""
    if session.get("rol") not in ("admin", "moderador"):
        return jsonify({"error": "No autorizado"}), 403
    
    # Si es POST, verificar si es para listar planes
    if request.method == "POST":
        accion = request.form.get("accion", "")
        if accion == "listar_planes":
            try:
                con = conectar()
                planes = con.execute("""
                    SELECT pg.id, pg.nombre_grupo, pg.descripcion, pg.max_miembros,
                           COUNT(mg.id) as total_miembros
                    FROM planes_grupales pg
                    LEFT JOIN miembros_grupo mg ON pg.id = mg.plan_grupal_id AND mg.activo = 1
                    WHERE pg.activo = 1
                    GROUP BY pg.id, pg.nombre_grupo, pg.descripcion, pg.max_miembros
                    ORDER BY pg.nombre_grupo
                """).fetchall()
                
                planes_lista = []
                for plan in planes:
                    planes_lista.append({
                        "id": plan[0],
                        "nombre_grupo": plan[1],
                        "descripcion": plan[2] or "",
                        "max_miembros": plan[3],
                        "total_miembros": plan[4]
                    })
                
                con.close()
                return jsonify({"planes": planes_lista})
                
            except Exception as e:
                print(f"Error al listar planes grupales: {e}")
                return jsonify({"error": "Error interno del servidor"}), 500
    
    # Funcionalidad original para buscar miembros
    busqueda = request.args.get("busqueda", "").strip()
    if len(busqueda) < 2:
        return jsonify({"miembros": []})
    
    try:
        con = conectar()
        # Buscar miembros por nombre o usuario
        miembros = con.execute("""
            SELECT id, nombre, usuario, modalidad
            FROM usuarios 
            WHERE rol = 'miembro' 
            AND modalidad NOT IN ('plan_familiar', 'plan_grupal')
            AND (LOWER(nombre) LIKE ? OR LOWER(usuario) LIKE ?)
            ORDER BY nombre
        """, (f'%{busqueda.lower()}%', f'%{busqueda.lower()}%')).fetchall()
        
        miembros_encontrados = []
        for miembro in miembros:
            miembros_encontrados.append({
                "id": miembro[0],
                "nombre": miembro[1],
                "usuario": miembro[2],
                "modalidad": miembro[3]
            })
        
        con.close()
        return jsonify({"miembros": miembros_encontrados})
        
    except Exception as e:
        print(f"Error al buscar miembros grupo: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route("/crear_miembro", methods=["POST"])
def crear_miembro():
    if session.get("rol") not in ("admin","moderador"):
        return redirect("/login")
    nip = generar_nip_unico()
    foto = request.files.get("foto")
    filename = ""
    if foto and foto.filename:
        safe = secure_filename(foto.filename)
        filename = f"{request.form['usuario']}_{safe}"
        foto.save(os.path.join(app.config["FOTOS_FOLDER"],filename))
    correo = request.form.get("correo", "")
    telefono_emergencia = request.form.get("telefono_emergencia", "")
    datos_medicos = request.form.get("datos_medicos", "")
    fecha_inicio = request.form.get("fecha_inicio", "")  # Nueva fecha de inicio
    
    try:
        con = conectar()
        
        # Insertar el nuevo miembro
        cursor = con.execute("""
          INSERT INTO usuarios
            (nombre,usuario,pin,nip_visible,modalidad,vigencia,foto,correo,telefono_emergencia,datos_medicos)
          VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            request.form["nombre"],
            request.form["usuario"],
            encriptar(nip),
            nip,
            request.form["modalidad"],
            calcular_vigencia(request.form["modalidad"], fecha_inicio if fecha_inicio else None),
            filename,
            correo,
            telefono_emergencia,
            datos_medicos
        ))
        
        nuevo_miembro_id = cursor.lastrowid
        
        # Si es plan familiar, crear el plan y vincular miembros
        if request.form["modalidad"] == "plan_familiar":
            # Crear el plan familiar
            cursor.execute("""
                INSERT INTO planes_familiares (nombre_plan, responsable_id, fecha_creacion)
                VALUES (?, ?, DATE('now'))
            """, (f"Plan Familiar - {request.form['nombre']}", nuevo_miembro_id))
            
            plan_id = cursor.lastrowid
            
            # Agregar el nuevo miembro al plan
            cursor.execute("""
                INSERT INTO miembros_familia (plan_familiar_id, miembro_id, fecha_vinculacion)
                VALUES (?, ?, DATE('now'))
            """, (plan_id, nuevo_miembro_id))
            
            # Obtener los miembros seleccionados
            miembros_familia = request.form.getlist("miembros_familia")
            
            for miembro_id in miembros_familia:
                # Cambiar modalidad del miembro existente a plan_familiar
                cursor.execute("""
                    UPDATE usuarios 
                    SET modalidad = 'plan_familiar' 
                    WHERE id = ?
                """, (miembro_id,))
                
                # Agregar al plan familiar
                cursor.execute("""
                    INSERT INTO miembros_familia (plan_familiar_id, miembro_id, fecha_vinculacion)
                    VALUES (?, ?, DATE('now'))
                """, (plan_id, miembro_id))
        
        # Si es plan grupal, verificar si se vincula a uno existente o se crea uno nuevo
        elif request.form["modalidad"] == "plan_grupal":
            plan_grupal_id = request.form.get("plan_grupal_id", "")
            
            if plan_grupal_id:
                # Vincular a un plan grupal existente
                cursor.execute("""
                    INSERT INTO miembros_grupo (plan_grupal_id, miembro_id, fecha_vinculacion)
                    VALUES (?, ?, DATE('now'))
                """, (plan_grupal_id, nuevo_miembro_id))
                
                flash(f"Miembro agregado exitosamente al plan grupal existente.")
                
            else:
                # Crear un nuevo plan grupal
                nombre_grupo = request.form.get("nombre_grupo", f"Grupo - {request.form['nombre']}")
                descripcion_grupo = request.form.get("descripcion_grupo", "")
                max_miembros = int(request.form.get("max_miembros", 10))
                
                cursor.execute("""
                    INSERT INTO planes_grupales (nombre_grupo, responsable_id, fecha_creacion, descripcion, max_miembros)
                    VALUES (?, ?, DATE('now'), ?, ?)
                """, (nombre_grupo, nuevo_miembro_id, descripcion_grupo, max_miembros))
                
                plan_id = cursor.lastrowid
                
                # Agregar el nuevo miembro al plan
                cursor.execute("""
                    INSERT INTO miembros_grupo (plan_grupal_id, miembro_id, fecha_vinculacion)
                    VALUES (?, ?, DATE('now'))
                """, (plan_id, nuevo_miembro_id))
                
                # Obtener los miembros seleccionados
                miembros_grupo = request.form.getlist("miembros_grupo")
                
                for miembro_id in miembros_grupo:
                    # Cambiar modalidad del miembro existente a plan_grupal
                    cursor.execute("""
                        UPDATE usuarios 
                        SET modalidad = 'plan_grupal' 
                        WHERE id = ?
                    """, (miembro_id,))
                    
                    # Agregar al plan grupal
                    cursor.execute("""
                        INSERT INTO miembros_grupo (plan_grupal_id, miembro_id, fecha_vinculacion)
                        VALUES (?, ?, DATE('now'))
                    """, (plan_id, miembro_id))
        
        con.commit()
        
    except sqlite3.IntegrityError:
        flash("El nombre de usuario ya existe.")
        return redirect("/admin" if session.get("rol")=="admin" else "/moderador")
    finally:
        con.close()
    if session.get("rol") == "moderador":
        return render_template_string("""
        <html><head><meta charset="utf-8"><title>NIP generado</title>
        <meta http-equiv="refresh" content="10;url=/moderador">
        <style>
        body{font-family:sans-serif;background:#f0f2f5;}
        .box{max-width:400px;margin:80px auto;background:#fff;padding:30px 20px;
        border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.08);text-align:center;}
        .nip{font-size:2.5em;font-weight:bold;color:#0066cc;margin:20px 0;}
        .countdown{background:#e3f2fd;padding:15px;border-radius:8px;margin:20px 0;color:#1565c0;}
        .btn{background:#0066cc;color:#fff;padding:10px 20px;border:none;border-radius:6px;text-decoration:none;display:inline-block;}
        .btn:hover{background:#0052a3;}
        </style>
        </head><body>
        <div class="box">
        <h2>¡Registro exitoso!</h2>
        <p>El NIP generado para el usuario <b>{{usuario}}</b> es:</p>
        <div class="nip">{{nip}}</div>
        <p><b>¡Guárdalo y entrégalo al usuario!</b></p>
        <div class="countdown">
        ⏱️ Regresando al panel en <span id="countdown">10</span> segundos
        </div>
        <a href="/moderador" class="btn">Volver Ahora</a>
        </div>
        
        <script>
        let seconds = 10;
        const countdownElement = document.getElementById('countdown');
        
        const timer = setInterval(() => {
            seconds--;
            countdownElement.textContent = seconds;
            
            if (seconds <= 0) {
                clearInterval(timer);
                window.location.href = '/moderador';
            }
        }, 1000);
        </script>
        </body></html>
        """, nip=nip, usuario=request.form["usuario"])
    return redirect("/admin" if session.get("rol")=="admin" else "/moderador")

# ——— Crear admin/moderador (solo admin) ———
@app.route("/crear_usuario", methods=["POST"])
def crear_usuario():
    if session.get("rol") != "admin":
        return redirect("/login")
    pin = request.form["pin"]
    if not (pin.isdigit() and len(pin) == 4):
        flash("El PIN debe ser numérico de 4 dígitos.")
        return redirect("/admin")
    try:
        con = conectar()
        con.execute("""
          INSERT INTO usuarios
            (nombre,usuario,pin,modalidad,vigencia,foto,rol,permisos)
          VALUES (?,?,?,?,?,?,?,?)
        """, (
            request.form["nombre"],
            request.form["usuario"],
            encriptar(pin),
            "mensual",
            calcular_vigencia("mensual"),
            "",
            request.form["rol"],
            ""
        ))
        con.commit()
    except sqlite3.IntegrityError:
        flash("El nombre de usuario o PIN ya existe.")
    finally:
        con.close()
    return redirect("/admin")

# ——— Ajustes de diseño ———
@app.route("/update_banner", methods=["POST"])
def update_banner():
    if session.get("rol") != "admin":
        return redirect("/login")
    f = request.files.get("banner")
    if f and f.filename:
        fn = secure_filename(f.filename)
        f.save(os.path.join(app.config["BANNER_FOLDER"], fn))
        con = conectar()
        con.execute("UPDATE banner SET filename=? WHERE id=1", (fn,))
        con.commit()
        con.close()
    return redirect("/diseno_plataforma")

@app.route("/remove_banner", methods=["POST"])
def remove_banner():
    if session.get("rol") != "admin":
        return redirect("/login")
    con = conectar()
    con.execute("UPDATE banner SET filename='' WHERE id=1")
    con.commit()
    con.close()
    return redirect("/diseno_plataforma")

@app.route("/update_logo", methods=["POST"])
def update_logo():
    if session.get("rol") != "admin":
        return redirect("/login")
    f = request.files.get("logo")
    if f and f.filename:
        fn = secure_filename(f.filename)
        f.save(os.path.join(app.config["LOGO_FOLDER"], fn))
        con = conectar()
        con.execute("UPDATE logo SET filename=? WHERE id=1", (fn,))
        con.commit()
        con.close()
    return redirect("/diseno_plataforma")

@app.route("/remove_logo", methods=["POST"])
def remove_logo():
    if session.get("rol") != "admin":
        return redirect("/login")
    con = conectar()
    con.execute("UPDATE logo SET filename='' WHERE id=1")
    con.commit()
    con.close()
    return redirect("/diseno_plataforma")

# ——— Renovar y eliminar usuario (solo admin) ———
@app.route("/renovar/<int:uid>", methods=["POST"])
def renovar(uid):
    if session.get("rol") != "admin":
        return redirect("/login")
    con = conectar()
    mod = con.execute("SELECT modalidad FROM usuarios WHERE id=?", (uid,)).fetchone()[0]
    # Usar la fecha actual para calcular la nueva vigencia desde hoy
    fecha_renovacion = datetime.now().strftime("%Y-%m-%d")
    nueva = calcular_vigencia(mod, fecha_renovacion)
    con.execute("UPDATE usuarios SET vigencia=? WHERE id=?", (nueva, uid))
    con.commit()
    con.close()
    return redirect("/admin")

@app.route("/eliminar_usuario/<int:uid>", methods=["POST"])
def eliminar_usuario(uid):
    if session.get("rol") != "admin":
        return redirect("/login")
    con = conectar()
    con.execute("DELETE FROM usuarios WHERE id=?", (uid,))
    con.commit()
    con.close()
    return redirect("/admin")

# ——— Reporte descargable de miembros (solo admin) ———
@app.route("/descargar_reporte")
def descargar_reporte():
    if session.get("rol") != "admin":
        return redirect("/login")
    con = conectar()
    miembros = con.execute("SELECT id,nombre,usuario,modalidad,vigencia,rol FROM usuarios").fetchall()
    con.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Nombre", "Usuario", "Modalidad", "Vigencia", "Rol"])
    for m in miembros:
        writer.writerow(m)
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="reporte_miembros.csv"
    )

# ——— Corte de Caja ———
@app.route("/corte_caja")
def corte_caja():
    if session.get("rol") != "admin":
        return redirect("/login")
    
    # Obtener fecha actual
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    fecha_inicio = request.args.get('fecha_inicio', fecha_hoy)
    fecha_fin = request.args.get('fecha_fin', fecha_hoy)
    
    con = conectar()
    
    # Obtener logo
    logo_row = con.execute("SELECT filename FROM logo WHERE id=1").fetchone()
    logo_fn = logo_row[0] if logo_row else ""
    
    # Datos de pagos en el rango de fechas
    pagos_periodo = con.execute("""
        SELECT usuario, monto, fecha, concepto
        FROM pagos 
        WHERE fecha BETWEEN ? AND ?
        ORDER BY fecha DESC, id DESC
    """, (fecha_inicio, fecha_fin)).fetchall()
    
    # Resumen del corte
    total_ingresos = sum(float(pago[1]) for pago in pagos_periodo)
    total_transacciones = len(pagos_periodo)
    
    # Ingresos por concepto
    ingresos_concepto = {}
    for pago in pagos_periodo:
        concepto = pago[3] or "Pago de membresía"
        if concepto in ingresos_concepto:
            ingresos_concepto[concepto] += float(pago[1])
        else:
            ingresos_concepto[concepto] = float(pago[1])
    
    con.close()
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Corte de Caja</title>
  {{ BASE_STYLES|safe }}
  <style>
    .print-only { display: none; }
    @media print {
      .no-print { display: none !important; }
      .print-only { display: block !important; }
      body { background: white !important; }
      .layout-container { display: block !important; }
      .sidebar { display: none !important; }
      .main-content { padding: 0 !important; }
      .content-header, .content-body { background: white !important; padding: 20px !important; }
      .card { box-shadow: none !important; border: 1px solid #ddd !important; }
    }
    .corte-header {
      text-align: center;
      border-bottom: 2px solid #3498db;
      padding-bottom: 20px;
      margin-bottom: 30px;
    }
    .corte-logo {
      width: 100px;
      height: 100px;
      margin: 0 auto 15px;
      display: block;
    }
    .fecha-selector {
      background: rgba(255,255,255,0.9);
      padding: 20px;
      border-radius: 10px;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 15px;
      flex-wrap: wrap;
    }
    .resumen-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    .resumen-item {
      background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
      color: white;
      padding: 25px;
      border-radius: 12px;
      text-align: center;
    }
    .resumen-valor {
      font-size: 2em;
      font-weight: bold;
      margin-bottom: 5px;
    }
    .resumen-label {
      font-size: 0.9em;
      opacity: 0.9;
    }
    .detalle-pagos {
      background: white;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
  </style>
</head>
<body>
  <div class="layout-container">
    <div class="sidebar no-print">
      <div class="sidebar-header">
        <h3>ADMIN PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="/admin"><i>🏠</i> Panel Principal</a></li>
        <li><a href="/reportes_financieros"><i>📊</i> Reportes Financieros</a></li>
        <li><a href="/estadisticas_globales"><i>📈</i> Estadísticas Globales</a></li>
        <li><a href="/analiticas_avanzadas"><i>🔍</i> Analíticas Avanzadas</a></li>
        <li><a href="/gestion_backups"><i>💾</i> Gestión de Backups</a></li>
        <li><a href="/gestion_usuarios_admin"><i>👑</i> Gestión Admins/Moderadores</a></li>
        <li><a href="/corte_caja" class="active"><i>💰</i> Corte de Caja</a></li>
        <li><a href="/diseno_plataforma"><i>🎨</i> Diseño de Plataforma</a></li>
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header no-print">
        <h1>💰 Corte de Caja</h1>
        <div class="breadcrumb">Panel Admin > Corte de Caja</div>
      </div>

      <div class="content-body">
        <!-- Selector de fechas -->
        <div class="fecha-selector no-print">
          <form method="GET" style="display: flex; align-items: center; gap: 15px; flex-wrap: wrap;">
            <label for="fecha_inicio" style="font-weight: 600;">Desde:</label>
            <input type="date" name="fecha_inicio" value="{{ fecha_inicio }}" style="width: auto;">
            
            <label for="fecha_fin" style="font-weight: 600;">Hasta:</label>
            <input type="date" name="fecha_fin" value="{{ fecha_fin }}" style="width: auto;">
            
            <button type="submit" class="btn">🔍 Filtrar</button>
            <button type="button" onclick="window.print()" class="btn btn-secondary">🖨️ Imprimir</button>
          </form>
        </div>

        <!-- Encabezado del corte -->
        <div class="corte-header print-only">
          {% if logo_fn %}
            <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="corte-logo">
          {% endif %}
          <h1 style="margin: 0; color: #2c3e50;">GIMNASIO LAMA</h1>
          <h2 style="margin: 10px 0; color: #3498db;">CORTE DE CAJA</h2>
          <p style="margin: 5px 0;">Periodo: {{ fecha_inicio }} al {{ fecha_fin }}</p>
          <p style="margin: 5px 0;">Fecha de emisión: {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}</p>
        </div>

        <!-- Resumen -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">📋 Resumen del Periodo</h3>
          </div>
          
          <div class="resumen-grid">
            <div class="resumen-item">
              <div class="resumen-valor">${{ "%.2f"|format(total_ingresos) }}</div>
              <div class="resumen-label">Total Ingresos</div>
            </div>
            <div class="resumen-item" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);">
              <div class="resumen-valor">{{ total_transacciones }}</div>
              <div class="resumen-label">Total Transacciones</div>
            </div>
            <div class="resumen-item" style="background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);">
              <div class="resumen-valor">${{ "%.2f"|format(total_ingresos / total_transacciones if total_transacciones > 0 else 0) }}</div>
              <div class="resumen-label">Promedio por Transacción</div>
            </div>
          </div>

          <!-- Ingresos por concepto -->
          {% if ingresos_concepto %}
          <h4 style="color: #2c3e50; margin: 30px 0 15px 0;">💼 Ingresos por Concepto</h4>
          <table>
            <thead>
              <tr>
                <th>Concepto</th>
                <th>Monto Total</th>
                <th>Porcentaje</th>
              </tr>
            </thead>
            <tbody>
              {% for concepto, monto in ingresos_concepto.items() %}
              <tr>
                <td>{{ concepto }}</td>
                <td>${{ "%.2f"|format(monto) }}</td>
                <td>{{ "%.1f"|format((monto / total_ingresos * 100) if total_ingresos > 0 else 0) }}%</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
          {% endif %}
        </div>

        <!-- Detalle de pagos -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">📝 Detalle de Transacciones</h3>
          </div>
          
          {% if pagos_periodo %}
          <div class="detalle-pagos">
            <table>
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Monto</th>
                  <th>Fecha</th>
                  <th>Concepto</th>
                </tr>
              </thead>
              <tbody>
                {% for usuario, monto, fecha, concepto in pagos_periodo %}
                <tr>
                  <td>{{ usuario }}</td>
                  <td style="font-weight: 600; color: #27ae60;">${{ "%.2f"|format(monto) }}</td>
                  <td>{{ fecha }}</td>
                  <td>{{ concepto or "Pago de membresía" }}</td>
                </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
          {% else %}
          <div style="text-align: center; padding: 40px; color: #7f8c8d;">
            <h3>📭 No hay transacciones en este periodo</h3>
            <p>Selecciona un rango de fechas diferente para ver los datos.</p>
          </div>
          {% endif %}
        </div>

        <!-- Pie del corte -->
        <div class="print-only" style="margin-top: 40px; text-align: center; border-top: 2px solid #3498db; padding-top: 20px;">
          <p style="margin: 5px 0; color: #7f8c8d;">Sistema LAMA Control - Gimnasio LAMA</p>
          <p style="margin: 5px 0; color: #7f8c8d;">Documento generado automáticamente</p>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
""", fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, total_ingresos=total_ingresos,
     total_transacciones=total_transacciones, pagos_periodo=pagos_periodo,
     ingresos_concepto=ingresos_concepto, logo_fn=logo_fn, BASE_STYLES=BASE_STYLES, datetime=datetime)


# —— Analíticas Avanzadas: Dashboard de Gráficas y Asistencias ——
@app.route("/analiticas_avanzadas")
def analiticas_avanzadas():
    if session.get("rol") != "admin":
        return redirect("/login")
    con = conectar()
    # Logo para el panel
    logo_row = con.execute("SELECT filename FROM logo WHERE id=1").fetchone()
    logo_fn = logo_row[0] if logo_row else ""

    # --------- Gráficas ---------
    # Ejemplo: Retención de miembros activos/vencidos
    retencion_labels = ["Activos", "Vencidos"]
    retencion_activos = con.execute("SELECT COUNT(*) FROM usuarios WHERE rol='miembro' AND vigencia >= ?", (datetime.now().strftime('%Y-%m-%d'),)).fetchone()[0]
    retencion_vencidos = con.execute("SELECT COUNT(*) FROM usuarios WHERE rol='miembro' AND vigencia < ?", (datetime.now().strftime('%Y-%m-%d'),)).fetchone()[0]

    # Frecuencia de asistencia (top 10)
    frecuencia_asistencia = con.execute("""
        SELECT u.nombre, COUNT(a.id) as total
        FROM usuarios u
        LEFT JOIN asistencias a ON u.usuario = a.usuario
        WHERE u.rol='miembro'
        GROUP BY u.nombre
        ORDER BY total DESC
        LIMIT 10
    """).fetchall()

    # Próximas renovaciones (top 10)
    proximas_renovaciones = con.execute("""
        SELECT nombre, vigencia FROM usuarios
        WHERE rol='miembro' AND vigencia >= ?
        ORDER BY vigencia ASC
        LIMIT 10
    """, (datetime.now().strftime('%Y-%m-%d'),)).fetchall()

    # Asistencias por semana (últimas 8 semanas)
    semana_labels = []
    semana_asistencias = []
    for i in range(7, 56, 7):
        inicio = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        fin = (datetime.now() - timedelta(days=i-7)).strftime('%Y-%m-%d')
        semana_labels.append(f"{inicio} a {fin}")
        count = con.execute("SELECT COUNT(*) FROM asistencias WHERE fecha BETWEEN ? AND ?", (inicio, fin)).fetchone()[0]
        semana_asistencias.append(count)

    # Crecimiento de miembros y asistencias por mes (últimos 6 meses)
    crecimiento_labels = []
    crecimiento_miembros = []
    crecimiento_asistencias = []
    for i in range(5, -1, -1):
        mes = (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m')
        crecimiento_labels.append(mes)
        miembros_mes = con.execute("SELECT COUNT(*) FROM usuarios WHERE rol='miembro' AND substr(vigencia,1,7)=?", (mes,)).fetchone()[0]
        asistencias_mes = con.execute("SELECT COUNT(*) FROM asistencias WHERE substr(fecha,1,7)=?", (mes,)).fetchone()[0]
        crecimiento_miembros.append(miembros_mes)
        crecimiento_asistencias.append(asistencias_mes)

    # --------- Tabla de asistencias (todos los tiempos) ---------
    asistencias = con.execute("""
        SELECT a.id, u.nombre, u.nip_visible, a.fecha, a.hora_entrada, a.hora_salida
        FROM asistencias a
        JOIN usuarios u ON a.usuario = u.usuario
        ORDER BY a.fecha DESC, a.hora_entrada DESC
        LIMIT 500
    """).fetchall()
    con.close()

    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Analíticas Avanzadas</title>
  {{ BASE_STYLES|safe }}
  <style>
    .search-box { margin-bottom: 18px; }
    .search-input { padding: 10px; border-radius: 6px; border: 1px solid #b2bec3; width: 260px; font-size: 1em; }
    .analytics-charts { display: flex; flex-wrap: wrap; gap: 30px; margin-bottom: 40px; }
    .chart-card { background: #fff; border-radius: 14px; box-shadow: 0 2px 12px #0001; padding: 24px; flex: 1 1 320px; min-width: 320px; }
    .attendance-table { background: #fff; border-radius: 14px; box-shadow: 0 2px 12px #0001; padding: 24px; }
    .attendance-table table { width: 100%; border-collapse: collapse; }
    .attendance-table th, .attendance-table td { padding: 8px; border-bottom: 1px solid #e9ecef; }
    .attendance-table th { background: #f8f9fa; }
    .attendance-table tr:last-child td { border-bottom: none; }
  </style>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>ADMIN PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="/admin"><i>🏠</i> Panel Principal</a></li>
        <li><a href="/reportes_financieros"><i>📊</i> Reportes Financieros</a></li>
        <li><a href="/estadisticas_globales"><i>📈</i> Estadísticas Globales</a></li>
        <li><a href="/analiticas_avanzadas" class="active"><i>🔍</i> Analíticas Avanzadas</a></li>
        <li><a href="/gestion_backups"><i>💾</i> Gestión de Backups</a></li>
        <li><a href="/gestion_usuarios_admin"><i>👑</i> Gestión Admins/Moderadores</a></li>
        <li><a href="/corte_caja"><i>💰</i> Corte de Caja</a></li>
        <li><a href="/diseno_plataforma"><i>🎨</i> Diseño de Plataforma</a></li>
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>
    <div class="main-content">
      <div class="content-header">
        <h1>🔍 Analíticas Avanzadas</h1>
        <div class="breadcrumb">Panel Admin > Analíticas Avanzadas</div>
      </div>
      <div class="content-body">
        <div class="analytics-charts">
          <div class="chart-card">
            <h3 class="card-title">Retención de Miembros</h3>
            <canvas id="retencionChart"></canvas>
          </div>
          <div class="chart-card">
            <h3 class="card-title">Frecuencia de Asistencia (Top 10)</h3>
            <canvas id="frecuenciaChart"></canvas>
          </div>
          <div class="chart-card">
            <h3 class="card-title">Próximas Renovaciones</h3>
            <table>
              <thead><tr><th>Nombre</th><th>Vigencia</th></tr></thead>
              <tbody>
                {% for nombre, vigencia in proximas_renovaciones %}
                <tr><td>{{ nombre }}</td><td>{{ vigencia }}</td></tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
          <div class="chart-card">
            <h3 class="card-title">Asistencias por Semana</h3>
            <canvas id="semanaChart"></canvas>
          </div>
          <div class="chart-card">
            <h3 class="card-title">Crecimiento Últimos 6 Meses</h3>
            <canvas id="crecimientoChart"></canvas>
          </div>
        </div>
        <div class="attendance-table">
          <h3 class="card-title">Asistencias de Todos los Tiempos</h3>
          <div class="search-box">
            <input type="text" id="searchInput" class="search-input" placeholder="Buscar por NIP o nombre...">
          </div>
          <table id="asistenciasTable">
            <thead>
              <tr><th>ID</th><th>Nombre</th><th>NIP</th><th>Fecha</th><th>Entrada</th><th>Salida</th></tr>
            </thead>
            <tbody>
              {% for id, nombre, nip, fecha, entrada, salida in asistencias %}
              <tr>
                <td>{{ id }}</td>
                <td>{{ nombre }}</td>
                <td>{{ nip }}</td>
                <td>{{ fecha }}</td>
                <td>{{ entrada }}</td>
                <td>{{ salida or '' }}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
  <script>
    // Buscador en la tabla de asistencias
    document.getElementById('searchInput').addEventListener('keyup', function() {
      var value = this.value.toLowerCase();
      var rows = document.querySelectorAll('#asistenciasTable tbody tr');
      rows.forEach(function(row) {
        var nombre = row.cells[1].textContent.toLowerCase();
        var nip = row.cells[2].textContent.toLowerCase();
        row.style.display = (nombre.includes(value) || nip.includes(value)) ? '' : 'none';
      });
    });
    // Chart.js: Retención
    new Chart(document.getElementById('retencionChart'), {
      type: 'doughnut',
      data: {
        labels: {{ retencion_labels|tojson }},
        datasets: [{ data: [{{ retencion_activos }}, {{ retencion_vencidos }}], backgroundColor: ['#27ae60','#e74c3c'] }]
      },
      options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
    });
    // Chart.js: Frecuencia de asistencia
    new Chart(document.getElementById('frecuenciaChart'), {
      type: 'bar',
      data: {
        labels: {{ frecuencia_asistencia|map(attribute=0)|list|tojson }},
        datasets: [{ label: 'Asistencias', data: {{ frecuencia_asistencia|map(attribute=1)|list|tojson }}, backgroundColor: '#3498db' }]
      },
      options: { responsive: true, plugins: { legend: { display: false } } }
    });
    // Chart.js: Asistencias por semana
    new Chart(document.getElementById('semanaChart'), {
      type: 'line',
      data: {
        labels: {{ semana_labels|tojson }},
        datasets: [{ label: 'Asistencias', data: {{ semana_asistencias|tojson }}, borderColor: '#8e44ad', backgroundColor: '#d2b4ee', fill: true }]
      },
      options: { responsive: true }
    });
    // Chart.js: Crecimiento
    new Chart(document.getElementById('crecimientoChart'), {
      type: 'bar',
      data: {
        labels: {{ crecimiento_labels|tojson }},
        datasets: [
          { label: 'Miembros', data: {{ crecimiento_miembros|tojson }}, backgroundColor: '#27ae60' },
          { label: 'Asistencias', data: {{ crecimiento_asistencias|tojson }}, backgroundColor: '#2980b9' }
        ]
      },
      options: { responsive: true }
    });
  </script>
</body>
</html>
''',
        retencion_labels=retencion_labels,
        retencion_activos=retencion_activos,
        retencion_vencidos=retencion_vencidos,
        frecuencia_asistencia=frecuencia_asistencia,
        proximas_renovaciones=proximas_renovaciones,
        semana_labels=semana_labels,
        semana_asistencias=semana_asistencias,
        crecimiento_labels=crecimiento_labels,
        crecimiento_miembros=crecimiento_miembros,
        crecimiento_asistencias=crecimiento_asistencias,
        BASE_STYLES=BASE_STYLES,
        logo_fn=logo_fn,
        asistencias=asistencias
    )

# ——— Reportes Financieros Avanzados ———
@app.route("/reportes_financieros")
def reportes_financieros():
    if session.get("rol") != "admin":
        return redirect("/login")
    
    con = conectar()
    
    # Obtener logo
    logo_row = con.execute("SELECT filename FROM logo ORDER BY id DESC LIMIT 1").fetchone()
    logo_fn = logo_row[0] if logo_row else ""
    
    # Ingresos por mes (últimos 12 meses)
    ingresos_mes = con.execute("""
        SELECT strftime('%Y-%m', fecha) as mes, SUM(monto) as total
        FROM pagos 
        WHERE fecha >= date('now', '-12 months')
        GROUP BY strftime('%Y-%m', fecha)
        ORDER BY mes
    """).fetchall()
    
    # Ingresos por modalidad
    ingresos_modalidad = con.execute("""
        SELECT u.modalidad, COUNT(p.id) as cantidad_pagos, SUM(p.monto) as total_ingresos
        FROM usuarios u
        LEFT JOIN pagos p ON u.usuario = p.usuario
        WHERE u.rol='miembro' AND p.fecha >= date('now', '-12 months')
        GROUP BY u.modalidad
    """).fetchall()
    
    # Comparación año anterior
    año_actual = datetime.now().year
    año_anterior = año_actual - 1
    
    ingresos_año_actual = con.execute("""
        SELECT SUM(monto) FROM pagos 
        WHERE strftime('%Y', fecha) = ?
    """, (str(año_actual),)).fetchone()[0] or 0
    
    ingresos_año_anterior = con.execute("""
        SELECT SUM(monto) FROM pagos 
        WHERE strftime('%Y', fecha) = ?
    """, (str(año_anterior),)).fetchone()[0] or 0
    
    # Proyección mensual
    promedio_mensual = con.execute("""
        SELECT AVG(total) FROM (
            SELECT SUM(monto) as total
            FROM pagos 
            WHERE fecha >= date('now', '-6 months')
            GROUP BY strftime('%Y-%m', fecha)
        )
    """).fetchone()[0] or 0
    
    # Top 10 miembros que más pagan
    top_pagadores = con.execute("""
        SELECT u.nombre, u.usuario, SUM(p.monto) as total_pagado
        FROM usuarios u
        JOIN pagos p ON u.usuario = p.usuario
        WHERE p.fecha >= date('now', '-12 months')
        GROUP BY u.usuario
        ORDER BY total_pagado DESC
        LIMIT 10
    """).fetchall()
    
    # Morosidad (miembros con vigencia vencida)
    miembros_morosos = con.execute("""
        SELECT nombre, usuario, vigencia, modalidad
        FROM usuarios 
        WHERE rol='miembro' AND date(vigencia) < date('now')
        ORDER BY vigencia ASC
    """).fetchall()
    
    con.close()
    
    # Procesar datos para gráficas
    if ingresos_mes:
        meses_labels = [m[0] for m in ingresos_mes]
        meses_data = [float(m[1]) for m in ingresos_mes]
    else:
        meses_labels = ["Sin datos"]
        meses_data = [0]
    
    if ingresos_modalidad:
        modalidad_labels = [m[0] for m in ingresos_modalidad]
        modalidad_data = [float(m[2]) for m in ingresos_modalidad]
    else:
        modalidad_labels = ["Sin datos"]
        modalidad_data = [0]
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Reportes Financieros</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
  {{ BASE_STYLES|safe }}
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>ADMIN PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="/admin"><i>🏠</i> Panel Principal</a></li>
        <li><a href="/reportes_financieros" class="active"><i>📊</i> Reportes Financieros</a></li>
        <li><a href="/estadisticas_globales"><i>📈</i> Estadísticas Globales</a></li>
        <li><a href="/analiticas_avanzadas"><i>🔍</i> Analíticas Avanzadas</a></li>
        <li><a href="/gestion_backups"><i>💾</i> Gestión de Backups</a></li>
        <li><a href="/gestion_usuarios_admin"><i>👑</i> Gestión Admins/Moderadores</a></li>
        <li><a href="/corte_caja"><i>💰</i> Corte de Caja</a></li>
        <li><a href="/diseno_plataforma"><i>🎨</i> Diseño de Plataforma</a></li>
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header">
        <h1>📊 Reportes Financieros</h1>
        <div class="breadcrumb">Panel Admin > Reportes Financieros</div>
      </div>

      <div class="content-body">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-number">${{ "%.2f"|format(ingresos_año_actual) }}</div>
            <div class="stat-label">Ingresos {{ año_actual }}</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);">
            <div class="stat-number">${{ "%.2f"|format(ingresos_año_anterior) }}</div>
            <div class="stat-label">Ingresos {{ año_anterior }}</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);">
            <div class="stat-number">${{ "%.2f"|format(promedio_mensual) }}</div>
            <div class="stat-label">Promedio Mensual</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">
            <div class="stat-number">{{ miembros_morosos|length }}</div>
            <div class="stat-label">Miembros Morosos</div>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 25px;">
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">📈 Ingresos por Mes (Últimos 12 meses)</h3>
            </div>
            <canvas id="chartIngresosMes" width="400" height="300"></canvas>
          </div>
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">🥧 Ingresos por Modalidad</h3>
            </div>
            <canvas id="chartIngresosModalidad" width="400" height="300"></canvas>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px;">
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">🏆 Top 10 Pagadores</h3>
            </div>
            <table>
              <thead><tr><th>Nombre</th><th>Usuario</th><th>Total Pagado</th></tr></thead>
              <tbody>
                {% for nombre, usuario, total in top_pagadores %}
                <tr><td>{{ nombre }}</td><td>{{ usuario }}</td><td>${{ "%.2f"|format(total) }}</td></tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">⚠️ Miembros Morosos</h3>
            </div>
            <table>
              <thead><tr><th>Nombre</th><th>Usuario</th><th>Vigencia</th><th>Modalidad</th></tr></thead>
              <tbody>
                {% for nombre, usuario, vigencia, modalidad in miembros_morosos %}
                <tr style="background: rgba(231, 76, 60, 0.1);"><td>{{ nombre }}</td><td>{{ usuario }}</td><td>{{ vigencia }}</td><td>{{ modalidad }}</td></tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    document.addEventListener('DOMContentLoaded', function() {
      // Gráfica de ingresos por mes
      const ctxMes = document.getElementById('chartIngresosMes');
      if (ctxMes) {
        new Chart(ctxMes, {
          type: 'line',
          data: {
            labels: {{ meses_labels|safe }},
            datasets: [{
              label: 'Ingresos ($)',
              data: {{ meses_data|safe }},
              backgroundColor: 'rgba(39, 174, 96, 0.2)',
              borderColor: '#27ae60',
              borderWidth: 3,
              fill: true,
              tension: 0.4
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: { 
                beginAtZero: true,
                ticks: {
                  callback: function(value) {
                    return '$' + value.toFixed(2);
                  }
                }
              }
            }
          }
        });
      }

      // Gráfica de ingresos por modalidad
      const ctxModalidad = document.getElementById('chartIngresosModalidad');
      if (ctxModalidad) {
        new Chart(ctxModalidad, {
          type: 'doughnut',
          data: {
            labels: {{ modalidad_labels|safe }},
            datasets: [{
              data: {{ modalidad_data|safe }},
              backgroundColor: ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c'],
              borderWidth: 2,
              borderColor: '#fff'
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { 
                position: 'bottom'
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return context.label + ': $' + context.parsed.toFixed(2);
                  }
                }
              }
            }
          }
        });
      }
    });
  </script>
</body>
</html>
""", ingresos_año_actual=ingresos_año_actual, ingresos_año_anterior=ingresos_año_anterior,
     promedio_mensual=promedio_mensual, miembros_morosos=miembros_morosos,
     top_pagadores=top_pagadores, meses_labels=meses_labels, meses_data=meses_data,
     modalidad_labels=modalidad_labels, modalidad_data=modalidad_data,
     año_actual=año_actual, año_anterior=año_anterior, logo_fn=logo_fn, BASE_STYLES=BASE_STYLES)

# ——— Panel de Moderador ———
@app.route("/moderador")
def moderador():
    if session.get("rol") != "moderador":
        return redirect("/login")
    
    con = conectar()
    logo_row = con.execute("SELECT filename FROM logo WHERE id=1").fetchone()
    logo_fn = logo_row[0] if logo_row else ""
    
    miembros = con.execute("""
        SELECT id, nombre, usuario, nip_visible, modalidad, vigencia, foto
        FROM usuarios WHERE rol='miembro'
        ORDER BY nombre
    """).fetchall()
    
    # Obtener últimos 10 pagos registrados
    pagos_recientes = con.execute("""
        SELECT usuario, monto, fecha, concepto 
        FROM pagos 
        ORDER BY fecha DESC, id DESC 
        LIMIT 10
    """).fetchall()
    
    con.close()
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Panel Moderador</title>
  {{ BASE_STYLES|safe }}
  <style>
    .moderador-grid { 
      display: grid; 
      grid-template-columns: 1fr 1fr; 
      gap: 25px; 
      margin-bottom: 25px; 
    }
    .form-section {
      background: white;
      padding: 25px;
      border-radius: 12px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .print-btn {
      background: #27ae60;
      color: white;
      padding: 8px 16px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.9em;
      margin-left: 10px;
      text-decoration: none;
      display: inline-block;
    }
    .print-btn:hover {
      background: #219a52;
    }
    .recent-payments {
      max-height: 300px;
      overflow-y: auto;
    }
    .payment-item {
      background: #f8f9fa;
      padding: 12px;
      border-radius: 6px;
      margin-bottom: 8px;
      border-left: 4px solid #27ae60;
    }
    .payment-item strong {
      color: #27ae60;
    }
  </style>
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>MODERADOR PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="/moderador" class="active"><i>🏠</i> Panel Principal</a></li>
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header">
        <h1>🏋️ Panel de Moderador</h1>
        <div class="breadcrumb">Sistema LAMA Control - Bienvenido {{ session.nombre }}</div>
      </div>

      <div class="content-body">
        <!-- Formularios de gestión -->
        <div class="moderador-grid">
          <!-- Crear Miembro -->
          <div class="form-section">
            <h3 style="color: #2c3e50; margin-bottom: 20px;">👥 Registrar Nuevo Miembro</h3>
            <form method="POST" action="/crear_miembro" enctype="multipart/form-data">
              <div class="form-group">
                <label class="form-label">Nombre completo</label>
                <input type="text" name="nombre" required>
              </div>
              <div class="form-group">
                <label class="form-label">Nombre de usuario</label>
                <input type="text" name="usuario" required>
              </div>
              <div class="form-group">
                <label class="form-label">Modalidad</label>
                <select name="modalidad" id="modalidad" required>
                  <option value="">Seleccionar modalidad</option>
                  <option value="semanal">Semanal</option>
                  <option value="mensual">Mensual</option>
                  <option value="trimestre">Trimestre</option>
                  <option value="semestre">Semestre</option>
                  <option value="anualidad">Anualidad</option>
                  <option value="plan_familiar">Plan Familiar</option>
                  <option value="plan_grupal">Plan Grupal</option>
                </select>
              </div>
              
              <!-- Contenedor para selección de familia (oculto por defecto) -->
              <div id="family-selection-container" style="display: none;">
                <div style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); border-radius: 15px; padding: 25px; margin: 20px 0; box-shadow: 0 8px 25px rgba(39, 174, 96, 0.2);">
                  <div style="display: flex; align-items: center; margin-bottom: 20px;">
                    <div style="background: rgba(255,255,255,0.2); border-radius: 50%; padding: 15px; margin-right: 15px;">
                      <span style="font-size: 2em;">👪</span>
                    </div>
                    <div>
                      <h3 style="color: white; margin: 0; font-size: 1.3em;">Plan Familiar Seleccionado</h3>
                      <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.95em;">
                        Configura los miembros que formarán parte de este plan familiar
                      </p>
                    </div>
                  </div>
                  
                  <div style="background: rgba(255,255,255,0.95); border-radius: 12px; padding: 20px;">
                    <div style="display: flex; align-items: center; margin-bottom: 15px;">
                      <span style="background: #27ae60; color: white; padding: 8px 12px; border-radius: 8px; font-size: 0.9em; font-weight: 600; margin-right: 10px;">🔍</span>
                      <span style="color: #2c3e50; font-weight: 600;">Buscar Miembros de la Familia</span>
                    </div>
                    
                    <p style="font-size: 0.9em; color: #7f8c8d; margin-bottom: 15px; line-height: 1.4;">
                      💡 <strong>Búsqueda Inteligente:</strong> El sistema detectará automáticamente miembros con apellidos similares cuando ingreses el nombre completo.
                    </p>
                    
                    <div id="family-members-list" style="border: 2px dashed #27ae60; border-radius: 10px; padding: 20px; background: linear-gradient(135deg, #f8fffe 0%, #f0fdf4 100%); min-height: 120px;">
                      <div style="text-align: center; color: #27ae60;">
                        <div style="font-size: 2.5em; margin-bottom: 10px;">👨‍👩‍👧‍👦</div>
                        <p style="margin: 0; font-weight: 600;">Familiares Detectados</p>
                        <p style="margin: 5px 0 0 0; font-size: 0.85em; color: #7f8c8d;">
                          Ingresa el nombre completo arriba para encontrar familiares automáticamente
                        </p>
                      </div>
                    </div>
                    
                    <div style="background: #e8f5e8; border-radius: 8px; padding: 15px; margin-top: 15px; border-left: 4px solid #27ae60;">
                      <div style="display: flex; align-items: center;">
                        <span style="font-size: 1.2em; margin-right: 8px;">ℹ️</span>
                        <div>
                          <strong style="color: #27ae60;">Información Importante:</strong>
                          <ul style="margin: 5px 0 0 0; padding-left: 20px; color: #2c3e50; font-size: 0.9em;">
                            <li>Todos los miembros familiares compartirán la misma fecha de vigencia</li>
                            <li>El pago se realiza una sola vez para toda la familia</li>
                            <li>Puedes agregar hasta 6 miembros por plan familiar</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Contenedor para plan grupal (oculto por defecto) -->
              <div id="group-selection-container" style="display: none;">
                <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); border-radius: 15px; padding: 25px; margin: 20px 0; box-shadow: 0 8px 25px rgba(52, 152, 219, 0.2);">
                  <div style="display: flex; align-items: center; margin-bottom: 20px;">
                    <div style="background: rgba(255,255,255,0.2); border-radius: 50%; padding: 15px; margin-right: 15px;">
                      <span style="font-size: 2em;">👥</span>
                    </div>
                    <div>
                      <h3 style="color: white; margin: 0; font-size: 1.3em;">Plan Grupal Seleccionado</h3>
                      <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.95em;">
                        Configura el plan grupal y sus miembros
                      </p>
                    </div>
                  </div>
                  
                  <div style="background: rgba(255,255,255,0.95); border-radius: 12px; padding: 20px;">
                    <!-- Configuración básica del grupo -->
                    <div style="display: flex; align-items: center; margin-bottom: 15px;">
                      <span style="background: #3498db; color: white; padding: 8px 12px; border-radius: 8px; font-size: 0.9em; font-weight: 600; margin-right: 10px;">⚙️</span>
                      <span style="color: #2c3e50; font-weight: 600;">Configuración del Grupo</span>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                      <div class="form-group" style="margin: 0;">
                        <label class="form-label">Nombre del Grupo</label>
                        <input type="text" name="nombre_grupo" placeholder="Ej: Grupo Entrenamiento, Crossfit Team, etc." style="border-color: #3498db;">
                      </div>
                      
                      <div class="form-group" style="margin: 0;">
                        <label class="form-label">Máximo de miembros</label>
                        <select name="max_miembros" style="border-color: #3498db;">
                          <option value="5">5 miembros</option>
                          <option value="10" selected>10 miembros</option>
                          <option value="15">15 miembros</option>
                          <option value="20">20 miembros</option>
                        </select>
                      </div>
                    </div>
                    
                    <div class="form-group" style="margin-bottom: 20px;">
                      <label class="form-label">Descripción (opcional)</label>
                      <textarea name="descripcion_grupo" rows="2" placeholder="Descripción del grupo..." style="border-color: #3498db;"></textarea>
                    </div>
                    
                    <!-- Búsqueda de miembros -->
                    <div style="border-top: 2px solid #e3f2fd; padding-top: 20px;">
                      <div style="display: flex; align-items: center; margin-bottom: 15px;">
                        <span style="background: #e67e22; color: white; padding: 8px 12px; border-radius: 8px; font-size: 0.9em; font-weight: 600; margin-right: 10px;">🔍</span>
                        <span style="color: #2c3e50; font-weight: 600;">Buscar y Agregar Miembros</span>
                      </div>
                      
                      <input type="text" id="buscar-miembros" placeholder="Buscar por nombre o apellido..." 
                             style="margin-bottom: 15px; border-color: #e67e22;" 
                             onkeyup="buscarMiembrosGrupo(this.value)">
                      
                      <div id="group-members-list" style="border: 2px dashed #3498db; border-radius: 10px; padding: 20px; background: linear-gradient(135deg, #f8fcff 0%, #e3f2fd 100%); min-height: 120px;">
                        <div style="text-align: center; color: #3498db;">
                          <div style="font-size: 2.5em; margin-bottom: 10px;">🏋️‍♂️</div>
                          <p style="margin: 0; font-weight: 600;">Miembros del Grupo</p>
                          <p style="margin: 5px 0 0 0; font-size: 0.85em; color: #7f8c8d;">
                            Busca y selecciona miembros para agregar al grupo
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div style="background: #e3f2fd; border-radius: 8px; padding: 15px; margin-top: 15px; border-left: 4px solid #3498db;">
                      <div style="display: flex; align-items: center;">
                        <span style="font-size: 1.2em; margin-right: 8px;">💡</span>
                        <div>
                          <strong style="color: #3498db;">Beneficios del Plan Grupal:</strong>
                          <ul style="margin: 5px 0 0 0; padding-left: 20px; color: #2c3e50; font-size: 0.9em;">
                            <li>Descuentos por volumen para grupos grandes</li>
                            <li>Gestión centralizada de la vigencia del grupo</li>
                            <li>Ideal para equipos deportivos y entrenamientos grupales</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="form-group">
                <label class="form-label">Correo electrónico (opcional)</label>
                <input type="email" name="correo">
              </div>
              <div class="form-group">
                <label class="form-label">Teléfono de emergencia (opcional)</label>
                <input type="text" name="telefono_emergencia">
              </div>
              <div class="form-group">
                <label class="form-label">Datos médicos (opcional)</label>
                <textarea name="datos_medicos" rows="3"></textarea>
              </div>
              <div class="form-group">
                <label class="form-label">Foto</label>
                <input type="file" name="foto" accept="image/*">
              </div>
              <button type="submit" class="btn">👥 Crear Miembro</button>
            </form>
          </div>

          <!-- Registrar Pago -->
          <div class="form-section">
            <h3 style="color: #2c3e50; margin-bottom: 20px;">💰 Registrar Pago</h3>
            <form method="POST" action="/registrar_pago">
              <div class="form-group">
                <label class="form-label">Seleccionar miembro</label>
                <select name="usuario" required>
                  <option value="">Seleccionar miembro...</option>
                  {% for id, nombre, usuario, nip, modalidad, vigencia, foto in miembros %}
                  <option value="{{ usuario }}">{{ nombre }} ({{ usuario }})</option>
                  {% endfor %}
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Concepto del pago</label>
                <select name="concepto" required onchange="actualizarMonto(this.value)">
                  <option value="">Seleccionar concepto...</option>
                  <optgroup label="🏋️ Membresías Individuales">
                    <option value="Mensualidad">Mensualidad - $400.00</option>
                    <option value="Semana">Semana - $120.00</option>
                    <option value="Clase">Clase - $50.00</option>
                    <option value="Tres clases">Tres clases - $100.00</option>
                  </optgroup>
                  <optgroup label="🧘 Yoga">
                    <option value="Semana con Yoga">Semana con Yoga - $150.00</option>
                    <option value="Clase de Yoga">Clase de Yoga - $80.00</option>
                  </optgroup>
                  <optgroup label="👥 Planes Familiares/Grupales">
                    <option value="Pareja">Pareja - $700.00 (por persona)</option>
                    <option value="Tres personas">Tres personas - $1000.00 (por persona)</option>
                    <option value="Cuatro personas">Cuatro personas - $1300.00 (por persona)</option>
                    <option value="Cinco personas">Cinco personas - $1600.00 (por persona)</option>
                  </optgroup>
                  <optgroup label="🛍️ Otros">
                    <option value="Productos/Suplementos">Productos/Suplementos</option>
                    <option value="Entrenamiento personal">Entrenamiento personal</option>
                    <option value="Otros servicios">Otros servicios</option>
                    <option value="Pago personalizado">Pago personalizado</option>
                  </optgroup>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Monto del pago</label>
                <input type="number" id="montoInput" name="monto" step="0.01" min="0" placeholder="Automático según concepto" readonly>
                <small style="color: #7f8c8d; display: block; margin-top: 5px;">
                  💡 El monto se calcula automáticamente. Para planes familiares/grupales se multiplicará por el número de miembros.
                </small>
              </div>
              <div style="background: #e8f5e8; padding: 12px; border-radius: 6px; margin-bottom: 15px; border-left: 4px solid #27ae60;">
                <small style="color: #27ae60; font-weight: 600;">
                  📅 Fecha: {{ fecha_actual }} (automática)
                </small>
              </div>
              <button type="submit" class="btn">💰 Registrar Pago</button>
            </form>
          </div>
        </div>

        <!-- Registrar Asistencia Manual -->
        <div class="card" style="margin-bottom: 25px;">
          <div class="card-header">
            <h3 class="card-title">📋 Registrar Asistencia Manual</h3>
          </div>
          <form method="POST" action="/registrar_asistencia" style="padding: 20px;">
            <div style="display: grid; grid-template-columns: 1fr auto; gap: 15px; align-items: end;">
              <div class="form-group" style="margin: 0;">
                <label class="form-label">Seleccionar miembro</label>
                <select name="usuario" required>
                  <option value="">Seleccionar miembro...</option>
                  {% for id, nombre, usuario, nip, modalidad, vigencia, foto in miembros %}
                  <option value="{{ usuario }}">{{ nombre }} ({{ usuario }})</option>
                  {% endfor %}
                </select>
              </div>
              <div>
                <button type="submit" class="btn">📋 Registrar Asistencia</button>
              </div>
            </div>
          </form>
        </div>

        <!-- Pagos Recientes -->
        <div class="card" style="margin-bottom: 25px;">
          <div class="card-header">
            <h3 class="card-title">💳 Últimos Pagos Registrados</h3>
            <button type="button" class="btn" onclick="imprimirCorteCaja()" style="background: #27ae60;">
              🖨️ Imprimir Corte de Caja
            </button>
          </div>
          <div class="recent-payments" style="padding: 20px;">
            {% if pagos_recientes %}
              {% for usuario, monto, fecha, concepto in pagos_recientes %}
              <div class="payment-item">
                <strong>${{ "%.2f"|format(monto) }}</strong> - {{ usuario }} 
                <span style="color: #666; font-size: 0.9em;">({{ fecha }})</span>
                <br>
                <small style="color: #666;">{{ concepto or "Pago de membresía" }}</small>
              </div>
              {% endfor %}
            {% else %}
              <p style="color: #666; text-align: center; padding: 20px;">
                No hay pagos registrados aún.
              </p>
            {% endif %}
          </div>
        </div>

        <!-- Lista de miembros -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">👥 Miembros Registrados ({{ miembros|length }})</h3>
          </div>
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Usuario</th>
                <th>Modalidad</th>
                <th>Vigencia</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {% for id, nombre, usuario, nip, modalidad, vigencia, foto in miembros %}
              <tr>
                <td>{{ nombre }}</td>
                <td>{{ usuario }}</td>
                <td>{{ modalidad }}</td>
                <td>{{ vigencia }}</td>
                <td>
                  {% set dias = vigencia|dias_restantes %}
                  {% if dias < 0 %}
                    <span style="color: #e74c3c; font-weight: 600;">Vencida</span>
                  {% elif dias <= 7 %}
                    <span style="color: #f39c12; font-weight: 600;">{{ dias }}d restantes</span>
                  {% else %}
                    <span style="color: #27ae60; font-weight: 600;">Vigente</span>
                  {% endif %}
                </td>
                <td>
                  {% if session['rol'] == 'admin' %}
                    <a href="/detalle_miembro/{{ usuario }}" class="btn" style="padding: 5px 10px; font-size: 0.8em; background: #3498db;">👁️ Ver</a>
                    <a href="/editar_miembro_por_id/{{ id }}" class="btn" style="padding: 5px 10px; font-size: 0.8em; background: #f39c12; margin-left: 5px;">✏️ Editar</a>
                  {% else %}
                    <span style="color: #999; font-size: 0.8em;">Sin permisos</span>
                  {% endif %}
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <script>
    function imprimirCorteCaja() {
      // Obtener datos para el corte de caja
      const fechaHoy = new Date().toISOString().split('T')[0];
      const fechaFormateada = new Date().toLocaleDateString('es-ES');
      const horaCorte = new Date().toLocaleTimeString('es-ES');
      
      // Obtener todos los pagos del día desde la interfaz actual
      const paymentItems = document.querySelectorAll('.payment-item');
      const pagosHoy = [];
      let totalDia = 0;
      
      paymentItems.forEach(item => {
        const texto = item.innerHTML;
        // Buscar fecha en el formato (YYYY-MM-DD)
        const fechaMatch = texto.match(/\\((\\d{4}-\\d{2}-\\d{2})\\)/);
        if (fechaMatch && fechaMatch[1] === fechaHoy) {
          // Extraer monto
          const montoMatch = texto.match(/\\$(\\d+(?:\\.\\d{2})?)/);
          if (montoMatch) {
            const monto = parseFloat(montoMatch[1]);
            totalDia += monto;
            
            // Extraer nombre del usuario (después del monto y antes de la fecha)
            const nombreMatch = texto.match(/\\$[\\d\\.]+\\s*-\\s*([^<(]+)/);
            
            // Extraer concepto (después del <br> y dentro de <small>)
            const conceptoMatch = texto.match(/<small[^>]*>([^<]+)<\\/small>/);
            
            pagosHoy.push({
              nombre: nombreMatch ? nombreMatch[1].trim() : 'Usuario',
              monto: monto,
              concepto: conceptoMatch ? conceptoMatch[1].trim() : 'Pago de membresía'
            });
          }
        }
      });
      
      // Crear nueva ventana para impresión
      const ventana = window.open('', '_blank', 'width=800,height=600');
      if (!ventana) {
        alert('Error: No se pudo abrir la ventana de impresión. Permite las ventanas emergentes y vuelve a intentar.');
        return;
      }
      
      ventana.document.write(`
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8">
            <title>Corte de Caja - ${fechaFormateada}</title>
            <style>
              body { 
                margin: 0;
                padding: 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: white;
                color: #2c3e50;
                line-height: 1.6;
              }
              .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 8px;
              }
              .header { 
                text-align: center;
                border-bottom: 3px solid #3498db;
                padding-bottom: 20px;
                margin-bottom: 30px;
              }
              .empresa-name {
                font-size: 2em;
                font-weight: bold;
                color: #2c3e50;
                margin: 10px 0;
              }
              .documento-title {
                font-size: 1.5em;
                color: #3498db;
                margin: 10px 0;
                font-weight: bold;
              }
              .info-general {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                border-left: 5px solid #3498db;
              }
              .info-row {
                display: flex;
                justify-content: space-between;
                margin: 8px 0;
                padding: 5px 0;
              }
              .info-label {
                font-weight: 600;
                color: #2c3e50;
              }
              .info-value {
                color: #34495e;
              }
              .resumen-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 25px 0;
              }
              .resumen-item {
                background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
              }
              .resumen-valor {
                font-size: 1.8em;
                font-weight: bold;
                margin-bottom: 5px;
              }
              .resumen-label {
                font-size: 0.9em;
                opacity: 0.9;
              }
              .detalle-section {
                margin: 30px 0;
              }
              .section-title {
                font-size: 1.3em;
                color: #2c3e50;
                margin-bottom: 15px;
                padding-bottom: 8px;
                border-bottom: 2px solid #ecf0f1;
              }
              .payment-list {
                background: #f8f9fa;
                border-radius: 8px;
                overflow: hidden;
                border: 1px solid #e9ecef;
              }
              .payment-item-print {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 20px;
                border-bottom: 1px solid #e9ecef;
                background: white;
                margin-bottom: 1px;
              }
              .payment-item-print:last-child {
                border-bottom: none;
              }
              .payment-info {
                flex: 1;
              }
              .payment-name {
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 3px;
              }
              .payment-concept {
                font-size: 0.9em;
                color: #7f8c8d;
              }
              .payment-amount {
                font-size: 1.1em;
                font-weight: bold;
                color: #27ae60;
                text-align: right;
              }
              .total-final {
                background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
                color: white;
                padding: 20px;
                text-align: center;
                font-size: 1.4em;
                font-weight: bold;
                border-radius: 8px;
                margin: 25px 0;
                box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
              }
              .footer {
                margin-top: 40px;
                text-align: center;
                padding-top: 20px;
                border-top: 2px solid #ecf0f1;
                color: #7f8c8d;
                font-size: 0.9em;
              }
              .no-transactions {
                text-align: center;
                padding: 40px;
                color: #7f8c8d;
                font-style: italic;
              }
              @media print {
                body { margin: 0; padding: 0; }
                .container { padding: 20px; }
                @page { margin: 1cm; }
              }
            </style>
          </head>
          <body>
            <div class="container">
              <!-- Header -->
              <div class="header">
                <div class="empresa-name">GIMNASIO LAMA</div>
                <div class="documento-title">CORTE DE CAJA</div>
                <div style="color: #7f8c8d; margin-top: 10px;">Sistema LAMA Control</div>
              </div>
              
              <!-- Información General -->
              <div class="info-general">
                <div class="info-row">
                  <span class="info-label">📅 Fecha del corte:</span>
                  <span class="info-value">${fechaFormateada}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">⏰ Hora de emisión:</span>
                  <span class="info-value">${horaCorte}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">👤 Generado por:</span>
                  <span class="info-value">Moderador</span>
                </div>
                <div class="info-row">
                  <span class="info-label">📊 Total de transacciones:</span>
                  <span class="info-value">${pagosHoy.length}</span>
                </div>
              </div>
              
              <!-- Resumen -->
              <div class="resumen-grid">
                <div class="resumen-item">
                  <div class="resumen-valor">$${totalDia.toFixed(2)}</div>
                  <div class="resumen-label">Total Ingresos</div>
                </div>
                <div class="resumen-item" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);">
                  <div class="resumen-valor">${pagosHoy.length}</div>
                  <div class="resumen-label">Transacciones</div>
                </div>
                <div class="resumen-item" style="background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);">
                  <div class="resumen-valor">$${pagosHoy.length > 0 ? (totalDia / pagosHoy.length).toFixed(2) : '0.00'}</div>
                  <div class="resumen-label">Promedio por Transacción</div>
                </div>
              </div>
              
              <!-- Detalle de Transacciones -->
              <div class="detalle-section">
                <h3 class="section-title">📝 Detalle de Transacciones del Día</h3>
                <div class="payment-list">
                  ${pagosHoy.length > 0 ? 
                    pagosHoy.map((pago, index) => `
                      <div class="payment-item-print">
                        <div class="payment-info">
                          <div class="payment-name">${pago.nombre}</div>
                          <div class="payment-concept">${pago.concepto}</div>
                        </div>
                        <div class="payment-amount">$${pago.monto.toFixed(2)}</div>
                      </div>
                    `).join('') 
                    : '<div class="no-transactions">📭 No hay transacciones registradas para el día de hoy</div>'
                  }
                </div>
              </div>
              
              <!-- Total Final -->
              <div class="total-final">
                💰 TOTAL DEL DÍA: $${totalDia.toFixed(2)}
              </div>
              
              <!-- Footer -->
              <div class="footer">
                <p>Documento generado automáticamente por el Sistema LAMA Control</p>
                <p>Gimnasio LAMA - Gestión Integral de Membresías</p>
                <p>${fechaFormateada} ${horaCorte}</p>
              </div>
            </div>
          </body>
        </html>
      `);
      
      // Dar tiempo para que cargue el contenido y luego imprimir
      ventana.document.close();
      setTimeout(() => {
        ventana.focus();
        ventana.print();
        ventana.close();
      }, 1000);
    }
  </script>

  <style media="print">
    .sidebar, .content-header, .print-btn, button {
      display: none !important;
    }
    .main-content {
      margin-left: 0 !important;
      width: 100% !important;
    }
    body {
      background: white !important;
    }
  </style>
  
  <script>
  // Función para mostrar/ocultar selección de miembros familia y grupo
  function toggleFamilySelection() {
    const modalidad = document.getElementById('modalidad');
    const familyContainer = document.getElementById('family-selection-container');
    const groupContainer = document.getElementById('group-selection-container');
    
    if (modalidad && familyContainer && groupContainer) {
      // Ocultar ambos containers primero
      familyContainer.style.display = 'none';
      groupContainer.style.display = 'none';
      
      if (modalidad.value === 'plan_familiar') {
        familyContainer.style.display = 'block';
        loadFamilyMembers();
      } else if (modalidad.value === 'plan_grupal') {
        groupContainer.style.display = 'block';
        initGroupSearch();
      }
    }
  }
  
  // Función para cargar miembros existentes con apellidos similares
  function loadFamilyMembers() {
    const nombre = document.querySelector('input[name="nombre"]').value.trim();
    const familyList = document.getElementById('family-members-list');
    
    if (nombre.length < 3) {
      familyList.innerHTML = `
        <div style="text-align: center; color: #27ae60;">
          <div style="font-size: 2.5em; margin-bottom: 10px;">👨‍👩‍👧‍👦</div>
          <p style="margin: 0; font-weight: 600;">Familiares Detectados</p>
          <p style="margin: 5px 0 0 0; font-size: 0.85em; color: #7f8c8d;">
            Ingresa al menos 3 caracteres del nombre para buscar familiares
          </p>
        </div>`;
      return;
    }
    
    // Mostrar indicador de carga
    familyList.innerHTML = `
      <div style="text-align: center; color: #27ae60; padding: 20px;">
        <div style="font-size: 2em; margin-bottom: 10px;">🔍</div>
        <p style="margin: 0; font-weight: 600;">Buscando familiares...</p>
        <p style="margin: 5px 0 0 0; font-size: 0.85em; color: #7f8c8d;">
          Detectando miembros con apellidos similares
        </p>
      </div>`;
    
    // Buscar familiares usando el endpoint correcto
    fetch('/buscar_familiares', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: 'nombre=' + encodeURIComponent(nombre)
    })
    .then(response => response.json())
    .then(data => {
      if (data.miembros && data.miembros.length > 0) {
        let html = `
          <div style="margin-bottom: 20px;">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
              <span style="background: #27ae60; color: white; padding: 6px 10px; border-radius: 50%; margin-right: 10px;">✅</span>
              <h4 style="margin: 0; color: #27ae60; font-size: 1.1em;">¡Familiares Encontrados!</h4>
            </div>
            <p style="color: #7f8c8d; font-size: 0.9em; margin: 0 0 15px 0;">
              Se encontraron ${data.miembros.length} miembro(s) con apellidos similares:
            </p>
          </div>`;
        
        data.miembros.forEach((miembro, index) => {
          html += `
            <div style="margin: 10px 0; padding: 15px; background: white; border-radius: 10px; border: 2px solid #e8f5e8; transition: all 0.3s ease; cursor: pointer;" 
                 onmouseover="this.style.borderColor='#27ae60'; this.style.transform='translateY(-2px)'" 
                 onmouseout="this.style.borderColor='#e8f5e8'; this.style.transform='translateY(0)'">
              <label style="display: flex; align-items: center; cursor: pointer; margin: 0;">
                <input type="checkbox" name="familia_miembros" value="${miembro.id}" 
                       style="width: 18px; height: 18px; cursor: pointer; margin-right: 15px;">
                <div style="flex: 1;">
                  <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <span style="background: #27ae60; color: white; padding: 4px 8px; border-radius: 20px; font-size: 0.8em; margin-right: 10px;">👤</span>
                    <strong style="color: #2c3e50;">${miembro.nombre}</strong>
                  </div>
                  <div style="margin-left: 30px; color: #7f8c8d; font-size: 0.9em;">
                    Usuario: <strong>${miembro.usuario}</strong> • 
                    Modalidad: ${miembro.modalidad} • 
                    Vigencia: ${miembro.vigencia}
                  </div>
                </div>
              </label>
            </div>`;
        });
        
        familyList.innerHTML = html;
      } else {
        familyList.innerHTML = `
          <div style="text-align: center; color: #7f8c8d; padding: 30px;">
            <div style="font-size: 3em; margin-bottom: 15px;">🔍</div>
            <h4 style="margin: 0 0 10px 0; color: #95a5a6;">No se encontraron familiares</h4>
            <p style="margin: 0; font-size: 0.9em;">
              No se detectaron miembros con apellidos similares.
            </p>
          </div>`;
      }
    })
    .catch(error => {
      console.error('Error:', error);
      familyList.innerHTML = `
        <div style="text-align: center; color: #e74c3c; padding: 30px;">
          <div style="font-size: 2.5em; margin-bottom: 10px;">⚠️</div>
          <h4 style="margin: 0 0 10px 0;">Error de Conexión</h4>
          <p style="margin: 0; font-size: 0.9em;">
            No se pudo buscar familiares. Intenta de nuevo.
          </p>
        </div>`;
    });
  }
  
  // Función para inicializar búsqueda de miembros para grupo
  function initGroupSearch() {
    const searchInput = document.getElementById('buscar-miembros');
    const container = document.getElementById('group-members-list');
    
    if (searchInput && container) {
      searchInput.addEventListener('input', function() {
        const busqueda = this.value.trim();
        if (busqueda.length >= 2) {
          buscarMiembrosGrupo(busqueda);
        } else {
          container.innerHTML = '<p style="color: #7f8c8d; font-style: italic;">Escribe al menos 2 caracteres para buscar...</p>';
        }
      });
    }
  }
  
  // Función para buscar miembros para el grupo
  function buscarMiembrosGrupo(busqueda) {
    const container = document.getElementById('group-members-list');
    
    if (busqueda.length < 2) {
      container.innerHTML = `
        <div style="text-align: center; color: #3498db;">
          <div style="font-size: 2.5em; margin-bottom: 10px;">🏋️‍♂️</div>
          <p style="margin: 0; font-weight: 600;">Miembros del Grupo</p>
          <p style="margin: 5px 0 0 0; font-size: 0.85em; color: #7f8c8d;">
            Escribe al menos 2 caracteres para buscar miembros
          </p>
        </div>`;
      return;
    }
    
    // Mostrar indicador de carga
    container.innerHTML = `
      <div style="text-align: center; color: #3498db; padding: 20px;">
        <div style="font-size: 2em; margin-bottom: 10px;">🔍</div>
        <p style="margin: 0; font-weight: 600;">Buscando miembros...</p>
        <p style="margin: 5px 0 0 0; font-size: 0.85em; color: #7f8c8d;">
          Buscando por "${busqueda}"
        </p>
      </div>`;
    
    fetch('/buscar_miembros_grupo?busqueda=' + encodeURIComponent(busqueda))
      .then(response => response.json())
      .then(data => {
        if (data.miembros && data.miembros.length > 0) {
          let html = `
            <div style="margin-bottom: 20px;">
              <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="background: #3498db; color: white; padding: 6px 10px; border-radius: 50%; margin-right: 10px;">✅</span>
                <h4 style="margin: 0; color: #3498db; font-size: 1.1em;">Miembros Encontrados</h4>
              </div>
              <p style="color: #7f8c8d; font-size: 0.9em; margin: 0 0 15px 0;">
                Se encontraron ${data.miembros.length} miembro(s) disponible(s) para el grupo:
              </p>
            </div>`;
          
          data.miembros.forEach((miembro, index) => {
            html += `
              <div style="margin: 10px 0; padding: 15px; background: white; border-radius: 10px; border: 2px solid #e3f2fd; transition: all 0.3s ease; cursor: pointer;" 
                   onmouseover="this.style.borderColor='#3498db'; this.style.transform='translateY(-2px)'" 
                   onmouseout="this.style.borderColor='#e3f2fd'; this.style.transform='translateY(0)'">
                <label style="display: flex; align-items: center; cursor: pointer; margin: 0;">
                  <input type="checkbox" name="miembros_grupo" value="${miembro.id}" 
                         style="width: 18px; height: 18px; cursor: pointer; margin-right: 15px;">
                  <div style="flex: 1;">
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                      <span style="background: #3498db; color: white; padding: 4px 8px; border-radius: 20px; font-size: 0.8em; margin-right: 10px;">👤</span>
                      <strong style="color: #2c3e50;">${miembro.nombre}</strong>
                    </div>
                    <div style="margin-left: 30px; color: #7f8c8d; font-size: 0.9em;">
                      Usuario: <strong>${miembro.usuario}</strong> • 
                      Modalidad: ${miembro.modalidad}
                    </div>
                  </div>
                </label>
              </div>`;
          });
          
          html += `
            <div style="background: #e3f2fd; border-radius: 8px; padding: 15px; margin-top: 20px; border-left: 4px solid #3498db;">
              <div style="display: flex; align-items: center;">
                <span style="font-size: 1.2em; margin-right: 8px;">💡</span>
                <div>
                  <strong style="color: #3498db;">Tip:</strong>
                  <span style="color: #2c3e50; font-size: 0.9em;">
                    Selecciona todos los miembros que deseas agregar al grupo antes de enviar el formulario.
                  </span>
                </div>
              </div>
            </div>`;
          
          container.innerHTML = html;
        } else {
          container.innerHTML = `
            <div style="text-align: center; color: #7f8c8d; padding: 30px;">
              <div style="font-size: 3em; margin-bottom: 15px;">🔍</div>
              <h4 style="margin: 0 0 10px 0; color: #95a5a6;">No se encontraron miembros</h4>
              <p style="margin: 0; font-size: 0.9em;">
                No hay miembros disponibles que coincidan con "${busqueda}".
              </p>
              <p style="margin: 10px 0 0 0; font-size: 0.85em; color: #bdc3c7;">
                Intenta con un nombre diferente o verifica la ortografía.
              </p>
            </div>`;
        }
      })
      .catch(error => {
        console.error('Error:', error);
        container.innerHTML = `
          <div style="text-align: center; color: #e74c3c; padding: 30px;">
            <div style="font-size: 2.5em; margin-bottom: 10px;">⚠️</div>
            <h4 style="margin: 0 0 10px 0;">Error de Conexión</h4>
            <p style="margin: 0; font-size: 0.9em;">
              No se pudo buscar miembros. Verifica tu conexión e intenta de nuevo.
            </p>
            <button onclick="buscarMiembrosGrupo('${busqueda}')" 
                    style="background: #e74c3c; color: white; border: none; padding: 10px 20px; border-radius: 6px; margin-top: 15px; cursor: pointer;">
              🔄 Reintentar
            </button>
          </div>`;
      });
  }
  
  // Event listeners
  document.addEventListener('DOMContentLoaded', function() {
    const modalidad = document.getElementById('modalidad');
    const nombre = document.querySelector('input[name="nombre"]');
    const buscarInput = document.getElementById('buscar-miembros');
    
    if (modalidad) {
      modalidad.addEventListener('change', toggleFamilySelection);
    }
    
    if (nombre) {
      nombre.addEventListener('input', function() {
        if (modalidad && modalidad.value === 'plan_familiar') {
          loadFamilyMembers();
        }
      });
    }
    
    if (buscarInput) {
      buscarInput.addEventListener('input', function() {
        const busqueda = this.value.trim();
        if (busqueda.length >= 2) {
          buscarMiembrosGrupo(busqueda);
        } else {
          const container = document.getElementById('group-members-list');
          if (container) {
            container.innerHTML = `
              <div style="text-align: center; color: #3498db;">
                <div style="font-size: 2.5em; margin-bottom: 10px;">🏋️‍♂️</div>
                <p style="margin: 0; font-weight: 600;">Miembros del Grupo</p>
                <p style="margin: 5px 0 0 0; font-size: 0.85em; color: #7f8c8d;">
                  Escribe al menos 2 caracteres para buscar miembros
                </p>
              </div>`;
          }
        }
      });
    }
  });
  
  // Función para actualizar el monto automáticamente según el concepto
  function actualizarMonto(concepto) {
    const montoInput = document.getElementById('montoInput');
    
    const montosAutomaticos = {
      'Mensualidad': 400.00,
      'Semana': 120.00,
      'Clase': 50.00,
      'Tres clases': 100.00,
      'Semana con Yoga': 150.00,
      'Clase de Yoga': 80.00,
      'Pareja': 700.00,
      'Tres personas': 1000.00,
      'Cuatro personas': 1300.00,
      'Cinco personas': 1600.00
    };
    
    if (montosAutomaticos[concepto]) {
      montoInput.value = montosAutomaticos[concepto].toFixed(2);
      montoInput.setAttribute('readonly', true);
      montoInput.style.backgroundColor = '#f8f9fa';
      montoInput.style.color = '#495057';
    } else {
      // Para conceptos personalizados, permitir edición manual
      montoInput.value = '';
      montoInput.removeAttribute('readonly');
      montoInput.style.backgroundColor = 'white';
      montoInput.style.color = 'black';
      montoInput.placeholder = 'Ingrese el monto personalizado';
    }
    
    // Mostrar información adicional para planes familiares/grupales
    const infoDiv = montoInput.nextElementSibling;
    if (['Pareja', 'Tres personas', 'Cuatro personas', 'Cinco personas'].includes(concepto)) {
      infoDiv.innerHTML = `
        💡 El monto se calcula automáticamente. Para planes familiares/grupales se multiplicará por el número de miembros.
        <br><strong>Ejemplo:</strong> $${montosAutomaticos[concepto]} × número de miembros = total a pagar
      `;
    } else {
      infoDiv.innerHTML = '💡 El monto se calcula automáticamente según el concepto seleccionado.';
    }
  }

  // Función para buscar miembros disponibles para agregar a un plan familiar
  function buscarMiembrosParaFamilia(busqueda, planId) {
    const container = document.getElementById('resultados-miembros-familia');
    
    if (busqueda.length < 2) {
      container.style.display = 'none';
      return;
    }
    
    container.style.display = 'block';
    container.innerHTML = '<div style="padding: 10px; text-align: center; color: #666;">Buscando...</div>';
    
    fetch('/buscar_miembros_familia?busqueda=' + encodeURIComponent(busqueda) + '&plan_id=' + planId)
      .then(response => response.json())
      .then(data => {
        if (data.miembros && data.miembros.length > 0) {
          let html = '';
          data.miembros.forEach(miembro => {
            html += `
              <div style="padding: 10px; border-bottom: 1px solid #eee; cursor: pointer; display: flex; justify-content: between; align-items: center;"
                   onclick="agregarMiembroAFamilia(${miembro.id}, '${miembro.nombre}', ${planId})">
                <div>
                  <strong>${miembro.nombre}</strong><br>
                  <small style="color: #666;">PIN: ${miembro.id}</small>
                </div>
                <button type="button" class="btn" style="background: #27ae60; padding: 5px 10px; font-size: 12px;">
                  Agregar
                </button>
              </div>`;
          });
          container.innerHTML = html;
        } else {
          container.innerHTML = '<div style="padding: 10px; text-align: center; color: #666;">No se encontraron miembros disponibles</div>';
        }
      })
      .catch(error => {
        console.error('Error:', error);
        container.innerHTML = '<div style="padding: 10px; text-align: center; color: #e74c3c;">Error al buscar miembros</div>';
      });
  }

  // Función para agregar un miembro a la familia
  function agregarMiembroAFamilia(miembroId, nombreMiembro, planId) {
    if (confirm(`¿Agregar a ${nombreMiembro} al plan familiar?`)) {
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = '/agregar_miembro_plan';
      
      const planInput = document.createElement('input');
      planInput.type = 'hidden';
      planInput.name = 'plan_id';
      planInput.value = planId;
      
      const miembroInput = document.createElement('input');
      miembroInput.type = 'hidden';
      miembroInput.name = 'miembro_id';
      miembroInput.value = miembroId;
      
      form.appendChild(planInput);
      form.appendChild(miembroInput);
      
      document.body.appendChild(form);
      form.submit();
    }
    
    // Ocultar resultados
    document.getElementById('resultados-miembros-familia').style.display = 'none';
    document.querySelector('input[name="query"]').value = '';
  }

  // Ocultar resultados al hacer clic fuera
  document.addEventListener('click', function(event) {
    const container = document.getElementById('resultados-miembros-familia');
    const input = document.querySelector('input[name="query"]');
    
    if (container && input && !container.contains(event.target) && event.target !== input) {
      container.style.display = 'none';
    }
  });
  </script>
</body>
</html>
""", miembros=miembros, logo_fn=logo_fn, pagos_recientes=pagos_recientes, 
     fecha_actual=datetime.now().strftime("%Y-%m-%d"), BASE_STYLES=BASE_STYLES)

@app.route("/panel_miembro")
def panel_miembro():
    if session.get("rol") != "miembro":
        return redirect("/login")
    
    usuario = session.get("usuario")
    nombre = session.get("nombre")
    
    con = conectar()
    
    # Datos del miembro
    miembro = con.execute("""
        SELECT modalidad, vigencia, foto
        FROM usuarios WHERE usuario=?
    """, (usuario,)).fetchone()
    
    con.close()
    
    if not miembro:
        flash("Error al cargar datos del miembro")
        return redirect("/login")
    
    modalidad, vigencia, foto = miembro
    dias_rest = dias_restantes(vigencia)
    
    # Verificar si la membresía ha vencido
    if dias_rest < 0:
        return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Membresía Vencida</title>
  <style>
    body {
      background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
      font-family: 'Segoe UI', Arial, sans-serif;
      min-height: 100vh;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .error-box {
      max-width: 450px;
      background: #fff;
      border-radius: 14px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
      padding: 40px 32px;
      text-align: center;
    }
    .error-icon {
      font-size: 4em;
      color: #e74c3c;
      margin-bottom: 20px;
    }
    h2 { color: #e74c3c; margin-bottom: 20px; }
    .btn {
      background: #e74c3c;
      color: #fff;
      padding: 12px 24px;
      border: none;
      border-radius: 6px;
      text-decoration: none;
      display: inline-block;
      margin-top: 20px;
    }
  </style>
</head>
<body>
  <div class="error-box">
    <div class="error-icon">⚠️</div>
    <h2>Membresía Vencida</h2>
    <p>Estimado(a) <strong>{{ nombre }}</strong>,</p>
    <p>Tu membresía <strong>{{ modalidad }}</strong> venció el <strong>{{ vigencia }}</strong> (hace {{ -dias_rest }} días)</p>
    <p>Por favor contacta a recepción para renovar tu membresía y continuar disfrutando de nuestros servicios.</p>
    <p><strong>¡Te esperamos pronto!</strong></p>
    <a href="/logout" class="btn">Volver al Inicio</a>
  </div>
</body>
</html>
""", nombre=nombre, modalidad=modalidad, vigencia=vigencia, dias_rest=dias_rest)
    
    # Panel normal para miembros con membresía vigente
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Panel Miembro</title>
  <meta http-equiv="refresh" content="5;url=/login">
  <style>
    body { 
      margin: 0; 
      font-family: 'Segoe UI', Arial, sans-serif; 
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .container { 
      max-width: 420px; 
      background: rgba(255, 255, 255, 0.95);
      border-radius: 20px;
      padding: 40px;
      text-align: center;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
    }
    .photo { 
      width: 120px; height: 120px; border-radius: 50%; 
      object-fit: cover; border: 4px solid white; 
      box-shadow: 0 4px 15px rgba(0,0,0,0.2); margin-bottom: 20px;
    }
    .member-name { 
      font-size: 1.8em; 
      font-weight: 600; 
      color: #2c3e50; 
      margin-bottom: 10px;
    }
    .info-grid { 
      display: grid; 
      gap: 15px; 
      margin: 25px 0;
      text-align: left;
    }
    .info-item { 
      background: #f8f9fa; 
      padding: 15px; 
      border-radius: 12px;
    }
    .info-label { font-weight: 600; color: #666; font-size: 0.9em; margin-bottom: 5px; }
    .info-value { font-size: 1.1em; color: #333; }
    .countdown {
      background: #e3f2fd;
      padding: 15px;
      border-radius: 12px;
      margin: 20px 0;
      color: #1565c0;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="container">
    {% if foto %}
      <img src="{{ url_for('static', filename='fotos/'+foto) }}" class="photo" alt="{{ nombre }}">
    {% endif %}
    
    <div class="member-name">{{ nombre }}</div>
    <p>Bienvenido a tu panel de miembro</p>

    <div class="info-grid">
      <div class="info-item">
        <div class="info-label">Modalidad</div>
        <div class="info-value">{{ modalidad.title() }}</div>
      </div>
      
      <div class="info-item">
        <div class="info-label">Vigencia</div>
        <div class="info-value">{{ vigencia }}</div>
      </div>
      
      <div class="info-item">
        <div class="info-label">Estado</div>
        <div class="info-value" style="color: {{ '#27ae60' if dias_rest > 7 else '#f39c12' if dias_rest > 0 else '#e74c3c' }};">
          {{ dias_rest }} días restantes
        </div>
      </div>
    </div>

    <div class="countdown">
      ⏱️ Serás redirigido al inicio en <span id="countdown">5</span> segundos
    </div>
  </div>

  <script>
    let seconds = 5;
    const countdownElement = document.getElementById('countdown');
    
    const timer = setInterval(() => {
      seconds--;
      countdownElement.textContent = seconds;
      
      if (seconds <= 0) {
        clearInterval(timer);
        window.location.href = '/login';
      }
    }, 1000);
  </script>
</body>
</html>
""", nombre=nombre, modalidad=modalidad, vigencia=vigencia, foto=foto, dias_rest=dias_rest)

# ——— Estadísticas Globales ———
@app.route("/estadisticas_globales")
def estadisticas_globales():
    if session.get("rol") != "admin":
        return redirect("/login")
    
    con = conectar()
    
    # Obtener logo
    logo_row = con.execute("SELECT filename FROM logo ORDER BY id DESC LIMIT 1").fetchone()
    logo_fn = logo_row[0] if logo_row else ""
    
    # Total de miembros por modalidad
    total_miembros_modalidad = con.execute("""
        SELECT modalidad, COUNT(*) as total
        FROM usuarios
        WHERE rol='miembro'
        GROUP BY modalidad
    """).fetchall()
    
    # Miembros activos e inactivos
    miembros_activos = con.execute("""
        SELECT COUNT(*) FROM usuarios WHERE rol='miembro' AND date(vigencia) >= date('now')
    """).fetchone()[0]
    
    miembros_inactivos = con.execute("""
        SELECT COUNT(*) FROM usuarios WHERE rol='miembro' AND date(vigencia) < date('now')
    """).fetchone()[0]
    
    # Total de ingresos por mes (últimos 6 meses)
    ingresos_mensuales = con.execute("""
        SELECT strftime('%Y-%m', fecha) as mes, SUM(monto) as total
        FROM pagos 
        WHERE fecha >= date('now', '-6 months')
        GROUP BY strftime('%Y-%m', fecha)
        ORDER BY mes
    """).fetchall()
    
    # Últimos miembros registrados
    miembros_registrados = con.execute("""
        SELECT nombre, usuario, modalidad, vigencia
        FROM usuarios 
        WHERE rol='miembro'
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()
    
    con.close()
    
    # Procesar datos para gráficas
    if total_miembros_modalidad:
        modalidades = [m[0] for m in total_miembros_modalidad]
        totales = [m[1] for m in total_miembros_modalidad]
    else:
        modalidades = ["Sin datos"]
        totales = [0]
    
    if ingresos_mensuales:
        meses_labels = [m[0] for m in ingresos_mensuales]
        meses_data = [float(m[1]) for m in ingresos_mensuales]
    else:
        meses_labels = ["Sin datos"]
        meses_data = [0]
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Estadísticas Globales</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
  {{ BASE_STYLES|safe }}
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>ADMIN PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="/admin"><i>🏠</i> Panel Principal</a></li>
        <li><a href="/reportes_financieros"><i>📊</i> Reportes Financieros</a></li>
        <li><a href="/estadisticas_globales" class="active"><i>📈</i> Estadísticas Globales</a></li>
        <li><a href="/analiticas_avanzadas"><i>🔍</i> Analíticas Avanzadas</a></li>
        <li><a href="/gestion_backups"><i>💾</i> Gestión de Backups</a></li>
        <li><a href="/gestion_usuarios_admin"><i>👑</i> Gestión Admins/Moderadores</a></li>
        <li><a href="/corte_caja"><i>💰</i> Corte de Caja</a></li>
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header">
        <h1>📈 Estadísticas Globales</h1>
        <div class="breadcrumb">Panel Admin > Estadísticas Globales</div>
      </div>

      <div class="content-body">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-number">{{ miembros_activos }}</div>
            <div class="stat-label">Miembros Activos</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">
            <div class="stat-number">{{ miembros_inactivos }}</div>
            <div class="stat-label">Miembros Inactivos</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);">
            <div class="stat-number">{{ modalidades|length }}</div>
            <div class="stat-label">Modalidades Activas</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);">
            <div class="stat-number">{{ (miembros_activos + miembros_inactivos) }}</div>
            <div class="stat-label">Total Miembros</div>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 25px;">
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">👥 Miembros por Modalidad</h3>
            </div>
            <canvas id="chartMiembrosModalidad" width="400" height="300"></canvas>
          </div>
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">📊 Estado de Miembros</h3>
            </div>
            <canvas id="chartMiembrosEstado" width="400" height="300"></canvas>
          </div>
        </div>

        <div class="card" style="margin-bottom: 25px;">
          <div class="card-header">
            <h3 class="card-title">💰 Ingresos por Mes (Últimos 6 meses)</h3>
          </div>
          <canvas id="chartIngresosMes" width="400" height="300"></canvas>
        </div>

        <div class="card">
          <div class="card-header">
            <h3 class="card-title">👥 Últimos Miembros Registrados</h3>
          </div>
          <table>
            <thead><tr><th>Nombre</th><th>Usuario</th><th>Modalidad</th><th>Vigencia</th></tr></thead>
            <tbody>
              {% for nombre, usuario, modalidad, vigencia in miembros_registrados %}
              <tr><td>{{ nombre }}</td><td>{{ usuario }}</td><td>{{ modalidad }}</td><td>{{ vigencia }}</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <script>
    document.addEventListener('DOMContentLoaded', function() {
      // Gráfica de miembros por modalidad
      const ctxModalidad = document.getElementById('chartMiembrosModalidad');
      if (ctxModalidad) {
        new Chart(ctxModalidad, {
          type: 'pie',
          data: {
            labels: {{ modalidades|safe }},
            datasets: [{
              label: 'Total de Miembros',
              data: {{ totales|safe }},
              backgroundColor: ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c'],
              borderWidth: 2,
              borderColor: '#fff'
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { 
                position: 'bottom'
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return context.label + ': ' + context.parsed + ' miembros';
                  }
                }
              }
            }
          }
        });
      }

      // Gráfica de miembros activos e inactivos
      const ctxEstado = document.getElementById('chartMiembrosEstado');
      if (ctxEstado) {
        new Chart(ctxEstado, {
          type: 'bar',
          data: {
            labels: ['Activos', 'Inactivos'],
            datasets: [{
              label: 'Total de Miembros',
              data: [{{ miembros_activos }}, {{ miembros_inactivos }}],
              backgroundColor: ['#27ae60', '#e74c3c'],
              borderWidth: 2,
              borderColor: '#fff'
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: { 
                beginAtZero: true,
                ticks: {
                  callback: function(value) {
                    return value;
                  }
                }
              }
            }
          }
        });
      }

      // Gráfica de ingresos por mes
      const ctxIngresosMes = document.getElementById('chartIngresosMes');
      if (ctxIngresosMes) {
        new Chart(ctxIngresosMes, {
          type: 'line',
          data: {
            labels: {{ meses_labels|safe }},
            datasets: [{
              label: 'Ingresos ($)',
              data: {{ meses_data|safe }},
              backgroundColor: 'rgba(39, 174, 96, 0.2)',
              borderColor: '#27ae60',
              borderWidth: 3,
              fill: true,
              tension: 0.4
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: { 
                beginAtZero: true,
                ticks: {
                  callback: function(value) {
                    return '$' + value.toFixed(2);
                  }
                }
              }
            }
          }
        });
      }
    });
  </script>
</body>
</html>
""", modalidades=modalidades, totales=totales, ingresos_mensuales=ingresos_mensuales,
     miembros_activos=miembros_activos, miembros_inactivos=miembros_inactivos,
     miembros_registrados=miembros_registrados, meses_labels=meses_labels, meses_data=meses_data,
     BASE_STYLES=BASE_STYLES, logo_fn=logo_fn)

    crecimiento_mensual = con.execute("""
        SELECT 
            strftime('%Y-%m', fecha) as mes,
            COUNT(DISTINCT usuario) as miembros_activos,
            COUNT(*) as total_asistencias
        FROM asistencias 
        WHERE fecha >= date('now', '-12 months')
        GROUP BY strftime('%Y-%m', fecha)
        ORDER BY mes
    """).fetchall()
    
    # Predicción de renovaciones (miembros que vencen en los próximos 30 días)
    proximas_renovaciones = con.execute("""
        SELECT nombre, usuario, vigencia, modalidad,
               (julianday(vigencia) - julianday('now')) as dias_restantes
        FROM usuarios 
        WHERE rol='miembro' 
        AND date(vigencia) BETWEEN date('now') AND date('now', '+30 days')
        ORDER BY vigencia ASC
    """).fetchall()
    
    con.close()
    
    # Procesar datos para gráficas
    if retencion_datos:
        retencion_labels = [r[0] for r in retencion_datos]
        retencion_activos = [r[2] for r in retencion_datos]
        retencion_vencidos = [r[3] for r in retencion_datos]
    else:
        retencion_labels = ["Sin datos"]
        retencion_activos = [0]
        retencion_vencidos = [0]
    
    if horarios_semana:
        semana_labels = [h[0] for h in horarios_semana]
        semana_asistencias = [h[1] for h in horarios_semana]
        semana_horas = [h[2] for h in horarios_semana]
    else:
        semana_labels = ["Sin datos"]
        semana_asistencias = [0]
        semana_horas = [0]
    
    if crecimiento_mensual:
        crecimiento_labels = [c[0] for c in crecimiento_mensual]
        crecimiento_miembros = [c[1] for c in crecimiento_mensual]
        crecimiento_asistencias = [c[2] for c in crecimiento_mensual]
    else:
        crecimiento_labels = ["Sin datos"]
        crecimiento_miembros = [0]
        crecimiento_asistencias = [0]
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Analíticas Avanzadas</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
  {{ BASE_STYLES|safe }}
  <style>
    .renovacion-urgente { background: rgba(231, 76, 60, 0.1) !important; }
    .renovacion-media { background: rgba(243, 156, 18, 0.1) !important; }
  </style>
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>ADMIN PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo" style="border-radius: 8px; object-fit: contain;">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="/admin"><i>🏠</i> Panel Principal</a></li>
        <li><a href="/reportes_financieros"><i>📊</i> Reportes Financieros</a></li>
        <li><a href="/estadisticas_globales"><i>📈</i> Estadísticas Globales</a></li>
        <li><a href="/analiticas_avanzadas" class="active"><i>🔍</i> Analíticas Avanzadas</a></li>
        <li><a href="/gestion_backups"><i>💾</i> Gestión de Backups</a></li>
        <li><a href="/gestion_usuarios_admin"><i>👑</i> Gestión Admins/Moderadores</a></li>
        <li><a href="/corte_caja"><i>💰</i> Corte de Caja</a></li>
        <li><a href="/diseno_plataforma"><i>🎨</i> Diseño de Plataforma</a></li>
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header">
        <h1>🔍 Analíticas Avanzadas</h1>
        <div class="breadcrumb">Panel Admin > Analíticas Avanzadas</div>
      </div>

      <div class="content-body">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 25px;">
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">📊 Retención por Modalidad</h3>
            </div>
            <canvas id="chartRetencion" width="400" height="300"></canvas>
          </div>
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">📅 Asistencias por Día de la Semana</h3>
            </div>
            <canvas id="chartSemana" width="400" height="300"></canvas>
          </div>
        </div>

        <div class="card" style="margin-bottom: 25px;">
          <div class="card-header">
            <h3 class="card-title">📈 Crecimiento Mensual</h3>
          </div>
          <canvas id="chartCrecimiento" width="400" height="200"></canvas>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px;">
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">🏃‍♂️ Top Asistencias (Último Mes)</h3>
            </div>
            <table>
              <thead><tr><th>Nombre</th><th>Usuario</th><th>Total</th><th>Días</th><th>Promedio/Día</th></tr></thead>
              <tbody>
                {% for usuario, nombre, total, dias, promedio in frecuencia_asistencia %}
                <tr>
                  <td>{{ nombre }}</td>
                  <td>{{ usuario }}</td>
                  <td>{{ total }}</td>
                  <td>{{ dias }}</td>
                  <td>{{ promedio }}</td>
                </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">⏰ Próximas Renovaciones (30 días)</h3>
            </div>
            <table>
              <thead><tr><th>Nombre</th><th>Usuario</th><th>Vigencia</th><th>Días Rest.</th></tr></thead>
              <tbody>
                {% for nombre, usuario, vigencia, modalidad, dias in proximas_renovaciones %}
                <tr class="{% if dias <= 7 %}renovacion-urgente{% elif dias <= 15 %}renovacion-media{% endif %}">
                  <td>{{ nombre }}</td>
                  <td>{{ usuario }}</td>
                  <td>{{ vigencia }}</td>
                  <td>{{ "%.0f"|format(dias) }}</td>
                </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    document.addEventListener('DOMContentLoaded', function() {
      // Gráfica de retención
      const ctxRetencion = document.getElementById('chartRetencion');
      if (ctxRetencion) {
        new Chart(ctxRetencion, {
          type: 'bar',
          data: {
            labels: {{ retencion_labels|safe }},
            datasets: [{
              label: 'Activos',
              data: {{ retencion_activos|safe }},
              backgroundColor: '#27ae60'
            }, {
              label: 'Vencidos',
              data: {{ retencion_vencidos|safe }},
              backgroundColor: '#e74c3c'
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { position: 'bottom' }
            },
            scales: {
              x: { stacked: true },
              y: { stacked: true, beginAtZero: true }
            }
          }
        });
      }

      // Gráfica de asistencias por semana
      const ctxSemana = document.getElementById('chartSemana');
      if (ctxSemana) {
        new Chart(ctxSemana, {
          type: 'radar',
          data: {
            labels: {{ semana_labels|safe }},
            datasets: [{
              label: 'Asistencias',
              data: {{ semana_asistencias|safe }},
              backgroundColor: 'rgba(52, 152, 219, 0.2)',
              borderColor: '#3498db',
              borderWidth: 2
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { position: 'bottom' }
            }
          }
        });
      }

      // Gráfica de crecimiento mensual
      const ctxCrecimiento = document.getElementById('chartCrecimiento');
      if (ctxCrecimiento) {
        new Chart(ctxCrecimiento, {
          type: 'line',
          data: {
            labels: {{ crecimiento_labels|safe }},
            datasets: [{
              label: 'Miembros Activos',
              data: {{ crecimiento_miembros|safe }},
              backgroundColor: 'rgba(52, 152, 219, 0.2)',
              borderColor: '#3498db',
              borderWidth: 2,
              yAxisID: 'y'
            }, {
              label: 'Asistencias',
              data: {{ crecimiento_asistencias|safe }},
              backgroundColor: 'rgba(231, 76, 60, 0.2)',
              borderColor: '#e74c3c',
              borderWidth: 2,
              yAxisID: 'y1'
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { position: 'bottom' }
            },
            scales: {
              y: {
                type: 'linear',
                display: true,
                position: 'left',
                beginAtZero: true
              },
              y1: {
                type: 'linear',
                display: true,
                position: 'right',
                beginAtZero: true,
                grid: {
                  drawOnChartArea: false,
                }
              }
            }
          }
        });
      }
    });
  </script>
</body>
</html>

  <script>
    document.addEventListener('DOMContentLoaded', function() {
      // Gráfica de retención
      const ctxRetencion = document.getElementById('chartRetencion');
      if (ctxRetencion) {
        new Chart(ctxRetencion, {
          type: 'bar',
          data: {
            labels: {{ retencion_labels|safe }},
            datasets: [{
              label: 'Activos',
              data: {{ retencion_activos|safe }},
              backgroundColor: '#27ae60'
            }, {
              label: 'Vencidos',
              data: {{ retencion_vencidos|safe }},
              backgroundColor: '#e74c3c'
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { position: 'bottom' }
            },
            scales: {
              x: { stacked: true },
              y: { stacked: true, beginAtZero: true }
            }
          }
        });
      }

      // Gráfica de asistencias por semana
      const ctxSemana = document.getElementById('chartSemana');
      if (ctxSemana) {
        new Chart(ctxSemana, {
          type: 'radar',
          data: {
            labels: {{ semana_labels|safe }},
            datasets: [{
              label: 'Asistencias',
              data: {{ semana_asistencias|safe }},
              backgroundColor: 'rgba(52, 152, 219, 0.2)',
              borderColor: '#3498db',
              borderWidth: 2
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { position: 'bottom' }
            }
          }
        });
      }

      // Gráfica de crecimiento mensual
      const ctxCrecimiento = document.getElementById('chartCrecimiento');
      if (ctxCrecimiento) {
        new Chart(ctxCrecimiento, {
          type: 'line',
          data: {
            labels: {{ crecimiento_labels|safe }},
            datasets: [{
              label: 'Miembros Activos',
              data: {{ crecimiento_miembros|safe }},
              backgroundColor: 'rgba(52, 152, 219, 0.2)',
              borderColor: '#3498db',
              borderWidth: 2,
              yAxisID: 'y'
            }, {
              label: 'Asistencias',
              data: {{ crecimiento_asistencias|safe }},
              backgroundColor: 'rgba(231, 76, 60, 0.2)',
              borderColor: '#e74c3c',
              borderWidth: 2,
              yAxisID: 'y1'
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { position: 'bottom' }
            },
            scales: {
              y: {
                type: 'linear',
                display: true,
                position: 'left',
                beginAtZero: true
              },
              y1: {
                type: 'linear',
                display: true,
                position: 'right',
                beginAtZero: true,
                grid: {
                  drawOnChartArea: false,
                }
              }
            }
          }
        });
      }
  <script>
    document.addEventListener('DOMContentLoaded', function() {
      // Estilos adicionales para tablas
      const style = document.createElement('style');
      style.textContent = `
        .renovacion-urgente { background: rgba(231, 76, 60, 0.1) !important; }
        .renovacion-media { background: rgba(243, 156, 18, 0.1) !important; }
      `;
      document.head.appendChild(style);

      // Gráfica de retención
      const ctxRetencion = document.getElementById('chartRetencion');
      if (ctxRetencion) {
        new Chart(ctxRetencion, {
          type: 'bar',
          data: {
            labels: {{ retencion_labels|safe }},
            datasets: [{
              label: 'Activos',
              data: {{ retencion_activos|safe }},
              backgroundColor: '#27ae60'
            }, {
              label: 'Vencidos',
              data: {{ retencion_vencidos|safe }},
              backgroundColor: '#e74c3c'
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { position: 'bottom' }
            },
            scales: {
              x: { stacked: true },
              y: { stacked: true, beginAtZero: true }
            }
          }
        });
      }

      // Gráfica de asistencias por semana
      const ctxSemana = document.getElementById('chartSemana');
      if (ctxSemana) {
        new Chart(ctxSemana, {
          type: 'radar',
          data: {
            labels: {{ semana_labels|safe }},
            datasets: [{
              label: 'Asistencias',
              data: {{ semana_asistencias|safe }},
              backgroundColor: 'rgba(52, 152, 219, 0.2)',
              borderColor: '#3498db',
              borderWidth: 2
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { position: 'bottom' }
            }
          }
        });
      }

      // Gráfica de crecimiento mensual
      const ctxCrecimiento = document.getElementById('chartCrecimiento');
      if (ctxCrecimiento) {
        new Chart(ctxCrecimiento, {
          type: 'line',
          data: {
            labels: {{ crecimiento_labels|safe }},
            datasets: [{
              label: 'Miembros Activos',
              data: {{ crecimiento_miembros|safe }},
              backgroundColor: 'rgba(52, 152, 219, 0.2)',
              borderColor: '#3498db',
              borderWidth: 2,
              yAxisID: 'y'
            }, {
              label: 'Asistencias',
              data: {{ crecimiento_asistencias|safe }},
              backgroundColor: 'rgba(231, 76, 60, 0.2)',
              borderColor: '#e74c3c',
              borderWidth: 2,
              yAxisID: 'y1'
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { position: 'bottom' }
            },
            scales: {
              y: {
                type: 'linear',
                display: true,
                position: 'left',
                beginAtZero: true
              },
              y1: {
                type: 'linear',
                display: true,
                position: 'right',
                beginAtZero: true,
                grid: {
                  drawOnChartArea: false,
                }
              }
            }
          }
        });
      }
    });
  </script>
</body>
</html>
""", retencion_labels=retencion_labels, retencion_activos=retencion_activos, retencion_vencidos=retencion_vencidos,
     frecuencia_asistencia=frecuencia_asistencia, proximas_renovaciones=proximas_renovaciones,
     semana_labels=semana_labels, semana_asistencias=semana_asistencias,
     crecimiento_labels=crecimiento_labels, crecimiento_miembros=crecimiento_miembros, 
     crecimiento_asistencias=crecimiento_asistencias, BASE_STYLES=BASE_STYLES, logo_fn=logo_fn)

# ——— Diseño de Plataforma ———
@app.route("/diseno_plataforma")
def diseno_plataforma():
    if session.get("rol") != "admin":
        return redirect("/login")
    
    con = conectar()
    # Obtener logo y banner actuales
    logo_row = con.execute("SELECT filename FROM logo ORDER BY id DESC LIMIT 1").fetchone()
    logo_fn = logo_row[0] if logo_row else ""
    
    banner_row = con.execute("SELECT filename FROM banner ORDER BY id DESC LIMIT 1").fetchone()
    banner_fn = banner_row[0] if banner_row else ""
    con.close()
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Diseño de Plataforma</title>
  {{ BASE_STYLES|safe }}
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>ADMIN PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo" style="border-radius: 8px; object-fit: contain;">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="/admin"><i>🏠</i> Panel Principal</a></li>
        <li><a href="/reportes_financieros"><i>📊</i> Reportes Financieros</a></li>
        <li><a href="/estadisticas_globales"><i>📈</i> Estadísticas Globales</a></li>
        <li><a href="/analiticas_avanzadas"><i>🔍</i> Analíticas Avanzadas</a></li>
        <li><a href="/gestion_backups"><i>💾</i> Gestión de Backups</a></li>
        <li><a href="/gestion_usuarios_admin"><i>👑</i> Gestión Admins/Moderadores</a></li>
        <li><a href="/corte_caja"><i>💰</i> Corte de Caja</a></li>
        <li><a href="/diseno_plataforma" class="active"><i>🎨</i> Diseño de Plataforma</a></li>
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header">
        <h1>🎨 Diseño de Plataforma</h1>
        <div class="breadcrumb">Panel Admin > Diseño de Plataforma</div>
      </div>

      <div class="content-body">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 25px;">
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">🖼️ Logo del Gimnasio</h3>
            </div>
            <div style="padding: 20px;">
              {% if logo_fn %}
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center;">
                  <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" style="max-width: 200px; max-height: 100px; object-fit: contain; border-radius: 8px; border: 2px solid #ddd;">
                  <p style="margin: 10px 0 0 0; color: #666; font-size: 14px;">Logo actual</p>
                </div>
              {% else %}
                <div style="background: #f8f9fa; padding: 40px; border-radius: 8px; margin-bottom: 20px; text-align: center; color: #666;">
                  <i>📷</i>
                  <p style="margin: 10px 0 0 0;">No hay logo configurado</p>
                </div>
              {% endif %}
              
              <form method="POST" action="/update_logo" enctype="multipart/form-data">
                <input type="file" name="logo" accept="image/*" required style="width: 100%; padding: 10px; border: 2px dashed #ddd; border-radius: 8px; margin-bottom: 15px;">
                <button type="submit" class="btn" style="width: 100%;">🔄 Actualizar Logo</button>
              </form>
              
              {% if logo_fn %}
                <form method="POST" action="/remove_logo" style="margin-top: 10px;">
                  <button type="submit" class="btn btn-danger" style="width: 100%;" onclick="return confirm('¿Eliminar el logo actual?')">🗑️ Eliminar Logo</button>
                </form>
              {% endif %}
            </div>
          </div>

          <div class="card">
            <div class="card-header">
              <h3 class="card-title">🌅 Banner Principal</h3>
            </div>
            <div style="padding: 20px;">
              {% if banner_fn %}
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center;">
                  <img src="{{ url_for('static', filename='banner/'+banner_fn) }}" style="max-width: 100%; max-height: 120px; object-fit: cover; border-radius: 8px; border: 2px solid #ddd;">
                  <p style="margin: 10px 0 0 0; color: #666; font-size: 14px;">Banner actual</p>
                </div>
              {% else %}
                <div style="background: #f8f9fa; padding: 40px; border-radius: 8px; margin-bottom: 20px; text-align: center; color: #666;">
                  <i>🖼️</i>
                  <p style="margin: 10px 0 0 0;">No hay banner configurado</p>
                </div>
              {% endif %}
              
              <form method="POST" action="/update_banner" enctype="multipart/form-data">
                <input type="file" name="banner" accept="image/*" required style="width: 100%; padding: 10px; border: 2px dashed #ddd; border-radius: 8px; margin-bottom: 15px;">
                <button type="submit" class="btn" style="width: 100%;">🔄 Actualizar Banner</button>
              </form>
              
              {% if banner_fn %}
                <form method="POST" action="/remove_banner" style="margin-top: 10px;">
                  <button type="submit" class="btn btn-danger" style="width: 100%;" onclick="return confirm('¿Eliminar el banner actual?')">🗑️ Eliminar Banner</button>
                </form>
              {% endif %}
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3 class="card-title">ℹ️ Información de Diseño</h3>
          </div>
          <div style="padding: 20px;">
            <div style="background: #e8f4fd; padding: 15px; border-radius: 8px; border-left: 4px solid #3498db; margin-bottom: 20px;">
              <h4 style="margin: 0 0 10px 0; color: #2c3e50;">📐 Recomendaciones de Tamaño</h4>
              <ul style="margin: 0; padding-left: 20px; color: #34495e;">
                <li><strong>Logo:</strong> Máximo 200x100 píxeles, formato rectangular preferido</li>
                <li><strong>Banner:</strong> Mínimo 1200x400 píxeles, formato horizontal</li>
                <li><strong>Formatos soportados:</strong> JPG, PNG, GIF</li>
                <li><strong>Tamaño máximo:</strong> 10MB por archivo</li>
              </ul>
            </div>
            
            <div style="background: #fff9e6; padding: 15px; border-radius: 8px; border-left: 4px solid #f39c12;">
              <h4 style="margin: 0 0 10px 0; color: #2c3e50;">💡 Consejos de Diseño</h4>
              <ul style="margin: 0; padding-left: 20px; color: #34495e;">
                <li>El logo se muestra en forma rectangular (no circular) como solicitaste</li>
                <li>Usar imágenes con fondo transparente para mejor integración</li>
                <li>El banner se muestra en la página de login y registro</li>
                <li>Asegúrate de que el texto en las imágenes sea legible</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
""", logo_fn=logo_fn, banner_fn=banner_fn, BASE_STYLES=BASE_STYLES)

# ——— Ruta para ver detalles de un miembro ———
@app.route("/detalle_miembro/<usuario>")
def detalle_miembro(usuario):
    if session.get("rol") != "admin":
        flash("Acceso denegado. Solo los administradores pueden ver detalles de miembros.")
        return redirect("/login")
    
    con = conectar()
    miembro = con.execute("""
        SELECT nombre, usuario, modalidad, vigencia, foto, correo, telefono_emergencia, datos_medicos
        FROM usuarios WHERE usuario=? AND rol='miembro'
    """, (usuario,)).fetchone()
    
    if not miembro:
        flash("Miembro no encontrado.")
        return redirect("/admin" if session.get("rol") == "admin" else "/moderador")
    
    nombre, usuario, modalidad, vigencia, foto, correo, telefono, datos_medicos = miembro
    dias_rest = dias_restantes(vigencia)
    
    # Obtener últimas 10 asistencias
    asistencias = con.execute("""
        SELECT fecha, hora_entrada, hora_salida
        FROM asistencias 
        WHERE usuario=? 
        ORDER BY fecha DESC, hora_entrada DESC 
        LIMIT 10
    """, (usuario,)).fetchall()
    
    con.close()
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Detalle - {{ nombre }}</title>
  <style>
    body { margin: 0; font-family: 'Segoe UI', Arial, sans-serif; background: #f8f9fa; }
    .container { max-width: 800px; margin: 20px auto; padding: 20px; }
    .header { 
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
      color: white; padding: 30px; border-radius: 12px; text-align: center; 
      box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 30px;
    }
    .photo { 
      width: 120px; height: 120px; border-radius: 50%; 
      object-fit: cover; border: 4px solid white; 
      box-shadow: 0 4px 15px rgba(0,0,0,0.2); margin-bottom: 20px;
    }
    .info { 
      background: white; padding: 25px; border-radius: 12px; 
      box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 25px;
    }
    .info p { margin: 12px 0; font-size: 16px; }
    .btn { 
      background: #667eea; color: white; padding: 10px 20px; 
      border: none, border-radius: 6px; text-decoration: none; 
      display: inline-block; transition: background 0.2s;
    }
    .btn:hover { background: #5a6fd8; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
    th { background: #f0f0f0; }
    .no-print { display: none; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      {% if foto %}
        <img src="{{ url_for('static', filename='fotos/'+foto) }}" class="photo">
      {% endif %}
      <h2>{{ nombre }}</h2>
      <div style="margin-top: 15px;">
        <a href="{{ '/admin' if session['rol']=='admin' else '/moderador' }}" class="btn">← Volver</a>
        <a href="/editar_miembro/{{ usuario }}" class="btn" style="background: #f39c12; margin-left: 10px;">✏️ Editar Datos</a>
      </div>
    </div>
    
    <div class="info">
      <p><strong>Usuario:</strong> {{ usuario }}</p>
      <p><strong>Modalidad:</strong> {{ modalidad }}</p>
      <p><strong>Vigencia:</strong> {{ vigencia }} 
        ({{ dias_rest }} días {{ 'restantes' if dias_rest > 0 else 'vencidos' }})
      </p>
      <p><strong>Correo:</strong> {{ correo or 'No especificado' }}</p>
      <p><strong>Teléfono:</strong> {{ telefono or 'No especificado' }}</p>
      <p><strong>Datos médicos:</strong> {{ datos_medicos or 'No especificado' }}</p>
    </div>
    
    <h3>Últimas Asistencias</h3>
    {% if asistencias %}
    <table>
      <thead><tr><th>Fecha</th><th>Entrada</th><th>Salida</th></tr></thead>
      <tbody>
        {% for fecha, entrada, salida in asistencias %}
        <tr><td>{{ fecha }}</td><td>{{ entrada }}</td><td>{{ salida or '-' }}</td></tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
    <p>No hay asistencias registradas.</p>
    {% endif %}
  </div>
</body>
</html>
""", nombre=nombre, usuario=usuario, modalidad=modalidad, vigencia=vigencia,
     foto=foto, correo=correo, telefono=telefono, datos_medicos=datos_medicos,
     dias_rest=dias_rest, asistencias=asistencias)

@app.route("/editar_miembro/<usuario>")
def editar_miembro(usuario):
    if session.get("rol") != "admin":
        flash("Acceso denegado. Solo los administradores pueden editar miembros.")
        return redirect("/login")
    
    con = conectar()
    
    # Debug: Verificar que usuario llegue correctamente
    print(f"DEBUG: Buscando usuario: '{usuario}'")
    
    # Intentar múltiples búsquedas para asegurar compatibilidad
    import urllib.parse
    usuario_decodificado = urllib.parse.unquote(usuario).strip()
    
    # Búsqueda 1: Exacta
    miembro = con.execute("""
        SELECT id, nombre, usuario, modalidad, vigencia, foto, correo, telefono_emergencia, datos_medicos, nip_visible
        FROM usuarios WHERE usuario=? AND rol='miembro'
    """, (usuario_decodificado,)).fetchone()
    
    # Búsqueda 2: Con TRIM si la primera falla
    if not miembro:
        miembro = con.execute("""
            SELECT id, nombre, usuario, modalidad, vigencia, foto, correo, telefono_emergencia, datos_medicos, nip_visible
            FROM usuarios WHERE TRIM(usuario)=? AND rol='miembro'
        """, (usuario_decodificado,)).fetchone()
    
    # Búsqueda 3: Case insensitive si las anteriores fallan
    if not miembro:
        miembro = con.execute("""
            SELECT id, nombre, usuario, modalidad, vigencia, foto, correo, telefono_emergencia, datos_medicos, nip_visible
            FROM usuarios WHERE LOWER(TRIM(usuario))=LOWER(?) AND rol='miembro'
        """, (usuario_decodificado,)).fetchone()
    
    if not miembro:
        # Debug adicional: verificar todos los usuarios
        todos_usuarios = con.execute("SELECT usuario FROM usuarios WHERE rol='miembro'").fetchall()
        print(f"DEBUG: Usuarios disponibles: {[u[0] for u in todos_usuarios]}")
        print(f"DEBUG: Usuario buscado: '{usuario_decodificado}'")
        print(f"DEBUG: Usuario original: '{usuario}'")
        
        flash(f"Miembro no encontrado: {usuario_decodificado}")
        con.close()
        return redirect("/admin" if session.get("rol") == "admin" else "/moderador")
    
    id_miembro, nombre, usuario_db, modalidad, vigencia, foto, correo, telefono, datos_medicos, nip = miembro
    
    # Obtener logo
    logo_row = con.execute("SELECT filename FROM logo ORDER BY id DESC LIMIT 1").fetchone()
    logo_fn = logo_row[0] if logo_row else ""
    con.close()
    
    # Calcular fecha de inicio estimada a partir de vigencia y modalidad
    fecha_inicio = None
    try:
        dias = 30
        if modalidad == "semanal":
            dias = 7
        elif modalidad == "mensual":
            dias = 30
        elif modalidad == "trimestre":
            dias = 90
        elif modalidad == "semestre":
            dias = 180
        elif modalidad == "anualidad":
            dias = 365
        elif modalidad in ("plan_familiar", "plan_grupal"):
            dias = 30
        if vigencia:
            fecha_inicio_dt = datetime.strptime(vigencia, "%Y-%m-%d") - timedelta(days=dias)
            fecha_inicio = fecha_inicio_dt.strftime("%Y-%m-%d")
    except Exception:
        fecha_inicio = ""
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Editar Miembro - {{ nombre }}</title>
  {{ BASE_STYLES|safe }}
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>{{ 'ADMIN' if session['rol']=='admin' else 'MODERADOR' }} PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="{{ '/admin' if session['rol']=='admin' else '/moderador' }}"><i>🏠</i> Panel Principal</a></li>
        {% if session['rol'] == 'admin' %}
        <li><a href="/reportes_financieros"><i>📊</i> Reportes Financieros</a></li>
        <li><a href="/estadisticas_globales"><i>📈</i> Estadísticas Globales</a></li>
        <li><a href="/analiticas_avanzadas"><i>🔍</i> Analíticas Avanzadas</a></li>
        <li><a href="/gestion_backups"><i>💾</i> Gestión de Backups</a></li>
        <li><a href="/gestion_usuarios_admin"><i>👑</i> Gestión Admins/Moderadores</a></li>
        <li><a href="/corte_caja"><i>💰</i> Corte de Caja</a></li>
        <li><a href="/diseno_plataforma"><i>🎨</i> Diseño de Plataforma</a></li>
        {% endif %}
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header">
        <h1>✏️ Editar Datos del Miembro</h1>
        <div class="breadcrumb">Panel {{ 'Admin' if session['rol']=='admin' else 'Moderador' }} > Editar Miembro > {{ nombre }}</div>
      </div>

      <div class="content-body">
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">📝 Modificar Información Personal</h3>
          </div>
          <form method="POST" action="/actualizar_miembro" enctype="multipart/form-data" style="padding: 25px;">
            <input type="hidden" name="id_miembro" value="{{ id_miembro }}">
            <input type="hidden" name="usuario_original" value="{{ usuario }}">
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 25px;">
              <div>
                <div class="form-group">
                  <label class="form-label">Nombre completo</label>
                  <input type="text" name="nombre" value="{{ nombre }}" required>
                </div>
                
                <div class="form-group">
                  <label class="form-label">Nombre de usuario</label>
                  <input type="text" name="usuario" value="{{ usuario }}" required>
                </div>
                
                <div class="form-group">
                  <label class="form-label">Modalidad</label>
                  <select name="modalidad" id="modalidad-admin" required>
                    <option value="semanal" {{ 'selected' if modalidad=='semanal' else '' }}>Semanal</option>
                    <option value="mensual" {{ 'selected' if modalidad=='mensual' else '' }}>Mensual</option>
                    <option value="trimestre" {{ 'selected' if modalidad=='trimestre' else '' }}>Trimestre</option>
                    <option value="semestre" {{ 'selected' if modalidad=='semestre' else '' }}>Semestre</option>
                    <option value="anualidad" {{ 'selected' if modalidad=='anualidad' else '' }}>Anualidad</option>
                    <option value="plan_familiar" {{ 'selected' if modalidad=='plan_familiar' else '' }}>Plan Familiar</option>
                    <option value="plan_grupal" {{ 'selected' if modalidad=='plan_grupal' else '' }}>Plan Grupal</option>
                  </select>
                </div>
               <div class="form-group">
                 <label class="form-label">Fecha de inicio de membresía (opcional)</label>
            <input type="date" name="fecha_inicio" value="{{ fecha_inicio or '' }}" placeholder="Si no se especifica, inicia desde hoy">
                 <small style="color: #666; font-size: 0.85em; display: block; margin-top: 5px;">
                   💡 Si no especificas una fecha, la membresía iniciará desde hoy
                 </small>
               </div>
                  
                  <!-- Contenedor para selección de familia ADMIN -->
                  <div id="family-selection-container-admin" style="display: none; grid-column: 1 / -1;">
                    <div class="form-group">
                      <label class="form-label" style="color: #27ae60; font-weight: bold;">👪 Miembros de la Familia</label>
                      <p style="font-size: 0.9em; color: #7f8c8d; margin-bottom: 15px;">
                        Selecciona los miembros existentes que pertenecen a esta familia. 
                        El sistema buscará automáticamente miembros con apellidos similares.
                      </p>
                      <div id="family-members-list-admin" style="border: 1px solid #ddd; border-radius: 5px; padding: 15px; background: #f9f9f9;">
                        <p style="color: #7f8c8d; font-style: italic;">Ingresa el nombre completo para buscar miembros de la familia...</p>
                      </div>
                    </div>
                  </div>
                
                <div class="form-group">
                  <label class="form-label">NIP de acceso (4 dígitos)</label>
                  <input type="text" name="nip" value="{{ nip }}" pattern="[0-9]{4}" maxlength="4" required>
                  <small style="color: #666; font-size: 0.85em; display: block; margin-top: 5px;">
                    💡 Código que usa el miembro para marcar asistencia
                  </small>
                </div>
              </div>
              
              <div>
                <div class="form-group">
                  <label class="form-label">Correo electrónico (opcional)</label>
                  <input type="email" name="correo" value="{{ correo or '' }}">
                </div>
                
                <div class="form-group">
                  <label class="form-label">Teléfono de emergencia (opcional)</label>
                  <input type="text" name="telefono_emergencia" value="{{ telefono or '' }}">
                </div>
                
                <div class="form-group">
                  <label class="form-label">Datos médicos (opcional)</label>
                  <textarea name="datos_medicos" rows="4">{{ datos_medicos or '' }}</textarea>
                </div>
                
                <div class="form-group">
                  <label class="form-label">Cambiar foto (opcional)</label>
                  <input type="file" name="foto" accept="image/*">
                  {% if foto %}
                    <small style="color: #666; font-size: 0.85em; display: block; margin-top: 5px;">
                      📷 Foto actual: {{ foto }}
                    </small>
                  {% endif %}
                </div>
              </div>
            </div>
            
            {% if foto %}
            <div style="text-align: center; margin-bottom: 25px;">
              <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; display: inline-block;">
                <img src="{{ url_for('static', filename='fotos/'+foto) }}" style="max-width: 150px; max-height: 150px; object-fit: cover; border-radius: 8px; border: 2px solid #ddd;">
                <p style="margin: 10px 0 0 0; color: #666; font-size: 14px;">Foto actual</p>
              </div>
            </div>
            {% endif %}
            
            <div style="background: #fff9e6; padding: 15px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #f39c12;">
              <h4 style="margin: 0 0 10px 0; color: #2c3e50;">⚠️ Información Importante</h4>
              <ul style="margin: 0; padding-left: 20px; color: #34495e;">
                <li>La vigencia actual se mantiene: <strong>{{ vigencia }}</strong></li>
                <li>Si cambias la modalidad, usa el botón "Renovar" en el panel principal para recalcular la vigencia</li>
                <li>El cambio de usuario afectará el acceso del miembro</li>
                <li>Todos los cambios se guardan inmediatamente</li>
              </ul>
            </div>
            
            <div style="display: flex; gap: 10px; justify-content: center;">
              <button type="submit" class="btn" style="background: #27ae60;">💾 Guardar Cambios</button>
              <a href="/detalle_miembro/{{ usuario }}" class="btn btn-secondary">❌ Cancelar</a>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
""", id_miembro=id_miembro, nombre=nombre, usuario=usuario_db, modalidad=modalidad, 
     vigencia=vigencia, foto=foto, correo=correo, telefono=telefono, 
     datos_medicos=datos_medicos, nip=nip, logo_fn=logo_fn, BASE_STYLES=BASE_STYLES)

@app.route("/actualizar_miembro", methods=["POST"])
def actualizar_miembro():
    if session.get("rol") != "admin":
        flash("Acceso denegado. Solo los administradores pueden editar miembros.")
        return redirect("/login")
    
    try:
        # Validar que todos los campos requeridos estén presentes
        campos_requeridos = ["id_miembro", "usuario_original", "nombre", "usuario", "modalidad", "nip"]
        for campo in campos_requeridos:
            if campo not in request.form:
                flash(f"Error: Campo requerido '{campo}' no encontrado en el formulario.")
                return redirect("/admin")
            if not request.form[campo].strip():
                flash(f"Error: El campo '{campo}' no puede estar vacío.")
                return redirect("/admin")
        
        id_miembro = request.form["id_miembro"]
        usuario_original = request.form["usuario_original"]
        nombre = request.form["nombre"].strip()
        usuario = request.form["usuario"].strip()
        modalidad = request.form["modalidad"]
        nip = request.form["nip"].strip()
        pin_nuevo = request.form.get("pin", "").strip()  # PIN es opcional
        correo = request.form.get("correo", "").strip() or None
        telefono_emergencia = request.form.get("telefono_emergencia", "").strip() or None
        datos_medicos = request.form.get("datos_medicos", "").strip() or None
        fecha_inicio = request.form.get("fecha_inicio", None)
        
        # Validar NIP
        if not (nip.isdigit() and len(nip) == 4):
            flash("El NIP debe ser numérico de 4 dígitos.")
            return redirect(f"/editar_miembro_por_id/{id_miembro}")
        
        # Validar PIN si se proporciona
        if pin_nuevo and not (pin_nuevo.isdigit() and len(pin_nuevo) == 4):
            flash("El PIN debe ser numérico de 4 dígitos.")
            return redirect(f"/editar_miembro_por_id/{id_miembro}")
        
        # Validar que el nombre de usuario no esté vacío
        if len(usuario) < 2:
            flash("El nombre de usuario debe tener al menos 2 caracteres.")
            return redirect(f"/editar_miembro_por_id/{id_miembro}")
        
        # Validar que el nombre completo no esté vacío
        if len(nombre) < 2:
            flash("El nombre completo debe tener al menos 2 caracteres.")
            return redirect(f"/editar_miembro_por_id/{id_miembro}")
    
        con = conectar()
        # Verificar que el miembro existe y obtener vigencia actual
        miembro_existe = con.execute("SELECT usuario, pin, vigencia FROM usuarios WHERE id=?", (id_miembro,)).fetchone()
        if not miembro_existe:
            flash("Error: El miembro no existe.")
            con.close()
            return redirect("/admin")
        vigencia = miembro_existe[2]
        # Determinar qué PIN usar
        pin_encriptado = encriptar(pin_nuevo) if pin_nuevo else miembro_existe[1]  # Mantener el PIN actual si no se proporciona uno nuevo
        
        # Manejar subida de nueva foto
        foto_filename = None
        if 'foto' in request.files and request.files['foto'].filename:
            foto = request.files['foto']
            if foto and foto.filename:
                # Obtener foto actual para eliminarla si existe
                foto_actual = con.execute("SELECT foto FROM usuarios WHERE id=?", (id_miembro,)).fetchone()
                
                # Eliminar foto anterior si existe
                if foto_actual and foto_actual[0]:
                    try:
                        os.remove(os.path.join(FOTOS_FOLDER, foto_actual[0]))
                    except:
                        pass
                
                # Guardar nueva foto
                foto_filename = f"{usuario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{foto.filename.split('.')[-1]}"
                foto.save(os.path.join(FOTOS_FOLDER, foto_filename))
        
        # Si se proporciona fecha_inicio o cambia modalidad, recalcular vigencia
        nueva_vigencia = None
        if fecha_inicio or modalidad:
            try:
                nueva_vigencia = calcular_vigencia(modalidad, fecha_inicio if fecha_inicio else None)
            except Exception as e:
                nueva_vigencia = None
        
        if foto_filename:
            con.execute("""
                UPDATE usuarios 
                SET nombre=?, usuario=?, modalidad=?, nip_visible=?, pin=?, 
                    correo=?, telefono_emergencia=?, datos_medicos=?, foto=?, vigencia=?
                WHERE id=?
            """, (nombre, usuario, modalidad, nip, pin_encriptado, correo, 
                  telefono_emergencia, datos_medicos, foto_filename, nueva_vigencia if nueva_vigencia else vigencia, id_miembro))
        else:
            con.execute("""
                UPDATE usuarios 
                SET nombre=?, usuario=?, modalidad=?, nip_visible=?, pin=?, 
                    correo=?, telefono_emergencia=?, datos_medicos=?, vigencia=?
                WHERE id=?
            """, (nombre, usuario, modalidad, nip, pin_encriptado, correo, 
                  telefono_emergencia, datos_medicos, nueva_vigencia if nueva_vigencia else vigencia, id_miembro))
        
        con.commit()
        con.close()
        
        flash(f"Datos de {nombre} actualizados exitosamente.")
        return redirect(f"/detalle_miembro/{usuario}")
        
    except sqlite3.IntegrityError as e:
        flash(f"Error de integridad: El nombre de usuario '{usuario}' ya existe.")
        return redirect(f"/editar_miembro_por_id/{id_miembro}")
    except KeyError as e:
        flash(f"Error: Campo requerido faltante: {str(e)}")
        return redirect("/admin")
    except Exception as e:
        flash(f"Error inesperado al actualizar miembro: {str(e)}")
        return redirect(f"/editar_miembro_por_id/{id_miembro}")

@app.route("/registrar_asistencia", methods=["POST"])
def registrar_asistencia():
    if session.get("rol") not in ("admin", "moderador"):
        return redirect("/login")
    
    usuario = request.form["usuario"]
    fecha = datetime.now().strftime("%Y-%m-%d")
    hora = datetime.now().strftime("%H:%M")
    
    con = conectar()
    
    # Verificar si ya existe asistencia hoy
    existe = con.execute("SELECT id FROM asistencias WHERE usuario=? AND fecha=?", (usuario, fecha)).fetchone()
    
    if existe:
        # Actualizar hora de salida
        con.execute("UPDATE asistencias SET hora_salida=? WHERE usuario=? AND fecha=?", (hora, usuario, fecha))
        flash(f"Hora de salida registrada para {usuario}")
    else:
        # Registrar entrada
        con.execute("INSERT INTO asistencias (usuario, fecha, hora_entrada, hora_salida) VALUES (?, ?, ?, ?)",
                   (usuario, fecha, hora, ""))
        flash(f"Asistencia registrada para {usuario}")
    
    con.commit()
    con.close()
    
    return redirect("/moderador" if session.get("rol") == "moderador" else "/admin")

@app.route("/registrar_pago", methods=["POST"])
def registrar_pago():
    if session.get("rol") not in ("admin", "moderador"):
        return redirect("/login")
    
    usuario = request.form["usuario"]
    concepto = request.form["concepto"]
    
    # Montos automáticos según el concepto
    montos_automaticos = {
        "Mensualidad": 400.00,
        "Semana": 120.00,
        "Clase": 50.00,
        "Tres clases": 100.00,
        "Semana con Yoga": 150.00,
        "Clase de Yoga": 80.00,
        "Pareja": 700.00,
        "Tres personas": 1000.00,
        "Cuatro personas": 1300.00,
        "Cinco personas": 1600.00
    }
    
    # Si hay un monto manual enviado, usarlo; si no, usar el automático
    monto_manual = request.form.get("monto")
    if monto_manual and float(monto_manual) > 0:
        monto = float(monto_manual)
    else:
        monto = montos_automaticos.get(concepto, 0.00)
    
    # Solo los admins pueden modificar la fecha, moderadores usan fecha actual
    if session.get("rol") == "admin" and request.form.get("fecha"):
        fecha = request.form["fecha"]
    else:
        fecha = datetime.now().strftime("%Y-%m-%d")
    
    con = conectar()
    
    # Obtener información del usuario que paga
    usuario_info = con.execute("""
        SELECT id, nombre, modalidad, vigencia 
        FROM usuarios 
        WHERE usuario = ? AND rol = 'miembro'
    """, (usuario,)).fetchone()
    
    if not usuario_info:
        con.close()
        flash(f"Usuario {usuario} no encontrado")
        return redirect("/moderador" if session.get("rol") == "moderador" else "/admin")
    
    usuario_id, nombre_usuario, modalidad_actual, vigencia_actual = usuario_info
    
    # Calcular nuevo monto y nuevas vigencias según el tipo de plan
    monto_final = monto
    miembros_a_actualizar = []
    
    if modalidad_actual == "plan_familiar":
        # Obtener miembros de la familia
        familia_info = con.execute("""
            SELECT pf.id, COUNT(mf.id) as total_miembros
            FROM planes_familiares pf
            JOIN miembros_familia mf ON pf.id = mf.plan_familiar_id
            WHERE pf.responsable_id = ? AND pf.activo = 1 AND mf.activo = 1
        """, (usuario_id,)).fetchone()
        
        if familia_info:
            plan_familiar_id, total_miembros = familia_info
            monto_final = monto * total_miembros
            
            # Obtener todos los miembros de la familia
            miembros_familia = con.execute("""
                SELECT u.id, u.usuario, u.nombre
                FROM miembros_familia mf
                JOIN usuarios u ON mf.miembro_id = u.id
                WHERE mf.plan_familiar_id = ? AND mf.activo = 1
            """, (plan_familiar_id,)).fetchall()
            
            miembros_a_actualizar = miembros_familia
    
    elif modalidad_actual == "plan_grupal":
        # Obtener miembros del grupo
        grupo_info = con.execute("""
            SELECT pg.id, COUNT(mg.id) as total_miembros
            FROM planes_grupales pg
            JOIN miembros_grupo mg ON pg.id = mg.plan_grupal_id
            WHERE pg.responsable_id = ? AND pg.activo = 1 AND mg.activo = 1
        """, (usuario_id,)).fetchone()
        
        if grupo_info:
            plan_grupal_id, total_miembros = grupo_info
            monto_final = monto * total_miembros
            
            # Obtener todos los miembros del grupo
            miembros_grupo = con.execute("""
                SELECT u.id, u.usuario, u.nombre
                FROM miembros_grupo mg
                JOIN usuarios u ON mg.miembro_id = u.id
                WHERE mg.plan_grupal_id = ? AND mg.activo = 1
            """, (plan_grupal_id,)).fetchall()
            
            miembros_a_actualizar = miembros_grupo
    else:
        # Plan individual
        miembros_a_actualizar = [(usuario_id, usuario, nombre_usuario)]
    
    # Calcular nueva vigencia según el concepto, usando la fecha del pago como base
    nueva_vigencia = None
    if concepto in ["Mensualidad", "Pareja", "Tres personas", "Cuatro personas", "Cinco personas"]:
        nueva_vigencia = calcular_vigencia("mensual", fecha)
    elif concepto in ["Semana", "Semana con Yoga"]:
        nueva_vigencia = calcular_vigencia("semanal", fecha)
    elif concepto in ["Clase", "Tres clases", "Clase de Yoga"]:
        # Para clases individuales, extender por días específicos desde la fecha del pago
        fecha_pago = datetime.strptime(fecha, "%Y-%m-%d")
        if concepto == "Clase" or concepto == "Clase de Yoga":
            # 1 día de vigencia desde la fecha del pago
            nueva_vigencia = (fecha_pago + timedelta(days=1)).strftime("%Y-%m-%d")
        elif concepto == "Tres clases":
            # 3 días de vigencia desde la fecha del pago
            nueva_vigencia = (fecha_pago + timedelta(days=3)).strftime("%Y-%m-%d")
    
    # Registrar el pago
    con.execute("INSERT INTO pagos (usuario, monto, fecha, concepto) VALUES (?, ?, ?, ?)",
               (usuario, monto_final, fecha, concepto))
    
    # Actualizar vigencia de todos los miembros afectados
    miembros_actualizados = []
    if nueva_vigencia:
        for miembro_id, miembro_usuario, miembro_nombre in miembros_a_actualizar:
            # Actualizar la vigencia del miembro
            con.execute("""
                UPDATE usuarios 
                SET vigencia = ? 
                WHERE id = ?
            """, (nueva_vigencia, miembro_id))
            miembros_actualizados.append(miembro_nombre)
    
    con.commit()
    con.close()
    
    # Mensaje de confirmación detallado
    if len(miembros_actualizados) > 1:
        mensaje = f"Pago de ${monto_final:.2f} registrado para {concepto}. "
        mensaje += f"Vigencia actualizada para {len(miembros_actualizados)} miembros: "
        mensaje += ", ".join(miembros_actualizados[:3])
        if len(miembros_actualizados) > 3:
            mensaje += f" y {len(miembros_actualizados) - 3} más"
        if nueva_vigencia:
            mensaje += f" hasta {nueva_vigencia}"
    else:
        mensaje = f"Pago de ${monto_final:.2f} registrado para {usuario} ({concepto})"
        if nueva_vigencia:
            mensaje += f". Vigencia actualizada hasta {nueva_vigencia}"
    
    flash(mensaje)
    return redirect("/moderador" if session.get("rol") == "moderador" else "/admin")

@app.route("/gestion_backups")
def gestion_backups():
    if session.get("rol") != "admin":
        return redirect("/login")
    
    con = conectar()
    # Obtener logo
    logo_row = con.execute("SELECT filename FROM logo ORDER BY id DESC LIMIT 1").fetchone()
    logo_fn = logo_row[0] if logo_row else ""
    con.close()
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Gestión de Backups</title>
  {{ BASE_STYLES|safe }}
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>ADMIN PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="/admin"><i>🏠</i> Panel Principal</a></li>
        <li><a href="/reportes_financieros"><i>📊</i> Reportes Financieros</a></li>
        <li><a href="/estadisticas_globales"><i>📈</i> Estadísticas Globales</a></li>
        <li><a href="/analiticas_avanzadas"><i>🔍</i> Analíticas Avanzadas</a></li>
        <li><a href="/gestion_backups" class="active"><i>💾</i> Gestión de Backups</a></li>
        <li><a href="/gestion_usuarios_admin"><i>👑</i> Gestión Admins/Moderadores</a></li>
        <li><a href="/corte_caja"><i>💰</i> Corte de Caja</a></li>
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header">
        <h1>💾 Gestión de Backups</h1>
        <div class="breadcrumb">Panel Admin > Gestión de Backups</div>
      </div>

      <div class="content-body">
        <div class="card" style="margin-bottom: 25px;">
          <div class="card-header">
            <h3 class="card-title">🔄 Crear Backup Manual</h3>
          </div>
          <div style="padding: 20px;">
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #3498db;">
              <p style="margin: 0 0 10px 0;"><strong>📂 Ubicación:</strong> Los backups se guardan en la carpeta <code>backups/</code></p>
              <p style="margin: 0;"><strong>⏰ Automático:</strong> Se crean backups automáticos cada vez que se inicia el sistema</p>
            </div>
            <button class="btn" onclick="createBackup()">🔄 Crear Backup Ahora</button>
          </div>
        </div>
        
        <div class="card" style="margin-bottom: 25px;">
          <div class="card-header">
            <h3 class="card-title">📋 Información del Sistema</h3>
          </div>
          <div style="padding: 20px;">
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #27ae60;">
              <p style="margin: 0 0 10px 0;"><strong>Base de datos:</strong> lama_control.db</p>
              <p style="margin: 0 0 10px 0;"><strong>Fotos de miembros:</strong> uploads/</p>
              <p style="margin: 0;"><strong>Última actualización:</strong> {{ fecha_actual }}</p>
            </div>
          </div>
        </div>
        
        <div class="card">
          <div class="card-header" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white;">
            <h3 class="card-title">⚠️ Zona de Peligro - Reset Completo</h3>
          </div>
          <div style="padding: 20px;">
            <div style="background: #fff5f5; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #e74c3c;">
              <h4 style="margin: 0 0 10px 0; color: #c0392b;">🚨 RESET DE LA PLATAFORMA</h4>
              <p style="margin: 0; color: #c0392b;"><strong>Esta acción eliminará:</strong></p>
              <ul style="margin: 10px 0 0 20px; color: #c0392b;">
                <li>Todos los miembros registrados</li>
                <li>Todas las asistencias</li>
                <li>Todos los administradores y moderadores (excepto alfredo)</li>
                <li>Fotos de miembros</li>
              </ul>
              <p style="margin: 10px 0 0 0; color: #27ae60;"><strong>Se conservarán:</strong></p>
              <ul style="margin: 10px 0 0 20px; color: #27ae60;">
                <li>La cuenta del administrador principal (alfredo)</li>
                <li>🎨 Logos y banners personalizados</li>
                <li>💰 <strong>Historial de pagos para reportes financieros</strong></li>
              </ul>
            </div>
            <button class="btn btn-danger" onclick="confirmCompleteReset()">🔥 RESETEAR PLATAFORMA (Conservar Logo/Banner/Pagos)</button>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <script>
    function createBackup() {
      if (confirm('¿Crear un backup manual de la base de datos?')) {
        fetch('/crear_backup', { method: 'POST' })
          .then(response => response.json())
          .then(data => alert(data.message))
          .catch(error => alert('Error al crear backup'));
      }
    }
    
    function confirmCompleteReset() {
      if (confirm('🚨 ¿ESTÁS SEGURO DE RESETEAR LA PLATAFORMA?\\n\\nEsta acción eliminará:\\n• Todos los miembros\\n• Todas las asistencias\\n• Todos los admins/moderadores (excepto alfredo)\\n• Fotos de miembros\\n\\n✅ SE CONSERVARÁN:\\n• Logos y banners\\n• Cuenta del administrador principal\\n• 💰 Historial de pagos (reportes financieros)\\n\\n❌ ESTA ACCIÓN ES IRREVERSIBLE ❌')) {
        if (confirm('⚠️ SEGUNDA CONFIRMACIÓN ⚠️\\n\\n¿Realmente quieres RESETEAR la plataforma?\\n\\nRecuerda: Los logos y banners se mantendrán.')) {
          if (confirm('🔥 ÚLTIMA CONFIRMACIÓN 🔥\\n\\n¿Proceder con el reset de la plataforma?\\n(Logos y banners se conservarán)')) {
            // Mostrar mensaje de proceso
            alert('🔄 Iniciando reset de la plataforma...\\n\\nEsto puede tomar unos segundos.');
            
            // Enviar solicitud al servidor
            fetch('/reset_database', {
              method: 'GET',
              credentials: 'same-origin'
            }).then(response => {
              if (response.ok) {
                alert('✅ PLATAFORMA RESETEADA EXITOSAMENTE\\n\\nLogos, banners e historial de pagos conservados.');
                window.location.href = '/admin';
              } else {
                alert('Error al resetear la plataforma. Inténtalo de nuevo.');
              }
            }).catch(error => {
              console.error('Error:', error);
              alert('Error de conexión. Inténtalo de nuevo.');
            });
          }
        }
      }
    }
  </script>
</body>
</html>
    """, fecha_actual=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), BASE_STYLES=BASE_STYLES, logo_fn=logo_fn)

@app.route("/crear_backup", methods=["POST"])
def crear_backup():
    if session.get("rol") != "admin":
        return {"error": "No autorizado"}, 401
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.db"
        backup_path = os.path.join("backups", backup_filename)
        
        # Crear directorio si no existe
        os.makedirs("backups", exist_ok=True)
        
        # Copiar la base de datos
        shutil.copy2("lama_control.db", backup_path)
        
        return {"message": f"Backup creado exitosamente: {backup_filename}"}
    except Exception as e:
        return {"error": f"Error al crear backup: {str(e)}"}, 500

@app.route("/reset_database")
def reset_database():
    if session.get("rol") != "admin":
        return redirect("/login")
    
    try:
        # Crear backup antes de resetear
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_before_reset_{timestamp}.db"
        backup_path = os.path.join("backups", backup_filename)
        os.makedirs("backups", exist_ok=True)
        shutil.copy2("lama_control.db", backup_path)
        
        # Resetear la base de datos completamente (excepto admin principal)
        con = conectar()
        
        # Eliminar todos los datos de miembros
        con.execute("DELETE FROM usuarios WHERE rol = 'miembro'")
        con.execute("DELETE FROM asistencias")
        # NO eliminar pagos - se conservan para reportes financieros e histórico
        # con.execute("DELETE FROM pagos")
        
        # Eliminar todos los administradores y moderadores excepto el principal
        con.execute("DELETE FROM usuarios WHERE rol IN ('admin', 'moderador') AND usuario != 'alfredo'")
        
        # NO eliminar logos y banners - se mantienen
        # con.execute("DELETE FROM logo")
        # con.execute("DELETE FROM banner")
        
        con.commit()
        con.close()
        
        # Limpiar archivos físicos SOLO de fotos de miembros
        try:
            # Limpiar SOLO fotos de miembros
            uploads_dir = "uploads"
            if os.path.exists(uploads_dir):
                for filename in os.listdir(uploads_dir):
                    if filename != ".gitkeep":  # Mantener archivo de control de git si existe
                        file_path = os.path.join(uploads_dir, filename)
                        try:
                            os.remove(file_path)
                            print(f"Eliminado: {file_path}")
                        except Exception as e:
                            print(f"No se pudo eliminar {file_path}: {e}")
            
            # NO limpiar logos ni banners - se mantienen
            # Los logos y banners se conservan después del reset
                        
        except Exception as file_error:
            print(f"Advertencia: No se pudieron limpiar algunos archivos: {file_error}")
        
        flash(f"✅ PLATAFORMA RESETEADA ✅\n" +
              f"• Todos los miembros eliminados\n" +
              f"• Todas las asistencias eliminadas\n" +
              f"• Todos los admins/moderadores eliminados (excepto alfredo)\n" +
              f"• Fotos de miembros eliminadas\n" +
              f"• 🎨 LOGOS Y BANNERS CONSERVADOS\n" +
              f"• 💰 HISTORIAL DE PAGOS CONSERVADO\n" +
              f"• Backup guardado como: {backup_filename}\n\n" +
              f"La plataforma ha sido reseteada manteniendo la personalización visual y reportes financieros.")
        return redirect("/admin")
    except Exception as e:
        flash(f"Error al resetear la base de datos: {str(e)}")
        return redirect("/gestion_backups")

@app.route("/gestion_usuarios_admin")
def gestion_usuarios_admin():
    if session.get("rol") != "admin" or session.get("usuario") != "alfredo":
        flash("Acceso denegado. Solo el administrador principal puede gestionar usuarios administrativos.")
        return redirect("/admin")
    
    con = conectar()
    usuarios_admin = con.execute("""
        SELECT id, nombre, usuario, rol
        FROM usuarios 
        WHERE rol IN ('admin', 'moderador') AND usuario != 'alfredo'
        ORDER BY rol, nombre
    """).fetchall()
    con.close()
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Gestión de Administradores y Moderadores</title>
  {{ BASE_STYLES|safe }}
  <style>
    .user-grid { 
      display: grid; 
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
      gap: 20px; 
    }
    .user-card { 
      background: rgba(255, 255, 255, 0.95);
      padding: 25px; 
      border-radius: 12px; 
      border-left: 5px solid #3498db;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
      transition: transform 0.3s ease;
    }
    .user-card:hover {
      transform: translateY(-3px);
    }
    .user-card.moderador { 
      border-left-color: #e67e22; 
    }
    .user-card h3 {
      margin: 0 0 15px 0;
      color: #2c3e50;
      font-size: 1.3em;
    }
    .user-card p {
      margin: 8px 0;
      color: #555;
    }
    .role-badge {
      background: #3498db;
      color: white;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.85em;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .role-badge.moderador {
      background: #e67e22;
    }
    .user-actions {
      margin-top: 20px;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .user-actions .btn {
      padding: 8px 16px;
      font-size: 0.9em;
      margin: 0;
    }
    .modal { 
      display: none; 
      position: fixed; 
      z-index: 1000; 
      left: 0; 
      top: 0; 
      width: 100%; 
      height: 100%; 
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(5px);
    }
    .modal-content { 
      background: white; 
      margin: 5% auto; 
      padding: 30px; 
      border-radius: 15px; 
      width: 90%; 
      max-width: 500px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }
    .close { 
      color: #aaa; 
      float: right; 
      font-size: 28px; 
      font-weight: bold; 
      cursor: pointer;
      transition: color 0.3s ease;
    }
    .close:hover { 
      color: #e74c3c; 
    }
    .access-warning {
      background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
      color: white;
      padding: 20px;
      border-radius: 12px;
      margin-bottom: 25px;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>ADMIN PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="/admin"><i>🏠</i> Panel Principal</a></li>
        <li><a href="/reportes_financieros"><i>📊</i> Reportes Financieros</a></li>
        <li><a href="/estadisticas_globales"><i>📈</i> Estadísticas Globales</a></li>
        <li><a href="/analiticas_avanzadas"><i>🔍</i> Analíticas Avanzadas</a></li>
        <li><a href="/gestion_backups"><i>💾</i> Gestión de Backups</a></li>
        <li><a href="/gestion_usuarios_admin" class="active"><i>👑</i> Gestión Admins/Moderadores</a></li>
        <li><a href="/corte_caja"><i>💰</i> Corte de Caja</a></li>
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header">
        <h1>👑 Gestión de Administradores y Moderadores</h1>
        <div class="breadcrumb">Panel Admin > Gestión de Usuarios Administrativos</div>
      </div>

      <div class="content-body">
        <div class="access-warning">
          <h3 style="margin: 0 0 10px 0;">⚠️ Zona de Administración Avanzada</h3>
          <p style="margin: 0;">Solo el administrador principal puede gestionar usuarios administrativos del sistema.</p>
        </div>
        
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">📋 Usuarios Administrativos Activos</h3>
          </div>
          
          {% if usuarios_admin %}
            <div class="user-grid">
              {% for id, nombre, usuario, rol in usuarios_admin %}
              <div class="user-card {{ rol }}">
                <h3>{{ nombre }}</h3>
                <p><strong>Usuario:</strong> {{ usuario }}</p>
                <p><strong>Rol:</strong> 
                  <span class="role-badge {{ rol }}">
                    {{ rol.upper() }}
                  </span>
                </p>
                <div class="user-actions">
                  <button class="btn btn-warning" onclick="editUser({{ id }}, '{{ nombre }}', '{{ usuario }}', '{{ rol }}')">
                    ✏️ Editar
                  </button>
                  <button class="btn btn-secondary" onclick="changePassword({{ id }}, '{{ usuario }}')">
                    🔑 Cambiar PIN
                  </button>
                  <button class="btn btn-danger" onclick="deleteUser({{ id }}, '{{ nombre }}', '{{ usuario }}')">
                    🗑️ Eliminar
                  </button>
                </div>
              </div>
              {% endfor %}
            </div>
          {% else %}
            <div style="text-align: center; padding: 40px; color: #7f8c8d;">
              <h3>👥 No hay usuarios administrativos adicionales</h3>
              <p>Puedes crear nuevos administradores y moderadores desde el panel principal.</p>
              <a href="/admin" class="btn">← Volver al Panel Principal</a>
            </div>
          {% endif %}
        </div>
      </div>
    </div>
  </div>

  <!-- Modal para editar usuario -->
  <div id="editModal" class="modal">
    <div class="modal-content">
      <span class="close" onclick="closeModal('editModal')">&times;</span>
      <h2>✏️ Editar Usuario Administrativo</h2>
      <form id="editForm" method="POST" action="/editar_usuario_admin">
        <input type="hidden" id="edit_id" name="id">
        <div class="form-group">
          <label class="form-label" for="edit_nombre">Nombre completo:</label>
          <input type="text" id="edit_nombre" name="nombre" required>
        </div>
        <div class="form-group">
          <label class="form-label" for="edit_usuario">Nombre de usuario:</label>
          <input type="text" id="edit_usuario" name="usuario" required>
        </div>
        <div class="form-group">
          <label class="form-label" for="edit_rol">Rol en el sistema:</label>
          <select id="edit_rol" name="rol" required>
            <option value="admin">Administrador</option>
            <option value="moderador">Moderador</option>
          </select>
        </div>
        <div style="margin-top: 25px;">
          <button type="submit" class="btn">💾 Guardar Cambios</button>
          <button type="button" class="btn btn-secondary" onclick="closeModal('editModal')">❌ Cancelar</button>
        </div>
      </form>
    </div>
  </div>

  <!-- Modal para cambiar contraseña -->
  <div id="passwordModal" class="modal">
    <div class="modal-content">
      <span class="close" onclick="closeModal('passwordModal')">&times;</span>
      <h2>🔑 Cambiar PIN de Acceso</h2>
      <form id="passwordForm" method="POST" action="/cambiar_pin_admin">
        <input type="hidden" id="pass_id" name="id">
        <input type="hidden" id="pass_usuario" name="usuario">
        <div class="form-group">
          <label class="form-label" for="nuevo_pin">Nuevo PIN (4 dígitos):</label>
          <input type="text" id="nuevo_pin" name="nuevo_pin" pattern="[0-9]{4}" maxlength="4" placeholder="0000" required>
        </div>
        <div class="form-group">
          <label class="form-label" for="confirmar_pin">Confirmar nuevo PIN:</label>
          <input type="text" id="confirmar_pin" name="confirmar_pin" pattern="[0-9]{4}" maxlength="4" placeholder="0000" required>
        </div>
        <div style="margin-top: 25px;">
          <button type="submit" class="btn">🔑 Cambiar PIN</button>
          <button type="button" class="btn btn-secondary" onclick="closeModal('passwordModal')">❌ Cancelar</button>
        </div>
      </form>
    </div>
  </div>

  <script>
    function editUser(id, nombre, usuario, rol) {
      document.getElementById('edit_id').value = id;
      document.getElementById('edit_nombre').value = nombre;
      document.getElementById('edit_usuario').value = usuario;
      document.getElementById('edit_rol').value = rol;
      document.getElementById('editModal').style.display = 'block';
    }

    function changePassword(id, usuario) {
      document.getElementById('pass_id').value = id;
      document.getElementById('pass_usuario').value = usuario;
      document.getElementById('nuevo_pin').value = '';
      document.getElementById('confirmar_pin').value = '';
      document.getElementById('passwordModal').style.display = 'block';
    }

    function deleteUser(id, nombre, usuario) {
      if (confirm(`¿Estás seguro de eliminar al usuario "${nombre}" (${usuario})?\\n\\nEsta acción es IRREVERSIBLE.`)) {
        if (confirm('⚠️ ÚLTIMA CONFIRMACIÓN: ¿Eliminar permanentemente este usuario administrativo?')) {
          window.location.href = `/eliminar_usuario_admin/${id}`;
        }
      }
    }

    function closeModal(modalId) {
      document.getElementById(modalId).style.display = 'none';
    }

    // Cerrar modal al hacer clic fuera de él
    window.onclick = function(event) {
      const editModal = document.getElementById('editModal');
      const passwordModal = document.getElementById('passwordModal');
      if (event.target == editModal) {
        editModal.style.display = 'none';
      }
      if (event.target == passwordModal) {
        passwordModal.style.display = 'none';
      }
    }
  </script>
</body>
</html>
""", usuarios_admin=usuarios_admin, logo_fn="", BASE_STYLES=BASE_STYLES)

@app.route("/editar_usuario_admin", methods=["POST"])
def editar_usuario_admin():
    if session.get("rol") != "admin" or session.get("usuario") != "alfredo":
        flash("Acceso denegado.")
        return redirect("/admin")
    
    user_id = request.form["id"]
    nombre = request.form["nombre"]
    usuario = request.form["usuario"]
    rol = request.form["rol"]
    
    try:
        con = conectar()
        con.execute("""
            UPDATE usuarios 
            SET nombre=?, usuario=?, rol=? 
            WHERE id=? AND usuario != 'alfredo'
        """, (nombre, usuario, rol, user_id))
        con.commit()
        con.close()
        flash(f"Usuario {usuario} actualizado exitosamente.")
    except sqlite3.IntegrityError:
        flash("Error: El nombre de usuario ya existe.")
    except Exception as e:
        flash(f"Error al actualizar usuario: {str(e)}")
    
    return redirect("/gestion_usuarios_admin")

@app.route("/cambiar_pin_admin", methods=["POST"])
def cambiar_pin_admin():
    if session.get("rol") != "admin" or session.get("usuario") != "alfredo":
        flash("Acceso denegado.")
        return redirect("/admin")
    
    user_id = request.form["id"]
    usuario = request.form["usuario"]
    nuevo_pin = request.form["nuevo_pin"]
    confirmar_pin = request.form["confirmar_pin"]
    
    if nuevo_pin != confirmar_pin:
        flash("Los PINs no coinciden.")
        return redirect("/gestion_usuarios_admin")
    
    if not (nuevo_pin.isdigit() and len(nuevo_pin) == 4):
        flash("El PIN debe ser numérico de 4 dígitos.")
        return redirect("/gestion_usuarios_admin")
    
    try:
        con = conectar()
        con.execute("""
            UPDATE usuarios 
            SET pin=?, nip_visible=? 
            WHERE id=? AND usuario != 'alfredo'
        """, (encriptar(nuevo_pin), nuevo_pin, user_id))
        con.commit()
        con.close()
        flash(f"PIN de {usuario} cambiado exitosamente.")
    except Exception as e:
        flash(f"Error al cambiar PIN: {str(e)}")
    
    return redirect("/gestion_usuarios_admin")

@app.route("/eliminar_usuario_admin/<int:user_id>")
def eliminar_usuario_admin(user_id):
    if session.get("rol") != "admin" or session.get("usuario") != "alfredo":
        flash("Acceso denegado.")
        return redirect("/admin")
    
    try:
        con = conectar()
        # Verificar que no sea el admin principal
        usuario_data = con.execute("SELECT usuario FROM usuarios WHERE id=?", (user_id,)).fetchone()
        if usuario_data and usuario_data[0] == "alfredo":
            flash("No se puede eliminar al administrador principal.")
            return redirect("/gestion_usuarios_admin")
        
        con.execute("DELETE FROM usuarios WHERE id=? AND usuario != 'alfredo'", (user_id,))
        con.commit()
        con.close()
        flash("Usuario eliminado exitosamente.")
    except Exception as e:
        flash(f"Error al eliminar usuario: {str(e)}")
    
    return redirect("/gestion_usuarios_admin")

@app.route("/generar_datos_prueba")
def generar_datos_prueba():
    if session.get("rol") != "admin":
        return redirect("/login")
    
    con = conectar()
    usuarios = con.execute("SELECT usuario FROM usuarios WHERE rol='miembro'").fetchall()
    
    if not usuarios:
        flash("No hay miembros para generar datos de prueba.")
        return redirect("/admin")
    
    # Generar asistencias aleatorias
    for i in range(30):
        fecha = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        usuarios_dia = random.sample(usuarios, random.randint(1, min(len(usuarios), 8)))
        
        for usuario_tuple in usuarios_dia:
            usuario = usuario_tuple[0]
            hora_entrada = random.choice(["06:00", "07:00", "08:00", "17:00", "18:00", "19:00"])
            hora_salida = f"{int(hora_entrada.split(':')[0]) + random.randint(1, 3):02d}:00"
            
            existe = con.execute("SELECT id FROM asistencias WHERE usuario=? AND fecha=?", (usuario, fecha)).fetchone()
            if not existe:
                con.execute("INSERT INTO asistencias (usuario, fecha, hora_entrada, hora_salida) VALUES (?, ?, ?, ?)",
                           (usuario, fecha, hora_entrada, hora_salida))
    
    con.commit()
    con.close()
    
    flash("Datos de prueba generados exitosamente.")
    return redirect("/admin")

@app.route("/gestion_planes_grupales")
def gestion_planes_grupales():
    if session.get("rol") not in ("admin", "moderador"):
        return redirect("/login")
    
    con = conectar()
    
    # Obtener logo
    logo_row = con.execute("SELECT filename FROM logo WHERE id=1").fetchone()
    logo_fn = logo_row[0] if logo_row else ""
    
    # Obtener todos los planes grupales con información del responsable
    planes_grupales = con.execute("""
        SELECT pg.id, pg.nombre_grupo, pg.descripcion, pg.max_miembros, pg.fecha_creacion, 
               pg.vigencia, pg.activo, u.nombre as responsable_nombre, u.usuario as responsable_usuario,
               COUNT(mg.id) as total_miembros
        FROM planes_grupales pg
        LEFT JOIN usuarios u ON pg.responsable_id = u.id
        LEFT JOIN miembros_grupo mg ON pg.id = mg.plan_grupal_id AND mg.activo = 1
        WHERE pg.activo = 1
        GROUP BY pg.id, pg.nombre_grupo, pg.descripcion, pg.max_miembros, pg.fecha_creacion, 
                 pg.vigencia, pg.activo, u.nombre, u.usuario
        ORDER BY pg.fecha_creacion DESC
    """).fetchall()
    
    # Obtener miembros disponibles (que no estén en plan familiar o grupal)
    miembros_disponibles = con.execute("""
        SELECT id, nombre, usuario, modalidad
        FROM usuarios 
        WHERE rol = 'miembro' 
        AND modalidad NOT IN ('plan_familiar', 'plan_grupal')
        ORDER BY nombre
    """).fetchall()
    
    con.close()
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Gestión de Planes Grupales - LAMA Control</title>
  {{ BASE_STYLES|safe }}
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>{{ 'ADMIN' if session['rol']=='admin' else 'MODERADOR' }} PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="{{ '/admin' if session['rol']=='admin' else '/moderador' }}"><i>🏠</i> Panel Principal</a></li>
        <li><a href="/gestion_planes_grupales" class="active"><i>👥</i> Gestión Planes Grupales</a></li>
        <li><a href="/gestionar_familias"><i>👪</i> Gestión Plan Familiar</a></li>
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header">
        <h1>👥 Gestión de Planes Grupales</h1>
        <div class="breadcrumb">Panel {{ 'Admin' if session['rol']=='admin' else 'Moderador' }} > Gestión de Planes Grupales</div>
      </div>

      <div class="content-body">
        <!-- Estadísticas rápidas -->
        <div class="stats-grid" style="margin-bottom: 30px;">
          <div class="stat-card" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);">
            <div class="stat-number">{{ planes_grupales|length }}</div>
            <div class="stat-label">Planes Activos</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);">
            <div class="stat-number">{{ planes_grupales|sum(attribute=9) }}</div>
            <div class="stat-label">Miembros en Grupos</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);">
            <div class="stat-number">{{ miembros_disponibles|length }}</div>
            <div class="stat-label">Miembros Disponibles</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);">
            <div class="stat-number">{{ (planes_grupales|sum(attribute=3) - planes_grupales|sum(attribute=9)) if planes_grupales else 0 }}</div>
            <div class="stat-label">Espacios Disponibles</div>
          </div>
        </div>

        <!-- Crear nuevo plan grupal -->
        <div class="card" style="margin-bottom: 30px;">
          <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); border-radius: 15px 15px 0 0; padding: 25px; color: white;">
            <div style="display: flex; align-items: center;">
              <div style="background: rgba(255,255,255,0.2); border-radius: 50%; padding: 15px; margin-right: 15px;">
                <span style="font-size: 2em;">🚀</span>
              </div>
              <div>
                <h3 style="margin: 0; font-size: 1.4em;">Crear Nuevo Plan Grupal</h3>
                <p style="margin: 5px 0 0 0; font-size: 0.95em; opacity: 0.9;">
                  Configura un nuevo grupo y asigna miembros disponibles
                </p>
              </div>
            </div>
          </div>
          
          <div style="background: rgba(255,255,255,0.95); padding: 30px;">
            <form method="POST" action="/crear_plan_grupal_admin">
              <!-- Información básica del grupo -->
              <div style="background: #f8fcff; border-radius: 10px; padding: 20px; margin-bottom: 25px; border-left: 4px solid #3498db;">
                <h4 style="color: #3498db; margin: 0 0 15px 0; display: flex; align-items: center;">
                  <span style="margin-right: 10px;">⚙️</span>
                  Información del Grupo
                </h4>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                  <div class="form-group" style="margin: 0;">
                    <label class="form-label">Nombre del Grupo</label>
                    <input type="text" name="nombre_grupo" required placeholder="Ej: Crossfit Elite, Yoga Matutino, Entrenamiento Funcional" style="border-color: #3498db;">
                  </div>
                  <div class="form-group" style="margin: 0;">
                    <label class="form-label">Máximo de Miembros</label>
                    <select name="max_miembros" required style="border-color: #3498db;">
                      <option value="5">5 miembros</option>
                      <option value="10" selected>10 miembros (Recomendado)</option>
                      <option value="15">15 miembros</option>
                      <option value="20">20 miembros</option>
                      <option value="25">25 miembros</option>
                    </select>
                  </div>
                </div>
                
                <div class="form-group" style="margin: 0;">
                  <label class="form-label">Descripción del Grupo</label>
                  <textarea name="descripcion" rows="3" placeholder="Describe el tipo de entrenamiento, horarios, objetivos del grupo, etc." style="border-color: #3498db;"></textarea>
                </div>
              </div>

              <!-- Selección de miembros -->
              <div style="background: #f0fdf4; border-radius: 10px; padding: 20px; margin-bottom: 25px; border-left: 4px solid #27ae60;">
                <h4 style="color: #27ae60; margin: 0 0 15px 0; display: flex; align-items: center;">
                  <span style="margin-right: 10px;">👥</span>
                  Seleccionar Miembros del Grupo
                </h4>
                
                {% if miembros_disponibles %}
                <div style="background: white; border-radius: 8px; padding: 15px; border: 2px dashed #27ae60; max-height: 300px; overflow-y: auto;">
                  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 10px;">
                    {% for id, nombre, usuario, modalidad in miembros_disponibles %}
                    <div style="background: #f8f9fa; border-radius: 6px; padding: 12px; border: 1px solid #e1e8ed; transition: all 0.3s ease;" 
                         onmouseover="this.style.borderColor='#27ae60'; this.style.backgroundColor='#f0fdf4'" 
                         onmouseout="this.style.borderColor='#e1e8ed'; this.style.backgroundColor='#f8f9fa'">
                      <label style="display: flex; align-items: center; cursor: pointer; margin: 0;">
                        <input type="checkbox" name="miembros" value="{{ id }}" style="margin-right: 12px; width: 16px; height: 16px;">
                        <div>
                          <strong style="color: #2c3e50;">{{ nombre }}</strong>
                          <br>
                          <small style="color: #7f8c8d;">{{ usuario }} • {{ modalidad.title() }}</small>
                        </div>
                      </label>
                    </div>
                    {% endfor %}
                  </div>
                  
                  <div style="background: #e8f5e8; border-radius: 6px; padding: 12px; margin-top: 15px;">
                    <small style="color: #27ae60; font-weight: 600;">
                      💡 Tip: Selecciona miembros que tengan horarios y objetivos similares para un mejor rendimiento grupal.
                    </small>
                  </div>
                </div>
                {% else %}
                <div style="text-align: center; padding: 40px; color: #7f8c8d; background: white; border-radius: 8px; border: 2px dashed #27ae60;">
                  <div style="font-size: 3em; margin-bottom: 15px;">😕</div>
                  <h4 style="margin: 0 0 10px 0; color: #95a5a6;">No hay miembros disponibles</h4>
                  <p style="margin: 0; font-size: 0.9em;">
                    Todos los miembros están asignados a planes familiares o grupales existentes.
                  </p>
                </div>
                {% endif %}
              </div>

              <div style="text-align: center;">
                <button type="submit" class="btn" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); padding: 15px 30px; font-size: 1.1em; font-weight: 600;">
                  🚀 Crear Plan Grupal
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Lista de planes grupales existentes -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">📋 Planes Grupales Activos ({{ planes_grupales|length }})</h3>
          </div>
          
          {% if planes_grupales %}
          <div style="padding: 0;">
            {% for plan in planes_grupales %}
            {% set espacios_disponibles = plan[3] - plan[9] %}
            {% set porcentaje_ocupacion = (plan[9] / plan[3] * 100) if plan[3] > 0 else 0 %}
            
            <div style="border-bottom: 1px solid #ecf0f1; padding: 25px; transition: background 0.3s ease;" 
                 onmouseover="this.style.backgroundColor='#f8f9fa'" 
                 onmouseout="this.style.backgroundColor='white'">
              
              <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                <div style="flex: 1;">
                  <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="background: #3498db; color: white; padding: 6px 10px; border-radius: 20px; font-size: 0.8em; margin-right: 12px;">🏆</span>
                    <h4 style="margin: 0; color: #2c3e50; font-size: 1.2em;">{{ plan[1] }}</h4>
                    <span style="background: {{ '#27ae60' if espacios_disponibles > 3 else '#f39c12' if espacios_disponibles > 0 else '#e74c3c' }}; 
                                color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; margin-left: 15px;">
                      {{ espacios_disponibles }} {{ 'espacio' if espacios_disponibles == 1 else 'espacios' }}
                    </span>
                  </div>
                  
                  {% if plan[2] %}
                  <p style="color: #7f8c8d; margin: 0 0 8px 35px; font-style: italic;">{{ plan[2] }}</p>
                  {% endif %}
                  
                  <div style="margin-left: 35px;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 10px;">
                      <div>
                        <small style="color: #7f8c8d;">👤 Responsable:</small>
                        <br>
                        <strong style="color: #2c3e50;">{{ plan[7] or 'Sin responsable' }}</strong>
                        {% if plan[8] %}
                        <small style="color: #95a5a6;">({{ plan[8] }})</small>
                        {% endif %}
                      </div>
                      
                      <div>
                        <small style="color: #7f8c8d;">📅 Creado:</small>
                        <br>
                        <strong style="color: #2c3e50;">{{ plan[4] }}</strong>
                      </div>
                      
                      <div>
                        <small style="color: #7f8c8d;">⏰ Vigencia:</small>
                        <br>
                        <strong style="color: #2c3e50;">{{ plan[5] }}</strong>
                      </div>
                    </div>
                    
                    <!-- Barra de progreso de ocupación -->
                    <div style="margin: 15px 0;">
                      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                        <small style="color: #7f8c8d;">👥 Ocupación del grupo:</small>
                        <small style="color: #2c3e50; font-weight: 600;">{{ plan[9] }}/{{ plan[3] }} miembros ({{ "%.0f"|format(porcentaje_ocupacion) }}%)</small>
                      </div>
                      <div style="background: #ecf0f1; height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: {{ '#27ae60' if porcentaje_ocupacion < 70 else '#f39c12' if porcentaje_ocupacion < 90 else '#e74c3c' }}; 
                                    height: 100%; width: {{ porcentaje_ocupacion }}%; transition: width 0.5s ease;"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Acciones -->
              <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-left: 35px;">
                <button onclick="verPlanGrupal({{ plan[0] }})" class="btn" style="background: #3498db; padding: 8px 15px; font-size: 0.9em;">
                  👁️ Ver Detalles
                </button>
                <button onclick="editarPlanGrupal({{ plan[0] }})" class="btn" style="background: #f39c12; padding: 8px 15px; font-size: 0.9em;">
                  ✏️ Editar
                </button>
                <button onclick="eliminarPlanGrupal({{ plan[0] }}, '{{ plan[1] }}')" class="btn" style="background: #e74c3c; padding: 8px 15px; font-size: 0.9em;">
                  🗑️ Eliminar
                </button>
              </div>
            </div>
            {% endfor %}
          </div>
          {% else %}
          <div style="text-align: center; padding: 60px; color: #7f8c8d;">
            <div style="font-size: 4em; margin-bottom: 20px;">👥</div>
            <h3 style="margin: 0 0 10px 0; color: #95a5a6;">No hay planes grupales creados</h3>
            <p style="margin: 0; font-size: 1.1em;">
              ¡Crea el primer plan grupal usando el formulario de arriba!
            </p>
            <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px auto; max-width: 500px; text-align: left;">
              <strong style="color: #6c757d;">💡 Ideas para planes grupales:</strong>
              <ul style="margin: 10px 0 0 20px; color: #6c757d;">
                <li>Equipos deportivos (fútbol, basketball, voleibol)</li>
                <li>Grupos de entrenamiento funcional</li>
                <li>Clases de yoga, pilates o zumba</li>
                <li>Entrenamientos corporativos</li>
                <li>Grupos de entrenamiento personal</li>
              </ul>
            </div>
          </div>
          {% endif %}
        </div>
      </div>
    </div>
  </div>

  <!-- Modal para ver detalles del plan -->
  <div id="planModal" class="modal">
    <div class="modal-content" style="max-width: 800px;">
      <div id="planModalContent">
        <!-- El contenido se cargará dinámicamente -->
      </div>
    </div>
  </div>

  <script>
    // Función para ver detalles del plan grupal
    function verPlanGrupal(planId) {
      fetch(`/api/plan_grupal/${planId}`)
        .then(response => response.json())
        .then(data => {
          document.getElementById('planModalContent').innerHTML = generarContenidoPlan(data);
          document.getElementById('planModal').style.display = 'block';
        })
        .catch(error => {
          console.error('Error:', error);
          alert('Error al cargar los detalles del plan');
        });
    }

    // Función para editar plan grupal
    function editarPlanGrupal(planId) {
      window.location.href = `/editar_plan_grupal/${planId}`;
    }

    // Función para eliminar plan grupal
    function eliminarPlanGrupal(planId, nombrePlan) {
      if (confirm(`¿ELIMINAR PERMANENTEMENTE el plan grupal "${nombrePlan}"?\\n\\nEsta acción no se puede deshacer y todos los miembros volverán a modalidad individual.`)) {
        window.location.href = `/eliminar_plan_grupal/${planId}`;
      }
    }

    // Función para generar contenido del modal
    function generarContenidoPlan(data) {
      return `
        <div style="border-bottom: 2px solid #3498db; padding-bottom: 20px; margin-bottom: 25px;">
          <h2 style="margin: 0; color: #2c3e50; display: flex; align-items: center;">
            <span style="background: #3498db; color: white; padding: 8px 12px; border-radius: 50%; margin-right: 15px;">👥</span>
            ${data.nombre_grupo}
          </h2>
          <p style="margin: 10px 0 0 50px; color: #7f8c8d; font-style: italic;">
            ${data.descripcion || 'Sin descripción'}
          </p>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
          <div>
            <h4 style="color: #3498db; margin: 0 0 10px 0;">📊 Información General</h4>
            <p><strong>Máximo de miembros:</strong> ${data.max_miembros}</p>
            <p><strong>Miembros actuales:</strong> ${data.total_miembros}</p>
            <p><strong>Espacios disponibles:</strong> ${data.max_miembros - data.total_miembros}</p>
            <p><strong>Fecha de creación:</strong> ${data.fecha_creacion}</p>
            <p><strong>Vigencia:</strong> ${data.vigencia}</p>
          </div>
          <div>
            <h4 style="color: #27ae60; margin: 0 0 10px 0;">👤 Responsable</h4>
            <p><strong>Nombre:</strong> ${data.responsable_nombre || 'Sin responsable'}</p>
            <p><strong>Usuario:</strong> ${data.responsable_usuario || 'N/A'}</p>
          </div>
        </div>
        
        <div style="margin-bottom: 25px;">
          <h4 style="color: #e67e22; margin: 0 0 15px 0;">👥 Lista de Miembros</h4>
          ${data.miembros && data.miembros.length > 0 ? 
            data.miembros.map(miembro => `
              <div style="background: #f8f9fa; padding: 10px; border-radius: 6px; margin: 5px 0; border-left: 4px solid #3498db;">
                <strong>${miembro.nombre}</strong> (${miembro.usuario})
                <br><small style="color: #7f8c8d;">Modalidad: ${miembro.modalidad} • Vigencia: ${miembro.vigencia}</small>
              </div>
            `).join('') : 
            '<p style="color: #7f8c8d; font-style: italic;">No hay miembros en este grupo.</p>'
          }
        </div>
        
        <div style="text-align: center; padding-top: 20px; border-top: 2px solid #ecf0f1;">
          <button onclick="editarPlanGrupal(${data.id})" class="btn" style="background: #f39c12; margin-right: 10px;">
            ✏️ Editar Plan
          </button>
          <button onclick="document.getElementById('planModal').style.display='none'" class="btn" style="background: #95a5a6;">
            ❌ Cerrar
          </button>
        </div>
      `;
    }

    // Cerrar modal al hacer clic fuera
    window.onclick = function(event) {
      const modal = document.getElementById('planModal');
      if (event.target === modal) {
        modal.style.display = 'none';
      }
    }

    // Función para seleccionar/deseleccionar todos los miembros
    function toggleTodosLosMiembros() {
      const checkboxes = document.querySelectorAll('input[name="miembros"]');
      const todosMarcados = Array.from(checkboxes).every(cb => cb.checked);
      
      checkboxes.forEach(cb => {
        cb.checked = !todosMarcados;
      });
    }

    // Agregar botón para seleccionar todos
    document.addEventListener('DOMContentLoaded', function() {
      const contenedorMiembros = document.querySelector('div[style*="max-height: 300px"]');
      if (contenedorMiembros && document.querySelectorAll('input[name="miembros"]').length > 0) {
        const botonToggle = document.createElement('div');
        botonToggle.style.cssText = 'text-align: center; margin-bottom: 15px; padding-bottom: 15px; border-bottom: 2px solid #27ae60;';
        botonToggle.innerHTML = `
          <button type="button" onclick="toggleTodosLosMiembros()" 
                  style="background: #27ae60; color: white; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; font-size: 0.9em;">
            👥 Seleccionar/Deseleccionar Todos
          </button>
        `;
        contenedorMiembros.insertBefore(botonToggle, contenedorMiembros.firstChild);
      }
    });
  </script>
</body>
</html>
""", planes_grupales=planes_grupales, miembros_disponibles=miembros_disponibles, 
     logo_fn=logo_fn, BASE_STYLES=BASE_STYLES)

@app.route("/crear_plan_grupal_admin", methods=["POST"])
def crear_plan_grupal_admin():
    if session.get("rol") not in ("admin", "moderador"):
        flash("Acceso denegado.")
        return redirect("/login")
    
    nombre_grupo = request.form.get("nombre_grupo", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    max_miembros = request.form.get("max_miembros", "10")
    miembros_ids = request.form.getlist("miembros")
    
    print(f"DEBUG crear_plan_grupal_admin: Iniciando creación de plan grupal")
    print(f"  Nombre: '{nombre_grupo}'")
    print(f"  Descripción: '{descripcion}'")
    print(f"  Max miembros: '{max_miembros}'")
    print(f"  Miembros IDs: {miembros_ids}")
    print(f"  Usuario: {session.get('usuario', 'unknown')}")
    
    # Validaciones de entrada
    if not nombre_grupo:
        flash("Error: El nombre del grupo es obligatorio.")
        print(f"DEBUG crear_plan_grupal_admin: ERROR - Nombre del grupo vacío")
        return redirect("/gestion_planes_grupales")
    
    if not miembros_ids:
        flash("Error: Debes seleccionar al menos un miembro para el grupo.")
        print(f"DEBUG crear_plan_grupal_admin: ERROR - No se seleccionaron miembros")
        return redirect("/gestion_planes_grupales")
    
    try:
        max_miembros_int = int(max_miembros)
        print(f"DEBUG crear_plan_grupal_admin: Max miembros convertido: {max_miembros_int}")
    except (ValueError, TypeError):
        max_miembros_int = 10
        print(f"DEBUG crear_plan_grupal_admin: Max miembros por defecto: {max_miembros_int}")
    
    if len(miembros_ids) > max_miembros_int:
        flash(f"Error: No puedes agregar más de {max_miembros_int} miembros al grupo.")
        print(f"DEBUG crear_plan_grupal_admin: ERROR - Demasiados miembros: {len(miembros_ids)} > {max_miembros_int}")
        return redirect("/gestion_planes_grupales")
    
    # Validar que todos los miembros existen y están disponibles
    con = conectar()
    try:
        miembros_validados = []
        for miembro_id in miembros_ids:
            print(f"DEBUG crear_plan_grupal_admin: Validando miembro ID: {miembro_id}")
            miembro = con.execute("SELECT id, nombre, modalidad FROM usuarios WHERE id=? AND rol='miembro'", (miembro_id,)).fetchone()
            if not miembro:
                flash(f"Error: Miembro con ID {miembro_id} no encontrado.")
                print(f"DEBUG crear_plan_grupal_admin: ERROR - Miembro {miembro_id} no encontrado")
                con.close()
                return redirect("/gestion_planes_grupales")
            if miembro[2] in ['plan_familiar', 'plan_grupal']:
                flash(f"Error: El miembro {miembro[1]} ya está en un plan ({miembro[2]}).")
                print(f"DEBUG crear_plan_grupal_admin: ERROR - Miembro {miembro[1]} ya en plan {miembro[2]}")
                con.close()
                return redirect("/gestion_planes_grupales")
            miembros_validados.append(miembro)
            print(f"DEBUG crear_plan_grupal_admin: Miembro validado: {miembro[1]}")
        
        con.close()
        print(f"DEBUG crear_plan_grupal_admin: Todos los miembros validados correctamente")
        
        # Crear el plan grupal
        print(f"DEBUG crear_plan_grupal_admin: Llamando a crear_plan_grupal...")
        responsable_id = miembros_ids[0]  # Usar el primer miembro como responsable
        plan_id = crear_plan_grupal(nombre_grupo, miembros_ids, responsable_id, descripcion, max_miembros_int)
        
        print(f"DEBUG crear_plan_grupal_admin: Plan creado con ID: {plan_id}")
        flash(f"¡Éxito! Plan grupal '{nombre_grupo}' creado exitosamente con {len(miembros_ids)} miembros.")
        
        # Verificar que el plan se creó correctamente
        con = conectar()
        verificacion = con.execute("SELECT COUNT(*) FROM planes_grupales WHERE id=?", (plan_id,)).fetchone()
        miembros_vinculados = con.execute("SELECT COUNT(*) FROM miembros_grupo WHERE plan_grupal_id=? AND activo=1", (plan_id,)).fetchone()
        con.close()
        
        print(f"DEBUG crear_plan_grupal_admin: Verificación - Plan existe: {verificacion[0]}, Miembros vinculados: {miembros_vinculados[0]}")
        
        if verificacion[0] == 0:
            flash("Advertencia: Hubo problemas con la creación del plan. Verifique en la lista.")
            print(f"DEBUG crear_plan_grupal_admin: ADVERTENCIA - Plan no encontrado en verificación")
        elif miembros_vinculados[0] != len(miembros_ids):
            flash(f"Advertencia: El plan se creó pero algunos miembros pueden no haberse vinculado correctamente. Esperados: {len(miembros_ids)}, Vinculados: {miembros_vinculados[0]}")
            print(f"DEBUG crear_plan_grupal_admin: ADVERTENCIA - Miembros vinculados incorrectamente: {miembros_vinculados[0]} != {len(miembros_ids)}")
        
    except Exception as e:
        print(f"DEBUG crear_plan_grupal_admin: EXCEPTION - {str(e)}")
        import traceback
        traceback.print_exc()
        try:
            con.close()
        except:
            pass
        flash(f"Error interno al crear plan grupal: {str(e)}")
    
    print(f"DEBUG crear_plan_grupal_admin: Redirigiendo a /gestion_planes_grupales")
    return redirect("/gestion_planes_grupales")

@app.route("/ver_plan_grupal/<int:plan_id>")
def ver_plan_grupal(plan_id):
    if session.get("rol") not in ("admin", "moderador"):
        return redirect("/login")
    
    con = conectar()
    
    # Obtener información del plan
    plan = con.execute("""
        SELECT pg.id, pg.nombre_grupo, pg.descripcion, pg.max_miembros, pg.fecha_creacion, 
               pg.vigencia, u.nombre as responsable_nombre, u.usuario as responsable_usuario
        FROM planes_grupales pg
        LEFT JOIN usuarios u ON pg.responsable_id = u.id
        WHERE pg.id = ? AND pg.activo = 1
    """, (plan_id,)).fetchone()
    
    if not plan:
        flash("Plan grupal no encontrado.")
        return redirect("/gestion_planes_grupales")
    
    # Obtener miembros del plan
    miembros = con.execute("""
        SELECT u.id, u.nombre, u.usuario, u.modalidad, u.vigencia, mg.fecha_vinculacion
        FROM miembros_grupo mg
        JOIN usuarios u ON mg.miembro_id = u.id
        WHERE mg.plan_grupal_id = ? AND mg.activo = 1
        ORDER BY u.nombre
    """, (plan_id,)).fetchall()
    
    con.close()
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Ver Plan Grupal</title>
  {{ BASE_STYLES|safe }}
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>LAMA Control</h3>
        <p>Plan Grupal</p>
      </div>
      <ul class="sidebar-nav">
        <li><a href="/admin"><i>🏠</i> Panel Principal</a></li>
        <li><a href="/gestion_planes_grupales"><i>👥</i> Planes Grupales</a></li>
        <li><a href="/ver_plan_grupal/{{ plan[0] }}" class="active"><i>👁️</i> Ver Plan</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header">
        <h1>👥 {{ plan[1] }}</h1>
        <div class="breadcrumb">Plan Grupal - {{ miembros|length }} miembros activos</div>
      </div>

      <div class="content-body">
        <!-- Información del plan -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">📋 Información del Plan</h3>
          </div>
          <div style="padding: 25px;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
              <div>
                <p><strong>Nombre del Grupo:</strong> {{ plan[1] }}</p>
                <p><strong>Descripción:</strong> {{ plan[2] or 'Sin descripción' }}</p>
                <p><strong>Fecha de Creación:</strong> {{ plan[4] }}</p>
              </div>
              <div>
                <p><strong>Responsable:</strong> {{ plan[6] or 'Sin responsable' }} ({{ plan[7] or '' }})</p>
                <p><strong>Máximo de Miembros:</strong> {{ plan[3] }}</p>
                <p><strong>Vigencia:</strong> {{ plan[5] }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Lista de miembros -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">👥 Miembros del Grupo ({{ miembros|length }}/{{ plan[3] }})</h3>
          </div>
          <div style="padding: 25px;">
            {% if miembros %}
            <table>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Usuario</th>
                  <th>Modalidad</th>
                  <th>Vigencia</th>
                  <th>Fecha Ingreso</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {% for miembro in miembros %}
                <tr>
                  <td><strong>{{ miembro[1] }}</strong></td>
                  <td>{{ miembro[2] }}</td>
                  <td>{{ miembro[3].title() }}</td>
                  <td>{{ miembro[4] }}</td>
                  <td>{{ miembro[5] }}</td>
                  <td>
                    {% set dias_rest = (miembro[4]|strptime('%Y-%m-%d') - moment().date()).days %}
                    {% if dias_rest >= 0 %}
                    <span style="color: #27ae60; font-weight: bold;">✅ Activo</span>
                    {% else %}
                    <span style="color: #e74c3c; font-weight: bold;">⚠️ Vencido</span>
                    {% endif %}
                  </td>
                </tr>
                {% endfor %}
              </tbody>
            </table>
            {% else %}
            <p style="text-align: center; color: #7f8c8d; font-style: italic;">No hay miembros en este grupo.</p>
            {% endif %}
          </div>
        </div>

        <!-- Acciones -->
        <div class="card">
          <div style="padding: 25px; text-align: center;">
            <a href="/editar_plan_grupal/{{ plan[0] }}" class="btn btn-warning">✏️ Editar Plan</a>
            <a href="/gestion_planes_grupales" class="btn btn-secondary">↩️ Volver a Gestión</a>
            <a href="/eliminar_plan_grupal/{{ plan[0] }}" class="btn btn-danger" 
               onclick="return confirm('¿Eliminar este plan grupal?\\n\\nEsta acción moverá a todos los miembros a modalidad individual.')">🗑️ Eliminar Plan</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
""", plan=plan, miembros=miembros, BASE_STYLES=BASE_STYLES)

@app.route("/api/plan_grupal/<int:plan_id>")
def api_plan_grupal(plan_id):
    if session.get("rol") not in ("admin", "moderador"):
        return jsonify({"error": "No autorizado"}), 403
    
    con = conectar()
    
    # Obtener información del plan
    plan = con.execute("""
        SELECT pg.id, pg.nombre_grupo, pg.descripcion, pg.max_miembros, pg.fecha_creacion, 
               pg.vigencia, u.nombre as responsable_nombre, u.usuario as responsable_usuario,
               COUNT(mg.id) as total_miembros
        FROM planes_grupales pg
        LEFT JOIN usuarios u ON pg.responsable_id = u.id
        LEFT JOIN miembros_grupo mg ON pg.id = mg.plan_grupal_id AND mg.activo = 1
        WHERE pg.id = ? AND pg.activo = 1
        GROUP BY pg.id, pg.nombre_grupo, pg.descripcion, pg.max_miembros, pg.fecha_creacion, 
                 pg.vigencia, u.nombre, u.usuario
    """, (plan_id,)).fetchone()
    
    if not plan:
        con.close()
        return jsonify({"error": "Plan no encontrado"}), 404
    
    # Obtener miembros del plan
    miembros = con.execute("""
        SELECT u.id, u.nombre, u.usuario, u.modalidad, u.vigencia, mg.fecha_vinculacion
        FROM miembros_grupo mg
        JOIN usuarios u ON mg.miembro_id = u.id
        WHERE mg.plan_grupal_id = ? AND mg.activo = 1
        ORDER BY u.nombre
    """, (plan_id,)).fetchall()
    
    con.close()
    
    # Estructurar los datos para JSON
    plan_data = {
        "id": plan[0],
        "nombre_grupo": plan[1],
        "descripcion": plan[2],
        "max_miembros": plan[3],
        "fecha_creacion": plan[4],
        "vigencia": plan[5],
        "responsable_nombre": plan[6],
        "responsable_usuario": plan[7],
        "total_miembros": plan[8],
        "miembros": [
            {
                "id": miembro[0],
                "nombre": miembro[1],
                "usuario": miembro[2],
                "modalidad": miembro[3],
                "vigencia": miembro[4],
                "fecha_vinculacion": miembro[5]
            }
            for miembro in miembros
        ]
    }
    
    return jsonify(plan_data)

@app.route("/eliminar_plan_grupal/<int:plan_id>")
def eliminar_plan_grupal(plan_id):
    if session.get("rol") not in ("admin", "moderador"):
        return redirect("/login")
    
    try:
        con = conectar()
        
        # Obtener miembros del plan antes de eliminarlo
        miembros = con.execute("""
            SELECT miembro_id FROM miembros_grupo 
            WHERE plan_grupal_id = ? AND activo = 1
        """, (plan_id,)).fetchall()
        
        # Cambiar modalidad de todos los miembros a 'mensual' con vigencia desde hoy
        fecha_conversion = datetime.now().strftime("%Y-%m-%d")
        for miembro in miembros:
            miembro_id = miembro[0]
            nueva_vigencia = calcular_vigencia("mensual", fecha_conversion)
            con.execute("""
                UPDATE usuarios 
                SET modalidad = 'mensual', vigencia = ?
                WHERE id = ?
            """, (nueva_vigencia, miembro_id))
        
        # Desactivar vinculaciones de miembros
        con.execute("""
            UPDATE miembros_grupo 
            SET activo = 0 
            WHERE plan_grupal_id = ?
        """, (plan_id,))
        
        # Desactivar el plan grupal
        con.execute("""
            UPDATE planes_grupales 
            SET activo = 0 
            WHERE id = ?
        """, (plan_id,))
        
        con.commit()
        con.close()
        
        flash(f"Plan grupal eliminado exitosamente. {len(miembros)} miembros cambiados a modalidad mensual.")
        
    except Exception as e:
        flash(f"Error al eliminar plan grupal: {str(e)}")
    
    return redirect("/gestion_planes_grupales")

# ——— Panel de Administrador ———
@app.route("/admin")
def admin():
    if session.get("rol") != "admin":
        return redirect("/login")
    
    con = conectar()
    logo_row = con.execute("SELECT filename FROM logo WHERE id=1").fetchone()
    logo_fn = logo_row[0] if logo_row else ""
    
    miembros_s = con.execute("""
        SELECT id, nombre, usuario, pin, nip_visible, modalidad, vigencia, foto
        FROM usuarios WHERE rol='miembro'
        ORDER BY id ASC
    """).fetchall()
    
    pagos = con.execute("SELECT usuario, monto, fecha, concepto FROM pagos ORDER BY fecha DESC LIMIT 20").fetchall()
    
    # Estadísticas básicas
    total_miembros = len(miembros_s)
    miembros_activos = len([m for m in miembros_s if dias_restantes(m[6]) >= 0])
    miembros_vencidos = total_miembros - miembros_activos
    
    # Ingresos del día
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    ingresos_hoy = con.execute("SELECT SUM(monto) FROM pagos WHERE fecha=?", (fecha_hoy,)).fetchone()[0] or 0
    
    con.close()

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Panel Admin - LAMA Control</title>
  {{ BASE_STYLES|safe }}
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>ADMIN PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="/admin" class="active"><i>🏠</i> Panel Principal</a></li>
        <li><a href="/reportes_financieros"><i>📊</i> Reportes Financieros</a></li>
        <li><a href="/estadisticas_globales"><i>📈</i> Estadísticas Globales</a></li>
        <li><a href="/analiticas_avanzadas"><i>🔍</i> Analíticas Avanzadas</a></li>
        <li><a href="/gestion_planes_grupales"><i>👥</i> Gestión Planes Grupales</a></li>
        <li><a href="/gestionar_familias"><i>👪</i> Gestión Plan Familiar</a></li>
        <li><a href="/gestion_backups"><i>💾</i> Gestión de Backups</a></li>
        <li><a href="/gestion_usuarios_admin"><i>👑</i> Gestión Admins/Moderadores</a></li>
        <li><a href="/corte_caja"><i>💰</i> Corte de Caja</a></li>
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header">
        <h1>🏋️ Panel de Administrador</h1>
        <div class="breadcrumb">Sistema LAMA Control - Bienvenido {{ session.nombre }}</div>
      </div>

      <div class="content-body">
        <!-- Estadísticas principales -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-number">{{ total_miembros }}</div>
            <div class="stat-label">Total Miembros</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);">
            <div class="stat-number">{{ miembros_activos }}</div>
            <div class="stat-label">Miembros Activos</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">
            <div class="stat-number">{{ miembros_vencidos }}</div>
            <div class="stat-label">Miembros Vencidos</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);">
            <div class="stat-number">${{ "%.2f"|format(ingresos_hoy) }}</div>
            <div class="stat-label">Ingresos Hoy</div>
          </div>
        </div>

        <!-- Acciones Rápidas -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">🚀 Acciones Rápidas</h3>
          </div>
          <div class="quick-actions">
            <a href="/reportes_financieros" class="quick-action">
              <i>📊</i>
              <strong>Reportes Financieros</strong>
              <small>Análisis de ingresos y ganancias</small>
            </a>
            <a href="/estadisticas_globales" class="quick-action">
              <i>📈</i>
              <strong>Estadísticas Globales</strong>
              <small>Métricas generales del gimnasio</small>
            </a>
            <a href="/analiticas_avanzadas" class="quick-action">
              <i>🔍</i>
              <strong>Analíticas Avanzadas</strong>
              <small>Análisis detallado de datos</small>
            </a>
            <a href="/gestion_backups" class="quick-action">
              <i>💾</i>
              <strong>Gestión de Backups</strong>
              <small>Respaldos del sistema</small>
            </a>
            <a href="/gestion_usuarios_admin" class="quick-action">
              <i>👑</i>
              <strong>Gestión Admins/Moderadores</strong>
              <small>Administrar usuarios del sistema</small>
            </a>
            <a href="/corte_caja" class="quick-action">
              <i>💰</i>
              <strong>Corte de Caja</strong>
              <small>Reporte de ingresos del día</small>
            </a>
            <a href="/descargar_reporte" class="quick-action">
              <i>📋</i>
              <strong>Descargar Reporte</strong>
              <small>Exportar datos de miembros</small>
            </a>
            <a href="/generar_datos_prueba" class="quick-action">
              <i>🎲</i>
              <strong>Generar Datos Prueba</strong>
              <small>Datos de ejemplo para testing</small>
            </a>
          </div>
        </div>

        <!-- Formularios de gestión -->
        <div class="card" style="margin-bottom: 30px;">
          <div class="card-header">
            <h3 class="card-title">📝 Formularios de Gestión</h3>
          </div>
          <div style="padding: 30px;">
            <!-- Crear Miembro -->
            <div style="margin-bottom: 40px; border-bottom: 2px solid #ecf0f1; padding-bottom: 30px;">
              <h4 style="color: #2c3e50; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                <span style="background: #3498db; color: white; padding: 8px 12px; border-radius: 50%; font-size: 18px;">👥</span>
                Crear Nuevo Miembro
              </h4>
              <form method="POST" action="/crear_miembro" enctype="multipart/form-data">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                  <div class="form-group">
                    <label class="form-label">Nombre completo</label>
                    <input type="text" name="nombre" required>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Nombre de usuario</label>
                    <input type="text" name="usuario" required>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Modalidad</label>
                    <select name="modalidad" id="modalidad-admin-main" required>
                      <option value="">Seleccionar modalidad</option>
                      <option value="semanal">Semanal</option>
                      <option value="mensual">Mensual</option>
                      <option value="trimestre">Trimestre</option>
                      <option value="semestre">Semestre</option>
                      <option value="anualidad">Anualidad</option>
                      <option value="plan_familiar">Plan Familiar</option>
                      <option value="plan_grupal">Plan Grupal</option>
                    </select>
                  </div>
                  
                  <!-- Contenedor para selección de familia ADMIN MAIN -->
                  <div id="family-selection-container-admin-main" style="display: none; grid-column: 1 / -1;">
                    <div style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); border-radius: 15px; padding: 25px; margin: 20px 0; box-shadow: 0 8px 25px rgba(39, 174, 96, 0.2);">
                      <div style="display: flex; align-items: center; margin-bottom: 20px;">
                        <div style="background: rgba(255,255,255,0.2); border-radius: 50%; padding: 15px; margin-right: 15px;">
                          <span style="font-size: 2em;">👪</span>
                        </div>
                        <div>
                          <h3 style="color: white; margin: 0; font-size: 1.3em;">Plan Familiar Seleccionado</h3>
                          <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.95em;">
                            Configura los miembros que formarán parte de este plan familiar
                          </p>
                        </div>
                      </div>
                      
                      <div style="background: rgba(255,255,255,0.95); border-radius: 12px; padding: 20px;">
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                          <span style="background: #27ae60; color: white; padding: 8px 12px; border-radius: 8px; font-size: 0.9em; font-weight: 600; margin-right: 10px;">🔍</span>
                          <span style="color: #2c3e50; font-weight: 600;">Buscar Miembros de la Familia</span>
                        </div>
                        
                        <p style="font-size: 0.9em; color: #7f8c8d; margin-bottom: 15px; line-height: 1.4;">
                          💡 <strong>Búsqueda Inteligente:</strong> El sistema detectará automáticamente miembros con apellidos similares cuando ingreses el nombre completo.
                        </p>
                        
                        <div id="family-members-list-admin-main" style="border: 2px dashed #27ae60; border-radius: 10px; padding: 20px; background: linear-gradient(135deg, #f8fffe 0%, #f0fdf4 100%); min-height: 120px;">
                          <div style="text-align: center; color: #27ae60;">
                            <div style="font-size: 2.5em; margin-bottom: 10px;">👨‍👩‍👧‍👦</div>
                            <p style="margin: 0; font-weight: 600;">Familiares Detectados</p>
                            <p style="margin: 5px 0 0 0; font-size: 0.85em; color: #7f8c8d;">
                              Ingresa el nombre completo arriba para encontrar familiares automáticamente
                            </p>
                          </div>
                        </div>
                        
                        <div style="background: #e8f5e8; border-radius: 8px; padding: 15px; margin-top: 15px; border-left: 4px solid #27ae60;">
                          <div style="display: flex; align-items: center;">
                            <span style="font-size: 1.2em; margin-right: 8px;">ℹ️</span>
                            <div>
                              <strong style="color: #27ae60;">Información Importante:</strong>
                              <ul style="margin: 5px 0 0 0; padding-left: 20px; color: #2c3e50; font-size: 0.9em;">
                                <li>Todos los miembros familiares compartirán la misma fecha de vigencia</li>
                                <li>El pago se realiza una sola vez para toda la familia</li>
                                <li>Puedes agregar hasta 6 miembros por plan familiar</li>
                              </ul>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Contenedor para selección de grupo ADMIN MAIN -->
                  <div id="group-selection-container-admin-main" style="display: none; grid-column: 1 / -1;">
                    <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); border-radius: 15px; padding: 25px; margin: 20px 0; box-shadow: 0 8px 25px rgba(52, 152, 219, 0.2);">
                      <div style="display: flex; align-items: center; margin-bottom: 20px;">
                        <div style="background: rgba(255,255,255,0.2); border-radius: 50%; padding: 15px; margin-right: 15px;">
                          <span style="font-size: 2em;">👥</span>
                        </div>
                        <div>
                          <h3 style="color: white; margin: 0; font-size: 1.3em;">Plan Grupal Seleccionado</h3>
                          <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.95em;">
                            Selecciona un plan grupal existente o crea uno nuevo
                          </p>
                        </div>
                      </div>
                      
                      <div style="background: rgba(255,255,255,0.95); border-radius: 12px; padding: 20px;">
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                          <span style="background: #3498db; color: white; padding: 8px 12px; border-radius: 8px; font-size: 0.9em; font-weight: 600; margin-right: 10px;">🏆</span>
                          <span style="color: #2c3e50; font-weight: 600;">Planes Grupales Disponibles</span>
                        </div>
                        
                        <div id="group-plans-list-admin-main" style="border: 2px dashed #3498db; border-radius: 10px; padding: 20px; background: linear-gradient(135deg, #f8fcff 0%, #e3f2fd 100%); min-height: 120px;">
                          <div style="text-align: center; color: #3498db;">
                            <div style="font-size: 2.5em; margin-bottom: 10px;">🏋️‍♂️</div>
                            <p style="margin: 0; font-weight: 600;">Cargando Planes Grupales...</p>
                            <p style="margin: 5px 0 0 0; font-size: 0.85em; color: #7f8c8d;">
                              Buscando planes con espacios disponibles
                            </p>
                          </div>
                        </div>
                        
                        <div style="display: flex; gap: 10px; margin-top: 20px; flex-wrap: wrap;">
                          <a href="/gestion_planes_grupales" target="_blank" 
                             style="background: linear-gradient(135deg, #e67e22 0%, #d35400 100%); color: white; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.9em; box-shadow: 0 4px 15px rgba(230, 126, 34, 0.3); transition: transform 0.2s;">
                            ➕ Crear Nuevo Plan Grupal
                          </a>
                          <a href="/gestionar_grupos" target="_blank"
                             style="background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); color: white; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.9em; box-shadow: 0 4px 15px rgba(155, 89, 182, 0.3); transition: transform 0.2s;">
                            📋 Gestionar Grupos Existentes
                          </a>
                        </div>
                        
                        <div style="background: #e3f2fd; border-radius: 8px; padding: 15px; margin-top: 15px; border-left: 4px solid #3498db;">
                          <div style="display: flex; align-items: center;">
                            <span style="font-size: 1.2em; margin-right: 8px;">💡</span>
                            <div>
                              <strong style="color: #3498db;">Beneficios del Plan Grupal:</strong>
                              <ul style="margin: 5px 0 0 0; padding-left: 20px; color: #2c3e50; font-size: 0.9em;">
                                <li>Descuentos por volumen para grupos grandes</li>
                                <li>Gestión centralizada de la vigencia del grupo</li>
                                <li>Ideal para equipos deportivos y entrenamientos grupales</li>
                              </ul>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Fecha de inicio de membresía (opcional)</label>
                    <input type="date" name="fecha_inicio" placeholder="Si no se especifica, inicia desde hoy">
                    <small style="color: #666; font-size: 0.85em; display: block; margin-top: 5px;">
                      💡 Si no especificas una fecha, la membresía iniciará desde hoy
                    </small>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Correo electrónico (opcional)</label>
                    <input type="email" name="correo">
                  </div>
                  <div class="form-group">
                    <label class="form-label">Teléfono de emergencia (opcional)</label>
                    <input type="text" name="telefono_emergencia">
                  </div>
                  <div class="form-group">
                    <label class="form-label">Datos médicos (opcional)</label>
                    <textarea name="datos_medicos" rows="3"></textarea>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Foto del miembro (opcional)</label>
                    <input type="file" name="foto" accept="image/*">
                  </div>
                </div>
                <div style="text-align: center; margin-top: 25px;">
                  <button type="submit" class="btn" style="padding: 12px 30px; font-size: 16px;">👥 Crear Miembro</button>
                </div>
              </form>
            </div>

            <!-- Crear Admin/Moderador -->
            <div style="margin-bottom: 40px; border-bottom: 2px solid #ecf0f1; padding-bottom: 30px;">
              <h4 style="color: #2c3e50; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                <span style="background: #9b59b6; color: white; padding: 8px 12px; border-radius: 50%; font-size: 18px;">👑</span>
                Crear Admin/Moderador
              </h4>
              <form method="POST" action="/crear_usuario">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                  <div class="form-group">
                    <label class="form-label">Nombre completo</label>
                    <input type="text" name="nombre" required>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Nombre de usuario</label>
                    <input type="text" name="usuario" required>
                  </div>
                  <div class="form-group">
                    <label class="form-label">PIN (4 dígitos)</label>
                    <input type="text" name="pin" pattern="[0-9]{4}" maxlength="4" required>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Rol</label>
                    <select name="rol" required>
                      <option value="">Seleccionar rol</option>
                      <option value="admin">Administrador</option>
                      <option value="moderador">Moderador</option>
                    </select>
                  </div>
                </div>
                <div style="text-align: center; margin-top: 25px;">
                  <button type="submit" class="btn" style="padding: 12px 30px; font-size: 16px; background: #9b59b6;">👑 Crear Usuario</button>
                </div>
              </form>
            </div>

            <!-- Registrar Pago -->
            <div style="margin-bottom: 20px;">
              <h4 style="color: #2c3e50; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                <span style="background: #27ae60; color: white; padding: 8px 12px; border-radius: 50%; font-size: 18px;">💰</span>
                Registrar Pago
              </h4>
              <form method="POST" action="/registrar_pago">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                  <div class="form-group">
                    <label class="form-label">Seleccionar miembro</label>
                    <select name="usuario" required>
                      <option value="">Seleccionar miembro...</option>
                      {% for id, nombre, usuario, pin, nip, modalidad, vigencia, foto in miembros_s %}
                      <option value="{{ usuario }}">{{ nombre }} ({{ usuario }})</option>
                      {% endfor %}
                    </select>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Monto del pago</label>
                    <input type="number" name="monto" id="montoInputAdmin1" step="0.01" min="0" placeholder="0.00" required>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Concepto del pago</label>
                    <select name="concepto" onchange="actualizarMontoAdmin(this.value)" required>
                      <option value="">Seleccionar concepto...</option>
                      <optgroup label="🏋️ Membresías Individuales">
                          <option value="Mensualidad">Mensualidad - $400.00</option>
                          <option value="Semana">Semana - $120.00</option>
                          <option value="Clase">Clase - $50.00</option>
                          <option value="Tres clases">Tres clases - $100.00</option>
                          <option value="Semana con Yoga">Semana con Yoga - $150.00</option>
                          <option value="Clase de Yoga">Clase de Yoga - $80.00</option>
                      </optgroup>
                      <optgroup label="👨‍👩‍👧‍👦 Planes Familiares/Grupales">
                          <option value="Pareja">Pareja - $700.00</option>
                          <option value="Tres personas">Tres personas - $1000.00</option>
                          <option value="Cuatro personas">Cuatro personas - $1300.00</option>
                          <option value="Cinco personas">Cinco personas - $1600.00</option>
                      </optgroup>
                      <optgroup label="💰 Otros Conceptos">
                          <option value="Descuento">Descuento</option>
                          <option value="Beca">Beca</option>
                          <option value="Reembolso">Reembolso</option>
                          <option value="Otro">Otro (personalizado)</option>
                      </optgroup>
                    </select>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Fecha del pago (opcional)</label>
                    <input type="date" name="fecha" placeholder="Si no se especifica, usa fecha actual">
                    <small style="color: #666; font-size: 0.85em; display: block; margin-top: 5px;">
                      📅 Solo los administradores pueden modificar la fecha del pago
                    </small>
                  </div>
                </div>
                <div style="text-align: center; margin-top: 25px;">
                  <button type="submit" class="btn" style="padding: 12px 30px; font-size: 16px; background: #27ae60;">💰 Registrar Pago</button>
                </div>
              </form>
            </div>
          </div>
        </div>

        <!-- Últimos pagos -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">💳 Últimos Pagos Registrados</h3>
          </div>
          <table>
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Monto</th>
                <th>Fecha</th>
                <th>Concepto</th>
              </tr>
            </thead>
            <tbody>
              {% for usuario, monto, fecha, concepto in pagos %}
              <tr>
                <td>{{ usuario }}</td>
                <td style="color: #27ae60; font-weight: 600;">${{ "%.2f"|format(monto) }}</td>
                <td>{{ fecha }}</td>
                <td>{{ concepto or "Pago de membresía" }}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>

        <!-- Lista de miembros -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">👥 Miembros Registrados ({{ total_miembros }})</h3>
          </div>
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Usuario</th>
                <th>NIP</th>
                <th>Modalidad</th>
                <th>Vigencia</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {% for id, nombre, usuario, pin, nip, modalidad, vigencia, foto in miembros_s %}
              <tr>
                <td>{{ nombre }}</td>
                <td>{{ usuario }}</td>
                <td><strong>{{ nip }}</strong></td>
                <td>{{ modalidad }}</td>
                <td>{{ vigencia }}</td>
                <td>
                  {% set dias = vigencia|dias_restantes %}
                  {% if dias < 0 %}
                    <span style="color: #e74c3c; font-weight: 600;">Vencida</span>
                  {% elif dias <= 7 %}
                    <span style="color: #f39c12; font-weight: 600;">{{ dias }}d restantes</span>
                  {% else %}
                    <span style="color: #27ae60; font-weight: 600;">Vigente</span>
                  {% endif %}
                </td>
                <td>
                  <a href="/detalle_miembro/{{ usuario }}" class="btn" style="padding: 5px 10px; font-size: 0.8em; background: #3498db;">👁️ Ver</a>
                  <a href="/editar_miembro_por_id/{{ id }}" class="btn" style="padding: 5px 10px; font-size: 0.8em; background: #f39c12; margin-left: 5px;">✏️ Editar</a>
                  <form method="POST" action="/renovar/{{ id }}" style="display: inline; margin-left: 5px;">
                    <button type="submit" class="btn btn-success" style="padding: 5px 10px; font-size: 0.8em;">🔄 Renovar</button>
                  </form>
                  <form method="POST" action="/eliminar_usuario/{{ id }}" style="display: inline; margin-left: 5px;" onsubmit="return confirm('¿Eliminar miembro {{ nombre }}?')">
                    <button type="submit" class="btn btn-danger" style="padding: 5px 10px; font-size: 0.8em;">🗑️ Eliminar</button>
                  </form>
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <script>
    // Función para calcular y mostrar la fecha de vencimiento
    function calcularVencimiento() {
      const modalidad = document.querySelector('select[name="modalidad"]').value;
      const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value;
      
      if (!modalidad) return;
      
      // Definir días por modalidad
      const diasPorModalidad = {
        'semanal': 7,
        'mensual': 30,
        'trimestre': 90,
        'semestre': 180,
        'anualidad': 365,
        'plan_familiar': 30
      };
      
      // Usar fecha de inicio o fecha actual
      const fechaBase = fechaInicio ? new Date(fechaInicio) : new Date();
      const diasAgregar = diasPorModalidad[modalidad] || 30;
      
      // Calcular fecha de vencimiento
      const fechaVencimiento = new Date(fechaBase);
      fechaVencimiento.setDate(fechaVencimiento.getDate() + diasAgregar);
      
      // Formatear fecha
      const opciones = { year: 'numeric', month: 'long', day: 'numeric' };
      const fechaFormateada = fechaVencimiento.toLocaleDateString('es-ES', opciones);
      
      // Determinar si la fecha de inicio es anterior, actual o futura
      const hoy = new Date();
      hoy.setHours(0, 0, 0, 0);
      fechaBase.setHours(0, 0, 0, 0);
      
      let estadoFecha = '';
      if (fechaBase < hoy) {
        estadoFecha = ' (retroactiva)';
      } else if (fechaBase > hoy) {
        estadoFecha = ' (futura)';
      }
      
      // Mostrar resultado
      const resultado = document.getElementById('resultado-vencimiento');
      if (resultado) {
        resultado.innerHTML = 
          '<div style="background: #e8f5e8; padding: 12px; border-radius: 6px; margin-top: 10px; border-left: 4px solid #27ae60;">' +
            '<strong>📅 Fecha de vencimiento calculada:</strong><br>' +
            fechaFormateada + estadoFecha +
          '</div>';
      }
    }

    // Agregar event listeners
    document.addEventListener('DOMContentLoaded', function() {
      const modalidadSelect = document.querySelector('select[name="modalidad"]');
      const fechaInicioInput = document.querySelector('input[name="fecha_inicio"]');
      
      if (modalidadSelect) {
        modalidadSelect.addEventListener('change', calcularVencimiento);
        modalidadSelect.addEventListener('change', manejarCambioModalidad);
      }
      if (fechaInicioInput) {
        fechaInicioInput.addEventListener('change', calcularVencimiento);
      }
      
      // Event listener para el nombre (para buscar familias)
      const nombreInput = document.querySelector('input[name="nombre"]');
      if (nombreInput) {
        nombreInput.addEventListener('input', buscarFamiliares);
      }
    });

    // Manejar cambio de modalidad
    function manejarCambioModalidad() {
      const modalidad = document.getElementById('modalidad-admin-main').value;
      const familyContainer = document.getElementById('family-selection-container-admin-main');
      const groupContainer = document.getElementById('group-selection-container-admin-main');
      
      // Ocultar ambos contenedores primero
      familyContainer.style.display = 'none';
      groupContainer.style.display = 'none';
      
      if (modalidad === 'plan_familiar') {
        familyContainer.style.display = 'block';
        buscarFamiliares(); // Buscar automáticamente cuando se selecciona plan familiar
      } else if (modalidad === 'plan_grupal') {
        groupContainer.style.display = 'block';
        cargarPlanesGrupales(); // Cargar planes grupales disponibles
      }
    }

    // Buscar familiares basado en el nombre
    function buscarFamiliares() {
      const modalidad = document.getElementById('modalidad-admin-main').value;
      if (modalidad !== 'plan_familiar') return;
      
      const nombre = document.querySelector('input[name="nombre"]').value.trim();
      const familyList = document.getElementById('family-members-list-admin-main');
      
      if (nombre.length < 3) {
        familyList.innerHTML = `
          <div style="text-align: center; color: #27ae60;">
            <div style="font-size: 2.5em; margin-bottom: 10px;">👨‍👩‍👧‍👦</div>
            <p style="margin: 0; font-weight: 600;">Familiares Detectados</p>
            <p style="margin: 5px 0 0 0; font-size: 0.85em; color: #7f8c8d;">
              Ingresa al menos 3 caracteres del nombre para buscar familiares
            </p>
          </div>`;
        return;
      }
      
      // Mostrar indicador de carga
      familyList.innerHTML = `
        <div style="text-align: center; color: #27ae60; padding: 20px;">
          <div style="font-size: 2em; margin-bottom: 10px;">🔍</div>
          <p style="margin: 0; font-weight: 600;">Buscando familiares...</p>
          <p style="margin: 5px 0 0 0; font-size: 0.85em; color: #7f8c8d;">
            Detectando miembros con apellidos similares
          </p>
        </div>`;
      
      // Buscar familiares potenciales usando apellidos
      fetch('/buscar_familiares', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'nombre=' + encodeURIComponent(nombre)
      })
      .then(response => response.json())
      .then(data => {
        if (data.miembros && data.miembros.length > 0) {
          let html = `
            <div style="margin-bottom: 20px;">
              <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="background: #27ae60; color: white; padding: 6px 10px; border-radius: 50%; margin-right: 10px;">✅</span>
                <h4 style="margin: 0; color: #27ae60; font-size: 1.1em;">¡Familiares Encontrados!</h4>
              </div>
              <p style="color: #7f8c8d; font-size: 0.9em; margin: 0 0 15px 0;">
                Se encontraron ${data.miembros.length} miembro(s) con apellidos similares. Selecciona los que pertenecen a la familia:
              </p>
            </div>`;
          
          data.miembros.forEach((miembro, index) => {
            html += `
              <div style="margin: 10px 0; padding: 15px; background: white; border-radius: 10px; border: 2px solid #e8f5e8; transition: all 0.3s ease; cursor: pointer;" 
                   onmouseover="this.style.borderColor='#27ae60'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(39,174,96,0.2)'" 
                   onmouseout="this.style.borderColor='#e8f5e8'; this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                <label style="display: flex; align-items: center; cursor: pointer; margin: 0;">
                  <div style="margin-right: 15px;">
                    <input type="checkbox" name="familia_miembros" value="${miembro.id}" 
                           style="width: 18px; height: 18px; cursor: pointer;">
                  </div>
                  <div style="flex: 1;">
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                      <span style="background: #27ae60; color: white; padding: 4px 8px; border-radius: 20px; font-size: 0.8em; margin-right: 10px;">👤</span>
                      <strong style="color: #2c3e50; font-size: 1.05em;">${miembro.nombre}</strong>
                    </div>
                    <div style="margin-left: 30px;">
                      <span style="color: #7f8c8d; font-size: 0.9em;">Usuario: <strong>${miembro.usuario}</strong></span>
                      <span style="margin: 0 10px; color: #bdc3c7;">•</span>
                      <span style="color: #3498db; font-size: 0.9em;">Modalidad: ${miembro.modalidad}</span>
                      <span style="margin: 0 10px; color: #bdc3c7;">•</span>
                      <span style="color: #e67e22; font-size: 0.9em;">Vigencia: ${miembro.vigencia}</span>
                    </div>
                  </div>
                </label>
              </div>`;
          });
          
          html += `
            <div style="background: #f0fdf4; border-radius: 8px; padding: 15px; margin-top: 20px; border-left: 4px solid #27ae60;">
              <div style="display: flex; align-items: center;">
                <span style="font-size: 1.2em; margin-right: 8px;">💰</span>
                <div>
                  <strong style="color: #27ae60;">Plan Familiar Económico:</strong>
                  <p style="margin: 5px 0 0 0; color: #2c3e50; font-size: 0.9em;">
                    ✨ Todos los miembros seleccionados compartirán la misma vigencia y tendrán acceso completo al gimnasio
                  </p>
                </div>
              </div>
            </div>`;
          
          familyList.innerHTML = html;
        } else {
          familyList.innerHTML = `
            <div style="text-align: center; color: #7f8c8d; padding: 30px;">
              <div style="font-size: 3em; margin-bottom: 15px;">🔍</div>
              <h4 style="margin: 0 0 10px 0; color: #95a5a6;">No se encontraron familiares</h4>
              <p style="margin: 0; font-size: 0.9em; line-height: 1.4;">
                No se detectaron miembros con apellidos similares a "<strong>${nombre}</strong>".<br>
                El sistema buscará automáticamente cuando agregues más miembros de la familia.
              </p>
              <div style="background: #f8f9fa; border-radius: 8px; padding: 15px; margin-top: 15px; text-align: left;">
                <strong style="color: #6c757d;">💡 Sugerencia:</strong>
                <ul style="margin: 5px 0 0 20px; color: #6c757d; font-size: 0.85em;">
                  <li>Verifica que el apellido esté escrito correctamente</li>
                  <li>Puedes crear el plan familiar y agregar miembros después</li>
                </ul>
              </div>
            </div>`;
        }
      })
      .catch(error => {
        console.error('Error:', error);
        familyList.innerHTML = `
          <div style="text-align: center; color: #e74c3c; padding: 30px;">
            <div style="font-size: 2.5em; margin-bottom: 10px;">⚠️</div>
            <h4 style="margin: 0 0 10px 0;">Error de Conexión</h4>
            <p style="margin: 0; font-size: 0.9em;">
              No se pudo buscar familiares. Verifica tu conexión e intenta de nuevo.
            </p>
            <button onclick="buscarFamiliares()" 
                    style="background: #e74c3c; color: white; border: none; padding: 10px 20px; border-radius: 6px; margin-top: 15px; cursor: pointer;">
              🔄 Reintentar
            </button>
          </div>`;
      });
    }

    // Cargar planes grupales disponibles
    function cargarPlanesGrupales() {
      const groupList = document.getElementById('group-plans-list-admin-main');
      
      fetch('/buscar_miembros_grupo', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'accion=listar_planes'
      })
      .then(response => response.json())
      .then(data => {
        if (data.planes && data.planes.length > 0) {
          let planesDisponibles = data.planes.filter(plan => (plan.max_miembros - plan.total_miembros) > 0);
          
          if (planesDisponibles.length > 0) {
            let html = `
              <div style="margin-bottom: 20px;">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                  <span style="background: #3498db; color: white; padding: 6px 10px; border-radius: 50%; margin-right: 10px;">✅</span>
                  <h4 style="margin: 0; color: #3498db; font-size: 1.1em;">Planes Grupales Disponibles</h4>
                </div>
                <p style="color: #7f8c8d; font-size: 0.9em; margin: 0 0 15px 0;">
                  Selecciona un plan grupal con espacios disponibles:
                </p>
              </div>`;
            
            planesDisponibles.forEach((plan, index) => {
              const espaciosDisponibles = plan.max_miembros - plan.total_miembros;
              const porcentajeOcupacion = (plan.total_miembros / plan.max_miembros) * 100;
              
              html += `
                <div style="margin: 10px 0; padding: 15px; background: white; border-radius: 10px; border: 2px solid #e3f2fd; transition: all 0.3s ease; cursor: pointer;" 
                     onmouseover="this.style.borderColor='#3498db'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(52,152,219,0.2)'" 
                     onmouseout="this.style.borderColor='#e3f2fd'; this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                  <label style="display: flex; align-items: center; cursor: pointer; margin: 0;">
                    <div style="margin-right: 15px;">
                      <input type="radio" name="plan_grupal_id" value="${plan.id}" 
                             style="width: 18px; height: 18px; cursor: pointer;">
                    </div>
                    <div style="flex: 1;">
                      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                        <div style="display: flex; align-items: center;">
                          <span style="background: #3498db; color: white; padding: 4px 8px; border-radius: 20px; font-size: 0.8em; margin-right: 10px;">🏆</span>
                          <strong style="color: #2c3e50; font-size: 1.05em;">${plan.nombre_grupo}</strong>
                        </div>
                        <span style="background: ${espaciosDisponibles > 3 ? '#27ae60' : espaciosDisponibles > 1 ? '#f39c12' : '#e74c3c'}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; font-weight: 600;">
                          ${espaciosDisponibles} ${espaciosDisponibles === 1 ? 'espacio' : 'espacios'}
                        </span>
                      </div>
                      
                      <div style="margin-left: 30px;">
                        <div style="display: flex; align-items: center; margin-bottom: 5px;">
                          <span style="color: #7f8c8d; font-size: 0.9em; margin-right: 15px;">
                            👥 <strong>${plan.total_miembros}/${plan.max_miembros}</strong> miembros
                          </span>
                          <div style="flex: 1; background: #ecf0f1; height: 6px; border-radius: 3px; margin-right: 10px;">
                            <div style="background: ${porcentajeOcupacion < 70 ? '#27ae60' : porcentajeOcupacion < 90 ? '#f39c12' : '#e74c3c'}; 
                                        height: 100%; width: ${porcentajeOcupacion}%; border-radius: 3px; transition: width 0.3s ease;"></div>
                          </div>
                          <span style="color: #7f8c8d; font-size: 0.8em;">${Math.round(porcentajeOcupacion)}%</span>
                        </div>
                        ${plan.descripcion ? `<p style="color: #95a5a6; font-size: 0.85em; margin: 5px 0 0 0; font-style: italic;">📝 ${plan.descripcion}</p>` : ''}
                      </div>
                    </div>
                  </label>
                </div>`;
            });
            
            html += `
              <div style="background: #e3f2fd; border-radius: 8px; padding: 15px; margin-top: 20px; border-left: 4px solid #3498db;">
                <div style="display: flex; align-items: center;">
                  <span style="font-size: 1.2em; margin-right: 8px;">⚡</span>
                  <div>
                    <strong style="color: #3498db;">Ventajas del Plan Grupal:</strong>
                    <p style="margin: 5px 0 0 0; color: #2c3e50; font-size: 0.9em;">
                      🎯 Gestión centralizada • 💰 Precios especiales • 🤝 Entrenamientos grupales
                    </p>
                  </div>
                </div>
              </div>`;
            
            groupList.innerHTML = html;
          } else {
            groupList.innerHTML = `
              <div style="text-align: center; color: #f39c12; padding: 30px;">
                <div style="font-size: 3em; margin-bottom: 15px;">🚫</div>
                <h4 style="margin: 0 0 10px 0; color: #e67e22;">Planes Completos</h4>
                <p style="margin: 0; font-size: 0.9em; line-height: 1.4; color: #7f8c8d;">
                  Todos los planes grupales existentes están completos.<br>
                  Puedes crear un nuevo plan grupal usando los botones de abajo.
                </p>
              </div>`;
          }
        } else {
          groupList.innerHTML = `
            <div style="text-align: center; color: #7f8c8d; padding: 30px;">
              <div style="font-size: 3em; margin-bottom: 15px;">🆕</div>
              <h4 style="margin: 0 0 10px 0; color: #95a5a6;">Sin Planes Grupales</h4>
              <p style="margin: 0; font-size: 0.9em; line-height: 1.4;">
                Aún no hay planes grupales creados.<br>
                ¡Crea el primer plan grupal para tu gimnasio!
              </p>
              <div style="background: #f8f9fa; border-radius: 8px; padding: 15px; margin-top: 15px; text-align: left;">
                <strong style="color: #6c757d;">� Ideas para planes grupales:</strong>
                <ul style="margin: 5px 0 0 20px; color: #6c757d; font-size: 0.85em;">
                  <li>Equipos deportivos (fútbol, basketball, etc.)</li>
                  <li>Grupos de entrenamiento funcional</li>
                  <li>Clases de yoga o pilates</li>
                  <li>Entrenamientos corporativos</li>
                </ul>
              </div>
            </div>`;
        }
      })
      .catch(error => {
        console.error('Error:', error);
        groupList.innerHTML = `
          <div style="text-align: center; color: #e74c3c; padding: 30px;">
            <div style="font-size: 2.5em; margin-bottom: 10px;">⚠️</div>
            <h4 style="margin: 0 0 10px 0;">Error de Conexión</h4>
            <p style="margin: 0; font-size: 0.9em;">
              No se pudieron cargar los planes grupales. Verifica tu conexión e intenta de nuevo.
            </p>
            <button onclick="cargarPlanesGrupales()" 
                    style="background: #e74c3c; color: white; border: none; padding: 10px 20px; border-radius: 6px; margin-top: 15px; cursor: pointer;">
              🔄 Reintentar
            </button>
          </div>`;
      });
    }
    
    // Función para filtrar miembros en tiempo real
    function filtrarMiembros() {
      const busqueda = document.getElementById('busquedaMiembros').value.toLowerCase();
      const filas = document.querySelectorAll('.miembro-fila');
      let filasVisibles = 0;
      
      filas.forEach(fila => {
        const nombre = fila.dataset.nombre || '';
        const usuario = fila.dataset.usuario || '';
        const nip = fila.dataset.nip || '';
        const modalidad = fila.dataset.modalidad || '';
        
        // Filtro de búsqueda
        const coincideBusqueda = busqueda === '' || 
                                nombre.includes(busqueda) || 
                                usuario.includes(busqueda) || 
                                nip.includes(busqueda) || 
                                modalidad.includes(busqueda);
        
        if (coincideBusqueda) {
          fila.style.display = '';
          filasVisibles++;
        } else {
          fila.style.display = 'none';
        }
      });
      
      // Mostrar mensaje si no hay resultados
      let mensajeNoResultados = document.getElementById('mensaje-no-resultados');
      if (filasVisibles === 0 && busqueda !== '') {
        if (!mensajeNoResultados) {
          mensajeNoResultados = document.createElement('tr');
          mensajeNoResultados.id = 'mensaje-no-resultados';
          mensajeNoResultados.innerHTML = '<td colspan="7" style="text-align: center; padding: 20px; color: #666;">No se encontraron miembros que coincidan con la búsqueda</td>';
          document.querySelector('#tablaMiembros tbody').appendChild(mensajeNoResultados);
        }
        mensajeNoResultados.style.display = '';
      } else if (mensajeNoResultados) {
        mensajeNoResultados.style.display = 'none';
      }
    }
    
    // Función para limpiar la búsqueda
    function limpiarBusqueda() {
      document.getElementById('busquedaMiembros').value = '';
      filtrarMiembros();
    }
    
    // Script específico para inicializar el buscador en el panel admin
    document.addEventListener('DOMContentLoaded', function() {
      // Detectar si estamos en el panel admin buscando el botón renovar específico
      const hasRenovarButton = Array.from(document.querySelectorAll('button')).some(btn => 
        btn.textContent.includes('🔄 Renovar') && btn.type === 'submit'
      );
      
      if (hasRenovarButton) {
        // Buscar la tabla de miembros específicamente
        const cardTitles = document.querySelectorAll('.card-title');
        let targetCard = null;
        
        cardTitles.forEach(title => {
          if (title.textContent.includes('👥 Miembros Registrados')) {
            targetCard = title.closest('.card');
          }
        });
        
        if (targetCard) {
          const cardHeader = targetCard.querySelector('.card-header');
          const table = targetCard.querySelector('table');
          
          // Solo agregar si no existe ya el buscador
          if (!document.getElementById('busquedaMiembros')) {
            // Crear interfaz de búsqueda
            const searchInterface = document.createElement('div');
            searchInterface.style.cssText = 'display: flex; align-items: center; gap: 10px; margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef;';
            searchInterface.innerHTML = `
              <div style="display: flex; align-items: center; flex: 1; gap: 10px;">
                <span style="color: #6c757d; font-weight: 600; font-size: 14px;">🔍 Buscar:</span>
                <input type="text" id="busquedaMiembros" placeholder="Nombre, usuario, NIP o modalidad..." 
                       onkeyup="filtrarMiembros()" 
                       style="flex: 1; padding: 8px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 14px; outline: none; transition: border-color 0.2s;"
                       onfocus="this.style.borderColor='#3498db'" onblur="this.style.borderColor='#ced4da'">
                <button onclick="limpiarBusqueda()" 
                        style="padding: 8px 16px; background: #e74c3c; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600; transition: background 0.2s;"
                        onmouseover="this.style.background='#c0392b'" onmouseout="this.style.background='#e74c3c'">
                  Limpiar
                </button>
              </div>
            `;
            cardHeader.appendChild(searchInterface);
            
            // Configurar tabla y filas
            if (table) {
              table.id = 'tablaMiembros';
              const rows = table.querySelectorAll('tbody tr');
              rows.forEach(row => {
                const cells = row.cells;
                if (cells.length >= 7) { // Verificar que tiene todas las columnas (incluyendo acciones)
                  row.className = 'miembro-fila';
                  row.setAttribute('data-nombre', cells[0].textContent.toLowerCase().trim());
                  row.setAttribute('data-usuario', cells[1].textContent.toLowerCase().trim());
                  row.setAttribute('data-nip', cells[2].textContent.replace(/\D/g, ''));
                  row.setAttribute('data-modalidad', cells[3].textContent.toLowerCase().trim());
                }
              });
              
              console.log(`✅ Buscador inicializado: ${rows.length} filas de miembros encontradas`);
            }
          }
        }
      }
    });

  </script>
</body>
</html>
""", miembros_s=miembros_s, pagos=pagos, total_miembros=total_miembros, 
     miembros_activos=miembros_activos, miembros_vencidos=miembros_vencidos, 
     ingresos_hoy=ingresos_hoy, logo_fn=logo_fn, BASE_STYLES=BASE_STYLES)

# ================================
# CORRECCIÓN APLICADA - ADMIN FORM MODIFICADO
# Panel de admin ahora tiene funcionalidad de familia
# ================================

@app.route("/debug_miembros")
def debug_miembros():
    """Ruta de debug temporal para verificar los datos de miembros"""
    if session.get("rol") != "admin":
        return redirect("/login")
    
    con = conectar()
    miembros = con.execute("""
        SELECT id, nombre, usuario, pin, nip_visible, modalidad, vigencia, foto
        FROM usuarios WHERE rol='miembro'
        ORDER BY id ASC
    """).fetchall()
    con.close()
    
    resultado = "<h1>Debug Miembros</h1><table border='1'>"
    resultado += "<tr><th>ID</th><th>Nombre</th><th>Usuario</th><th>Pin</th><th>NIP</th><th>Modalidad</th><th>Vigencia</th><th>Foto</th><th>Enlace Editar</th></tr>"
    
    for miembro in miembros:
        id_m, nombre, usuario, pin, nip, modalidad, vigencia, foto = miembro
        enlace = f"/editar_miembro/{usuario}"
        resultado += f"<tr><td>{id_m}</td><td>{nombre}</td><td>{usuario}</td><td>{pin}</td><td>{nip}</td><td>{modalidad}</td><td>{vigencia}</td><td>{foto}</td><td><a href='{enlace}'>Editar</a></td></tr>"
    
    resultado += "</table>"
    return resultado

@app.route("/gestionar_familias")
def gestionar_familias():
    """Página para gestionar planes familiares y sugerencias"""
    if session.get("rol") not in ["admin", "moderador"]:
        flash("Acceso denegado.")
        return redirect("/login")
    
    # Detectar nuevas sugerencias automáticamente
    detectar_apellidos_similares()
    
    # Obtener sugerencias pendientes
    sugerencias = obtener_sugerencias_pendientes()
    
    # Obtener planes familiares existentes
    con = conectar()
    planes = con.execute("""
        SELECT pf.id, pf.nombre_plan, pf.fecha_creacion, pf.vigencia, pf.activo,
               COUNT(mf.miembro_id) as total_miembros
        FROM planes_familiares pf
        LEFT JOIN miembros_familia mf ON pf.id = mf.plan_familiar_id
        GROUP BY pf.id
        ORDER BY pf.fecha_creacion DESC
    """).fetchall()
    
    logo_row = con.execute("SELECT filename FROM logo ORDER BY id DESC LIMIT 1").fetchone()
    logo_fn = logo_row[0] if logo_row else ""
    con.close()
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Gestión de Familias - LAMA Control</title>
  {{ BASE_STYLES|safe }}
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>{{ 'ADMIN' if session['rol']=='admin' else 'MODERADOR' }} PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="{{ '/admin' if session['rol']=='admin' else '/moderador' }}"><i>🏠</i> Panel Principal</a></li>
        <li><a href="/gestionar_familias" class="active"><i>👨‍👩‍👧‍👦</i> Gestión de Familias</a></li>
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header">
        <h1>👨‍👩‍👧‍👦 Gestión de Planes Familiares</h1>
        <div class="breadcrumb">Panel {{ 'Admin' if session['rol']=='admin' else 'Moderador' }} > Gestión de Familias</div>
      </div>

      <div class="content-body">
        <!-- Sugerencias de vinculación -->
        {% if sugerencias %}
        <div class="card" style="margin-bottom: 30px;">
          <div class="card-header">
            <h3 class="card-title">🔍 Sugerencias de Vinculación Familiar ({{ sugerencias|length }})</h3>
          </div>
          <table>
            <thead>
              <tr>
                <th>Miembro 1</th>
                <th>Miembro 2</th>
                <th>Razón</th>
                <th>Fecha</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {% for id, nombre1, nombre2, razon, fecha, id1, id2 in sugerencias %}
              <tr>
                <td>{{ nombre1 }}</td>
                <td>{{ nombre2 }}</td>
                <td>{{ razon }}</td>
                <td>{{ fecha }}</td>
                <td>
                  <form method="POST" action="/vincular_familia" style="display: inline;">
                    <input type="hidden" name="miembro1_id" value="{{ id1 }}">
                    <input type="hidden" name="miembro2_id" value="{{ id2 }}">
                    <input type="hidden" name="sugerencia_id" value="{{ id }}">
                    <button type="submit" class="btn" style="background: #27ae60; padding: 5px 10px; font-size: 0.8em;">✓ Aceptar</button>
                  </form>
                  <form method="POST" action="/rechazar_sugerencia" style="display: inline; margin-left: 5px;">
                    <input type="hidden" name="sugerencia_id" value="{{ id }}">
                    <button type="submit" class="btn" style="background: #e74c3c; padding: 5px 10px; font-size: 0.8em;">✗ Rechazar</button>
                  </form>
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
        {% endif %}

        <!-- Planes familiares existentes -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">👨‍👩‍👧‍👦 Planes Familiares Activos ({{ planes|length }})</h3>
          </div>
          {% if planes %}
          <table>
            <thead>
              <tr>
                <th>Nombre del Plan</th>
                <th>Fecha Creación</th>
                <th>Vigencia</th>
                <th>Total Miembros</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {% for id, nombre, fecha, vigencia, activo, total in planes %}
              <tr>
                <td>{{ nombre }}</td>
                <td>{{ fecha }}</td>
                <td>{{ vigencia }}</td>
                <td>{{ total }}</td>
                <td>
                  {% if activo %}
                    <span style="color: #27ae60; font-weight: 600;">Activo</span>
                  {% else %}
                    <span style="color: #e74c3c; font-weight: 600;">Inactivo</span>
                  {% endif %}
                </td>
                <td>
                  <a href="/ver_plan_familiar/{{ id }}" class="btn" style="padding: 5px 10px; font-size: 0.8em; background: #3498db;">👁️ Ver</a>
                  <form method="POST" action="/eliminar_plan_familiar" style="display: inline; margin-left: 5px;">
                    <input type="hidden" name="plan_id" value="{{ id }}">
                    <button type="submit" class="btn" style="background: #e74c3c; padding: 5px 10px; font-size: 0.8em;" onclick="return confirm('¿ELIMINAR PERMANENTEMENTE el plan familiar {{ nombre }}? Esta acción eliminará el plan y todos sus miembros volverán a modalidad individual.')">🗑️ Eliminar</button>
                  </form>
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
          {% else %}
          <div style="padding: 20px; text-align: center; color: #666;">
            No hay planes familiares registrados aún.
          </div>
          {% endif %}
        </div>
      </div>
    </div>
  </div>
</body>
</html>
""", sugerencias=sugerencias, planes=planes, logo_fn=logo_fn, BASE_STYLES=BASE_STYLES)

@app.route("/vincular_familia", methods=["POST"])
def vincular_familia():
    """Crear un plan familiar con los miembros sugeridos"""
    if session.get("rol") not in ["admin", "moderador"]:
        flash("Acceso denegado.")
        return redirect("/login")
    
    miembro1_id = request.form.get("miembro1_id")
    miembro2_id = request.form.get("miembro2_id")
    sugerencia_id = request.form.get("sugerencia_id")
    
    con = conectar()
    try:
        # Obtener nombres de los miembros
        miembro1 = con.execute("SELECT nombre FROM usuarios WHERE id=?", (miembro1_id,)).fetchone()
        miembro2 = con.execute("SELECT nombre FROM usuarios WHERE id=?", (miembro2_id,)).fetchone()
        
        if miembro1 and miembro2:
            # Obtener apellido común
            apellido1 = miembro1[0].split()[-1] if miembro1[0] else ""
            apellido2 = miembro2[0].split()[-1] if miembro2[0] else ""
            
            if apellido1.lower() != apellido2.lower():
                flash("Error: Los miembros deben tener el mismo apellido para formar un plan familiar.")
                return redirect("/gestionar_familias")
            
            nombre_plan = f"{apellido1} - Plan Familiar"
            
            # Marcar sugerencia como aceptada ANTES de crear el plan
            con.execute("""
                UPDATE sugerencias_familia 
                SET estado='aceptada', fecha_decision=?, decidido_por=?
                WHERE id=?
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), session.get("nombre"), sugerencia_id))
            con.commit()
            con.close()
            
            try:
                # Crear el plan familiar (esta función maneja su propia conexión)
                plan_id = crear_plan_familiar(nombre_plan, [miembro1_id, miembro2_id], miembro1_id)
                flash(f"Plan familiar '{nombre_plan}' creado exitosamente.")
            except ValueError as e:
                flash(f"Error al crear plan familiar: {str(e)}")
            except Exception as e:
                print(f"Error inesperado en vincular_familia: {e}")
                flash(f"Error inesperado: {str(e)}")
        else:
            flash("Error: No se encontraron los miembros especificados.")
            con.close()
            
    except Exception as e:
        print(f"Error en vincular_familia: {e}")
        flash(f"Error al procesar la solicitud: {str(e)}")
        con.close()
    
    return redirect("/gestionar_familias")

@app.route("/rechazar_sugerencia", methods=["POST"])
def rechazar_sugerencia():
    """Rechazar una sugerencia de vinculación familiar"""
    if session.get("rol") not in ["admin", "moderador"]:
        flash("Acceso denegado.")
        return redirect("/login")
    
    sugerencia_id = request.form.get("sugerencia_id")
    
    con = conectar()
    con.execute("""
        UPDATE sugerencias_familia 
        SET estado='rechazada', fecha_decision=?, decidido_por=?
        WHERE id=?
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), session.get("nombre"), sugerencia_id))
    
    con.commit()
    con.close()
    
    flash("Sugerencia rechazada.")
    return redirect("/gestionar_familias")

@app.route("/editar_miembro_por_id/<int:id_miembro>")
def editar_miembro_por_id(id_miembro):
    if session.get("rol") != "admin":
        flash("Acceso denegado. Solo los administradores pueden editar miembros.")
        return redirect("/login")
    
    con = conectar()
    
    # Buscar por ID es más confiable que por usuario
    miembro = con.execute("""
        SELECT id, nombre, usuario, modalidad, vigencia, foto, correo, telefono_emergencia, datos_medicos, nip_visible
        FROM usuarios WHERE id=? AND rol='miembro'
    """, (id_miembro,)).fetchone()
    
    if not miembro:
        flash(f"Miembro con ID {id_miembro} no encontrado.")
        con.close()
        return redirect("/admin" if session.get("rol") == "admin" else "/moderador")

    id_miembro, nombre, usuario_db, modalidad, vigencia, foto, correo, telefono, datos_medicos, nip = miembro
    
    # Obtener logo
    logo_row = con.execute("SELECT filename FROM logo ORDER BY id DESC LIMIT 1").fetchone()
    logo_fn = logo_row[0] if logo_row else ""
    con.close()

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Editar Miembro - {{ nombre }}</title>
  {{ BASE_STYLES|safe }}
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>{{ 'ADMIN' if session['rol']=='admin' else 'MODERADOR' }} PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="{{ '/admin' if session['rol']=='admin' else '/moderador' }}"><i>🏠</i> Panel Principal</a></li>
        {% if session['rol'] == 'admin' %}
        <li><a href="/reportes_financieros"><i>📊</i> Reportes Financieros</a></li>
        <li><a href="/estadisticas_globales"><i>📈</i> Estadísticas Globales</a></li>
        <li><a href="/analiticas_avanzadas"><i>🔍</i> Analíticas Avanzadas</a></li>
        <li><a href="/gestion_backups"><i>💾</i> Gestión de Backups</a></li>
        <li><a href="/gestion_usuarios_admin"><i>👑</i> Gestión Admins/Moderadores</a></li>
        <li><a href="/corte_caja"><i>💰</i> Corte de Caja</a></li>
        <li><a href="/diseno_plataforma"><i>🎨</i> Diseño de Plataforma</a></li>
        {% endif %}
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header">
        <h1>✏️ Editar Datos del Miembro</h1>
        <div class="breadcrumb">Panel {{ 'Admin' if session['rol']=='admin' else 'Moderador' }} > Editar Miembro > {{ nombre }}</div>
      </div>

      <div class="content-body">
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">📝 Modificar Información Personal</h3>
          </div>
          <form method="POST" action="/actualizar_miembro" enctype="multipart/form-data" style="padding: 25px;">
            <input type="hidden" name="id_miembro" value="{{ id_miembro }}">
            <input type="hidden" name="usuario_original" value="{{ usuario }}">
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 25px;">
              <div>
                <div class="form-group">
                  <label class="form-label">Nombre completo</label>
                  <input type="text" name="nombre" value="{{ nombre }}" required>
                </div>
                
                <div class="form-group">
                  <label class="form-label">Nombre de usuario</label>
                  <input type="text" name="usuario" value="{{ usuario }}" required>
                </div>
                
                <div class="form-group">
                  <label class="form-label">Modalidad</label>
                  <select name="modalidad" required>
                    <option value="semanal" {{ 'selected' if modalidad=='semanal' else '' }}>Semanal</option>
                    <option value="mensual" {{ 'selected' if modalidad=='mensual' else '' }}>Mensual</option>
                    <option value="trimestre" {{ 'selected' if modalidad=='trimestre' else '' }}>Trimestre</option>
                    <option value="semestre" {{ 'selected' if modalidad=='semestre' else '' }}>Semestre</option>
                    <option value="anualidad" {{ 'selected' if modalidad=='anualidad' else '' }}>Anualidad</option>
                    <option value="plan_familiar" {{ 'selected' if modalidad=='plan_familiar' else '' }}>Plan Familiar</option>
                  </select>
                </div>
                
                <div class="form-group">
                  <label class="form-label">NIP Visible</label>
                  <input type="text" name="nip" value="{{ nip }}" maxlength="4" pattern="[0-9]{4}" title="Debe ser un número de 4 dígitos" required>
                </div>
                
                <div class="form-group">
                  <label class="form-label">PIN de Acceso</label>
                  <input type="password" name="pin" maxlength="4" pattern="[0-9]{4}" title="Debe ser un número de 4 dígitos" placeholder="Dejar vacío para mantener actual">
                </div>
              </div>
              
              <div>
                <div class="form-group">
                  <label class="form-label">Correo electrónico</label>
                  <input type="email" name="correo" value="{{ correo or '' }}">
                </div>
                
                <div class="form-group">
                  <label class="form-label">Teléfono de emergencia</label>
                  <input type="text" name="telefono_emergencia" value="{{ telefono or '' }}">
                </div>
                
                <div class="form-group">
                  <label class="form-label">Datos médicos</label>
                  <textarea name="datos_medicos" rows="3">{{ datos_medicos or '' }}</textarea>
                </div>
                
                <div class="form-group">
                  <label class="form-label">Cambiar foto</label>
                  <input type="file" name="foto" accept="image/*">
                  {% if foto %}
                    <small style="color: #666; font-size: 0.85em; display: block; margin-top: 5px;">
                      📷 Foto actual: {{ foto }}
                    </small>
                  {% endif %}
                </div>
              </div>
            </div>
            
            {% if foto %}
            <div style="text-align: center; margin-bottom: 25px;">
              <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; display: inline-block;">
                <img src="{{ url_for('static', filename='fotos/'+foto) }}" style="max-width: 150px; max-height: 150px; object-fit: cover; border-radius: 8px; border: 2px solid #ddd;">
                <p style="margin: 10px 0 0 0; color: #666; font-size: 14px;">Foto actual</p>
              </div>
            </div>
            {% endif %}
            
            <div style="background: #fff9e6; padding: 15px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #f39c12;">
              <h4 style="margin: 0 0 10px 0; color: #2c3e50;">⚠️ Información Importante</h4>
              <ul style="margin: 0; padding-left: 20px; color: #666;">
                <li>Los cambios se aplicarán inmediatamente</li>
                <li>Si cambias el PIN, asegúrate de informar al miembro</li>
                <li>El NIP visible debe ser único y tener exactamente 4 dígitos</li>
                <li>La vigencia actual se mantendrá: <strong>{{ vigencia }}</strong></li>
              </ul>
            </div>
            
            <div style="text-align: center; gap: 15px; display: flex; justify-content: center;">
              <button type="submit" class="btn" style="padding: 12px 30px; font-size: 16px;">💾 Guardar Cambios</button>
              <a href="{{ '/admin' if session['rol']=='admin' else '/moderador' }}" class="btn" style="padding: 12px 30px; font-size: 16px; background: #95a5a6; text-decoration: none; color: white;">❌ Cancelar</a>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
""", id_miembro=id_miembro, nombre=nombre, usuario=usuario_db, modalidad=modalidad, 
     vigencia=vigencia, foto=foto, correo=correo, telefono=telefono, 
     datos_medicos=datos_medicos, nip=nip, logo_fn=logo_fn, BASE_STYLES=BASE_STYLES)

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Panel Admin - LAMA Control</title>
  {{ BASE_STYLES|safe }}
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>ADMIN PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="/admin" class="active"><i>🏠</i> Panel Principal</a></li>
        <li><a href="/reportes_financieros"><i>📊</i> Reportes Financieros</a></li>
        <li><a href="/estadisticas_globales"><i>📈</i> Estadísticas Globales</a></li>
        <li><a href="/analiticas_avanzadas"><i>🔍</i> Analíticas Avanzadas</a></li>
        <li><a href="/gestion_backups"><i>💾</i> Gestión de Backups</a></li>
        <li><a href="/gestion_usuarios_admin"><i>👑</i> Gestión Admins/Moderadores</a></li>
        <li><a href="/corte_caja"><i>💰</i> Corte de Caja</a></li>
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header">
        <h1>🏋️ Panel de Administrador</h1>
        <div class="breadcrumb">Sistema LAMA Control - Bienvenido {{ session.nombre }}</div>
      </div>

      <div class="content-body">
        <!-- Estadísticas principales -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-number">{{ total_miembros }}</div>
            <div class="stat-label">Total Miembros</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);">
            <div class="stat-number">{{ miembros_activos }}</div>
            <div class="stat-label">Miembros Activos</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">
            <div class="stat-number">{{ miembros_vencidos }}</div>
            <div class="stat-label">Miembros Vencidos</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);">
            <div class="stat-number">${{ "%.2f"|format(ingresos_hoy) }}</div>
            <div class="stat-label">Ingresos Hoy</div>
          </div>
        </div>

        <!-- Acciones Rápidas -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">🚀 Acciones Rápidas</h3>
          </div>
          <div class="quick-actions">
            <a href="/reportes_financieros" class="quick-action">
              <i>📊</i>
              <strong>Reportes Financieros</strong>
              <small>Análisis de ingresos y ganancias</small>
            </a>
            <a href="/estadisticas_globales" class="quick-action">
              <i>📈</i>
              <strong>Estadísticas Globales</strong>
              <small>Métricas generales del gimnasio</small>
            </a>
            <a href="/analiticas_avanzadas" class="quick-action">
              <i>🔍</i>
              <strong>Analíticas Avanzadas</strong>
              <small>Análisis detallado de datos</small>
            </a>
            <a href="/gestion_backups" class="quick-action">
              <i>💾</i>
              <strong>Gestión de Backups</strong>
              <small>Respaldos del sistema</small>
            </a>
            <a href="/gestion_usuarios_admin" class="quick-action">
              <i>👑</i>
              <strong>Gestión Admins/Moderadores</strong>
              <small>Administrar usuarios del sistema</small>
            </a>
            <a href="/corte_caja" class="quick-action">
              <i>💰</i>
              <strong>Corte de Caja</strong>
              <small>Reporte de ingresos del día</small>
            </a>
            <a href="/descargar_reporte" class="quick-action">
              <i>📋</i>
              <strong>Descargar Reporte</strong>
              <small>Exportar datos de miembros</small>
            </a>
            <a href="/generar_datos_prueba" class="quick-action">
              <i>🎲</i>
              <strong>Generar Datos Prueba</strong>
              <small>Datos de ejemplo para testing</small>
            </a>
          </div>
        </div>

        <!-- Formularios de gestión -->
        <div class="card" style="margin-bottom: 30px;">
          <div class="card-header">
            <h3 class="card-title">📝 Formularios de Gestión</h3>
          </div>
          <div style="padding: 30px;">
            <!-- Crear Miembro -->
            <div style="margin-bottom: 40px; border-bottom: 2px solid #ecf0f1; padding-bottom: 30px;">
              <h4 style="color: #2c3e50; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                <span style="background: #3498db; color: white; padding: 8px 12px; border-radius: 50%; font-size: 18px;">👥</span>
                Crear Nuevo Miembro
              </h4>
              <form method="POST" action="/crear_miembro" enctype="multipart/form-data" id="form-crear-miembro">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                  <div class="form-group">
                    <label class="form-label">Nombre completo</label>
                    <input type="text" name="nombre" id="nombre-admin" required>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Nombre de usuario</label>
                    <input type="text" name="usuario" required>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Modalidad</label>
                    <select name="modalidad" id="modalidad-admin-main" required>
                      <option value="">Seleccionar modalidad</option>
                      <option value="semanal">Semanal</option>
                      <option value="mensual">Mensual</option>
                      <option value="trimestre">Trimestre</option>
                      <option value="semestre">Semestre</option>
                      <option value="anualidad">Anualidad</option>
                      <option value="plan_familiar">Plan Familiar</option>
                    </select>
                  </div>
                 <div class="form-group">
                   <label class="form-label">Fecha de inicio de membresía (opcional)</label>
                   <input type="date" name="fecha_inicio" value="{{ fecha_inicio or '' }}" placeholder="Si no se especifica, inicia desde hoy">
                   <small style="color: #666; font-size: 0.85em; display: block; margin-top: 5px;">
                     💡 Si no especificas una fecha, la membresía iniciará desde hoy
                   </small>
                 </div>
                  <div class="form-group">
                    <label class="form-label">Fecha de inicio de membresía (opcional)</label>
                    <input type="date" name="fecha_inicio" placeholder="Si no se especifica, inicia desde hoy">
                    <small style="color: #666; font-size: 0.85em; display: block; margin-top: 5px;">
                      💡 Si no especificas una fecha, la membresía iniciará desde hoy
                    </small>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Correo electrónico (opcional)</label>
                    <input type="email" name="correo">
                  </div>
                  <div class="form-group">
                    <label class="form-label">Teléfono de emergencia (opcional)</label>
                    <input type="text" name="telefono_emergencia">
                  </div>
                  <div class="form-group">
                    <label class="form-label">Datos médicos (opcional)</label>
                    <textarea name="datos_medicos" rows="3"></textarea>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Foto del miembro (opcional)</label>
                    <input type="file" name="foto" accept="image/*">
                  </div>
                </div>
                <div style="text-align: center; margin-top: 25px;">
                  <button type="submit" class="btn" style="padding: 12px 30px; font-size: 16px;">👥 Crear Miembro</button>
                </div>
              </form>
            </div>

            <!-- Crear Admin/Moderador -->
            <div style="margin-bottom: 40px; border-bottom: 2px solid #ecf0f1; padding-bottom: 30px;">
              <h4 style="color: #2c3e50; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                <span style="background: #9b59b6; color: white; padding: 8px 12px; border-radius: 50%; font-size: 18px;">👑</span>
                Crear Admin/Moderador
              </h4>
              <form method="POST" action="/crear_usuario">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                  <div class="form-group">
                    <label class="form-label">Nombre completo</label>
                    <input type="text" name="nombre" required>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Nombre de usuario</label>
                    <input type="text" name="usuario" required>
                  </div>
                  <div class="form-group">
                    <label class="form-label">PIN (4 dígitos)</label>
                    <input type="text" name="pin" pattern="[0-9]{4}" maxlength="4" required>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Rol</label>
                    <select name="rol" required>
                      <option value="">Seleccionar rol</option>
                      <option value="admin">Administrador</option>
                      <option value="moderador">Moderador</option>
                    </select>
                  </div>
                </div>
                <div style="text-align: center; margin-top: 25px;">
                  <button type="submit" class="btn" style="padding: 12px 30px; font-size: 16px; background: #9b59b6;">👑 Crear Usuario</button>
                </div>
              </form>
            </div>

            <!-- Registrar Pago -->
            <div style="margin-bottom: 20px;">
              <h4 style="color: #2c3e50; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                <span style="background: #27ae60; color: white; padding: 8px 12px; border-radius: 50%; font-size: 18px;">💰</span>
                Registrar Pago
              </h4>
              <form method="POST" action="/registrar_pago">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                  <div class="form-group">
                    <label class="form-label">Seleccionar miembro</label>
                    <select name="usuario" required>
                      <option value="">Seleccionar miembro...</option>
                      {% for id, nombre, usuario, pin, nip, modalidad, vigencia, foto in miembros_s %}
                      <option value="{{ usuario }}">{{ nombre }} ({{ usuario }})</option>
                      {% endfor %}
                    </select>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Monto del pago</label>
                    <input type="number" name="monto" id="montoInputAdmin2" step="0.01" min="0" placeholder="0.00" required>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Concepto del pago</label>
                    <select name="concepto" onchange="actualizarMontoAdmin2(this.value)" required>
                      <option value="">Seleccionar concepto...</option>
                      <optgroup label="🏋️ Membresías Individuales">
                          <option value="Mensualidad">Mensualidad - $400.00</option>
                          <option value="Semana">Semana - $120.00</option>
                          <option value="Clase">Clase - $50.00</option>
                          <option value="Tres clases">Tres clases - $100.00</option>
                          <option value="Semana con Yoga">Semana con Yoga - $150.00</option>
                          <option value="Clase de Yoga">Clase de Yoga - $80.00</option>
                      </optgroup>
                      <optgroup label="👨‍👩‍👧‍👦 Planes Familiares/Grupales">
                          <option value="Pareja">Pareja - $700.00</option>
                          <option value="Tres personas">Tres personas - $1000.00</option>
                          <option value="Cuatro personas">Cuatro personas - $1300.00</option>
                          <option value="Cinco personas">Cinco personas - $1600.00</option>
                      </optgroup>
                      <optgroup label="💰 Otros Conceptos">
                          <option value="Descuento">Descuento</option>
                          <option value="Beca">Beca</option>
                          <option value="Reembolso">Reembolso</option>
                          <option value="Otro">Otro (personalizado)</option>
                      </optgroup>
                    </select>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Fecha del pago (opcional)</label>
                    <input type="date" name="fecha" placeholder="Si no se especifica, usa fecha actual">
                    <small style="color: #666; font-size: 0.85em; display: block; margin-top: 5px;">
                      📅 Solo los administradores pueden modificar la fecha del pago
                    </small>
                  </div>
                </div>
                <div style="text-align: center; margin-top: 25px;">
                  <button type="submit" class="btn" style="padding: 12px 30px; font-size: 16px; background: #27ae60;">💰 Registrar Pago</button>
                </div>
              </form>
            </div>
          </div>
        </div>

        <!-- Últimos pagos -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">💳 Últimos Pagos Registrados</h3>
          </div>
          <table>
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Monto</th>
                <th>Fecha</th>
                <th>Concepto</th>
              </tr>
            </thead>
            <tbody>
              {% for usuario, monto, fecha, concepto in pagos %}
              <tr>
                <td>{{ usuario }}</td>
                <td style="color: #27ae60; font-weight: 600;">${{ "%.2f"|format(monto) }}</td>
                <td>{{ fecha }}</td>
                <td>{{ concepto or "Pago de membresía" }}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>

        <!-- Lista de miembros -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">👥 Miembros Registrados ({{ total_miembros }})</h3>
          </div>
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Usuario</th>
                <th>NIP</th>
                <th>Modalidad</th>
                <th>Vigencia</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {% for id, nombre, usuario, pin, nip, modalidad, vigencia, foto in miembros_s %}
              <tr>
                <td>{{ nombre }}</td>
                <td>{{ usuario }}</td>
                <td><strong>{{ nip }}</strong></td>
                <td>{{ modalidad }}</td>
                <td>{{ vigencia }}</td>
                <td>
                  {% set dias = vigencia|dias_restantes %}
                  {% if dias < 0 %}
                    <span style="color: #e74c3c; font-weight: 600;">Vencida</span>
                  {% elif dias <= 7 %}
                    <span style="color: #f39c12; font-weight: 600;">{{ dias }}d restantes</span>
                  {% else %}
                    <span style="color: #27ae60; font-weight: 600;">Vigente</span>
                  {% endif %}
                </td>
                <td>
                  <a href="/detalle_miembro/{{ usuario }}" class="btn" style="padding: 5px 10px; font-size: 0.8em; background: #3498db;">👁️ Ver</a>
                  <a href="/editar_miembro_por_id/{{ id }}" class="btn" style="padding: 5px 10px; font-size: 0.8em; background: #f39c12; margin-left: 5px;">✏️ Editar</a>
                  <form method="POST" action="/renovar/{{ id }}" style="display: inline; margin-left: 5px;">
                    <button type="submit" class="btn btn-success" style="padding: 5px 10px; font-size: 0.8em;">🔄 Renovar</button>
                  </form>
                  <form method="POST" action="/eliminar_usuario/{{ id }}" style="display: inline; margin-left: 5px;" onsubmit="return confirm('¿Eliminar miembro {{ nombre }}?')">
                    <button type="submit" class="btn btn-danger" style="padding: 5px 10px; font-size: 0.8em;">🗑️ Eliminar</button>
                  </form>
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <script>
    // Función para calcular y mostrar la fecha de vencimiento
    function calcularVencimiento() {
      const modalidad = document.querySelector('select[name="modalidad"]').value;
      const fechaInicio = document.querySelector('input[name="fecha_inicio"]').value;
      
      if (!modalidad) return;
      
      // Definir días por modalidad
      const diasPorModalidad = {
        'semanal': 7,
        'mensual': 30,
        'trimestre': 90,
        'semestre': 180,
        'anualidad': 365,
        'plan_familiar': 30
      };
      
      // Usar fecha de inicio o fecha actual
      const fechaBase = fechaInicio ? new Date(fechaInicio) : new Date();
      const diasAgregar = diasPorModalidad[modalidad] || 30;
      
      // Calcular fecha de vencimiento
      const fechaVencimiento = new Date(fechaBase);
      fechaVencimiento.setDate(fechaVencimiento.getDate() + diasAgregar);
      
      // Formatear fecha
      const opciones = { year: 'numeric', month: 'long', day: 'numeric' };
      const fechaFormateada = fechaVencimiento.toLocaleDateString('es-ES', opciones);
      
      // Determinar si la fecha de inicio es anterior, actual o futura
      const hoy = new Date();
      hoy.setHours(0, 0, 0, 0);
      fechaBase.setHours(0, 0, 0, 0);
      
      let estadoFecha = '';
      if (fechaBase < hoy) {
        const diasPasados = Math.floor((hoy - fechaBase) / (1000 * 60 * 60 * 24));
        estadoFecha = ` (hace ${diasPasados} días)`;
      } else if (fechaBase > hoy) {
        const diasFuturos = Math.floor((fechaBase - hoy) / (1000 * 60 * 60 * 24));
        estadoFecha = ` (en ${diasFuturos} días)`;
      } else {
        estadoFecha = ' (hoy)';
      }
      
      // Determinar el estado de la membresía
      let estadoMembresia = '';
      const fechaVencimientoTime = fechaVencimiento.getTime();
      const hoyTime = hoy.getTime();
      
      if (fechaVencimientoTime < hoyTime) {
        const diasVencidos = Math.floor((hoyTime - fechaVencimientoTime) / (1000 * 60 * 60 * 24));
        estadoMembresia = `<span style="color: #e74c3c;">⚠️ Vencida hace ${diasVencidos} días</span>`;
      } else if (fechaVencimientoTime === hoyTime) {
        estadoMembresia = '<span style="color: #f39c12;">⏰ Vence hoy</span>';
      } else {
        const diasRestantes = Math.floor((fechaVencimientoTime - hoyTime) / (1000 * 60 * 60 * 24));
        if (diasRestantes <= 7) {
          estadoMembresia = `<span style="color: #f39c12;">⚠️ Vence en ${diasRestantes} días</span>`;
        } else {
          estadoMembresia = `<span style="color: #27ae60;">✅ Vigente por ${diasRestantes} días</span>`;
        }
      }
      
      // Mostrar información
      let infoElement = document.getElementById('info-vencimiento');
      if (!infoElement) {
        infoElement = document.createElement('div');
        infoElement.id = 'info-vencimiento';
        infoElement.style.cssText = 'background: #e8f5e8; padding: 10px; border-radius: 6px; margin-top: 10px; border-left: 4px solid #27ae60; font-size: 0.9em;';
        document.querySelector('input[name="fecha_inicio"]').parentNode.appendChild(infoElement);
      }
      
      const fechaInicioTexto = fechaInicio ? 
        new Date(fechaInicio).toLocaleDateString('es-ES', opciones) + estadoFecha : 
        'hoy (' + new Date().toLocaleDateString('es-ES', opciones) + ')';
      
      infoElement.innerHTML = `
        <strong>📅 Vista previa de membresía:</strong><br>
        • Inicio: ${fechaInicioTexto}<br>
        • Vencimiento: ${fechaFormateada}<br>
        • Duración: ${diasAgregar} días (${modalidad})<br>
        • Estado: ${estadoMembresia}
      `;
    }
    
    // Agregar event listeners cuando se carga la página
    document.addEventListener('DOMContentLoaded', function() {
      const modalidadSelect = document.querySelector('select[name="modalidad"]');
      const fechaInicioInput = document.querySelector('input[name="fecha_inicio"]');
      
      if (modalidadSelect) {
        modalidadSelect.addEventListener('change', calcularVencimiento);
      }
      
      if (fechaInicioInput) {
        fechaInicioInput.addEventListener('change', calcularVencimiento);
      }
      
      // Permitir fechas anteriores y futuras (sin restricción de fecha mínima)
      // Esto permite registrar membresías que ya estaban activas desde antes
      
      // ========== FUNCIONALIDAD PLAN FAMILIAR ADMIN ==========
      
      // Función para mostrar/ocultar selección de miembros familia cuando se elige Plan Familiar
      function toggleFamilySelectionAdmin() {
        const modalidadAdmin = document.getElementById('modalidad-admin');
        const modalidadAdminMain = document.getElementById('modalidad-admin-main');
        const familyContainer = document.getElementById('family-selection-container-admin');
        const familyContainerMain = document.getElementById('family-selection-container-admin-main');
        
        // Obtener el valor de cualquiera de los dos selects que exista
        const modalidadValue = (modalidadAdmin && modalidadAdmin.value) || (modalidadAdminMain && modalidadAdminMain.value);
        
        // Mostrar/ocultar el contenedor apropiado
        if (familyContainer) {
          familyContainer.style.display = modalidadValue === 'plan_familiar' ? 'block' : 'none';
        }
        if (familyContainerMain) {
          familyContainerMain.style.display = modalidadValue === 'plan_familiar' ? 'block' : 'none';
        }
        
        if (modalidadValue === 'plan_familiar') {
          loadFamilyMembersAdmin();
        }
      }
      
      // Función para cargar miembros existentes con apellidos similares
      function loadFamilyMembersAdmin() {
        const nombre = document.querySelector('input[name="nombre"]').value.trim();
        if (!nombre) return;
        
        // Extraer apellido (última palabra del nombre)
        const apellido = nombre.split(' ').pop();
        if (!apellido) return;
        
        // Obtener miembros con apellidos similares
        fetch('/buscar_familia?apellido=' + encodeURIComponent(apellido))
          .then(response => response.json())
          .then(data => {
            const container = document.getElementById('family-members-list-admin');
            const containerMain = document.getElementById('family-members-list-admin-main');
            
            // Función para crear el contenido
            function createFamilyContent(targetContainer) {
              if (targetContainer && data.miembros) {
                targetContainer.innerHTML = '';
                
                if (data.miembros.length > 0) {
                  const title = document.createElement('h4');
                  title.textContent = 'Miembros con apellidos similares:';
                  title.style.color = '#2c3e50';
                  title.style.marginBottom = '10px';
                  targetContainer.appendChild(title);
                  
                  data.miembros.forEach(miembro => {
                    const div = document.createElement('div');
                    div.style.cssText = 'background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 10px; margin: 5px 0; cursor: pointer;';
                    
                    div.innerHTML = `
                      <input type="checkbox" name="miembros_familia" value="${miembro.id}" style="margin-right: 10px;">
                      <strong>${miembro.nombre}</strong> - 
                      ${miembro.modalidad} - Registrado: ${miembro.fecha_registro}
                    `;
                    
                    targetContainer.appendChild(div);
                  });
                } else {
                  targetContainer.innerHTML = '<p style="color: #7f8c8d; font-style: italic;">No se encontraron miembros con apellidos similares.</p>';
                }
              }
            }
            
            // Crear contenido en ambos contenedores
            createFamilyContent(container);
            createFamilyContent(containerMain);
          })
          .catch(error => {
            console.log('Error al buscar familia:', error);
          });
      }
      
      // Event listeners para el admin
      const modalidadAdmin = document.getElementById('modalidad-admin');
      const modalidadAdminMain = document.getElementById('modalidad-admin-main');
      const nombreAdmin = document.getElementById('nombre-admin');
      
      if (modalidadAdmin) {
        modalidadAdmin.addEventListener('change', toggleFamilySelectionAdmin);
      }
      
      if (modalidadAdminMain) {
        modalidadAdminMain.addEventListener('change', toggleFamilySelectionAdmin);
      }
      
      if (nombreAdmin) {
        nombreAdmin.addEventListener('blur', function() {
          const modalidadValue = (modalidadAdmin && modalidadAdmin.value) || (modalidadAdminMain && modalidadAdminMain.value);
          if (modalidadValue === 'plan_familiar') {
            loadFamilyMembersAdmin();
          }
        });
      }
      
    });
  </script>
</body>
</html>
""", total_miembros=total_miembros, miembros_activos=miembros_activos, 
     miembros_vencidos=miembros_vencidos, pagos=pagos, miembros_s=miembros_s,
     logo_fn=logo_fn, ingresos_hoy=ingresos_hoy, BASE_STYLES=BASE_STYLES)

@app.route("/ver_plan_familiar/<int:plan_id>")
def ver_plan_familiar(plan_id):
    """Ver detalles de un plan familiar específico"""
    if session.get("rol") not in ["admin", "moderador"]:
        flash("Acceso denegado.")
        return redirect("/login")
    
    con = conectar()
    
    # Obtener información del plan
    plan = con.execute("""
        SELECT id, nombre_plan, fecha_creacion, vigencia, activo
        FROM planes_familiares 
        WHERE id=?
    """, (plan_id,)).fetchone()
    
    if not plan:
        flash("Plan familiar no encontrado.")
        return redirect("/gestionar_familias")
    
    # Obtener miembros del plan
    miembros = con.execute("""
        SELECT u.id, u.nombre, u.usuario, u.modalidad, u.vigencia, 
               mf.fecha_vinculacion, mf.activo as vinculo_activo
        FROM miembros_familia mf
        JOIN usuarios u ON mf.miembro_id = u.id
        WHERE mf.plan_familiar_id = ?
        ORDER BY mf.fecha_vinculacion ASC
    """, (plan_id,)).fetchall()
    
    logo_row = con.execute("SELECT filename FROM logo ORDER BY id DESC LIMIT 1").fetchone()
    logo_fn = logo_row[0] if logo_row else ""
    con.close()
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Plan Familiar - LAMA Control</title>
  {{ BASE_STYLES|safe }}
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>{{ 'ADMIN' if session['rol']=='admin' else 'MODERADOR' }} PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="{{ '/admin' if session['rol']=='admin' else '/moderador' }}"><i>🏠</i> Panel Principal</a></li>
        <li><a href="/gestionar_familias"><i>👨‍👩‍👧‍👦</i> Gestión de Familias</a></li>
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header">
        <h1>👨‍👩‍👧‍👦 {{ plan[1] }}</h1>
        <div class="breadcrumb">
          <a href="/gestionar_familias">Gestión de Familias</a> > Plan Familiar
        </div>
      </div>

      <div class="content-body">
        <!-- Información del Plan -->
        <div class="card" style="margin-bottom: 30px;">
          <div class="card-header">
            <h3 class="card-title">📋 Información del Plan</h3>
          </div>
          <div style="padding: 20px;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
              <div>
                <strong>Nombre del Plan:</strong><br>
                <span style="color: #2c3e50; font-size: 1.1em;">{{ plan[1] }}</span>
              </div>
              <div>
                <strong>Fecha de Creación:</strong><br>
                <span style="color: #7f8c8d;">{{ plan[2] }}</span>
              </div>
              <div>
                <strong>Vigencia del Plan:</strong><br>
                <span style="color: #3498db;">{{ plan[3] }}</span>
              </div>
              <div>
                <strong>Estado:</strong><br>
                {% if plan[4] %}
                  <span style="color: #27ae60; font-weight: 600;">✅ Activo</span>
                {% else %}
                  <span style="color: #e74c3c; font-weight: 600;">❌ Inactivo</span>
                {% endif %}
              </div>
            </div>
          </div>
        </div>

        <!-- Miembros del Plan -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">👥 Miembros del Plan ({{ miembros|length }})</h3>
          </div>
          {% if miembros %}
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Usuario</th>
                <th>Modalidad Individual</th>
                <th>Vigencia Individual</th>
                <th>Fecha Vinculación</th>
                <th>Estado Vínculo</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {% for id, nombre, usuario, modalidad, vigencia, fecha_vinc, vinculo_activo in miembros %}
              <tr>
                <td>{{ nombre }}</td>
                <td>{{ usuario }}</td>
                <td>{{ modalidad }}</td>
                <td>{{ vigencia }}</td>
                <td>{{ fecha_vinc }}</td>
                <td>
                  {% if vinculo_activo %}
                    <span style="color: #27ae60; font-weight: 600;">✅ Activo</span>
                  {% else %}
                    <span style="color: #e74c3c; font-weight: 600;">❌ Inactivo</span>
                  {% endif %}
                </td>
                <td>
                  <a href="/editar_miembro_por_id/{{ id }}" class="btn" style="padding: 5px 10px; font-size: 0.8em; background: #3498db;">✏️ Editar</a>
                  {% if vinculo_activo %}
                    <form method="POST" action="/desvincular_miembro" style="display: inline; margin-left: 5px;">
                      <input type="hidden" name="plan_id" value="{{ plan[0] }}">
                      <input type="hidden" name="miembro_id" value="{{ id }}">
                      <button type="submit" class="btn" style="background: #f39c12; padding: 5px 10px; font-size: 0.8em;" onclick="return confirm('¿Desvincular temporalmente este miembro del plan familiar?')">⏸️ Desvincular</button>
                    </form>
                    <form method="POST" action="/eliminar_miembro_plan" style="display: inline; margin-left: 5px;">
                      <input type="hidden" name="plan_id" value="{{ plan[0] }}">
                      <input type="hidden" name="miembro_id" value="{{ id }}">
                      <button type="submit" class="btn" style="background: #e74c3c; padding: 5px 10px; font-size: 0.8em;" onclick="return confirm('¿ELIMINAR PERMANENTEMENTE este miembro del plan familiar? Esta acción no se puede deshacer.')">🗑️ Eliminar</button>
                    </form>
                  {% endif %}
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
          {% else %}
          <div style="padding: 20px; text-align: center; color: #666;">
            No hay miembros vinculados a este plan familiar.
          </div>
          {% endif %}
        </div>

        <!-- Agregar Nuevo Miembro -->
        {% if plan[4] %}
        <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px;">
          <h4 style="margin-bottom: 15px; color: #333;">➕ Agregar Nuevo Miembro</h4>
          <form method="POST" action="/agregar_miembro_plan" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
            <input type="hidden" name="plan_id" value="{{ plan[0] }}">
            <input type="text" name="query" placeholder="Buscar miembro por nombre o PIN..." 
                   style="flex: 1; min-width: 200px; padding: 8px; border: 1px solid #ddd; border-radius: 4px;"
                   onkeyup="buscarMiembrosParaFamilia(this.value, {{ plan[0] }})">
            <div id="resultados-miembros-familia" style="position: absolute; background: white; border: 1px solid #ddd; 
                 border-radius: 4px; max-height: 200px; overflow-y: auto; z-index: 1000; display: none; min-width: 200px;"></div>
          </form>
          <p style="font-size: 12px; color: #666; margin-top: 5px;">
            <strong>Nota:</strong> Solo se pueden agregar miembros con el mismo apellido ({{ plan[1].split(' - ')[0] }})
          </p>
        </div>
        {% endif %}

        <!-- Acciones del Plan -->
        <div style="margin-top: 30px; text-align: center;">
          <a href="/gestionar_familias" class="btn" style="background: #95a5a6; margin-right: 10px;">← Volver a Gestión de Familias</a>
          {% if plan[4] %}
            <form method="POST" action="/desactivar_plan_familiar" style="display: inline; margin-left: 10px;">
              <input type="hidden" name="plan_id" value="{{ plan[0] }}">
              <button type="submit" class="btn" style="background: #e74c3c;" onclick="return confirm('¿Desactivar este plan familiar?')">❌ Desactivar Plan</button>
            </form>
          {% else %}
            <form method="POST" action="/activar_plan_familiar" style="display: inline; margin-left: 10px;">
              <input type="hidden" name="plan_id" value="{{ plan[0] }}">
              <button type="submit" class="btn" style="background: #27ae60;">✅ Activar Plan</button>
            </form>
          {% endif %}
          <form method="POST" action="/eliminar_plan_familiar" style="display: inline; margin-left: 10px;">
            <input type="hidden" name="plan_id" value="{{ plan[0] }}">
            <button type="submit" class="btn" style="background: #c0392b;" onclick="return confirm('¿ELIMINAR PERMANENTEMENTE este plan familiar? Esta acción no se puede deshacer y todos los miembros volverán a modalidad individual.')">🗑️ Eliminar Plan</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
""", plan=plan, miembros=miembros, logo_fn=logo_fn, BASE_STYLES=BASE_STYLES)

@app.route("/desvincular_miembro", methods=["POST"])
def desvincular_miembro():
    """Desvincular un miembro de un plan familiar"""
    if session.get("rol") not in ["admin", "moderador"]:
        flash("Acceso denegado.")
        return redirect("/login")
    
    plan_id = request.form.get("plan_id")
    miembro_id = request.form.get("miembro_id")
    
    con = conectar()
    
    # Marcar el vínculo como inactivo
    con.execute("""
        UPDATE miembros_familia 
        SET activo = 0, fecha_desvinculacion = ?
        WHERE plan_familiar_id = ? AND miembro_id = ? AND activo = 1
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), plan_id, miembro_id))
    
    # Cambiar modalidad del miembro de vuelta a individual con vigencia desde hoy
    fecha_desvinculacion = datetime.now().strftime("%Y-%m-%d")
    con.execute("""
        UPDATE usuarios 
        SET modalidad = 'mensual', vigencia = ?
        WHERE id = ?
    """, (calcular_vigencia("mensual", fecha_desvinculacion), miembro_id))
    
    con.commit()
    con.close()
    
    flash("Miembro desvinculado del plan familiar exitosamente.")
    return redirect(f"/ver_plan_familiar/{plan_id}")

@app.route("/eliminar_miembro_plan", methods=["POST"])
def eliminar_miembro_plan():
    """Eliminar permanentemente un miembro de un plan familiar"""
    if session.get("rol") not in ["admin", "moderador"]:
        flash("Acceso denegado.")
        return redirect("/login")
    
    plan_id = request.form.get("plan_id")
    miembro_id = request.form.get("miembro_id")
    
    con = conectar()
    
    # Verificar que el plan y miembro existen
    plan_existe = con.execute("SELECT id FROM planes_familiares WHERE id=?", (plan_id,)).fetchone()
    miembro_existe = con.execute("SELECT id FROM usuarios WHERE id=?", (miembro_id,)).fetchone()
    
    if not plan_existe or not miembro_existe:
        flash("Plan familiar o miembro no encontrado.")
        con.close()
        return redirect("/gestionar_familias")
    
    # Eliminar completamente del plan familiar
    con.execute("""
        DELETE FROM miembros_familia 
        WHERE plan_familiar_id = ? AND miembro_id = ?
    """, (plan_id, miembro_id))
    
    # Cambiar modalidad del miembro de vuelta a individual con vigencia desde hoy
    fecha_eliminacion = datetime.now().strftime("%Y-%m-%d")
    con.execute("""
        UPDATE usuarios 
        SET modalidad = 'mensual', vigencia = ?
        WHERE id = ?
    """, (calcular_vigencia("mensual", fecha_eliminacion), miembro_id))
    
    # Verificar si el plan se queda sin miembros activos
    miembros_restantes = con.execute("""
        SELECT COUNT(*) FROM miembros_familia 
        WHERE plan_familiar_id = ? AND activo = 1
    """, (plan_id,)).fetchone()[0]
    
    if miembros_restantes == 0:
        # Desactivar el plan si no tiene miembros
        con.execute("""
            UPDATE planes_familiares 
            SET activo = 0 
            WHERE id = ?
        """, (plan_id,))
        flash("Miembro eliminado del plan. El plan familiar ha sido desactivado por falta de miembros.")
    else:
        flash("Miembro eliminado del plan familiar exitosamente.")
    
    con.commit()
    con.close()
    
    return redirect(f"/ver_plan_familiar/{plan_id}")

@app.route("/agregar_miembro_plan", methods=["POST"])
def agregar_miembro_plan():
    """Agregar un miembro adicional a un plan familiar existente"""
    if session.get("rol") not in ["admin", "moderador"]:
        flash("Acceso denegado.")
        return redirect("/login")
    
    plan_id = request.form.get("plan_id")
    miembro_id = request.form.get("miembro_id")
    
    print(f"DEBUG agregar_miembro_plan: Iniciando con plan_id={plan_id}, miembro_id={miembro_id}")
    
    # Validación de entrada
    if not plan_id or not miembro_id:
        flash("Error: Datos incompletos.")
        print("DEBUG agregar_miembro_plan: ERROR - Datos incompletos")
        return redirect("/gestionar_familias")
    
    con = conectar()
    
    try:
        # Verificar que el plan existe y está activo
        plan = con.execute("SELECT nombre_plan FROM planes_familiares WHERE id=? AND activo=1", (plan_id,)).fetchone()
        if not plan:
            flash("Plan familiar no encontrado o inactivo.")
            print(f"DEBUG agregar_miembro_plan: ERROR - Plan {plan_id} no encontrado o inactivo")
            con.close()
            return redirect("/gestionar_familias")
        
        print(f"DEBUG agregar_miembro_plan: Plan encontrado: {plan[0]}")
        
        # Verificar que el miembro existe y no está ya en un plan familiar
        miembro = con.execute("SELECT nombre, modalidad FROM usuarios WHERE id=? AND rol='miembro'", (miembro_id,)).fetchone()
        if not miembro:
            flash("Miembro no encontrado.")
            print(f"DEBUG agregar_miembro_plan: ERROR - Miembro {miembro_id} no encontrado")
            con.close()
            return redirect(f"/ver_plan_familiar/{plan_id}")
        
        print(f"DEBUG agregar_miembro_plan: Miembro encontrado: {miembro[0]}, modalidad: {miembro[1]}")
        
        if miembro[1] == 'plan_familiar':
            flash("El miembro ya pertenece a un plan familiar.")
            print(f"DEBUG agregar_miembro_plan: ERROR - Miembro ya en plan familiar")
            con.close()
            return redirect(f"/ver_plan_familiar/{plan_id}")
        
        # Verificar si ya está en miembros_familia (por si acaso)
        miembro_existente = con.execute("""
            SELECT COUNT(*) FROM miembros_familia 
            WHERE miembro_id = ? AND activo = 1
        """, (miembro_id,)).fetchone()
        
        if miembro_existente[0] > 0:
            flash("El miembro ya está asociado a otro plan familiar.")
            print(f"DEBUG agregar_miembro_plan: ERROR - Miembro ya en miembros_familia")
            con.close()
            return redirect(f"/ver_plan_familiar/{plan_id}")
        
        # Obtener apellido del miembro
        apellido_nuevo = miembro[0].split()[-1].lower() if miembro[0] else ""
        print(f"DEBUG agregar_miembro_plan: Apellido nuevo miembro: {apellido_nuevo}")
        
        # Verificar que el apellido coincida con los miembros del plan
        miembros_plan = con.execute("""
            SELECT u.nombre FROM usuarios u
            JOIN miembros_familia mf ON u.id = mf.miembro_id
            WHERE mf.plan_familiar_id = ? AND mf.activo = 1
            LIMIT 1
        """, (plan_id,)).fetchone()
        
        if miembros_plan:
            apellido_plan = miembros_plan[0].split()[-1].lower() if miembros_plan[0] else ""
            print(f"DEBUG agregar_miembro_plan: Apellido del plan: {apellido_plan}")
            if apellido_nuevo != apellido_plan:
                flash(f"El miembro debe tener el mismo apellido que la familia ({apellido_plan.title()}).")
                print(f"DEBUG agregar_miembro_plan: ERROR - Apellidos no coinciden: {apellido_nuevo} vs {apellido_plan}")
                con.close()
                return redirect(f"/ver_plan_familiar/{plan_id}")
        
        # Agregar miembro al plan
        fecha_vinculacion = datetime.now().strftime("%Y-%m-%d")
        print(f"DEBUG agregar_miembro_plan: Insertando en miembros_familia...")
        
        cursor = con.execute("""
            INSERT INTO miembros_familia (plan_familiar_id, miembro_id, fecha_vinculacion, activo)
            VALUES (?, ?, ?, 1)
        """, (plan_id, miembro_id, fecha_vinculacion))
        
        print(f"DEBUG agregar_miembro_plan: Rows affected by INSERT: {cursor.rowcount}")
        
        # Actualizar modalidad del miembro
        print(f"DEBUG agregar_miembro_plan: Actualizando modalidad del usuario...")
        cursor = con.execute("""
            UPDATE usuarios 
            SET modalidad = 'plan_familiar', vigencia = (
                SELECT vigencia FROM planes_familiares WHERE id = ?
            )
            WHERE id = ?
        """, (plan_id, miembro_id))
        
        print(f"DEBUG agregar_miembro_plan: Rows affected by UPDATE: {cursor.rowcount}")
        
        con.commit()
        print(f"DEBUG agregar_miembro_plan: Commit realizado")
        
        # Verificar que el miembro fue agregado correctamente
        verificacion = con.execute("""
            SELECT COUNT(*) FROM miembros_familia 
            WHERE plan_familiar_id = ? AND miembro_id = ? AND activo = 1
        """, (plan_id, miembro_id)).fetchone()
        
        if verificacion[0] == 0:
            print(f"DEBUG agregar_miembro_plan: ERROR - Verificación falló, miembro no encontrado en tabla")
            flash("Error: No se pudo verificar que el miembro fue agregado correctamente.")
            con.close()
            return redirect(f"/ver_plan_familiar/{plan_id}")
        
        # Verificar actualización de modalidad
        usuario_actualizado = con.execute("""
            SELECT modalidad FROM usuarios WHERE id = ?
        """, (miembro_id,)).fetchone()
        
        if not usuario_actualizado or usuario_actualizado[0] != 'plan_familiar':
            print(f"DEBUG agregar_miembro_plan: ERROR - Modalidad no actualizada correctamente")
            flash("Advertencia: El miembro fue agregado pero puede haber problemas con la modalidad.")
        
        print(f"DEBUG agregar_miembro_plan: Miembro agregado exitosamente - Verificaciones pasadas")
        con.close()
        
        flash(f"Miembro {miembro[0]} agregado exitosamente al plan familiar.")
        return redirect(f"/ver_plan_familiar/{plan_id}")
        
    except Exception as e:
        print(f"DEBUG agregar_miembro_plan: EXCEPTION - {str(e)}")
        try:
            con.rollback()
            print(f"DEBUG agregar_miembro_plan: Rollback realizado")
        except:
            pass
        con.close()
        flash("Error interno al agregar el miembro.")
        return redirect(f"/ver_plan_familiar/{plan_id}")

@app.route("/desactivar_plan_familiar", methods=["POST"])
def desactivar_plan_familiar():
    """Desactivar un plan familiar"""
    if session.get("rol") not in ["admin", "moderador"]:
        flash("Acceso denegado.")
        return redirect("/login")
    
    plan_id = request.form.get("plan_id")
    
    con = conectar()
    con.execute("UPDATE planes_familiares SET activo = 0 WHERE id = ?", (plan_id,))
    con.commit()
    con.close()
    
    flash("Plan familiar desactivado.")
    return redirect("/gestionar_familias")

@app.route("/activar_plan_familiar", methods=["POST"])
def activar_plan_familiar():
    """Activar un plan familiar"""
    if session.get("rol") not in ["admin", "moderador"]:
        flash("Acceso denegado.")
        return redirect("/login")
    
    plan_id = request.form.get("plan_id")
    
    con = conectar()
    con.execute("UPDATE planes_familiares SET activo = 1 WHERE id = ?", (plan_id,))
    con.commit()
    con.close()
    
    flash("Plan familiar activado.")
    return redirect("/gestionar_familias")

@app.route("/eliminar_plan_familiar", methods=["POST"])
def eliminar_plan_familiar():
    """Eliminar permanentemente un plan familiar"""
    if session.get("rol") not in ["admin", "moderador"]:
        flash("Acceso denegado.")
        return redirect("/login")
    
    plan_id = request.form.get("plan_id")
    
    con = conectar()
    
    # Verificar que el plan existe
    plan = con.execute("SELECT nombre_plan FROM planes_familiares WHERE id=?", (plan_id,)).fetchone()
    if not plan:
        flash("Plan familiar no encontrado.")
        con.close()
        return redirect("/gestionar_familias")
    
    # Obtener miembros del plan para cambiar su modalidad
    miembros = con.execute("""
        SELECT miembro_id FROM miembros_familia 
        WHERE plan_familiar_id = ? AND activo = 1
    """, (plan_id,)).fetchall()
    
    # Cambiar modalidad de todos los miembros de vuelta a individual con vigencia desde hoy
    fecha_eliminacion = datetime.now().strftime("%Y-%m-%d")
    for miembro in miembros:
        con.execute("""
            UPDATE usuarios 
            SET modalidad = 'mensual', vigencia = ?
            WHERE id = ?
        """, (calcular_vigencia("mensual", fecha_eliminacion), miembro[0]))
    
    # Eliminar todas las vinculaciones
    con.execute("DELETE FROM miembros_familia WHERE plan_familiar_id = ?", (plan_id,))
    
    # Eliminar el plan familiar
    con.execute("DELETE FROM planes_familiares WHERE id = ?", (plan_id,))
    
    con.commit()
    con.close()
    
    flash(f"Plan familiar '{plan[0]}' eliminado permanentemente.")
    return redirect("/gestionar_familias")

@app.route("/gestionar_miembros")
def gestionar_miembros():
    """Página dedicada para gestionar miembros con búsqueda y filtros"""
    if session.get("rol") != "admin":
        flash("Acceso denegado. Solo los administradores pueden gestionar miembros.")
        return redirect("/login")
    
    con = conectar()
    
    # Obtener todos los miembros con información completa
    miembros = con.execute("""
        SELECT id, nombre, usuario, pin, nip, modalidad, vigencia, foto,
               correo, telefono_emergencia, datos_medicos, fecha_registro
        FROM usuarios 
        WHERE rol='miembro' 
        ORDER BY nombre ASC
    """).fetchall()
    
    # Obtener sugerencias familiares automáticamente
    detectar_apellidos_similares()
    sugerencias_count = con.execute("""
        SELECT COUNT(*) FROM sugerencias_familia WHERE estado='pendiente'
    """).fetchone()[0]
    
    # Obtener estadísticas
    total_miembros = len(miembros)
    miembros_activos = len([m for m in miembros if dias_restantes(m[6]) >= 0])
    miembros_vencidos = total_miembros - miembros_activos
    
    logo_row = con.execute("SELECT filename FROM logo ORDER BY id DESC LIMIT 1").fetchone()
    logo_fn = logo_row[0] if logo_row else ""
    con.close()
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Gestión de Miembros - LAMA Control</title>
  {{ BASE_STYLES|safe }}
  <style>
    .miembro-row { transition: background-color 0.2s ease; }
    .miembro-row:hover { background-color: #f8f9fa; }
    .miembro-row.oculto { display: none; }
    .estado-activo { color: #27ae60; font-weight: 600; }
    .estado-vencido { color: #e74c3c; font-weight: 600; }
    .estado-por-vencer { color: #f39c12; font-weight: 600; }
    .filtro-container { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); }
    .badge-familiar { background: #8e44ad; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.7em; }
  </style>
</head>
<body>
  <div class="layout-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>{{ 'ADMIN' if session['rol']=='admin' else 'MODERADOR' }} PANEL</h3>
        {% if logo_fn %}
          <img src="{{ url_for('static', filename='logo/'+logo_fn) }}" class="sidebar-logo">
        {% endif %}
      </div>
      <ul class="sidebar-nav">
        <li><a href="{{ '/admin' if session['rol']=='admin' else '/moderador' }}"><i>🏠</i> Panel Principal</a></li>
        <li><a href="/gestionar_miembros" class="active"><i>👥</i> Gestión de Miembros</a></li>
        <li><a href="/gestionar_familias"><i>👨‍👩‍👧‍👦</i> Gestión de Familias</a></li>
        {% if sugerencias_count > 0 %}
          <li><a href="/gestionar_familias" style="position: relative;"><i>🔔</i> Sugerencias <span style="background: #e74c3c; color: white; border-radius: 50%; padding: 2px 6px; font-size: 0.7em; position: absolute; top: -5px; right: -5px;">{{ sugerencias_count }}</span></a></li>
        {% endif %}
        <li><a href="/logout"><i>🚪</i> Cerrar Sesión</a></li>
      </ul>
    </div>

    <div class="main-content">
      <div class="content-header">
        <h1>👥 Gestión de Miembros</h1>
        <div class="breadcrumb">Panel {{ 'Admin' if session['rol']=='admin' else 'Moderador' }} > Gestión de Miembros</div>
      </div>

      <div class="content-body">
        <!-- Estadísticas -->
        <div class="stats-grid" style="margin-bottom: 30px;">
          <div class="stat-card">
            <div class="stat-number">{{ total_miembros }}</div>
            <div class="stat-label">Total Miembros</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);">
            <div class="stat-number">{{ miembros_activos }}</div>
            <div class="stat-label">Miembros Activos</div>
          </div>
          <div class="stat-card" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">
            <div class="stat-number">{{ miembros_vencidos }}</div>
            <div class="stat-label">Miembros Vencidos</div>
          </div>
        </div>

        <!-- Filtros y búsqueda -->
        <div class="card filtro-container" style="margin-bottom: 30px;">
          <div class="card-header">
            <h3 class="card-title">🔍 Filtros y Búsqueda</h3>
          </div>
          <div style="padding: 20px;">
            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr auto; gap: 15px; align-items: end;">
              <div class="form-group" style="margin: 0;">
                <label class="form-label">Buscar miembro</label>
                <input type="text" id="buscar-miembro" placeholder="Buscar por nombre, usuario, NIP o teléfono..." style="width: 100%;" oninput="aplicarFiltros()">
              </div>
              <div class="form-group" style="margin: 0;">
                <label class="form-label">Modalidad</label>
                <select id="filtro-modalidad" onchange="aplicarFiltros()" style="width: 100%;">
                  <option value="">Todas</option>
                  <option value="mensual">Mensual</option>
                  <option value="semanal">Semanal</option>
                  <option value="diario">Diario</option>
                  <option value="plan_familiar">Plan Familiar</option>
                </select>
              </div>
              <div class="form-group" style="margin: 0;">
                <label class="form-label">Estado</label>
                <select id="filtro-estado" onchange="aplicarFiltros()" style="width: 100%;">
                  <option value="">Todos</option>
                  <option value="activo">Activos</option>
                  <option value="vencido">Vencidos</option>
                  <option value="por-vencer">Por vencer (7 días)</option>
                </select>
              </div>
              <div class="form-group" style="margin: 0;">
                <label class="form-label">Ordenar por</label>
                <select id="ordenar-por" onchange="aplicarFiltros()" style="width: 100%;">
                  <option value="nombre">Nombre</option>
                  <option value="fecha">Fecha registro</option>
                  <option value="vigencia">Vigencia</option>
                  <option value="modalidad">Modalidad</option>
                </select>
              </div>
              <button type="button" onclick="limpiarFiltros()" class="btn" style="background: #95a5a6; padding: 8px 15px;">🗑️ Limpiar</button>
            </div>
          </div>
        </div>

        <!-- Lista de miembros -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">👥 Lista de Miembros</h3>
            <div style="color: #666; font-size: 0.9em;">
              Mostrando <span id="contador-visible">{{ total_miembros }}</span> de {{ total_miembros }} miembros
            </div>
          </div>
          <table id="tabla-miembros">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Usuario</th>
                <th>NIP</th>
                <th>Modalidad</th>
                <th>Vigencia</th>
                <th>Estado</th>
                <th>Contacto</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {% for id, nombre, usuario, pin, nip, modalidad, vigencia, foto, correo, telefono, datos_medicos, fecha_registro in miembros %}
              {% set dias = vigencia|dias_restantes %}
              <tr class="miembro-row" 
                  data-nombre="{{ nombre|lower }}" 
                  data-usuario="{{ usuario|lower }}" 
                  data-nip="{{ nip }}" 
                  data-modalidad="{{ modalidad }}"
                  data-telefono="{{ telefono or '' }}"
                  data-dias="{{ dias }}"
                  data-fecha="{{ fecha_registro }}">
                <td>
                  <div style="display: flex; align-items: center; gap: 10px;">
                    {% if foto %}
                      <img src="{{ url_for('static', filename='fotos/'+foto) }}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 2px solid #ddd;">
                    {% else %}
                      <div style="width: 40px; height: 40px; border-radius: 50%; background: #3498db; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold;">{{ nombre[0] }}</div>
                    {% endif %}
                    <div>
                      <strong>{{ nombre }}</strong>
                      {% if modalidad == 'plan_familiar' %}
                        <span class="badge-familiar">👨‍👩‍👧‍👦 FAMILIA</span>
                      {% endif %}
                    </div>
                  </div>
                </td>
                <td>{{ usuario }}</td>
                <td><strong style="background: #ecf0f1; padding: 2px 8px; border-radius: 4px;">{{ nip }}</strong></td>
                <td>
                  <span style="text-transform: capitalize;">{{ modalidad.replace('_', ' ') }}</span>
                </td>
                <td>{{ vigencia }}</td>
                <td>
                  {% if dias < 0 %}
                    <span class="estado-vencido">❌ Vencida ({{ -dias }}d)</span>
                  {% elif dias <= 7 %}
                    <span class="estado-por-vencer">⚠️ {{ dias }}d restantes</span>
                  {% else %}
                    <span class="estado-activo">✅ Vigente ({{ dias }}d)</span>
                  {% endif %}
                </td>
                <td>
                  {% if telefono %}
                    <div style="font-size: 0.8em;">📞 {{ telefono }}</div>
                  {% endif %}
                  {% if correo %}
                    <div style="font-size: 0.8em;">📧 {{ correo }}</div>
                  {% endif %}
                  {% if not telefono and not correo %}
                    <span style="color: #999;">Sin contacto</span>
                  {% endif %}
                </td>
                <td>
                  <div style="display: flex; gap: 5px; flex-wrap: wrap;">
                    <a href="/editar_miembro_por_id/{{ id }}" class="btn" style="padding: 4px 8px; font-size: 0.75em; background: #3498db;">✏️ Editar</a>
                    <a href="/detalle_miembro/{{ usuario }}" class="btn" style="padding: 4px 8px; font-size: 0.75em; background: #27ae60;">👁️ Ver</a>
                  </div>
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <script>
    function aplicarFiltros() {
      const busqueda = document.getElementById('buscar-miembro').value.toLowerCase();
      const modalidad = document.getElementById('filtro-modalidad').value;
      const estado = document.getElementById('filtro-estado').value;
      const ordenar = document.getElementById('ordenar-por').value;
      
      const filas = Array.from(document.querySelectorAll('.miembro-row'));
      let filasVisibles = 0;
      
      // Aplicar filtros
      filas.forEach(fila => {
        let mostrar = true;
        
        // Filtro de búsqueda
        if (busqueda) {
          const nombre = fila.dataset.nombre || '';
          const usuario = fila.dataset.usuario || '';
          const nip = fila.dataset.nip || '';
          const telefono = fila.dataset.telefono || '';
          
          if (!nombre.includes(busqueda) && 
              !usuario.includes(busqueda) && 
              !nip.includes(busqueda) && 
              !telefono.includes(busqueda)) {
            mostrar = false;
          }
        }
        
        // Filtro de modalidad
        if (modalidad && fila.dataset.modalidad !== modalidad) {
          mostrar = false;
        }
        
        // Filtro de estado
        if (estado) {
          const dias = parseInt(fila.dataset.dias);
          if (estado === 'activo' && dias < 0) mostrar = false;
          if (estado === 'vencido' && dias >= 0) mostrar = false;
          if (estado === 'por-vencer' && (dias < 0 || dias > 7)) mostrar = false;
        }
        
        if (mostrar) {
          fila.classList.remove('oculto');
          filasVisibles++;
        } else {
          fila.classList.add('oculto');
        }
      });
      
      // Ordenar filas visibles
      const tbody = document.querySelector('#tabla-miembros tbody');
      const filasOrdenadas = filas
        .filter(fila => !fila.classList.contains('oculto'))
        .sort((a, b) => {
          switch(ordenar) {
            case 'nombre':
              return a.dataset.nombre.localeCompare(b.dataset.nombre);
            case 'fecha':
              return new Date(a.dataset.fecha) - new Date(b.dataset.fecha);
            case 'vigencia':
              return parseInt(b.dataset.dias) - parseInt(a.dataset.dias);
            case 'modalidad':
              return a.dataset.modalidad.localeCompare(b.dataset.modalidad);
            default:
              return 0;
          }
        });
      
      // Reorganizar filas en la tabla
      const filasOcultas = filas.filter(fila => fila.classList.contains('oculto'));
      [...filasOrdenadas, ...filasOcultas].forEach(fila => tbody.appendChild(fila));
      
      // Actualizar contador
      document.getElementById('contador-visible').textContent = filasVisibles;
    }
    
    function limpiarFiltros() {
      document.getElementById('buscar-miembro').value = '';
      document.getElementById('filtro-modalidad').value = '';
      document.getElementById('filtro-estado').value = '';
      document.getElementById('ordenar-por').value = 'nombre';
      aplicarFiltros();
    }
    
    // Aplicar filtros al cargar la página
    document.addEventListener('DOMContentLoaded', function() {
      aplicarFiltros();
    });
    
    // Función para actualizar el monto automáticamente según el concepto (Admin)
    function actualizarMontoAdmin(concepto) {
      const montoInput = document.getElementById('montoInputAdmin1');
      
      const montosAutomaticos = {
        'Mensualidad': 400.00,
        'Semana': 120.00,
        'Clase': 50.00,
        'Tres clases': 100.00,
        'Semana con Yoga': 150.00,
        'Clase de Yoga': 80.00,
        'Pareja': 700.00,
        'Tres personas': 1000.00,
        'Cuatro personas': 1300.00,
        'Cinco personas': 1600.00
      };
      
      if (montosAutomaticos[concepto]) {
        montoInput.value = montosAutomaticos[concepto].toFixed(2);
        montoInput.setAttribute('readonly', true);
        montoInput.style.backgroundColor = '#f8f9fa';
        montoInput.style.color = '#495057';
      } else {
        // Para conceptos personalizados, permitir edición manual
        montoInput.value = '';
        montoInput.removeAttribute('readonly');
        montoInput.style.backgroundColor = 'white';
        montoInput.style.color = 'black';
        montoInput.placeholder = 'Ingrese el monto personalizado';
      }
    }

    // Función para actualizar el segundo formulario admin (si existe)
    function actualizarMontoAdmin2(concepto) {
      const montoInput = document.getElementById('montoInputAdmin2');
      
      const montosAutomaticos = {
        'Mensualidad': 400.00,
        'Semana': 120.00,
        'Clase': 50.00,
        'Tres clases': 100.00,
        'Semana con Yoga': 150.00,
        'Clase de Yoga': 80.00,
        'Pareja': 700.00,
        'Tres personas': 1000.00,
        'Cuatro personas': 1300.00,
        'Cinco personas': 1600.00
      };
      
      if (montosAutomaticos[concepto]) {
        if (montoInput) {
          montoInput.value = montosAutomaticos[concepto].toFixed(2);
          montoInput.setAttribute('readonly', true);
          montoInput.style.backgroundColor = '#f8f9fa';
          montoInput.style.color = '#495057';
        }
      } else {
        // Para conceptos personalizados, permitir edición manual
        if (montoInput) {
          montoInput.value = '';
          montoInput.removeAttribute('readonly');
          montoInput.style.backgroundColor = 'white';
          montoInput.style.color = 'black';
          montoInput.placeholder = 'Ingrese el monto personalizado';
        }
      }
    }
  </script>
</body>
</html>
""", miembros=miembros, total_miembros=total_miembros, miembros_activos=miembros_activos, 
     miembros_vencidos=miembros_vencidos, sugerencias_count=sugerencias_count,
     logo_fn=logo_fn, BASE_STYLES=BASE_STYLES)

# ——— Sistema de Keep-Alive Avanzado ———
class KeepAliveSystem:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.running = False
        self.timer = None
        self.interval = 300  # 5 minutos
        self.local_url = f"http://localhost:{port}"
        self.external_url = f"http://{host}:{port}"
        
    def start(self):
        """Inicia el sistema de keep-alive"""
        self.running = True
        print(f"🔄 Sistema Keep-Alive iniciado (cada {self.interval//60} minutos)")
        self._schedule_next_ping()
        
    def stop(self):
        """Detiene el sistema de keep-alive"""
        self.running = False
        if self.timer:
            self.timer.cancel()
        print("🛑 Sistema Keep-Alive detenido")
        
    def _schedule_next_ping(self):
        """Programa el siguiente ping"""
        if self.running:
            self.timer = Timer(self.interval, self._perform_keep_alive)
            self.timer.daemon = True
            self.timer.start()
            
    def _perform_keep_alive(self):
        """Ejecuta el keep-alive"""
        if not self.running:
            return
            
        try:
            # Intentar hacer ping a localhost primero
            try:
                if REQUESTS_AVAILABLE:
                    response = requests.get(f"{self.local_url}/ping", timeout=10)
                    if response.status_code == 200:
                        print(f"✅ Keep-Alive exitoso: {datetime.now().strftime('%H:%M:%S')}")
                    else:
                        print(f"⚠️ Keep-Alive con código {response.status_code}")
                else:
                    # Si no hay requests, usar urllib
                    with urllib.request.urlopen(f"{self.local_url}/ping", timeout=10) as response:
                        if response.getcode() == 200:
                            print(f"✅ Keep-Alive exitoso (urllib): {datetime.now().strftime('%H:%M:%S')}")
                        else:
                            print(f"⚠️ Keep-Alive con código {response.getcode()}")
            except Exception as e:
                print(f"⚠️ Keep-Alive falló: {e}")
                
        except Exception as e:
            print(f"❌ Error en Keep-Alive: {e}")
        finally:
            # Programar el siguiente ping
            self._schedule_next_ping()

# Variable global para el sistema keep-alive
keep_alive_system = None

def setup_keep_alive(host, port):
    """Configura y inicia el sistema de keep-alive"""
    global keep_alive_system
    keep_alive_system = KeepAliveSystem(host, port)
    keep_alive_system.start()
    return keep_alive_system

def stop_keep_alive():
    """Detiene el sistema de keep-alive"""
    global keep_alive_system
    if keep_alive_system:
        keep_alive_system.stop()

def get_local_ip():
    """Obtiene la IP local de la máquina"""
    try:
        # Crear socket temporal para obtener IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def create_external_keep_alive_script(host, port):
    """Crea un script externo de keep-alive que puede ejecutarse independientemente"""
    script_content = f'''@echo off
REM Script de Keep-Alive para LAMAControl
REM Mantiene el servidor activo haciendo ping cada 5 minutos

echo ========================================
echo     LAMA Control Keep-Alive Script
echo ========================================
echo Servidor: http://{host}:{port}
echo Presiona Ctrl+C para detener
echo ========================================

:loop
echo [%date% %time%] Enviando keep-alive...

REM Intentar con curl si está disponible
curl -s "http://localhost:{port}/ping" >nul 2>&1
if %errorlevel%==0 (
    echo [%date% %time%] ✓ Keep-alive exitoso ^(curl^)
    goto wait
)

REM Si no hay curl, intentar con PowerShell
powershell -Command "try {{ Invoke-WebRequest -Uri 'http://localhost:{port}/ping' -TimeoutSec 10 -UseBasicParsing | Out-Null; Write-Host '[%date% %time%] ✓ Keep-alive exitoso (PowerShell)' }} catch {{ Write-Host '[%date% %time%] ✗ Keep-alive falló (PowerShell)' }}" 2>nul
if %errorlevel%==0 goto wait

REM Fallback usando ping
ping -n 1 localhost >nul 2>&1
echo [%date% %time%] ○ Ping de respaldo ejecutado

:wait
echo [%date% %time%] Esperando 5 minutos...
timeout /t 300 /nobreak >nul 2>&1
goto loop
'''
    
    script_path = os.path.join(BASE_DIR, 'keep_alive_external.bat')
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"✅ Script externo de keep-alive creado: {script_path}")
        return script_path
    except Exception as e:
        print(f"⚠️ No se pudo crear script externo: {e}")
        return None

def create_powershell_keep_alive_script(host, port):
    """Crea un script PowerShell de keep-alive más avanzado"""
    ps_content = f'''# Script PowerShell de Keep-Alive para LAMAControl
# Mantiene el servidor activo y monitorea su estado

$host_url = "http://localhost:{port}"
$external_url = "http://{host}:{port}"
$interval = 300  # 5 minutos

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LAMA Control Keep-Alive (PowerShell)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Servidor Local: $host_url" -ForegroundColor Yellow
Write-Host "Servidor Externo: $external_url" -ForegroundColor Yellow
Write-Host "Intervalo: $($interval/60) minutos" -ForegroundColor Yellow
Write-Host "Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

function Send-KeepAlive {{
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    try {{
        # Intentar localhost primero
        $response = Invoke-WebRequest -Uri "$host_url/ping" -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {{
            Write-Host "[$timestamp] ✓ Keep-alive exitoso (local)" -ForegroundColor Green
            return $true
        }}
    }} catch {{
        Write-Host "[$timestamp] ✗ Keep-alive local falló: $($_.Exception.Message)" -ForegroundColor Red
        
        # Intentar URL externa
        try {{
            $response = Invoke-WebRequest -Uri "$external_url/ping" -TimeoutSec 15 -UseBasicParsing
            if ($response.StatusCode -eq 200) {{
                Write-Host "[$timestamp] ✓ Keep-alive exitoso (externo)" -ForegroundColor Yellow
                return $true
            }}
        }} catch {{
            Write-Host "[$timestamp] ✗ Keep-alive externo falló: $($_.Exception.Message)" -ForegroundColor Red
        }}
    }}
    
    return $false
}}

# Loop principal
while ($true) {{
    $success = Send-KeepAlive
    
    if (-not $success) {{
        Write-Host "$(Get-Date -Format "yyyy-MM-dd HH:mm:ss") ⚠️ Todos los intentos fallaron" -ForegroundColor Red
    }}
    
    Write-Host "$(Get-Date -Format "yyyy-MM-dd HH:mm:ss") ⏳ Esperando $($interval/60) minutos..." -ForegroundColor Cyan
    Start-Sleep -Seconds $interval
}}
'''
    
    ps_path = os.path.join(BASE_DIR, 'keep_alive_external.ps1')
    try:
        with open(ps_path, 'w', encoding='utf-8') as f:
            f.write(ps_content)
        print(f"✅ Script PowerShell de keep-alive creado: {ps_path}")
        return ps_path
    except Exception as e:
        print(f"⚠️ No se pudo crear script PowerShell: {e}")
        return None

# ——— Manejador de señales para cleanup ———
def signal_handler(signum, frame):
    """Manejador para cierre limpio del servidor"""
    print(f"\n🔄 Recibida señal {signum}, cerrando servidor...")
    stop_keep_alive()
    print("👋 ¡Hasta luego!")
    sys.exit(0)

# Registrar manejadores de señales
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ——— Función para encontrar puerto libre ———
def encontrar_puerto_libre(puerto_inicial=5000, max_intentos=10):
    """Encuentra un puerto libre comenzando desde puerto_inicial"""
    import socket
    for puerto in range(puerto_inicial, puerto_inicial + max_intentos):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', puerto))
                return puerto
        except OSError:
            continue
    return None

def abrir_navegador(url, delay=2):
    """Abre el navegador automáticamente después de un delay"""
    import webbrowser
    import threading
    import time
    
    def abrir():
        time.sleep(delay)
        try:
            webbrowser.open(url)
            print(f"🌐 Abriendo navegador en: {url}")
        except Exception as e:
            print(f"⚠️  No se pudo abrir el navegador automáticamente: {e}")
            print(f"   Abre manualmente: {url}")
    
    thread = threading.Thread(target=abrir)
    thread.daemon = True
    thread.start()

# ——— Configuración final y ejecución ———
if __name__ == "__main__":
    print("=" * 70)
    print("🏋️  INICIANDO LAMA CONTROL - SISTEMA DE GIMNASIO  🏋️")
    print("=" * 70)
    
    # Usar puerto 3000 fijo
    puerto_libre = 3000
    
    if puerto_libre:
        # Obtener IP local
        local_ip = get_local_ip()
        
        # Configurar tiempo de inicio para uptime
        app.config['START_TIME'] = time.time()
        
        # Crear scripts externos de keep-alive
        print("📝 Creando scripts de keep-alive externos...")
        bat_script = create_external_keep_alive_script(local_ip, puerto_libre)
        ps_script = create_powershell_keep_alive_script(local_ip, puerto_libre)
        
        url_local = f"http://localhost:{puerto_libre}"
        url_red = f"http://0.0.0.0:{puerto_libre}"
        
        print(f"🌐 Servidor Flask iniciando...")
        print(f"📍 URL Local: {url_local}")
        print(f"🌍 URL Red: {url_red}")
        print(f"🌐 Acceso desde otros dispositivos: http://{local_ip}:{puerto_libre}")
        print(f"💾 Base de datos: {DB_PATH}")
        print(f"👤 Usuario admin: alfredo / PIN: 2121")
        print("=" * 70)
        print("✅ Funciones disponibles:")
        print("   • Panel de Administrador (/admin)")
        print("   • Panel de Moderador (/moderador)")
        print("   • Panel de Miembro (/panel_miembro)")
        print("   • Reportes Financieros (/reportes_financieros)")
        print("   • Analíticas Avanzadas (/analiticas_avanzadas)")
        print("   • Gestión de Backups (/gestion_backups)")
        print("   • Estadísticas Globales (/estadisticas_globales)")
        print("🔄 Keep-Alive: http://{}/keep_alive".format(local_ip + ":" + str(puerto_libre)))
        print("🏥 Health Check: http://{}/health".format(local_ip + ":" + str(puerto_libre)))
        print("📊 Estado del servidor: http://{}/server_status".format(local_ip + ":" + str(puerto_libre)))
        print("=" * 70)
        if bat_script:
            print(f"📄 Script Keep-Alive (BAT): {bat_script}")
        if ps_script:
            print(f"📄 Script Keep-Alive (PS1): {ps_script}")
        print("=" * 70)
        print(f"🚀 Iniciando servidor en el puerto {puerto_libre}...")
        print("🔄 Sistema Keep-Alive automático activado")
        print("💡 Para keep-alive externo ejecuta: keep_alive_external.bat")
        print("   Presiona Ctrl+C para detener el servidor")
        print("   El navegador se abrirá automáticamente en 3 segundos...")
        print("=" * 70)
        
        # Iniciar sistema de keep-alive
        setup_keep_alive(local_ip, puerto_libre)
        
        # Abrir navegador automáticamente
        abrir_navegador(url_local, delay=3)
        
        try:
            app.run(
                debug=False,  # Cambiado para evitar conflictos con keep-alive
                host="0.0.0.0", 
                port=puerto_libre, 
                threaded=True,
                use_reloader=False  # Cambiado para evitar conflictos con keep-alive
            )
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido por el usuario")
            stop_keep_alive()
            print("👋 ¡Hasta la próxima!")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            stop_keep_alive()
            print("💡 Revisa los logs para más detalles")
        finally:
            stop_keep_alive()
    else:
        print("❌ El puerto 3000 no está disponible.")
        print("💡 Intenta cerrar otras aplicaciones que usen el puerto 3000")
        print("   o ejecuta manualmente especificando un puerto:")
        print("   python -c \"from LAMAControl import app; app.run(port=9000)\"")
        input("Presiona Enter para salir...")