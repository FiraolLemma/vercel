from django.conf import settings


class OnboardingMiddleware:
    allowed_url_names = {
        "login",
        "register",
        "logout",
        "profile_create",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        user = request.user
        if (
            not user.is_authenticated
            or user.onboarding_complete
            or request.path.startswith((settings.STATIC_URL, settings.MEDIA_URL))
        ):
            return None

        match = request.resolver_match
        if (
            match
            and match.namespace == "users"
            and match.url_name in self.allowed_url_names
        ):
            return None

        from django.shortcuts import redirect

        return redirect("users:profile_create")
