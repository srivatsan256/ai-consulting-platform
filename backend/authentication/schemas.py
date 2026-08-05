"""
drf-spectacular OpenAPI extensions for the authentication app.
"""

from drf_spectacular.extensions import OpenApiAuthenticationExtension

from authentication.services.jwt import CustomJWTAuthentication


class CustomJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    Register CustomJWTAuthentication as a Bearer JWT scheme in the OpenAPI docs.
    """

    target_class = CustomJWTAuthentication
    name = "JWTAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
