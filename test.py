from tensorflow import keras
model = keras.models.load_model("model_FINAL.h5", compile=False)
print("Modelo cargado correctamente!")
