from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import KYCDocument
from accounts.models import ActivityLog
from notifications.models import Notification

# File upload limits
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']


def validate_uploaded_file(file, field_name):
    """Validate uploaded file size and type."""
    if not file:
        return None
    
    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(f'{field_name}: File size must be less than 5MB. Your file is {file.size / (1024*1024):.1f}MB.')
    
    # Check file type
    content_type = file.content_type
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise ValidationError(f'{field_name}: Only JPEG, PNG, and WebP images are allowed. Got: {content_type}')
    
    return file


@login_required
def upload_kyc(request):
    """Upload KYC documents."""
    existing_kyc = KYCDocument.objects.filter(user=request.user).first()
    if existing_kyc and existing_kyc.status in ['submitted', 'verified']:
        messages.info(request, 'You have already submitted KYC documents.')
        return redirect('kyc:status')

    if request.method == 'POST':
        document_type = request.POST.get('document_type')
        document_number = request.POST.get('document_number', '').strip()
        issuing_country = request.POST.get('issuing_country', '').strip()
        issuing_authority = request.POST.get('issuing_authority', '').strip()
        date_of_birth = request.POST.get('date_of_birth') or None
        nationality = request.POST.get('nationality', '').strip()
        issue_date = request.POST.get('issue_date') or None
        expires_at = request.POST.get('expires_at') or None
        front_image = request.FILES.get('front_image')
        back_image = request.FILES.get('back_image')
        selfie_image = request.FILES.get('selfie_image')

        if not all([document_type, document_number, issuing_country, front_image, selfie_image]):
            messages.error(request, 'Please fill all required fields and upload both front image and selfie.')
            return redirect('kyc:upload')
        
        # Validate uploaded files
        try:
            front_image = validate_uploaded_file(front_image, 'Front Image')
            back_image = validate_uploaded_file(back_image, 'Back Image')
            selfie_image = validate_uploaded_file(selfie_image, 'Selfie')
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('kyc:upload')

        kyc_document_fields = dict(
            document_type=document_type,
            document_number=document_number,
            issuing_country=issuing_country,
            issuing_authority=issuing_authority,
            date_of_birth=date_of_birth,
            nationality=nationality,
            issue_date=issue_date,
            expires_at=expires_at,
            front_image=front_image,
            selfie_image=selfie_image,
            status='submitted',
            rejection_reason='',
        )

        if existing_kyc:
            for attr, field_value in kyc_document_fields.items():
                setattr(existing_kyc, attr, field_value)
            if back_image:
                existing_kyc.back_image = back_image
            existing_kyc.save()
        else:
            KYCDocument.objects.create(
                user=request.user,
                back_image=back_image,
                **kyc_document_fields,
            )

        request.user.kyc_status = 'submitted'
        request.user.save()

        ActivityLog.objects.create(
            user=request.user,
            action='kyc_submitted',
            description='KYC documents submitted for verification',
        )

        Notification.create_notification(
            user=request.user,
            title='KYC Submitted',
            message='Your KYC documents have been submitted for verification.',
            notification_type='info',
        )

        messages.success(request, 'KYC documents submitted successfully! We will review them within 24–48 hours.')
        return redirect('kyc:status')

    return render(request, 'kyc/upload.html')


@login_required
def kyc_status(request):
    """Check KYC status."""
    kyc = KYCDocument.objects.filter(user=request.user).first()
    return render(request, 'kyc/status.html', {'kyc': kyc})

