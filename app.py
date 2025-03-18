from datetime import datetime, timedelta
from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///turnos.db'
db = SQLAlchemy(app)

# Modelo de la base de datos
class CirujanosTurno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    nombre_turno = db.Column(db.String(50), nullable=False)
    cirujano1 = db.Column(db.String(100))
    cirujano2 = db.Column(db.String(100))

# Configuración de turnos
class TurnoCiclo:
    def __init__(self, nombre, color, fecha_inicial, dias_ciclo):
        self.nombre = nombre
        self.color = color
        self.fecha_inicial = fecha_inicial
        self.dias_ciclo = dias_ciclo

class TurnoVolante:
    def __init__(self, nombre, color, fecha_inicial):
        self.nombre = nombre
        self.color = color
        self.fecha_inicial = fecha_inicial

TURNOS = {
    "Turno miércoles": TurnoCiclo("Turno miércoles", "lightblue", datetime(2025, 1, 1).date(), 3),
    "Turno jueves": TurnoCiclo("Turno jueves", "plum", datetime(2025, 1, 2).date(), 4),
    "Volante 1": TurnoVolante("Volante 1", "khaki", datetime(2025, 1, 3).date()),
    "Volante 2": TurnoVolante("Volante 2", "salmon", datetime(2025, 1, 4).date()),
    "Turno lunes": TurnoCiclo("Turno lunes", "pink", datetime(2025, 1, 6).date(), 2),
    "Turno martes": TurnoCiclo("Turno martes", "lightgreen", datetime(2025, 1, 7).date(), 3)
}

COLORES_TURNOS = {
    "Turno miércoles": "lightblue",
    "Turno jueves": "plum",
    "Volante 1": "khaki",
    "Volante 2": "salmon",
    "Turno lunes": "pink",
    "Turno martes": "lightgreen"
}

DIAS_POR_MES = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
NOMBRES_MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

def inicializar_db():
    with app.app_context():
        db.create_all()

def generar_calendario_año_desde_marzo(año):
    calendario = {}
    for mes in range(2, 12):  # Empezar desde marzo (índice 2)
        for dia in range(1, 32):
            try:
                fecha = datetime(año, mes + 1, dia).date()
                turno_db = CirujanosTurno.query.filter_by(fecha=fecha).first()
                if turno_db:
                    calendario[fecha] = {
                        'nombre': turno_db.nombre_turno,
                        'color': COLORES_TURNOS[turno_db.nombre_turno],
                        'cirujanos': [turno_db.cirujano1, turno_db.cirujano2]
                    }
            except ValueError:
                continue
    return calendario

def generar_calendario_año(año):
    calendario = {}
    for mes in range(12):
        for dia in range(1, 32):
            try:
                fecha = datetime(año, mes + 1, dia).date()
                turno_db = CirujanosTurno.query.filter_by(fecha=fecha).first()
                if turno_db:
                    calendario[fecha] = {
                        'nombre': turno_db.nombre_turno,
                        'color': COLORES_TURNOS[turno_db.nombre_turno],
                        'cirujanos': [turno_db.cirujano1, turno_db.cirujano2]
                    }
            except ValueError:
                continue
    return calendario

@app.route('/')
def view_calendar():
    calendarios = {
        2025: generar_calendario_año_desde_marzo(2025),
        2026: generar_calendario_año(2026)
    }
    return render_template_string(
        HTML_TEMPLATE,
        datetime=datetime,
        calendarios=calendarios,
        dias_por_mes=DIAS_POR_MES,
        nombres_meses=NOMBRES_MESES,
        mes_inicial=2
    )

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Calendario de Turnos 2025-2026</title>
    <style>
        .calendar-container {
            padding: 20px;
        }
        
        .mes {
            margin-bottom: 20px;
            display: inline-block;
            vertical-align: top;
            margin-right: 20px;
        }
        
        .dias-container {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 2px;
            background-color: #f0f0f0;
            padding: 2px;
        }
        
        .weekday {
            font-weight: bold;
            text-align: center;
            padding: 5px;
            background-color: #f0f0f0;
            color: black;
        }
        
        .dia {
            width: 100px;
            height: 80px;
            background-color: white;
            padding: 5px;
            box-sizing: border-box;
        }
        
        .turno-info {
            padding: 5px;
            border-radius: 3px;
        }
        
        .nombre-turno {
            font-size: 12px;
            margin-bottom: 3px;
            color: black;
        }
        
        .cirujanos {
            font-size: 14px;
            font-weight: 500;
            margin-top: 2px;
            line-height: 1.2;
            color: black;
        }
    </style>
</head>
<body>
    <div class="calendar-container">
        {% for año in [2025, 2026] %}
        <h1>Calendario de Turnos {{ año }}</h1>
        {% for mes in range(mes_inicial if año == 2025 else 0, 12) %}
        <div class="mes">
            <h2>{{ nombres_meses[mes] }}</h2>
            <div class="dias-container">
                {% for dia in ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"] %}
                    <div class="weekday">{{ dia }}</div>
                {% endfor %}
                
                {% set primer_dia = datetime(año, mes + 1, 1).weekday() %}
                {% for _ in range(primer_dia) %}
                    <div class="dia"></div>
                {% endfor %}
                
                {% for dia in range(1, dias_por_mes[mes] + 1) %}
                    {% set fecha = datetime(año, mes + 1, dia).date() %}
                    <div class="dia">
                        {{ dia }}
                        {% if fecha in calendarios[año] %}
                            <div class="turno-info" 
                                 style="background-color: {{ calendarios[año][fecha].color }}">
                                <div class="nombre-turno">{{ calendarios[año][fecha].nombre }}</div>
                                <div class="cirujanos">
                                    {{ calendarios[año][fecha].cirujanos[0] }}<br>
                                    {{ calendarios[año][fecha].cirujanos[1] }}
                                </div>
                            </div>
                        {% endif %}
                    </div>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
        {% endfor %}
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    inicializar_db()
    app.run(debug=True, port=8080)