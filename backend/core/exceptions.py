from rest_framework.exceptions import APIException


class CompanyNotFound(APIException):
    status_code = 403
    default_detail = "Company not found."
    default_code = "company_not_found"


class SubscriptionExpired(APIException):
    status_code = 403
    default_detail = "Subscription expired."
    default_code = "subscription_expired"


class FeatureDisabled(APIException):
    status_code = 403
    default_detail = "Feature disabled."
    default_code = "feature_disabled"
