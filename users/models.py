from django.db import models


class User(models.Model):

    ROLE_CHOICES = (
        ('worker', 'Worker'),
        ('contractor', 'Contractor'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
    )

    phone = models.CharField(
        max_length=15
    )

    password = models.CharField(
        max_length=255
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    skill = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    experience = models.IntegerField(
        default=0
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    state = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    expected_salary = models.IntegerField(
        default=0
    )

    available = models.BooleanField(
        default=True
    )

    profile_image = models.URLField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.name


class Job(models.Model):

    contractor = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    salary = models.IntegerField()

    location = models.CharField(
        max_length=200
    )

    required_skill = models.CharField(
        max_length=100
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.title


class JobApplication(models.Model):

    worker = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=20,
        default='pending'
    )

    class Meta:

        unique_together = (
            'worker',
            'job'
        )

    def __str__(self):

        return f"{self.worker.name} applied for {self.job.title}"


class DoctorProfile(models.Model):

    doctor = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    specialization = models.CharField(
        max_length=100
    )

    experience = models.IntegerField(
        default=0
    )

    clinic_name = models.CharField(
        max_length=200
    )

    clinic_address = models.TextField()

    consultation_fee = models.IntegerField(
        default=0
    )

    available_days = models.CharField(
        max_length=200
    )

    available_time = models.CharField(
        max_length=100
    )

    is_verified = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.doctor.name


class Appointment(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    worker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='worker_appointments'
    )

    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_appointments'
    )

    appointment_date = models.DateField()

    appointment_time = models.CharField(
        max_length=50
    )

    problem_description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    prescription_file = models.FileField(
        upload_to='prescriptions/',
        null=True,
        blank=True
    )

    doctor_notes = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.worker.name} -> {self.doctor.name}"



class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.title
    

class ChatMessage(models.Model):

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.sender.name} -> {self.receiver.name}"
