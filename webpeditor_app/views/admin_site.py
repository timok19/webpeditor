from django_otp.admin import OTPAdminSite


class JazzminOTPAdminSite(OTPAdminSite):
    login_template = "admin/login.html"
    # site_url = ""
