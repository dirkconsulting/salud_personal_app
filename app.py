from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from models import db, Registro, Suplemento, SuplementoRegistro, Ejercicio, EjercicioRegistro, Alimento, Receta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'una_clave_secreta_segura'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///salud.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

    # Suplementos base
    suplementos_iniciales = [
        ("Glutamina", "Noche", "5g Glutamina con agua"),
        ("Omega 3", "Mañana", "Omega 3 (1000-2000 mg)"),
        ("Vitamina D", "Mañana", "Vitamina D (2000 UI) con comida"),
        ("Ubiquinol", "Mañana", "Ubiquinol (100 mg)"),
        ("Zinc quelado", "Mañana", "Zinc quelado (15-25 mg, junto al desayuno)"),
        ("Ashwagandha", "Mañana", "Ashwagandha (300-600 mg)"),
        ("Curcuma + Pimienta negra", "Mediodía", "Curcuma + Pimienta negra"),
        ("NAC", "Mediodía", "NAC (600 mg)"),
        ("Vitamina C", "Mediodía", "Vitamina C (500-1000 mg)"),
        ("Extracto de ajo", "Mediodía", "Extracto de ajo"),
        ("Magnesio Citrato", "Noche", "Magnesio Citrato (200-400 mg)"),
        ("Jengibre", "Noche", "Jengibre (en capsula o infusion)"),
    ]

    for nombre, hora, descripcion in suplementos_iniciales:
        if not Suplemento.query.filter_by(nombre=nombre).first():
            db.session.add(Suplemento(nombre=nombre, hora=hora, descripcion=descripcion))

    # Ejercicios base
    ejercicios_iniciales = [
        {
            "nombre": "Respiración diafragmática",
            "descripcion": "Acuéstate boca arriba, respira profundo expandiendo el abdomen.",
            "repeticiones": "10 respiraciones",
            "series": "2"
        },
        {
            "nombre": "Estiramiento de psoas izquierdo",
            "descripcion": "Zancada con rodilla derecha apoyada, inclinación pélvica.",
            "repeticiones": "30 segundos por lado",
            "series": "2"
        },
        {
            "nombre": "Activación de glúteo izquierdo",
            "descripcion": "Puentes de glúteo con énfasis en el lado izquierdo.",
            "repeticiones": "12 por lado",
            "series": "2"
        },
        {
            "nombre": "Plancha lateral izquierda",
            "descripcion": "Apóyate en el antebrazo izquierdo, activa el core.",
            "repeticiones": "30 segundos",
            "series": "2"
        },
        {
            "nombre": "Movilidad torácica",
            "descripcion": "Rotaciones en cuadrupedia o tumbado, abre el pecho.",
            "repeticiones": "10 por lado",
            "series": "2"
        },
        {
            "nombre": "Pausa postural cada 90 min",
            "descripcion": "Levantarse y caminar o estirar cada 90 minutos.",
            "repeticiones": "Libre",
            "series": "Durante todo el día"
        },
        {
            "nombre": "10 min descalzo activando pie izquierdo",
            "descripcion": "Caminar o hacer equilibrio sobre un solo pie.",
            "repeticiones": "10 minutos",
            "series": "1"
        }
    ]
    for e in ejercicios_iniciales:
        if not Ejercicio.query.filter_by(nombre=e["nombre"]).first():
            db.session.add(Ejercicio(
                nombre=e["nombre"],
                descripcion=e["descripcion"],
                repeticiones=e["repeticiones"],
                series=e["series"]
            ))

    # Alimentos base
    alimentos_base = [
        ("Huevos", "permitido", "proteína"),
        ("Salmón", "permitido", "proteína"),
        ("Aguacate", "permitido", "grasa saludable"),
        ("Aceite de oliva virgen extra", "permitido", "grasa saludable"),
        ("Espinacas", "permitido", "verdura"),
        ("Brócoli", "permitido", "verdura"),
        ("Frutos rojos", "permitido", "fruta"),
        ("Manzana", "permitido", "fruta"),
        ("Almendras activadas", "permitido", "fruto seco"),
        ("Boniato", "permitido", "carbohidrato bueno"),
        ("Yogur natural", "permitido", "lácteo"),
        ("Chocolate 85%", "permitido", "snack"),
        ("Azúcar refinada", "prohibido", "azúcar"),
        ("Refrescos", "prohibido", "bebida"),
        ("Harinas blancas", "prohibido", "cereal"),
        ("Aceites vegetales refinados", "prohibido", "grasa"),
        ("Bollería", "prohibido", "procesado"),
        ("Alcohol", "prohibido", "bebida")
    ]
    for nombre, tipo, categoria in alimentos_base:
        if not Alimento.query.filter_by(nombre=nombre).first():
            db.session.add(Alimento(nombre=nombre, tipo=tipo, categoria=categoria))

    # Recetas base
    recetas_base = [
        {
            "titulo": "Tortilla de espinacas con aguacate",
            "tipo": "desayuno",
            "ingredientes": "2 huevos, un puñado de espinacas, 1/2 aguacate, sal y AOVE",
            "pasos": "Batir los huevos, saltear las espinacas, mezclar y cocinar como tortilla. Servir con aguacate en rodajas."
        },
        {
            "titulo": "Salmón al horno con boniato",
            "tipo": "comida",
            "ingredientes": "1 filete de salmón, 1 boniato, especias, AOVE",
            "pasos": "Cortar el boniato en rodajas, hornear junto al salmón con especias a 200ºC durante 25 minutos."
        },
        {
            "titulo": "Yogur natural con frutos rojos y nueces",
            "tipo": "snack",
            "ingredientes": "1 yogur natural sin azúcar, 1 puñado de frutos rojos, 1 puñado de nueces",
            "pasos": "Mezclar todos los ingredientes y servir frío."
        }
    ]
    for r in recetas_base:
        if not Receta.query.filter_by(titulo=r["titulo"]).first():
            db.session.add(Receta(
                titulo=r["titulo"],
                tipo=r["tipo"],
                ingredientes=r["ingredientes"],
                pasos=r["pasos"]
            ))

    db.session.commit()

@app.route('/index', methods=['GET', 'POST'])
def index():
    # Obtención de suplementos ordenados por hora
    suplementos = Suplemento.query.order_by(Suplemento.hora).all()  # Ordenar por hora
    ejercicios = Ejercicio.query.all()

    if request.method == 'POST':
        # Obtener los datos del formulario
        dolor = request.form.get('dolor')
        digestion = request.form.get('digestion')
        energia = request.form.get('energia')
        notas = request.form.get('notas')

        # Obtener los suplementos y ejercicios seleccionados
        tomados = request.form.getlist('suplementos')
        realizados = request.form.getlist('ejercicios')

        # Crear un nuevo registro
        nuevo = Registro(
            dolor=dolor,
            digestion=digestion,
            energia=energia,
            notas=notas
        )
        db.session.add(nuevo)
        db.session.commit()

        # Registrar los suplementos tomados
        for suplemento_id in tomados:
            db.session.add(SuplementoRegistro(
                suplemento_id=suplemento_id,
                fecha=nuevo.fecha
            ))

        # Registrar los ejercicios realizados
        for ejercicio_id in realizados:
            db.session.add(EjercicioRegistro(
                ejercicio_id=ejercicio_id,
                fecha=nuevo.fecha
            ))

        db.session.commit()

        # Redirigir de nuevo a la misma página después de guardar
        return redirect(url_for('index'))

    # Obtener los registros de la base de datos
    registros = Registro.query.order_by(Registro.fecha.desc()).all()

    return render_template('index.html', today=date.today(), registros=registros,
                           suplementos=suplementos, ejercicios=ejercicios)

@app.route('/alimentacion', methods=['GET', 'POST'])
def alimentacion():
    # Crear alimento
    if request.method == 'POST':
        if 'nuevo_alimento' in request.form:
            nombre = request.form['nombre_alimento']
            tipo = request.form['tipo_alimento']
            categoria = request.form['categoria_alimento']
            if not Alimento.query.filter_by(nombre=nombre).first():
                db.session.add(Alimento(nombre=nombre, tipo=tipo, categoria=categoria))
                db.session.commit()
        elif 'nueva_receta' in request.form:
            titulo = request.form['titulo']
            tipo = request.form['tipo_receta']
            ingredientes = request.form['ingredientes']
            pasos = request.form['pasos']
            if not Receta.query.filter_by(titulo=titulo).first():
                db.session.add(Receta(titulo=titulo, tipo=tipo, ingredientes=ingredientes, pasos=pasos))
                db.session.commit()

    # Filtros GET
    filtro_tipo = request.args.get('filtro_tipo')
    filtro_categoria = request.args.get('filtro_categoria')
    filtro_receta = request.args.get('filtro_receta')

    alimentos_query = Alimento.query
    recetas_query = Receta.query

    if filtro_tipo:
        alimentos_query = alimentos_query.filter_by(tipo=filtro_tipo)
    if filtro_categoria:
        alimentos_query = alimentos_query.filter_by(categoria=filtro_categoria)
    if filtro_receta:
        recetas_query = recetas_query.filter_by(tipo=filtro_receta)

    alimentos = alimentos_query.order_by(Alimento.tipo, Alimento.categoria).all()
    recetas = recetas_query.order_by(Receta.tipo).all()

    return render_template(
        'alimentacion.html',
        alimentos=alimentos,
        recetas=recetas,
        tipos_alimento=TIPOS_ALIMENTO,
        categorias_alimento=CATEGORIAS_ALIMENTO,
        tipos_receta=TIPOS_RECETA,
        filtro_tipo=filtro_tipo,
        filtro_categoria=filtro_categoria,
        filtro_receta=filtro_receta
    )

if __name__ == '__main__':
    app.run(debug=True)
