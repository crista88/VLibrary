import json
import os

from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from .factories import PaymentProcessorFactory


def index(request):
    return render(request, 'index.html')


@csrf_exempt
def checkout(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        package_type = data.get('package_type')
        email = data.get('email')
        processor_type = 'stripe'

        try:
            processor = PaymentProcessorFactory.get_processor(processor_type)
            session = processor.create_session(package_type, settings.SUCCESS_URL, settings.CANCEL_URL, email)
            return JsonResponse({'id': session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return render(request, 'checkout.html', {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    })


def success(request):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        package_type = request.POST.get('package_type')
        if user_email and package_type:
            send_email_with_zip(user_email, package_type)
        return redirect('thank_you')
    else:
        return render(request, 'success.html')


def thank_you(request):
    return render(request,'thank_you.html')


def send_email_with_zip(user_email, package_type):
    if package_type == 'individual_use':
        zip_file_path = 'C:/Users/Personal/Desktop/Packages/individual_use.zip'
    elif package_type == 'professional_use':
        zip_file_path = 'C:/Users/Personal/Desktop/Packages/professional_package.zip'
    elif package_type == 'master_use':
        zip_file_path = 'C:/Users/Personal/Desktop/Packages/master_package.zip'
    else:
        raise ValueError("Invalid package type")

    if os.path.exists(zip_file_path):
        email = EmailMessage(
            'Your Video Library Access',
            'Thank you for your purchase. Please find attached the zip file with the courses.',
            'from@example.com',
            [user_email],
        )
        with open(zip_file_path, 'rb') as f:
            email.attach('courses.zip', f.read(), 'application/zip')
        email.send()
    else:
        raise FileNotFoundError("Zip file not found")


def cancel(request):
    return render(request, 'cancel.html')
