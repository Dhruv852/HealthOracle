from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import PredictionHistory
from .chatbot_models import ChatbotSuggestion
import google.generativeai as genai
import json
from django.conf import settings

# Configure Gemini API
def configure_gemini():
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        return genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        print(f"Error configuring Gemini: {str(e)}")
        return None

@login_required
def chatbot_view(request, prediction_id=None):
    prediction = None
    is_prediction_specific = False
    
    if prediction_id:
        prediction = get_object_or_404(PredictionHistory, id=prediction_id, user=request.user)
        is_prediction_specific = True
    
    return render(request, 'chatbot.html', {
        'prediction': prediction,
        'is_prediction_specific': is_prediction_specific
    })

@login_required
def get_suggestions(request, prediction_id):
    if request.method == 'POST':
        try:
            prediction = get_object_or_404(PredictionHistory, id=prediction_id, user=request.user)
            
            # Check if we already have suggestions for this prediction
            existing_suggestion = ChatbotSuggestion.objects.filter(prediction=prediction).first()
            if existing_suggestion:
                return JsonResponse({
                    'success': True,
                    'suggestion': existing_suggestion.suggestion_text
                })
            
            # Format the prediction data for Gemini
            context = {
                'test_type': prediction.get_test_type_display(),
                'risk_percentage': prediction.risk_percentage,
                'category': prediction.category,
                'input_data': prediction.input_data,
                'date': prediction.date_created.strftime('%Y-%m-%d')
            }
            
            # Generate prompt for Gemini
            prompt = f"""Based on the following health test data, provide 10-15 specific, actionable health suggestions:
            Test Type: {context['test_type']}
            Risk Level: {context['category']} ({context['risk_percentage']}%)
            Test Date: {context['date']}
            Input Data: {json.dumps(context['input_data'], indent=2)}
            
            Format your response as a bullet-pointed list (10-15 points total) covering:
            • Immediate actions and precautions
            • Recommended medical tests and screenings
            • Diet and exercise modifications
            • Lifestyle changes and stress management
            • Monitoring and warning signs
            • Prevention strategies
            
            IMPORTANT FORMATTING INSTRUCTIONS:
            1. Start each point with a bullet point (•)
            2. Keep each point concise (1-2 sentences maximum)
            3. Use **bold** for important terms or concepts
            4. Keep the total response under 200 words
            5. Make each point specific, actionable, and directly related to the test results and risk level
            6. Focus on practical steps the patient can take immediately
            
            Your response should be professional, evidence-based, and easy to read."""
            
            try:
                # Initialize Gemini
                model = configure_gemini()
                if not model:
                    raise Exception("Failed to initialize Gemini model")
                
                response = model.generate_content(prompt)
                
                if not response or not response.text:
                    raise Exception("Empty response from Gemini API")
                
                # Store suggestion in database
                suggestion = ChatbotSuggestion.objects.create(
                    prediction=prediction,
                    suggestion_text=response.text
                )
                
                return JsonResponse({
                    'success': True,
                    'suggestion': suggestion.suggestion_text
                })
            except Exception as e:
                print(f"Gemini API Error: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': 'Unable to generate health suggestions at this time. Please try again later.'
                })
                
        except PredictionHistory.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Prediction not found'
            })
        except Exception as e:
            print(f"General Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'An unexpected error occurred. Please try again later.'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def handle_chatbot_query(request, prediction_id=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({
                    'response': 'Please enter a valid question.'
                })
            
            # Initialize Gemini
            model = configure_gemini()
            if not model:
                raise Exception("Failed to initialize Gemini model")

            if prediction_id:
                # Prediction-specific chat mode
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
                
                IMPORTANT FORMATTING INSTRUCTIONS:
                1. Keep your response under 200 words
                2. Use bullet points (•) for lists and recommendations
                3. Focus on specific advice related to the user's test results and condition
                4. Be empathetic and professional
                5. Include relevant medical terminology while keeping it understandable
                """
            else:
                # General healthcare chat mode
                context = f"""
                You are a knowledgeable and empathetic healthcare AI assistant using the Gemini 2.0 Flash model. 
                Your role is to provide helpful, evidence-based health information and guidance while maintaining 
                appropriate medical disclaimers. 

                CORE RESPONSIBILITIES:
                1. Provide accurate, up-to-date health information
                2. Explain medical concepts in clear, understandable terms
                3. Encourage appropriate professional medical consultation
                4. Maintain a professional yet friendly tone
                5. Focus on general wellness and preventive care
                6. Respect medical ethics and privacy

                RESPONSE GUIDELINES:
                1. Keep responses clear and concise (under 200 words)
                2. Use bullet points (•) for lists and recommendations
                3. Bold (**) important terms or warnings
                4. Include relevant medical terminology with plain language explanations
                5. Always clarify that this is general information, not medical diagnosis
                6. Recommend professional medical consultation when appropriate

                IMPORTANT: If the question involves emergency medical situations, mental health crises, 
                or serious medical conditions, always emphasize the importance of seeking immediate 
                professional medical care.

                User's Question: {user_message}

                Please provide a helpful, accurate, and professional response while following the above guidelines.
                """
            
            try:
                response = model.generate_content(context)
                
                if not response or not response.text:
                    raise Exception("Empty response from Gemini API")
                
                return JsonResponse({
                    'response': response.text
                })
                
            except Exception as e:
                print(f"Gemini API Error: {str(e)}")
                return JsonResponse({
                    'response': 'I apologize, but I encountered an error generating a response. Please try again or rephrase your question.'
                })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'response': 'Invalid request format. Please try again.'
            })
        except Exception as e:
            print(f"Error in handle_chatbot_query: {str(e)}")
            return JsonResponse({
                'response': 'I apologize, but I encountered an error processing your request. Please try again.'
            })
    
    return JsonResponse({'response': 'Invalid request method'})