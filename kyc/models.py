import uuid
from django.db import models
from django.conf import settings


class KYCDocument(models.Model):
    """KYC verification documents with country-specific ID details."""

    DOCUMENT_TYPES = [
        ('passport', 'Passport'),
        ('drivers_license', "Driver's License"),
        ('national_id', 'National ID Card'),
        ('residence_permit', 'Residence Permit'),
        ('voter_id', 'Voter ID Card'),
        ('tax_id', 'Tax Identification Card'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='kyc_document')

    # Document identity details
    document_type = models.CharField(max_length=25, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=100, help_text='ID/passport number as shown on document')

    # Country-specific fields
    issuing_country = models.CharField(
        max_length=100,
        help_text='Country that issued the document',
    )
    issuing_authority = models.CharField(
        max_length=200,
        blank=True,
        help_text='Issuing authority or department (e.g. Home Office, DMV)',
    )

    # Personal details for cross-verification
    date_of_birth = models.DateField(
        null=True, blank=True,
        help_text='Date of birth as shown on the document',
    )
    nationality = models.CharField(
        max_length=100,
        blank=True,
        help_text='Nationality as shown on the document',
    )

    # Document validity
    issue_date = models.DateField(null=True, blank=True, help_text='Date the document was issued')
    expires_at = models.DateField(null=True, blank=True, help_text='Expiry date of the document')

    # Document images
    front_image = models.ImageField(upload_to='kyc/front/')
    back_image = models.ImageField(upload_to='kyc/back/', blank=True, null=True)
    selfie_image = models.ImageField(upload_to='kyc/selfie/')

    # Review workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_kyc',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'KYC Document'
        verbose_name_plural = 'KYC Documents'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.email} - {self.document_type} ({self.status})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Sync user KYC status with document status
        status_map = {
            'verified': 'verified',
            'rejected': 'rejected',
            'submitted': 'submitted',
        }
        new_status = status_map.get(self.status)
        if new_status:
            self.user.kyc_status = new_status
            self.user.save(update_fields=['kyc_status'])

