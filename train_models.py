from HealthOracle.ml_models import (
    train_heart_model,
    train_lung_model,
    train_liver_model,
    train_diabetes_model
)

def main():
    print("Starting model training...")
    
    print("\nTraining Heart Disease Model...")
    heart_model = train_heart_model()
    print("Heart Disease Model trained successfully!")
    
    print("\nTraining Lung Disease Model...")
    lung_model = train_lung_model()
    print("Lung Disease Model trained successfully!")
    
    print("\nTraining Liver Disease Model...")
    liver_model = train_liver_model()
    print("Liver Disease Model trained successfully!")
    
    print("\nTraining Diabetes Model...")
    diabetes_model = train_diabetes_model()
    print("Diabetes Model trained successfully!")
    
    print("\nAll models have been trained successfully!")

if __name__ == "__main__":
    main() 