from django.utils import timezone

def meta_pixel_events(request):
    trigger_registration = False

    if request.user.is_authenticated and not request.user.pixel_registration_tracked:
        trigger_registration = True
        # Маркираме в базата и запазваме само това поле за бързина
        request.user.pixel_registration_tracked = True
        request.user.save(update_fields=['pixel_registration_tracked'])

    return {
        'trigger_pixel_registration': trigger_registration
    }