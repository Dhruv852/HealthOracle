import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.regularizers import l1_l2
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report
import joblib
# Removed: import pandas as pd, import matplotlib.pyplot as plt, import seaborn as sns, from imblearn.over_sampling import SMOTE

def build_model(input_dim):
    model = Sequential()
    model.add(Dense(24, input_dim=input_dim, activation='relu', kernel_regularizer=l1_l2(l1=0.001, l2=0.001)))
    model.add(Dropout(0.2))
    model.add(Dense(12, activation='relu', kernel_regularizer=l1_l2(l1=0.001, l2=0.001)))
    model.add(Dropout(0.2))
    model.add(Dense(6, activation='relu', kernel_regularizer=l1_l2(l1=0.001, l2=0.001)))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.AUC()])
    return model

# Helper Functions
def get_risk_category(risk_percentage):
    if risk_percentage > 60:
        return "High Risk"
    elif risk_percentage >= 30:
        return "Moderate Risk"
    else:
        return "Low Risk"

def get_health_advice(category):
    if category == "High Risk":
        return "Immediate medical attention is advised. Consult a specialist as soon as possible."
    elif category == "Moderate Risk":
        return "It's recommended to schedule a health check-up. Consider lifestyle changes and follow a balanced diet."
    else:
        return "You are at low risk. Maintain a healthy lifestyle and regular check-ups."

# Common training function with improvements
def train_model_with_improvements(X, y, scaler_filename, model_filename, features_filename=None, feature_names=None):
    # Split data with stratification
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Scale features
    scaler = StandardScaler().fit(X_train)
    joblib.dump(scaler, scaler_filename)
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Apply SMOTE to balance the dataset
    smote = SMOTE(random_state=42)
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train_scaled, y_train)
    
    # Print class distribution before and after SMOTE
    print(f"Original class distribution: {np.bincount(y_train)}")
    print(f"Balanced class distribution: {np.bincount(y_train_balanced)}")
    
    # Set up early stopping
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    )
    
    # Build model
    model = build_model(X_train_balanced.shape[1])
    
    # Use class weights to further address imbalance
    class_weights = {0: 1.0, 1: 3.0}
    
    # Train model with early stopping and smaller batch size
    history = model.fit(
        X_train_balanced, y_train_balanced,
        epochs=100,
        batch_size=16,
        validation_split=0.2,
        callbacks=[early_stopping],
        class_weight=class_weights,
        verbose=1
    )
    
    # Evaluate model
    y_pred_proba = model.predict(X_test_scaled)
    y_pred = (y_pred_proba > 0.5).astype(int)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    # Print evaluation metrics
    print(f"\nModel Evaluation Metrics for {model_filename}:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"ROC AUC: {roc_auc:.4f}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    # Save model and feature names if provided
    model.save(model_filename)
    if feature_names is not None and features_filename is not None:
        joblib.dump(feature_names, features_filename)
    
    return model

# Heart Disease Prediction Model
def train_heart_model():
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
    column_names = [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang",
        "oldpeak", "slope", "ca", "thal", "target"
    ]
    data = pd.read_csv(url, names=column_names, na_values="?").dropna()
    
    # Feature engineering for heart disease
    data['age_sex'] = data['age'] * data['sex']  # Interaction between age and sex
    data['chol_age'] = data['chol'] / data['age']  # Cholesterol adjusted for age
    data['trestbps_chol'] = data['trestbps'] * data['chol'] / 10000  # BP and cholesterol interaction
    data['exang_oldpeak'] = data['exang'] * data['oldpeak']  # Exercise angina and ST depression
    data['risk_factors'] = data['fbs'] + data['exang']  # Sum of binary risk factors
    
    # Define features
    features = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang',
                'oldpeak', 'slope', 'ca', 'thal', 'age_sex', 'chol_age', 'trestbps_chol', 
                'exang_oldpeak', 'risk_factors']
    
    X = data[features].values
    y = (data['target'] > 0).astype(int).values
    
    # Train model with improvements
    return train_model_with_improvements(X, y, 'heart_scaler.pkl', 'heart_model.h5', 'heart_model_features.pkl', features)

# Lung Disease Prediction Model
def train_lung_model():
    try:
        # Generate synthetic data with realistic patterns
        np.random.seed(42)
        n_samples = 1000
        
        # Base features
        age = np.random.normal(50, 15, n_samples).clip(20, 80)
        smoking = np.random.binomial(1, 0.3, n_samples)  # 30% smokers
        air_quality = np.random.normal(100, 50, n_samples).clip(20, 300)
        alcohol = np.random.binomial(1, 0.4, n_samples)  # 40% drinkers
        bmi = np.random.normal(25, 5, n_samples).clip(18, 40)
        family_history = np.random.binomial(1, 0.2, n_samples)  # 20% with family history
        activity = np.random.randint(0, 4, n_samples)  # 0-3 activity levels
        occupation = np.random.binomial(1, 0.25, n_samples)  # 25% with occupational exposure
        
        # Create engineered features
        age_smoking = age * smoking * 2
        smoking_air_quality = smoking * air_quality / 100
        bmi_activity = bmi / (activity + 1)
        risk_factor_sum = (smoking * 2 + 
                          family_history * 1.5 + 
                          occupation * 1.5 + 
                          alcohol * 1)
        
        # Combine all features
        X = np.column_stack([
            age, smoking, air_quality, alcohol, bmi, family_history,
            activity, occupation, age_smoking, smoking_air_quality,
            bmi_activity, risk_factor_sum
        ])
        
        # Generate target variable with realistic risk patterns
        base_risk = (
            (age - 20) / 60 * 0.3 +  # Age contribution
            smoking * 0.3 +           # Smoking contribution
            (air_quality - 20) / 280 * 0.2 +  # Air quality contribution
            alcohol * 0.1 +           # Alcohol contribution
            (bmi - 18) / 22 * 0.2 +  # BMI contribution
            family_history * 0.2 +    # Family history contribution
            (3 - activity) / 3 * 0.2 +  # Activity level contribution
            occupation * 0.2          # Occupation contribution
        )
        
        # Add some noise and ensure values are between 0 and 1
        base_risk = base_risk + np.random.normal(0, 0.1, n_samples)
        base_risk = base_risk.clip(0, 1)
        
        # Convert to binary target with probability based on risk
        y = np.random.binomial(1, base_risk)
        
        # Save feature names
        features = ['Age', 'Smoking Status', 'Area Air Quality Index', 'Alcohol Consumption',
                   'BMI', 'Family History', 'Physical Activity Level', 'Occupation Exposure',
                   'Age_Smoking', 'Smoking_AirQuality', 'BMI_Activity', 'Risk_Factor_Sum']
        
        # Train model with improvements
        model = train_model_with_improvements(X, y, 'lung_scaler.pkl', 'lung_model.h5', 'lung_model_features.pkl', features)
        
        return model
        
    except Exception as e:
        print(f"Error training lung model: {str(e)}")
        raise ValueError("Error training lung disease model. Please check the training data.")

# Load models and scalers at module level
try:
    heart_model = load_model('heart_model.h5')
    heart_scaler = joblib.load('heart_scaler.pkl')
    print("Successfully loaded heart model")
except Exception as e:
    raise RuntimeError("Pretrained heart model files are missing. Please upload them.") from e

try:
    liver_model = load_model('liver_model.h5')
    liver_scaler = joblib.load('liver_scaler.pkl')
    print("Successfully loaded liver model")
except Exception as e:
    raise RuntimeError("Pretrained liver model files are missing. Please upload them.") from e

try:
    diabetes_model = load_model('diabetes_model.h5')
    diabetes_scaler = joblib.load('diabetes_scaler.pkl')
    print("Successfully loaded diabetes model")
except Exception as e:
    raise RuntimeError("Pretrained diabetes model files are missing. Please upload them.") from e

try:
    lung_model = load_model('lung_model.h5')
    lung_scaler = joblib.load('lung_scaler.pkl')
    print("Successfully loaded lung model")
except Exception as e:
    raise RuntimeError("Pretrained lung model files are missing. Please upload them.") from e

def calibrate_prediction(raw_prediction):
    if raw_prediction > 0.8:
        # High predictions are slightly reduced to avoid overconfidence
        return 0.8 + (raw_prediction - 0.8) * 0.7
    elif raw_prediction < 0.2:
        # Low predictions are slightly increased to avoid underestimation
        return raw_prediction * 1.3
    else:
        # Mid-range predictions are kept as is
        return raw_prediction

def predict_lung_disease(features):
    global lung_model, lung_scaler
    
    # Ensure model and scaler are loaded
    if lung_model is None or lung_scaler is None:
        try:
            lung_model = load_model('lung_model.h5')
            lung_scaler = joblib.load('lung_scaler.pkl')
        except Exception as e:
            print(f"Error loading lung model: {str(e)}")
            lung_model = train_lung_model()
            lung_scaler = joblib.load('lung_scaler.pkl')
    
    try:
        # Convert input features to appropriate types
        age = float(features[0])
        smoking = int(features[1])
        air_quality = float(features[2])
        alcohol = int(features[3])
        bmi = float(features[4])
        family_history = int(features[5])
        activity = int(features[6])
        occupation = int(features[7])
        
        # Create engineered features with adjusted weights
        age_smoking = age * smoking * 2
        smoking_air_quality = smoking * air_quality / 100
        bmi_activity = bmi / (activity + 1)
        risk_factor_sum = (smoking * 2 + 
                          family_history * 1.5 + 
                          occupation * 1.5 + 
                          alcohol * 1)
        
        # Combine all features in the same order as training (12 features)
        features_array = np.array([[
            age, smoking, air_quality, alcohol, bmi, family_history, 
            activity, occupation, age_smoking, smoking_air_quality, 
            bmi_activity, risk_factor_sum
        ]])
        
        # Scale features
        scaled_features = lung_scaler.transform(features_array)
        
        # Make prediction
        prediction = lung_model.predict(scaled_features)
        raw_prediction = float(prediction[0][0])
        calibrated_prediction = calibrate_prediction(raw_prediction)
        
        # Calculate risk metrics
        risk_percentage = round(calibrated_prediction * 100, 2)
        category = get_risk_category(risk_percentage)
        advice = get_health_advice(category)
        
        return risk_percentage, category, advice
        
    except Exception as e:
        print(f"Error in lung disease prediction: {str(e)}")
        # If prediction fails, retrain the model and try again
        try:
            print("Retraining lung model...")
            lung_model = train_lung_model()
            lung_scaler = joblib.load('lung_scaler.pkl')
            return predict_lung_disease(features)  # Try prediction again
        except Exception as retrain_error:
            raise ValueError(f"Error in lung disease prediction after retraining: {str(retrain_error)}")

# Liver Disease Prediction Model
def train_liver_model():
    df = pd.read_csv('HealthOracle/indian_liver_patient.csv')
    df['Gender'] = (df['Gender'] == 'Male').astype(int)
    
    # Handle missing values if any
    df = df.fillna(df.median())
    
    # Feature engineering for liver disease
    df['Age_Gender'] = df['Age'] * df['Gender']  # Interaction between age and gender
    df['Bilirubin_Ratio'] = df['Direct_Bilirubin'] / (df['Total_Bilirubin'] + 0.001)  # Ratio of direct to total bilirubin
    df['Enzyme_Ratio'] = df['Aspartate_Aminotransferase'] / (df['Alamine_Aminotransferase'] + 0.001)  # AST/ALT ratio
    df['Protein_Ratio'] = df['Albumin'] / (df['Total_Protiens'] + 0.001)  # Albumin to total protein ratio
    df['Liver_Score'] = (df['Total_Bilirubin'] + df['Direct_Bilirubin']) * df['Enzyme_Ratio']  # Combined liver score
    
    features = ['Age', 'Gender', 'Total_Bilirubin', 'Direct_Bilirubin', 'Alkaline_Phosphotase',
                'Alamine_Aminotransferase', 'Aspartate_Aminotransferase', 'Total_Protiens',
                'Albumin', 'Albumin_and_Globulin_Ratio', 'Age_Gender', 'Bilirubin_Ratio', 
                'Enzyme_Ratio', 'Protein_Ratio', 'Liver_Score']
    
    X = df[features].values
    y = (df['Dataset'] == 1).astype(int).values
    
    # Train model with improvements
    return train_model_with_improvements(X, y, 'liver_scaler.pkl', 'liver_model.h5', 'liver_model_features.pkl', features)

# Diabetes Prediction Model
def train_diabetes_model():
    url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
    column_names = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin", 
                     "BMI", "DiabetesPedigreeFunction", "Age", "Outcome"]
    data = pd.read_csv(url, names=column_names)
    
    # Handle missing values (zeros in some columns are likely missing values)
    for column in ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']:
        data[column] = data[column].replace(0, np.nan)
        data[column] = data[column].fillna(data[column].median())
    
    # Feature engineering for diabetes
    data['Glucose_BMI'] = data['Glucose'] * data['BMI'] / 100  # Interaction between glucose and BMI
    data['Age_BMI'] = data['Age'] * data['BMI'] / 100  # Age adjusted for BMI
    data['Glucose_Insulin'] = data['Glucose'] / (data['Insulin'] + 1)  # Glucose to insulin ratio
    data['Preg_Age'] = data['Pregnancies'] / (data['Age'] + 1)  # Pregnancies adjusted for age
    data['Risk_Score'] = data['Glucose'] / 100 + data['BMI'] / 30 + data['Age'] / 50  # Combined risk score
    
    features = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin',
                'BMI', 'DiabetesPedigreeFunction', 'Age', 'Glucose_BMI', 'Age_BMI',
                'Glucose_Insulin', 'Preg_Age', 'Risk_Score']
    
    X = data[features].values
    y = data['Outcome'].values
    
    # Train model with improvements
    return train_model_with_improvements(X, y, 'diabetes_scaler.pkl', 'diabetes_model.h5', 'diabetes_model_features.pkl', features)

# Prediction Functions with calibration
def predict_heart_disease(features):
    try:
        feature_names = joblib.load('heart_model_features.pkl')
        
        if len(features) == 13:  # Original features count
            age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal = features
            
            # Create engineered features
            age_sex = age * sex
            chol_age = chol / age
            trestbps_chol = trestbps * chol / 10000
            exang_oldpeak = exang * oldpeak
            risk_factors = fbs + exang
            
            # Combine all features
            features = features + [age_sex, chol_age, trestbps_chol, exang_oldpeak, risk_factors]
    except:
        pass
    
    scaled_features = heart_scaler.transform([features])
    prediction = heart_model.predict(scaled_features)
    
    raw_prediction = float(prediction[0][0])
    calibrated_prediction = calibrate_prediction(raw_prediction)
    
    risk_percentage = round(calibrated_prediction * 100, 2)
    category = get_risk_category(risk_percentage)
    advice = get_health_advice(category)
    
    return risk_percentage, category, advice

def predict_liver_disease(features):
    try:
        feature_names = joblib.load('liver_model_features.pkl')
        
        if len(features) == 10:  # Original features count
            age, gender, total_bili, direct_bili, alk_phos, alt, ast, total_proteins, albumin, ag_ratio = features
            
            # Create engineered features
            age_gender = age * gender
            bili_ratio = direct_bili / (total_bili + 0.001)
            enzyme_ratio = ast / (alt + 0.001)
            protein_ratio = albumin / (total_proteins + 0.001)
            liver_score = (total_bili + direct_bili) * enzyme_ratio
            
            # Combine all features
            features = features + [age_gender, bili_ratio, enzyme_ratio, protein_ratio, liver_score]
    except:
        pass
    
    scaled_features = liver_scaler.transform([features])
    prediction = liver_model.predict(scaled_features)
    
    raw_prediction = float(prediction[0][0])
    calibrated_prediction = calibrate_prediction(raw_prediction)
    
    risk_percentage = round(calibrated_prediction * 100, 2)
    category = get_risk_category(risk_percentage)
    advice = get_health_advice(category)
    
    return risk_percentage, category, advice

def predict_diabetes(features):
    try:
        feature_names = joblib.load('diabetes_model_features.pkl')
        
        if len(features) == 8:  # Original features count
            pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, pedigree, age = features
            
            # Create engineered features
            glucose_bmi = glucose * bmi / 100
            age_bmi = age * bmi / 100
            glucose_insulin = glucose / (insulin + 1)
            preg_age = pregnancies / (age + 1)
            risk_score = glucose / 100 + bmi / 30 + age / 50
            
            # Combine all features
            features = features + [glucose_bmi, age_bmi, glucose_insulin, preg_age, risk_score]
    except:
        pass
    
    scaled_features = diabetes_scaler.transform([features])
    prediction = diabetes_model.predict(scaled_features)
    
    raw_prediction = float(prediction[0][0])
    calibrated_prediction = calibrate_prediction(raw_prediction)
    
    risk_percentage = round(calibrated_prediction * 100, 2)
    category = get_risk_category(risk_percentage)
    advice = get_health_advice(category)
    
    return risk_percentage, category, advice
