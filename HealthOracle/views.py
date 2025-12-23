from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .ml_models import predict_heart_disease, predict_lung_disease, predict_diabetes, predict_liver_disease
from .models import PredictionHistory
import numpy as np
import json
from django.http import JsonResponse
import google.genai as genai
from django.conf import settings

# Configure Gemini API
client = genai.Client(api_key=settings.GEMINI_API_KEY)

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

@login_required
def prediction_detail(request, prediction_id):
    prediction = get_object_or_404(PredictionHistory, id=prediction_id, user=request.user)
    return render(request, 'prediction_detail.html', {'prediction': prediction})

# Heart Prediction
@login_required
def heart_prediction(request):
    prediction_result = None
    risk_percentage = None
    category = None
    advice = None

    if request.method == 'POST':
        try:
            features = [
                int(request.POST.get('age')),
                int(request.POST.get('sex')),
                int(request.POST.get('cp')),
                int(request.POST.get('trestbps')),
                int(request.POST.get('chol')),
                int(request.POST.get('fbs')),
                int(request.POST.get('restecg')),
                int(request.POST.get('thalach')),
                int(request.POST.get('exang')),
                float(request.POST.get('oldpeak')),
                int(request.POST.get('slope')),
                int(request.POST.get('ca')),
                int(request.POST.get('thal')),
            ]
            risk_percentage, category, advice = predict_heart_disease(features)
            prediction_result = 1 if category == "High Risk" else 0
            
            # Save prediction to history
            if request.user.is_authenticated:
                input_data = {
                    'age': request.POST.get('age'),
                    'sex': 'Male' if request.POST.get('sex') == '1' else 'Female',
                    'chest_pain_type': request.POST.get('cp'),
                    'resting_blood_pressure': request.POST.get('trestbps'),
                    'cholesterol': request.POST.get('chol'),
                    'fasting_blood_sugar': 'Yes' if request.POST.get('fbs') == '1' else 'No',
                    'resting_ecg': request.POST.get('restecg'),
                    'max_heart_rate': request.POST.get('thalach'),
                    'exercise_induced_angina': 'Yes' if request.POST.get('exang') == '1' else 'No',
                    'st_depression': request.POST.get('oldpeak'),
                    'st_slope': request.POST.get('slope'),
                    'num_major_vessels': request.POST.get('ca'),
                    'thalassemia': request.POST.get('thal')
                }
                
                print(f"Saving prediction for user {request.user.username}")
                prediction = PredictionHistory.objects.create(
                    user=request.user,
                    test_type='heart',
                    risk_percentage=risk_percentage,
                    category=category,
                    advice=advice,
                    input_data=input_data
                )
                print(f"Prediction saved with ID: {prediction.id}")
                messages.success(request, 'Heart disease prediction completed and saved to your history.')
        except Exception as e:
            print(f"Error during heart disease prediction: {e}")
            prediction_result = "Error"
            messages.error(request, 'An error occurred during prediction. Please try again.')

    return render(request, 'heart.html', {
        'prediction_result': prediction_result,
        'risk_percentage': risk_percentage,
        'category': category,
        'advice': advice
    })


# Diabetes Prediction
@login_required
def diabetes_prediction(request):
    prediction_result = None
    risk_percentage = None
    category = None
    advice = None

    if request.method == 'POST':
        try:
            features = [
                float(request.POST.get('pregnancies')),
                float(request.POST.get('glucose')),
                float(request.POST.get('blood_pressure')),
                float(request.POST.get('skin_thickness')),
                float(request.POST.get('insulin')),
                float(request.POST.get('bmi')),
                float(request.POST.get('diabetes_pedigree')),
                float(request.POST.get('age')),
            ]
            risk_percentage, category, advice = predict_diabetes(features)
            prediction_result = 1 if category == "High Risk" else 0
            
            # Save prediction to history
            if request.user.is_authenticated:
                input_data = {
                    'pregnancies': request.POST.get('pregnancies'),
                    'glucose': request.POST.get('glucose'),
                    'blood_pressure': request.POST.get('blood_pressure'),
                    'skin_thickness': request.POST.get('skin_thickness'),
                    'insulin': request.POST.get('insulin'),
                    'bmi': request.POST.get('bmi'),
                    'diabetes_pedigree': request.POST.get('diabetes_pedigree'),
                    'age': request.POST.get('age')
                }
                
                PredictionHistory.objects.create(
                    user=request.user,
                    test_type='diabetes',
                    risk_percentage=risk_percentage,
                    category=category,
                    advice=advice,
                    input_data=input_data
                )
                messages.success(request, 'Diabetes prediction completed and saved to your history.')
        except Exception as e:
            print(f"Error during diabetes prediction: {e}")
            prediction_result = "Error"
            messages.error(request, 'An error occurred during prediction. Please try again.')

    return render(request, 'diabetes.html', {
        'prediction_result': prediction_result,
        'risk_percentage': risk_percentage,
        'category': category,
        'advice': advice
    })


# Lung Prediction
@login_required
def lung_prediction(request):
    prediction_result = None
    risk_percentage = None
    category = None
    advice = None

    if request.method == 'POST':
        try:
            # Convert input features to appropriate format
            features = [
                float(request.POST.get('age')),
                int(request.POST.get('smoking_status')),  # Convert to int (1 or 0)
                float(request.POST.get('area_air_quality_index')),
                int(request.POST.get('alcohol_consumption')),  # Convert to int (1 or 0)
                float(request.POST.get('bmi')),
                int(request.POST.get('family_history')),  # Convert to int (1 or 0)
                int(request.POST.get('physical_activity_level')),  # Convert to int (days)
                int(request.POST.get('occupation_exposure'))  # Convert to int (1 or 0)
            ]
            
            print("Input features:", features)  # Debug print
            
            risk_percentage, category, advice = predict_lung_disease(features)
            prediction_result = 1 if category == "High Risk" else 0
            
            # Save prediction to history
            if request.user.is_authenticated:
                input_data = {
                    'age': request.POST.get('age'),
                    'smoking_status': 'Yes' if request.POST.get('smoking_status') == '1' else 'No',
                    'area_air_quality_index': request.POST.get('area_air_quality_index'),
                    'alcohol_consumption': 'Yes' if request.POST.get('alcohol_consumption') == '1' else 'No',
                    'bmi': request.POST.get('bmi'),
                    'family_history': 'Yes' if request.POST.get('family_history') == '1' else 'No',
                    'physical_activity_level': request.POST.get('physical_activity_level'),
                    'occupation_exposure': 'Yes' if request.POST.get('occupation_exposure') == '1' else 'No'
                }
                
                print(f"Saving prediction for user {request.user.username}")
                prediction = PredictionHistory.objects.create(
                    user=request.user,
                    test_type='lung',
                    risk_percentage=risk_percentage,
                    category=category,
                    advice=advice,
                    input_data=input_data
                )
                print(f"Prediction saved with ID: {prediction.id}")
                messages.success(request, 'Lung disease prediction completed and saved to your history.')
        except Exception as e:
            print(f"Error during lung disease prediction: {e}")
            prediction_result = "Error"
            messages.error(request, 'An error occurred during prediction. Please try again.')

    return render(request, 'lung.html', {
        'prediction_result': prediction_result,
        'risk_percentage': risk_percentage,
        'category': category,
        'advice': advice
    })


# Liver Prediction
@login_required
def liver_prediction(request):
    prediction_result = None
    risk_percentage = None
    category = None
    advice = None

    if request.method == 'POST':
        try:
            features = [
                int(request.POST.get('age')),
                int(request.POST.get('gender')),
                float(request.POST.get('total_bilirubin')),
                float(request.POST.get('direct_bilirubin')),
                int(request.POST.get('alkaline_phosphotase')),
                int(request.POST.get('alamine_aminotransferase')),
                int(request.POST.get('aspartate_aminotransferase')),
                float(request.POST.get('total_proteins')),
                float(request.POST.get('albumin')),
                float(request.POST.get('albumin_globulin_ratio')),
            ]
            risk_percentage, category, advice = predict_liver_disease(features)
            prediction_result = 1 if category == "High Risk" else 0
            
            # Save prediction to history
            if request.user.is_authenticated:
                input_data = {
                    'age': request.POST.get('age'),
                    'gender': 'Male' if request.POST.get('gender') == '1' else 'Female',
                    'total_bilirubin': request.POST.get('total_bilirubin'),
                    'direct_bilirubin': request.POST.get('direct_bilirubin'),
                    'alkaline_phosphotase': request.POST.get('alkaline_phosphotase'),
                    'alamine_aminotransferase': request.POST.get('alamine_aminotransferase'),
                    'aspartate_aminotransferase': request.POST.get('aspartate_aminotransferase'),
                    'total_proteins': request.POST.get('total_proteins'),
                    'albumin': request.POST.get('albumin'),
                    'albumin_globulin_ratio': request.POST.get('albumin_globulin_ratio')
                }
                
                PredictionHistory.objects.create(
                    user=request.user,
                    test_type='liver',
                    risk_percentage=risk_percentage,
                    category=category,
                    advice=advice,
                    input_data=input_data
                )
                messages.success(request, 'Liver disease prediction completed and saved to your history.')
        except Exception as e:
            print(f"Error during liver disease prediction: {e}")
            prediction_result = "Error"
            messages.error(request, 'An error occurred during prediction. Please try again.')

    return render(request, 'liver.html', {
        'prediction_result': prediction_result,
        'risk_percentage': risk_percentage,
        'category': category,
        'advice': advice
    })

def get_suggestions(prediction_type, risk_percentage, category):
    suggestions = {
        'heart': {
            'High Risk': {
                'diet': [
                    "Follow a heart-healthy Mediterranean diet",
                    "Limit saturated fats and trans fats",
                    "Reduce sodium intake to less than 2,300mg per day",
                    "Increase consumption of omega-3 rich foods"
                ],
                'lifestyle': [
                    "Schedule an immediate appointment with a cardiologist",
                    "Monitor blood pressure daily",
                    "Start a supervised exercise program",
                    "Consider stress management techniques"
                ],
                'medical': [
                    "Consult with a cardiologist within 1 week",
                    "Get a complete lipid panel test",
                    "Consider cardiac stress test",
                    "Discuss medication options with your doctor"
                ]
            },
            'Moderate Risk': {
                'diet': [
                    "Increase fruits and vegetables intake",
                    "Choose whole grains over refined grains",
                    "Limit processed foods",
                    "Monitor portion sizes"
                ],
                'lifestyle': [
                    "Exercise for 30 minutes, 5 days a week",
                    "Practice stress reduction techniques",
                    "Maintain a healthy sleep schedule",
                    "Track your daily steps"
                ],
                'medical': [
                    "Schedule a check-up within a month",
                    "Monitor blood pressure weekly",
                    "Get regular cholesterol checks",
                    "Discuss preventive measures with your doctor"
                ]
            },
            'Low Risk': {
                'diet': [
                    "Maintain a balanced diet",
                    "Stay hydrated with water",
                    "Include heart-healthy fats",
                    "Limit alcohol consumption"
                ],
                'lifestyle': [
                    "Continue regular physical activity",
                    "Maintain healthy weight",
                    "Practice good sleep habits",
                    "Stay active throughout the day"
                ],
                'medical': [
                    "Schedule routine check-ups",
                    "Monitor blood pressure monthly",
                    "Get annual physical examinations",
                    "Keep track of family health history"
                ]
            }
        },
        'lung': {
            'High Risk': {
                'diet': [
                    "Increase antioxidant-rich foods",
                    "Consume foods high in vitamin C and E",
                    "Add anti-inflammatory foods to diet",
                    "Stay well-hydrated"
                ],
                'lifestyle': [
                    "Quit smoking immediately",
                    "Avoid secondhand smoke exposure",
                    "Use air purifiers at home",
                    "Practice deep breathing exercises"
                ],
                'medical': [
                    "See a pulmonologist immediately",
                    "Get a chest X-ray or CT scan",
                    "Schedule pulmonary function tests",
                    "Discuss medication options"
                ]
            },
            'Moderate Risk': {
                'diet': [
                    "Eat more fruits and vegetables",
                    "Include foods rich in beta-carotene",
                    "Avoid processed foods",
                    "Maintain healthy weight through diet"
                ],
                'lifestyle': [
                    "Reduce exposure to air pollutants",
                    "Exercise in clean air environments",
                    "Practice respiratory exercises",
                    "Keep indoor air clean"
                ],
                'medical': [
                    "Schedule a pulmonologist visit",
                    "Get baseline lung function tests",
                    "Monitor respiratory symptoms",
                    "Consider preventive medications"
                ]
            },
            'Low Risk': {
                'diet': [
                    "Follow a balanced diet",
                    'Stay hydrated',
                    'Include lung-healthy foods',
                    'Maintain proper nutrition'
                ],
                'lifestyle': [
                    'Exercise regularly',
                    'Avoid smoking and smoke exposure',
                    'Practice good posture',
                    'Keep indoor air quality high'
                ],
                'medical': [
                    'Get regular check-ups',
                    'Monitor any changes in breathing',
                    'Keep vaccination records updated',
                    'Discuss prevention strategies'
                ]
            }
        },
        'liver': {
            'High Risk': {
                'diet': [
                    "Eliminate alcohol consumption",
                    "Follow a low-fat diet",
                    "Avoid processed foods",
                    "Increase fiber intake"
                ],
                'lifestyle': [
                    "Stop alcohol consumption immediately",
                    "Maintain healthy weight",
                    "Get adequate rest",
                    "Avoid hepatotoxic substances"
                ],
                'medical': [
                    "See a hepatologist immediately",
                    "Get liver function tests",
                    "Schedule an ultrasound",
                    "Discuss treatment options"
                ]
            },
            'Moderate Risk': {
                'diet': [
                    "Limit fatty foods",
                    "Increase whole grains",
                    "Add liver-supporting vegetables",
                    "Reduce sugar intake"
                ],
                'lifestyle': [
                    "Limit alcohol intake",
                    "Exercise regularly",
                    "Maintain work-life balance",
                    "Practice stress management"
                ],
                'medical': [
                    "Schedule liver function tests",
                    "Consult with a specialist",
                    "Monitor enzyme levels",
                    "Get regular check-ups"
                ]
            },
            'Low Risk': {
                'diet': [
                    "Maintain balanced nutrition",
                    "Stay hydrated",
                    "Eat liver-healthy foods",
                    "Limit processed foods"
                ],
                'lifestyle': [
                    "Exercise moderately",
                    "Practice good sleep habits",
                    "Manage stress levels",
                    "Maintain healthy weight"
                ],
                'medical': [
                    "Get annual check-ups",
                    "Monitor liver health",
                    "Keep medical records updated",
                    "Discuss prevention strategies"
                ]
            }
        },
        'diabetes': {
            'High Risk': {
                'diet': [
                    "Monitor carbohydrate intake strictly",
                    "Follow a diabetes-specific meal plan",
                    "Control portion sizes",
                    "Choose low glycemic foods"
                ],
                'lifestyle': [
                    "Check blood sugar regularly",
                    "Exercise under supervision",
                    "Maintain foot care",
                    "Monitor weight closely"
                ],
                'medical': [
                    "See an endocrinologist immediately",
                    "Get HbA1c tested",
                    "Discuss medication options",
                    "Schedule regular check-ups"
                ]
            },
            'Moderate Risk': {
                'diet': [
                    "Reduce refined carbohydrates",
                    "Increase fiber intake",
                    "Choose whole grains",
                    "Monitor sugar intake"
                ],
                'lifestyle': [
                    "Exercise regularly",
                    "Maintain healthy weight",
                    "Monitor blood sugar",
                    "Practice stress management"
                ],
                'medical': [
                    "Schedule diabetes screening",
                    "Consult with nutritionist",
                    "Get regular check-ups",
                    "Monitor blood pressure"
                ]
            },
            'Low Risk': {
                'diet': [
                    "Follow balanced diet",
                    "Limit added sugars",
                    "Choose complex carbs",
                    "Stay hydrated"
                ],
                'lifestyle': [
                    "Regular physical activity",
                    "Maintain healthy weight",
                    "Get adequate sleep",
                    "Manage stress levels"
                ],
                'medical': [
                    "Annual check-ups",
                    "Regular blood sugar tests",
                    "Monitor health changes",
                    "Discuss prevention strategies"
                ]
            }
        }
    }
    
    return suggestions.get(prediction_type, {}).get(category, {})

@login_required
def chatbot_view(request, prediction_id):
    prediction = get_object_or_404(PredictionHistory, id=prediction_id, user=request.user)
    
    # Get suggestions based on prediction type and category
    suggestions = get_suggestions(prediction.test_type, prediction.risk_percentage, prediction.category)
    
    context = {
        'prediction': prediction,
        'suggestions': suggestions,
    }
    
    return render(request, 'chatbot.html', context)

@login_required
def handle_chatbot_query(request, prediction_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not user_message.strip():
                return JsonResponse({
                    'response': 'Please enter a valid question.'
                })
            
            prediction = get_object_or_404(PredictionHistory, id=prediction_id, user=request.user)
            
            # Create context for Gemini
            context = f"""
            You are a medical AI assistant. Based on the following health information and user's question, 
            provide a detailed, professional response. Focus on giving actionable advice while being empathetic.
            
            User's Health Information:
            - Test Type: {prediction.get_test_type_display()}
            - Risk Level: {prediction.category}
            - Risk Percentage: {prediction.risk_percentage}%
            - Previous Advice: {prediction.advice}
            - Test Date: {prediction.date_created.strftime('%Y-%m-%d')}
            
            User's Input Data:
            {json.dumps(prediction.input_data, indent=2)}
            
            User's Question: {user_message}
            
            Please provide a detailed response that:
            1. Directly addresses the user's question
            2. Gives specific recommendations based on their risk level
            3. Suggests lifestyle modifications if relevant
            4. Provides actionable steps they can take
            5. Mentions when they should consult a healthcare provider
            
            Keep the tone professional but friendly, and ensure all advice is evidence-based.
            """
            
            try:
                # Get response from Gemini
                response = client.models.generate_content(
                    model='models/gemini-2.5-flash',
                    contents=context
                )
                
                if not response or not response.text:
                    raise Exception("Empty response from Gemini API")
                
                # Format the response for better readability
                formatted_response = response.text.replace('\n', '<br>')
                
                return JsonResponse({'response': formatted_response})
                
            except Exception as e:
                print(f"Gemini API Error: {str(e)}")
                return JsonResponse({
                    'response': 'I apologize, but I encountered an error processing your question. Please try rephrasing your question or try again later.'
                })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'response': 'Invalid request format. Please try again.'
            })
        except PredictionHistory.DoesNotExist:
            return JsonResponse({
                'response': 'Prediction not found. Please try again.'
            })
        except Exception as e:
            print(f"General Error: {str(e)}")
            return JsonResponse({
                'response': 'An unexpected error occurred. Please try again later.'
            })
    
    return JsonResponse({'response': 'Invalid request method.'})
