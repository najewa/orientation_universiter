from flask import Flask, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# Charger le modèle Extra Trees
with open(r'C:\Users\user\Desktop\orientation_universitaire\server\modele_orientation_extratrees.pkl', 'rb') as f:
    model = pickle.load(f)

@app.route('/')
def home():
    return jsonify({'message': 'API Flask pour la prédiction est en ligne'})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        # 🔹 Assurer la conversion en float
        features = np.array([
            float(data['Credit_totale____2emme'] or 0),
            float(data['Moyenne_generale__2emme'] or 0),
            float(data['diagnostic__financier'] or 0),
            float(data['gestion_de_production'] or 0),
            float(data['fondamentaux_du_managment'] or 0),
            float(data['fondamenteaux_du_marketing'] or 0),
            float(data['Mathematiques_financieres'] or 0),
            float(data['Principe_de_gestion_1'] or 0),
            float(data['principe_de_gestion_2'] or 0),
            float(data['moyenne_elements_specifiques'] or 0),
            float(data['scrore'] or 0)
        ]).reshape(1, -1)

        prediction = model.predict(features)

        return jsonify({
            'status': 'success',
            'prediction': float(prediction[0])
        })

    except KeyError as e:
        return jsonify({'status': 'error', 'message': f"Champ manquant: {e}"})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    # debug=True uniquement pour dev
    app.run(debug=True)
