import json
import os

from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
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

            if package_type == 'individual_use':
                return redirect('apply_coupon')  # Redirectează către aplicarea cuponului pentru pachetul individual_use
            else:
                return redirect('thank_you')  # Redirectează către pagina de mulțumire pentru celelalte pachete
    else:
        return render(request, 'success.html')


def thank_you(request):
    return render(request,'thank_you.html')


# def send_email_with_zip(user_email, package_type):
#     if package_type == 'individual_use':
#         zip_file_path = 'C:/Users/Personal/Desktop/Packages/individual_use.zip'
#     elif package_type == 'professional_use':
#         zip_file_path = 'C:/Users/Personal/Desktop/Packages/professional_package.zip'
#     elif package_type == 'master_use':
#         zip_file_path = 'C:/Users/Personal/Desktop/Packages/master_package.zip'
#     else:
#         raise ValueError("Invalid package type")
#
#     if os.path.exists(zip_file_path):
#         email = EmailMessage(
#             'Your Video Library Access',
#             'Thank you for your purchase. Please find attached the zip file with the courses.',
#             'from@example.com',
#             [user_email],
#         )
#         with open(zip_file_path, 'rb') as f:
#             email.attach('courses.zip', f.read(), 'application/zip')
#         email.send()
#     else:
#         raise FileNotFoundError("Zip file not found")

def send_email_with_zip(user_email, package_type):
    if package_type == 'individual_use':
        zip_file_path = 'C:/Users/Personal/Desktop/Packages/individual_use.zip'
        coupon_code = 'Q2YFF7gn'  # Codul cuponului de folosit

        if os.path.exists(zip_file_path):
            email_subject = 'Your Video Library Access'
            email_body_html = render_to_string('individual_use_email.html', {
                'coupon_code': coupon_code,
                'stripe_payment_url': reverse('stripe_checkout'),
            })
            email_body_text = strip_tags(email_body_html)  # Transformăm HTML-ul în text simplu

            email = EmailMessage(
                email_subject,
                email_body_text,
                'contact@vlibrary.pro',
                [user_email],
            )
            email.attach('courses.zip', open(zip_file_path, 'rb').read(), 'application/zip')
            email.send()

            return redirect('apply_coupon')
        else:
            raise FileNotFoundError("Zip file not found")

    elif package_type in ['professional_use', 'master_use']:
        zip_file_path = 'C:/Users/Personal/Desktop/Packages/' + package_type + '_package.zip'
        if os.path.exists(zip_file_path):
            email_subject = 'Your Video Library Access'
            email_body_html = render_to_string(package_type + '_use_email.html')
            email_body_text = strip_tags(email_body_html)
            email = EmailMessage(
                email_subject,
                email_body_text,
                'contact@vlibrary.pro',
                [user_email],
            )
            email.attach('courses.zip', open(zip_file_path, 'rb').read(), 'application/zip')
            email.send()

        else:
            raise FileNotFoundError("Zip file not found")

    else:
        raise ValueError("Invalid package type")


def cancel(request):
    return render(request, 'cancel.html')


def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        if coupon_code == 'Q2YFF7gn':  #  logica ta de validare a cuponului
            messages.success(request, 'Coupon applied successfully!')
            # Redirectează utilizatorul către pagina de succes
            return redirect('stripe_checkout')
        else:
            messages.error(request, 'Invalid coupon code. Please try again.')

            # Întoarce o pagină pentru aplicarea cuponului
    return render(request, 'apply_coupon_page.html')