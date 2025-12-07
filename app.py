import streamlit as st
from tensorflow import keras
import numpy as np
from PIL import Image
import mysql.connector
import os
from datetime import datetime
from urllib.parse import urlparse

# ----------------------
# CONEXIÓN MYSQL
# ----------------------
def conexion_mysql():
    db_url = os.getenv("MYSQL_URL")

    if not db_url:
        raise Exception("MYSQL_URL no está configurada en Railway.")

    url = urlparse(db_url)

    return mysql.connector.connect(
        host=url.hostname,
        port=url.port,
        user=url.username,
        password=url.password,
        database=url.path.replace("/", "")
    )

# Test de conexión
try:
    conn = conexion_mysql()
    conn.close()
    st.success("✔ Conexión MySQL exitosa")
except Exception as e:
    st.error(f"❌ Error de conexión MySQL: {e}")


# ----------------------
# CARGAR MODELO IA
# ----------------------
model = keras.models.load_model("model_FINAL.h5", compile=False)
IMG_SIZE = (224, 224)
CLASSES = ["infractor", "no_infractor"]


# ----------------------
# MENÚ PRINCIPAL
# ----------------------
opciones_menu = {
    "🏠 Inicio": "inicio",
    "🔎 Análisis Normal": "analisis_normal",
    "🧾 Análisis para Cliente": "analisis_cliente"
}

seleccion = st.sidebar.selectbox("📌 Navegación", list(opciones_menu.keys()))
menu = opciones_menu[seleccion]


# ----------------------
# INICIO
# ----------------------
if menu == "inicio":
    st.title("PrintSafeAI")
    st.write("Este sistema analiza imágenes para detectar contenido protegido (personajes, marcas, logos, fanarts), usado como filtro legal ANTES de proceder a la impresión de productos (polos, tazas, poleras).")

# ----------------------
# ANÁLISIS NORMAL (SIN CLIENTE)
# ----------------------
elif menu == "analisis_normal":
    st.title("Análisis IA - Modo Normal")

    uploaded = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])

    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        st.image(img, caption="Imagen cargada", width=300)

        # Preprocesamiento
        img = img.resize(IMG_SIZE)
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        pred = model.predict(img_array)[0][0]
        clase = CLASSES[1] if pred > 0.5 else CLASSES[0]
        # Probabilidad ajustada según la clase
        if clase == "infractor":
            conf_pct = (1 - pred) * 100
        else:
            conf_pct = pred * 100


        st.subheader("Resultado")
        if clase == "infractor":
            st.error(f"💥 Resultado: **CONTENIDO POTENCIALMENTE PROTEGIDO** — Probabilidad: {conf_pct:.2f}%")
            st.error("""
            ⚠️ **Advertencia de posible infracción**
            La IA detectó elementos que podrían estar relacionados con:
            - Marcas comerciales registradas
            - Personajes protegidos
            - Logotipos oficiales
            - Obras con derechos de autor

            **Recomendación:** Evite imprimir sin autorización legal. El análisis es una estimación y puede requerir verificación manual.
            """)
        else:
            st.success(f"🟢 Resultado: **SIN SEÑALES RELEVANTES DE CONTENIDO PROTEGIDO** — Probabilidad: {conf_pct:.2f}%")
            st.info("""
            ℹ️ No se identificaron indicios claros de contenido protegido.

            Sin embargo, se recomienda verificar la procedencia si la imagen proviene de internet o terceros.
            """)


# ----------------------
# ANÁLISIS PARA CLIENTES
# ----------------------
elif menu == "analisis_cliente":
    st.title("Registro + Análisis IA para Cliente")

    st.header("Datos del Cliente")
    nombre = st.text_input("Nombres")
    apellido = st.text_input("Apellidos")
    dni_ruc = st.text_input("DNI / RUC")
    celular = st.text_input("Celular")
    empresa = st.text_input("Empresa (opcional)")

    st.header("Empleado responsable")

    # OBTENER EMPLEADO
    try:
        conn = conexion_mysql()
        cursor = conn.cursor()
        cursor.execute("SELECT id_empleado, nombres, apellidos FROM empleado")
        empleados = cursor.fetchall()
        conn.close()

        opciones = {f"{e[1]} {e[2]}": e[0] for e in empleados}
        empleado_nombre = st.selectbox("Empleado:", list(opciones.keys()))
        empleado_id = opciones[empleado_nombre]

    except Exception as e:
        st.error(f"Error cargando empleados: {e}")
        empleado_id = None

    # SUBIR MÚLTIPLES IMÁGENES
    uploaded_files = st.file_uploader(
        "Sube imágenes del cliente",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    resultados = []

    if uploaded_files:
        st.subheader("🔍 Resultados del análisis IA")

        for archivo in uploaded_files:
            img = Image.open(archivo).convert("RGB")

            # Preprocesamiento
            img_resized = img.resize(IMG_SIZE)
            img_array = np.array(img_resized) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            pred = model.predict(img_array)[0][0]
            clase = CLASSES[1] if pred > 0.5 else CLASSES[0]
            # Probabilidad ajustada según la clase
            if clase == "infractor":
                conf_pct = (1 - pred) * 100
            else:
                conf_pct = pred * 100


            # Mostrar imagen
            st.image(img, caption=f"{archivo.name}", width=300)

            # Mostrar advertencias unificadas
            if clase == "infractor":
                st.error(f"💥 Resultado: **CONTENIDO POTENCIALMENTE PROTEGIDO** — Probabilidad: {conf_pct:.2f}%")
                st.error("""
                ⚠️ **Advertencia de contenido protegido**
                La IA identificó posibles elementos con derechos de autor:
                - Personajes comerciales
                - Marcas registradas
                - Logotipos oficiales

                No se recomienda imprimir sin autorización correspondiente.
                """)
            else:
                st.success(f"🟢 Resultado: **SIN SEÑALES RELEVANTES DE CONTENIDO PROTEGIDO** — Probabilidad: {conf_pct:.2f}%")
                st.info("""
                ℹ️ No se identificaron señales claras de contenido protegido.
                La impresión puede continuar bajo criterio del operador.
                """)

            st.markdown("---")

            resultados.append({
                "archivo": archivo,
                "clase": clase,
                "confianza": float(pred)
            })

    # GUARDAR EN BD
    if st.button("📁 Guardar análisis en la base de datos"):
        if not nombre or not apellido or not celular:
            st.error("Completa todos los campos obligatorios.")
        elif not resultados:
            st.error("Primero sube imágenes y espera el análisis.")
        else:
            conn = conexion_mysql()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO cliente (nombres, apellidos, dni_ruc, celular, empresa) VALUES (%s, %s, %s, %s, %s)",
                (nombre, apellido, dni_ruc, celular, empresa)
            )
            conn.commit()
            cliente_id = cursor.lastrowid

            if not os.path.exists("imagenes_guardadas"):
                os.mkdir("imagenes_guardadas")

            for r in resultados:
                archivo = r["archivo"]
                clase = r["clase"]
                conf = r["confianza"]

                img = Image.open(archivo).convert("RGB")
                img_path = f"imagenes_guardadas/{datetime.now().timestamp()}_{archivo.name}"
                img.save(img_path)

                cursor.execute("""
                    INSERT INTO imagen_analisis
                    (id_empleado, id_cliente, nombre_archivo, resultado, probabilidad, confianza, ruta_imagen)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (empleado_id, cliente_id, archivo.name, clase, conf, conf, img_path)
                )

            conn.commit()
            conn.close()

            st.success("✔ Análisis guardado exitosamente en la base de datos.")
