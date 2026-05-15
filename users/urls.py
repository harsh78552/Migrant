from django.urls import path

from .views import (
    delete_user,
    my_notifications,
    signup,
    login,
    profile,
    update_profile,
    search_workers,
    create_job,
    list_jobs,
    apply_job,
    my_applications,
    create_doctor_profile,
    list_doctors,
    book_appointment,
    doctor_appointments,
    update_appointment_status,
    my_appointments,
    cancel_appointment,
    all_users,
    delete_user,
    admin_dashboard,
    verify_doctor,
    pending_doctors,
    upload_profile_image,
    my_notifications,
    upload_prescription,
    my_prescriptions,
    send_message,
    get_messages,
    jobs
)

urlpatterns = [

    path(
        'signup/',
        signup
    ),

    path(
        'login/',
        login
    ),

    path(
        'profile/',
        profile
    ),

    path(
        'update-profile/',
        update_profile
    ),

    path(
        'search-workers/',
        search_workers
    ),

    path(
        'create-job/',
        create_job
    ),

    path(
        'jobs/',
        list_jobs
    ),

    path(
        'apply-job/<int:job_id>/',
        apply_job
    ),

    path(
        'my-applications/',
        my_applications
    ),

    path(
        'create-doctor-profile/',
        create_doctor_profile
    ),

    path(
        'doctors/',
        list_doctors
    ),

    path(
        'book-appointment/',
        book_appointment
    ),

    path(
        'doctor-appointments/',
        doctor_appointments
    ),

    path(
        'update-appointment-status/<int:appointment_id>/',
        update_appointment_status
    ),

    path(
        'my-appointments/',
        my_appointments
    ),

    path(
        'cancel-appointment/<int:appointment_id>/',
        cancel_appointment
    ),

    path(
        'all-users/',
        all_users
    ),

    path(
        'delete-user/<int:user_id>/',
        delete_user
    ),

    path(
        'admin-dashboard/',
        admin_dashboard
    ),

    path(
        'verify-doctor/<int:doctor_profile_id>/',
        verify_doctor
    ),

    path(
        'pending-doctors/',
        pending_doctors
    ),

    path(
        'upload-profile-image/',
        upload_profile_image
    ),

    path(
        'my-notifications/',
        my_notifications
    ),

    path(
    'upload-prescription/<int:appointment_id>/',
    upload_prescription
),

    path(
    'my-prescriptions/',
    my_prescriptions
),

    path(
    'send-message/',
    send_message
),


path(
    'get-messages/<int:appointment_id>/',
    get_messages
),

path(
    'jobs/', jobs
    ),
]
