from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.hashers import (
    make_password,
    check_password
)

import cloudinary.uploader

from .models import (
    User,
    Job,
    JobApplication,
    DoctorProfile,
    Appointment,
    Notification,
    ChatMessage
)

from .jwt_utils import (
    generate_token,
    decode_token
)


@api_view(['POST'])
def signup(request):
    data = request.data

    user = User.objects.create(

        name=data['name'],

        email=data['email'],

        phone=data['phone'],

        password=make_password(
            data['password']
        ),

        role=data['role'],

        skill=data.get('skill'),

        experience=data.get(
            'experience',
            0
        ),

        city=data.get('city'),

        state=data.get('state'),

        expected_salary=data.get(
            'expected_salary',
            0
        ),

        available=data.get(
            'available',
            True
        )
    )

    return Response({

        "message": "User created successfully",

        "user_id": user.id
    })


@api_view(['POST'])
def login(request):
    email = request.data.get('email')

    password = request.data.get('password')

    try:

        user = User.objects.get(
            email=email
        )

    except User.DoesNotExist:

        return Response(

            {
                "message": "User not found"
            },

            status=400
        )

    if not check_password(
            password,
            user.password
    ):
        return Response(

            {
                "message": "Invalid password"
            },

            status=400
        )

    refresh = RefreshToken.for_user(
        user
    )

    return Response({

        "message": "Login successful",

        "access": str(
            refresh.access_token
        ),

        "refresh": str(
            refresh
        ),

        "role": user.role,

        "name": user.name,

        "email": user.email,
    })


@api_view(['GET'])
def profile(request):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    try:

        token = auth_header.split(' ')[1]

    except:

        return Response({
            "error": "Invalid token format"
        })

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid or expired token"
        })

    try:

        user = User.objects.get(
            id=payload['user_id']
        )

        return Response({

            "user_id": user.id,

            "name": user.name,

            "email": user.email,

            "phone": user.phone,

            "role": user.role,

            "skill": user.skill,

            "experience": user.experience,

            "city": user.city,

            "state": user.state,

            "expected_salary": user.expected_salary,

            "available": user.available
        })

    except User.DoesNotExist:

        return Response({
            "error": "User not found"
        })


@api_view(['PUT'])
def update_profile(request):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    try:

        token = auth_header.split(' ')[1]

    except:

        return Response({
            "error": "Invalid token format"
        })

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid or expired token"
        })

    try:

        user = User.objects.get(
            id=payload['user_id']
        )

        data = request.data

        user.name = data.get(
            'name',
            user.name
        )

        user.phone = data.get(
            'phone',
            user.phone
        )

        user.role = data.get(
            'role',
            user.role
        )

        user.skill = data.get(
            'skill',
            user.skill
        )

        user.experience = data.get(
            'experience',
            user.experience
        )

        user.city = data.get(
            'city',
            user.city
        )

        user.state = data.get(
            'state',
            user.state
        )

        user.expected_salary = data.get(
            'expected_salary',
            user.expected_salary
        )

        user.available = data.get(
            'available',
            user.available
        )

        user.save()

        return Response({
            "message": "Profile updated successfully"
        })

    except User.DoesNotExist:

        return Response({
            "error": "User not found"
        })


@api_view(['GET'])
def search_workers(request):
    skill = request.GET.get('skill')

    city = request.GET.get('city')

    workers = User.objects.filter(
        role='worker'
    )

    if skill:
        workers = workers.filter(
            skill__icontains=skill
        )

    if city:
        workers = workers.filter(
            city__icontains=city
        )

    data = []

    for worker in workers:
        data.append({

            "id": worker.id,

            "name": worker.name,

            "skill": worker.skill,

            "experience": worker.experience,

            "city": worker.city,

            "state": worker.state,

            "expected_salary": worker.expected_salary,

            "available": worker.available
        })

    return Response(data)


@api_view(['POST'])
def create_job(request):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    token = auth_header.split(' ')[1]

    payload = decode_token(token)

    contractor = User.objects.get(
        id=payload['user_id']
    )

    if contractor.role != 'contractor':
        return Response({
            "error": "Only contractors can create jobs"
        })

    data = request.data

    job = Job.objects.create(

        contractor=contractor,

        title=data['title'],

        description=data['description'],

        salary=data['salary'],

        location=data['location'],

        required_skill=data['required_skill']
    )

    return Response({

        "message": "Job created successfully",

        "job_id": job.id
    })


@api_view(['GET'])
def list_jobs(request):
    jobs = Job.objects.all().order_by('-id')

    data = []

    for job in jobs:
        data.append({

            "job_id": job.id,

            "title": job.title,

            "description": job.description,

            "salary": job.salary,

            "location": job.location,

            "required_skill": job.required_skill,

            "contractor_name": job.contractor.name
        })

    return Response(data)


@api_view(['POST'])
def apply_job(request, job_id):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    token = auth_header.split(' ')[1]

    payload = decode_token(token)

    worker = User.objects.get(
        id=payload['user_id']
    )

    if worker.role != 'worker':
        return Response({
            "error": "Only workers can apply"
        })

    job = Job.objects.get(id=job_id)

    application, created = JobApplication.objects.get_or_create(

        worker=worker,

        job=job
    )

    if not created:
        return Response({
            "error": "Already applied"
        })

    return Response({
        "message": "Job applied successfully"
    })


@api_view(['GET'])
def my_applications(request):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    token = auth_header.split(' ')[1]

    payload = decode_token(token)

    worker = User.objects.get(
        id=payload['user_id']
    )

    applications = JobApplication.objects.filter(
        worker=worker
    )

    data = []

    for application in applications:
        job = application.job

        data.append({

            "application_id": application.id,

            "job_title": job.title,

            "company": job.contractor.name,

            "status": application.status
        })

    return Response(data)


@api_view(['POST'])
def create_doctor_profile(request):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    try:

        token = auth_header.split(' ')[1]

    except:

        return Response({
            "error": "Invalid token format"
        })

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid or expired token"
        })

    try:

        doctor = User.objects.get(
            id=payload['user_id']
        )

        if doctor.role != 'doctor':
            return Response({
                "error": "Only doctors can create profile"
            })

        if DoctorProfile.objects.filter(
                doctor=doctor
        ).exists():
            return Response({
                "error": "Profile already exists"
            })

        data = request.data

        profile = DoctorProfile.objects.create(

            doctor=doctor,

            specialization=data['specialization'],

            experience=data['experience'],

            clinic_name=data['clinic_name'],

            clinic_address=data['clinic_address'],

            consultation_fee=data['consultation_fee'],

            available_days=data['available_days'],

            available_time=data['available_time']
        )

        return Response({

            "message": "Doctor profile created successfully",

            "profile_id": profile.id,

            "doctor_name": doctor.name,

            "specialization": profile.specialization,

            "experience": profile.experience,

            "clinic_name": profile.clinic_name,

            "clinic_address": profile.clinic_address,

            "consultation_fee": profile.consultation_fee,

            "available_days": profile.available_days,

            "available_time": profile.available_time
        })

    except User.DoesNotExist:

        return Response({
            "error": "Doctor not found"
        })

    except Exception as e:

        return Response({
            "error": str(e)
        })


@api_view(['GET'])
def list_doctors(request):
    specialization = request.GET.get(
        'specialization'
    )

    doctors = DoctorProfile.objects.filter(
        is_verified=True
    )

    if specialization:
        doctors = doctors.filter(
            specialization__icontains=specialization
        )

    data = []

    for doctor in doctors:
        data.append({

            "profile_id": doctor.id,

            "doctor_name": doctor.doctor.name,

            "email": doctor.doctor.email,

            "phone": doctor.doctor.phone,

            "specialization": doctor.specialization,

            "experience": doctor.experience,

            "clinic_name": doctor.clinic_name,

            "clinic_address": doctor.clinic_address,

            "consultation_fee": doctor.consultation_fee,

            "available_days": doctor.available_days,

            "available_time": doctor.available_time
        })

    return Response(data)


@api_view(['POST'])
def book_appointment(request):
    token = request.headers.get('Authorization')

    if not token:
        return Response({
            "error": "Token required"
        }, status=401)

    try:
        token = token.split(" ")[1]
    except:
        return Response({
            "error": "Invalid token format"
        }, status=401)

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid token"
        }, status=401)

    worker = User.objects.filter(
        id=payload['user_id']
    ).first()

    if not worker:
        return Response({
            "error": "User not found"
        }, status=404)

    if worker.role != "worker":
        return Response({
            "error": "Only workers can book appointments"
        }, status=403)

    doctor_id = request.data.get('doctor_id')

    doctor = User.objects.filter(
        id=doctor_id,
        role="doctor"
    ).first()

    if not doctor:
        return Response({
            "error": "Doctor not found"
        }, status=404)

    appointment = Appointment.objects.create(

        worker=worker,
        doctor=doctor,
        appointment_date=request.data.get('appointment_date'),
        appointment_time=request.data.get('appointment_time'),
        problem_description=request.data.get('problem_description'),
        status="pending"
    )

    # NOTIFICATION CREATE 😎🔥
    Notification.objects.create(

        user=doctor,
        title="New Appointment",
        message=f"{worker.name} booked an appointment with you"
    )

    return Response({

        "message": "Appointment booked successfully",

        "appointment_id": appointment.id,

        "doctor_name": doctor.name,

        "appointment_date": appointment.appointment_date,

        "appointment_time": appointment.appointment_time,

        "status": appointment.status
    })


@api_view(['GET'])
def doctor_appointments(request):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    try:

        token = auth_header.split(' ')[1]

    except:

        return Response({
            "error": "Invalid token format"
        })

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid or expired token"
        })

    try:

        doctor = User.objects.get(
            id=payload['user_id']
        )

        if doctor.role != 'doctor':
            return Response({
                "error": "Only doctors can view appointments"
            })

        appointments = Appointment.objects.filter(
            doctor=doctor
        ).order_by('-id')

        data = []

        for appointment in appointments:
            data.append({

                "appointment_id": appointment.id,

                "worker_name": appointment.worker.name,

                "worker_phone": appointment.worker.phone,

                "appointment_date": appointment.appointment_date,

                "appointment_time": appointment.appointment_time,

                "problem_description": appointment.problem_description,

                "status": appointment.status
            })

        return Response(data)

    except User.DoesNotExist:

        return Response({
            "error": "Doctor not found"
        })

    except Exception as e:

        return Response({
            "error": str(e)
        })


@api_view(['PUT'])
def update_appointment_status(
        request,
        appointment_id
):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    try:

        token = auth_header.split(' ')[1]

    except:

        return Response({
            "error": "Invalid token format"
        })

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid or expired token"
        })

    try:

        doctor = User.objects.get(
            id=payload['user_id']
        )

        if doctor.role != 'doctor':
            return Response({
                "error": "Only doctors can update appointments"
            })

        try:

            appointment = Appointment.objects.get(
                id=appointment_id,
                doctor=doctor
            )

        except Appointment.DoesNotExist:

            return Response({
                "error": "Appointment not found"
            })

        status = request.data.get('status')

        valid_status = [
            'pending',
            'accepted',
            'rejected',
            'completed'
        ]

        if status not in valid_status:
            return Response({
                "error": "Invalid status"
            })

        appointment.status = status

        appointment.save()

        return Response({

            "message": "Appointment status updated",

            "appointment_id": appointment.id,

            "worker_name": appointment.worker.name,

            "status": appointment.status
        })

    except User.DoesNotExist:

        return Response({
            "error": "Doctor not found"
        })

    except Exception as e:

        return Response({
            "error": str(e)
        })


@api_view(['GET'])
def my_appointments(request):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    try:

        token = auth_header.split(' ')[1]

    except:

        return Response({
            "error": "Invalid token format"
        })

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid or expired token"
        })

    try:

        worker = User.objects.get(
            id=payload['user_id']
        )

        if worker.role != 'worker':
            return Response({
                "error": "Only workers can view appointments"
            })

        appointments = Appointment.objects.filter(
            worker=worker
        ).order_by('-id')

        data = []

        for appointment in appointments:
            data.append({

                "appointment_id": appointment.id,

                "doctor_name": appointment.doctor.name,

                "doctor_phone": appointment.doctor.phone,

                "appointment_date": appointment.appointment_date,

                "appointment_time": appointment.appointment_time,

                "problem_description": appointment.problem_description,

                "status": appointment.status
            })

        return Response(data)

    except User.DoesNotExist:

        return Response({
            "error": "Worker not found"
        })

    except Exception as e:

        return Response({
            "error": str(e)
        })
    # LAST PART ONLY ADD KARO users/views.py ke END me


@api_view(['GET'])
def my_appointments(request):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    try:

        token = auth_header.split(' ')[1]

    except:

        return Response({
            "error": "Invalid token format"
        })

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid or expired token"
        })

    try:

        worker = User.objects.get(
            id=payload['user_id']
        )

        if worker.role != 'worker':
            return Response({
                "error": "Only workers can view appointments"
            })

        appointments = Appointment.objects.filter(
            worker=worker
        ).order_by('-id')

        data = []

        for appointment in appointments:
            data.append({

                "appointment_id": appointment.id,

                "doctor_name": appointment.doctor.name,

                "doctor_phone": appointment.doctor.phone,

                "appointment_date": appointment.appointment_date,

                "appointment_time": appointment.appointment_time,

                "problem_description": appointment.problem_description,

                "status": appointment.status
            })

        return Response(data)

    except User.DoesNotExist:

        return Response({
            "error": "Worker not found"
        })

    except Exception as e:

        return Response({
            "error": str(e)
        })


@api_view(['DELETE'])
def cancel_appointment(
        request,
        appointment_id
):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    try:

        token = auth_header.split(' ')[1]

    except:

        return Response({
            "error": "Invalid token format"
        })

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid or expired token"
        })

    try:

        worker = User.objects.get(
            id=payload['user_id']
        )

        if worker.role != 'worker':
            return Response({
                "error": "Only workers can cancel appointments"
            })

        try:

            appointment = Appointment.objects.get(
                id=appointment_id,
                worker=worker
            )

        except Appointment.DoesNotExist:

            return Response({
                "error": "Appointment not found"
            })

        appointment.delete()

        return Response({

            "message": "Appointment cancelled successfully"
        })

    except User.DoesNotExist:

        return Response({
            "error": "Worker not found"
        })

    except Exception as e:

        return Response({
            "error": str(e)
        })


@api_view(['GET'])
def all_users(request):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    try:

        token = auth_header.split(' ')[1]

    except:

        return Response({
            "error": "Invalid token format"
        })

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid or expired token"
        })

    try:

        admin = User.objects.get(
            id=payload['user_id']
        )

        if admin.role != 'admin':
            return Response({
                "error": "Only admins can view users"
            })

        role = request.GET.get('role')

        users = User.objects.all().order_by('-id')

        if role:
            users = users.filter(
                role=role
            )

        data = []

        for user in users:
            data.append({

                "user_id": user.id,

                "name": user.name,

                "email": user.email,

                "phone": user.phone,

                "role": user.role,

                "city": user.city,

                "state": user.state
            })

        return Response(data)

    except User.DoesNotExist:

        return Response({
            "error": "Admin not found"
        })

    except Exception as e:

        return Response({
            "error": str(e)
        })


@api_view(['DELETE'])
def delete_user(
        request,
        user_id
):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    try:

        token = auth_header.split(' ')[1]

    except:

        return Response({
            "error": "Invalid token format"
        })

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid or expired token"
        })

    try:

        admin = User.objects.get(
            id=payload['user_id']
        )

        if admin.role != 'admin':
            return Response({
                "error": "Only admins can delete users"
            })

        try:

            user = User.objects.get(
                id=user_id
            )

        except User.DoesNotExist:

            return Response({
                "error": "User not found"
            })

        if user.role == 'admin':
            return Response({
                "error": "Admin cannot be deleted"
            })

        user.delete()

        return Response({

            "message": "User deleted successfully"
        })

    except User.DoesNotExist:

        return Response({
            "error": "Admin not found"
        })

    except Exception as e:

        return Response({
            "error": str(e)
        })


@api_view(['GET'])
def admin_dashboard(request):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    try:

        token = auth_header.split(' ')[1]

    except:

        return Response({
            "error": "Invalid token format"
        })

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid or expired token"
        })

    try:

        admin = User.objects.get(
            id=payload['user_id']
        )

        if admin.role != 'admin':
            return Response({
                "error": "Only admins can access dashboard"
            })

        total_users = User.objects.count()

        total_workers = User.objects.filter(
            role='worker'
        ).count()

        total_doctors = User.objects.filter(
            role='doctor'
        ).count()

        total_contractors = User.objects.filter(
            role='contractor'
        ).count()

        total_admins = User.objects.filter(
            role='admin'
        ).count()

        total_jobs = Job.objects.count()

        total_appointments = Appointment.objects.count()

        return Response({

            "total_users": total_users,

            "total_workers": total_workers,

            "total_doctors": total_doctors,

            "total_contractors": total_contractors,

            "total_admins": total_admins,

            "total_jobs": total_jobs,

            "total_appointments": total_appointments
        })

    except User.DoesNotExist:

        return Response({
            "error": "Admin not found"
        })

    except Exception as e:

        return Response({
            "error": str(e)
        })


@api_view(['PUT'])
def verify_doctor(
        request,
        doctor_profile_id
):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    try:

        token = auth_header.split(' ')[1]

    except:

        return Response({
            "error": "Invalid token format"
        })

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid or expired token"
        })

    try:

        admin = User.objects.get(
            id=payload['user_id']
        )

        if admin.role != 'admin':
            return Response({
                "error": "Only admins can verify doctors"
            })

        try:

            doctor_profile = DoctorProfile.objects.get(
                id=doctor_profile_id
            )

        except DoctorProfile.DoesNotExist:

            return Response({
                "error": "Doctor profile not found"
            })

        doctor_profile.is_verified = True

        doctor_profile.save()

        return Response({

            "message": "Doctor verified successfully",

            "doctor_name": doctor_profile.doctor.name,

            "is_verified": doctor_profile.is_verified
        })

    except User.DoesNotExist:

        return Response({
            "error": "Admin not found"
        })

    except Exception as e:

        return Response({
            "error": str(e)
        })


@api_view(['GET'])
def pending_doctors(request):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    try:

        token = auth_header.split(' ')[1]

    except:

        return Response({
            "error": "Invalid token format"
        })

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid or expired token"
        })

    try:

        admin = User.objects.get(
            id=payload['user_id']
        )

        if admin.role != 'admin':
            return Response({
                "error": "Only admins can view pending doctors"
            })

        doctors = DoctorProfile.objects.filter(
            is_verified=False
        ).order_by('-id')

        data = []

        for doctor in doctors:
            data.append({

                "profile_id": doctor.id,

                "doctor_name": doctor.doctor.name,

                "email": doctor.doctor.email,

                "phone": doctor.doctor.phone,

                "specialization": doctor.specialization,

                "experience": doctor.experience,

                "clinic_name": doctor.clinic_name,

                "clinic_address": doctor.clinic_address,

                "consultation_fee": doctor.consultation_fee,

                "available_days": doctor.available_days,

                "available_time": doctor.available_time,

                "is_verified": doctor.is_verified
            })

        return Response(data)

    except User.DoesNotExist:

        return Response({
            "error": "Admin not found"
        })

    except Exception as e:

        return Response({
            "error": str(e)
        })


@api_view(['POST'])
def upload_profile_image(request):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    try:

        token = auth_header.split(' ')[1]

    except:

        return Response({
            "error": "Invalid token format"
        })

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid or expired token"
        })

    try:

        user = User.objects.get(
            id=payload['user_id']
        )

        if 'image' not in request.FILES:
            return Response({
                "error": "Image file is required"
            })

        image = request.FILES['image']

        upload_result = cloudinary.uploader.upload(
            image
        )

        image_url = upload_result['secure_url']

        user.profile_image = image_url

        user.save()

        return Response({

            "message": "Profile image uploaded successfully",

            "profile_image": image_url
        })

    except User.DoesNotExist:

        return Response({
            "error": "User not found"
        })

    except Exception as e:

        return Response({
            "error": str(e)
        })


@api_view(['GET'])
def my_notifications(request):
    auth_header = request.headers.get(
        'Authorization'
    )

    if not auth_header:
        return Response({
            "error": "Token missing"
        })

    try:

        token = auth_header.split(' ')[1]

    except:

        return Response({
            "error": "Invalid token format"
        })

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid or expired token"
        })

    try:

        user = User.objects.get(
            id=payload['user_id']
        )

        notifications = Notification.objects.filter(
            user=user
        ).order_by('-id')

        data = []

        for notification in notifications:
            data.append({

                "id": notification.id,

                "title": notification.title,

                "message": notification.message,

                "is_read": notification.is_read,

                "created_at": notification.created_at
            })

        return Response(data)

    except User.DoesNotExist:

        return Response({
            "error": "User not found"
        })

    except Exception as e:

        return Response({
            "error": str(e)
        })


@api_view(['GET'])
def doctor_appointments(request):
    token = request.headers.get('Authorization')

    if not token:
        return Response({
            "error": "Token required"
        }, status=401)

    try:
        token = token.split(" ")[1]
    except:
        return Response({
            "error": "Invalid token format"
        }, status=401)

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid token"
        }, status=401)

    doctor = User.objects.filter(
        id=payload['user_id'],
        role="doctor"
    ).first()

    if not doctor:
        return Response({
            "error": "Doctor not found"
        }, status=404)

    appointments = Appointment.objects.filter(
        doctor=doctor
    ).order_by('-id')

    data = []

    for appointment in appointments:
        data.append({

            "appointment_id": appointment.id,

            "worker_name": appointment.worker.name,

            "worker_email": appointment.worker.email,

            "appointment_date": appointment.appointment_date,

            "appointment_time": appointment.appointment_time,

            "problem_description": appointment.problem_description,

            "status": appointment.status
        })

    return Response(data)


@api_view(['POST'])
def update_appointment_status(request):
    token = request.headers.get('Authorization')

    if not token:
        return Response({
            "error": "Token required"
        }, status=401)

    try:
        token = token.split(" ")[1]
    except:
        return Response({
            "error": "Invalid token format"
        }, status=401)

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid token"
        }, status=401)

    doctor = User.objects.filter(
        id=payload['user_id'],
        role="doctor"
    ).first()

    if not doctor:
        return Response({
            "error": "Doctor not found"
        }, status=404)

    appointment_id = request.data.get('appointment_id')

    status_value = request.data.get('status')

    appointment = Appointment.objects.filter(
        id=appointment_id,
        doctor=doctor
    ).first()

    if not appointment:
        return Response({
            "error": "Appointment not found"
        }, status=404)

    if status_value not in ['accepted', 'rejected']:
        return Response({
            "error": "Invalid status"
        }, status=400)

    appointment.status = status_value
    appointment.save()

    # Worker Notification 😎🔥
    Notification.objects.create(

        user=appointment.worker,

        title="Appointment Update",

        message=f"Your appointment has been {status_value}"
    )

    return Response({

        "message": "Appointment status updated successfully",

        "appointment_id": appointment.id,

        "new_status": appointment.status
    })


@api_view(['GET'])
def my_appointments(request):
    token = request.headers.get('Authorization')

    if not token:
        return Response({
            "error": "Token required"
        }, status=401)

    try:
        token = token.split(" ")[1]
    except:
        return Response({
            "error": "Invalid token format"
        }, status=401)

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid token"
        }, status=401)

    worker = User.objects.filter(
        id=payload['user_id'],
        role="worker"
    ).first()

    if not worker:
        return Response({
            "error": "Worker not found"
        }, status=404)

    appointments = Appointment.objects.filter(
        worker=worker
    ).order_by('-id')

    data = []

    for appointment in appointments:
        data.append({

            "appointment_id": appointment.id,

            "doctor_name": appointment.doctor.name,

            "doctor_email": appointment.doctor.email,

            "appointment_date": appointment.appointment_date,

            "appointment_time": appointment.appointment_time,

            "problem_description": appointment.problem_description,

            "status": appointment.status
        })

    return Response(data)


@api_view(['POST'])
def cancel_appointment(request, appointment_id):
    token = request.headers.get('Authorization')

    if not token:
        return Response({
            "error": "Token required"
        }, status=401)

    try:
        token = token.split(" ")[1]
    except:
        return Response({
            "error": "Invalid token format"
        }, status=401)

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid token"
        }, status=401)

    worker = User.objects.filter(
        id=payload['user_id']
    ).first()

    if not worker:
        return Response({
            "error": "User not found"
        }, status=404)

    appointment = Appointment.objects.filter(
        id=appointment_id
    ).first()

    if not appointment:
        return Response({
            "error": "Appointment not found"
        }, status=404)

    appointment.status = "cancelled"
    appointment.save()

    return Response({
        "message": "Appointment cancelled successfully"
    })


@api_view(['POST'])
def upload_prescription(request, appointment_id):
    token = request.headers.get('Authorization')

    if not token:
        return Response({
            "error": "Token required"
        }, status=401)

    try:
        token = token.split(" ")[1]
    except:
        return Response({
            "error": "Invalid token format"
        }, status=401)

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid token"
        }, status=401)

    doctor = User.objects.filter(
        id=payload['user_id'],
        role='doctor'
    ).first()

    if not doctor:
        return Response({
            "error": "Doctor not found"
        }, status=404)

    appointment = Appointment.objects.filter(
        id=appointment_id,
        doctor=doctor
    ).first()

    if not appointment:
        return Response({
            "error": "Appointment not found"
        }, status=404)

    prescription_file = request.FILES.get(
        'prescription_file'
    )

    doctor_notes = request.data.get(
        'doctor_notes'
    )

    if prescription_file:
        appointment.prescription_file = prescription_file

    appointment.doctor_notes = doctor_notes

    appointment.status = "completed"

    appointment.save()

    Notification.objects.create(

        user=appointment.worker,

        title="Prescription Uploaded",

        message="Doctor uploaded your prescription"
    )

    return Response({

        "message": "Prescription uploaded successfully",

        "appointment_id": appointment.id,

        "status": appointment.status,

        "doctor_notes": appointment.doctor_notes,

        "prescription_file": appointment.prescription_file.url
        if appointment.prescription_file else None
    })


@api_view(['GET'])
def my_prescriptions(request):
    token = request.headers.get('Authorization')

    if not token:
        return Response({
            "error": "Token required"
        }, status=401)

    try:
        token = token.split(" ")[1]
    except:
        return Response({
            "error": "Invalid token format"
        }, status=401)

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid token"
        }, status=401)

    worker = User.objects.filter(
        id=payload['user_id']
    ).first()

    if not worker:
        return Response({
            "error": "Worker not found"
        }, status=404)

    appointments = Appointment.objects.filter(
        worker=worker,
        prescription_file__isnull=False
    ).order_by('-created_at')

    data = []

    for appointment in appointments:
        data.append({

            "appointment_id": appointment.id,

            "doctor_name": appointment.doctor.name,

            "appointment_date": appointment.appointment_date,

            "appointment_time": appointment.appointment_time,

            "doctor_notes": appointment.doctor_notes,

            "prescription_file": request.build_absolute_uri(
                appointment.prescription_file.url
            ) if appointment.prescription_file else None,

            "status": appointment.status
        })

    return Response(data)


@api_view(['POST'])
def send_message(request):
    token = request.headers.get('Authorization')

    if not token:
        return Response({
            "error": "Token required"
        }, status=401)

    try:
        token = token.split(" ")[1]
    except:
        return Response({
            "error": "Invalid token format"
        }, status=401)

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid token"
        }, status=401)

    sender = User.objects.filter(
        id=payload['user_id']
    ).first()

    appointment = Appointment.objects.filter(
        id=request.data.get('appointment_id')
    ).first()

    if not appointment:
        return Response({
            "error": "Appointment not found"
        }, status=404)

    if sender.id == appointment.worker.id:
        receiver = appointment.doctor
    else:
        receiver = appointment.worker

    chat = ChatMessage.objects.create(
        appointment=appointment,
        sender=sender,
        receiver=receiver,
        message=request.data.get('message')
    )

    return Response({
        "message": "Message sent successfully",
        "chat_id": chat.id,
        "sender": sender.name,
        "receiver": receiver.name,
        "text": chat.message
    })


@api_view(['GET'])
def get_messages(request, appointment_id):
    token = request.headers.get('Authorization')

    if not token:
        return Response({
            "error": "Token required"
        }, status=401)

    try:
        token = token.split(" ")[1]
    except:
        return Response({
            "error": "Invalid token format"
        }, status=401)

    payload = decode_token(token)

    if not payload:
        return Response({
            "error": "Invalid token"
        }, status=401)

    chats = ChatMessage.objects.filter(
        appointment_id=appointment_id
    ).order_by('created_at')

    data = []

    for chat in chats:
        data.append({
            "chat_id": chat.id,
            "sender": chat.sender.name,
            "receiver": chat.receiver.name,
            "message": chat.message,
            "time": chat.created_at
        })

    return Response(data)


@api_view(['GET'])
def jobs(request):
    data = [

        {
            "title": "Electrician",
            "location": "Delhi",
            "salary": "25000"
        },

        {
            "title": "Plumber",
            "location": "Patna",
            "salary": "18000"
        },

        {
            "title": "Welder",
            "location": "Mumbai",
            "salary": "30000"
        },

        {
            "title": "Driver",
            "location": "Lucknow",
            "salary": "22000"
        },

        {
            "title": "Painter",
            "location": "Kolkata",
            "salary": "20000"
        },

        {
            "title": "Carpenter",
            "location": "Bangalore",
            "salary": "27000"
        },
    ]

    return Response(data)
