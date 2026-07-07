import uuid

def generate_username_from_email(request, user):
    base = user.email.split("@")[0]
    unique = f"{base}_{uuid.uuid4().hex[:6]}"
    return unique