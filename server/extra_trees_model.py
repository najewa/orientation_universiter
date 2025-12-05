import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import pickle


# 1️⃣ Déterminer le chemin absolu du fichier CSV
file_path = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'Fact_Admission.csv')
file_path = os.path.abspath(file_path)

# 2️⃣ Charger les données
df = pd.read_csv(file_path, sep=',', quotechar='"', engine='python')

# 3️⃣ Définir les features
features = [
    'Credit_totale____2emme',
    'Moyenne_generale__2emme',
    'diagnostic__financier',
    'gestion_de_production',
    'fondamentaux_du_managment',
    'fondamenteaux_du_marketing',
    'Mathematiques_financieres',
    'Principe_de_gestion_1',
    'principe_de_gestion_2',
    'moyenne_elements_specifiques',
    'scrore'
]

# 4️⃣ Conversion des données en float
for col in features + ['moyenne_generale___3emme']:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.').str.strip(), errors='coerce')

# 5️⃣ Nettoyage des valeurs manquantes
df = df.dropna(subset=features + ['moyenne_generale___3emme'])






# 6️⃣ Séparation des variables
X = df[features].astype(float)
y = df['moyenne_generale___3emme'].astype(float)

# 7️⃣ Split train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)






# 6️⃣ Définir et entraîner le modèle Extra Trees
et_model = ExtraTreesRegressor(n_estimators=200, random_state=42)
et_model.fit(X_train, y_train)

# 7️⃣ Prédictions
et_preds = et_model.predict(X_test)

# 8️⃣ Évaluation
et_rmse = np.sqrt(mean_squared_error(y_test, et_preds))
et_mae = mean_absolute_error(y_test, et_preds)
et_r2 = r2_score(y_test, et_preds)

print("🔹 Extra Trees Regressor")
print(f"RMSE : {et_rmse:.3f}")
print(f"MAE  : {et_mae:.3f}")
print(f"R²   : {et_r2:.3f}")

# 9️⃣ Visualisation : Réel vs Prédit
import matplotlib.pyplot as plt

plt.figure(figsize=(8,6))
plt.scatter(y_test, et_preds, color='purple', alpha=0.6, edgecolors='k', s=80, label='Prédictions')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()],
         color='red', linestyle='--', linewidth=2, label='Prédiction parfaite')
plt.xlabel("Moyenne réelle")
plt.ylabel("Moyenne prédite")
plt.title("Extra Trees Regressor : Comparaison Réel vs Prédit")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()









# 4️⃣ Diviser les données
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5️⃣ Définir et entraîner le modèle Extra Trees
model = ExtraTreesRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 6️⃣ Évaluer le modèle
y_pred = model.predict(X_test)
print("MSE :", mean_squared_error(y_test, y_pred))

# 🔟 Sauvegarde du modèle
base_dir = os.path.dirname(os.path.abspath(__file__))  # <-- définir base_dir
model_path = os.path.join(base_dir, 'modele_orientation_extratrees.pkl')
with open(model_path, 'wb') as file:
    pickle.dump(model, file)

print("✅ Modèle sauvegardé :", model_path)
print("📊 Colonnes du DataFrame :", list(df.columns))
