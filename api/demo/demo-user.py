from funkwhale_api.users.models import User


u = User.objects.create(email="demo@demo.com", username="demo", is_staff=True)
u.set_password("demo")
u.subsonic_api_token = "demo"
u.save()
