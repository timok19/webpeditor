from django_otp.admin import OTPAdminSite  # pyright: ignore [reportMissingTypeStubs]


class JazzminOTPAdminSite(OTPAdminSite):
    login_template = "admin/login.html"
