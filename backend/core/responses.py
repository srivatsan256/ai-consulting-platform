from rest_framework.response import Response


def success_response(data=None, message="Success.", status=200):
    return Response({
        "success": True,
        "message": message,
        "data": data,
        "errors": None,
    }, status=status)


def error_response(message="An error occurred.", errors=None, status=400):
    return Response({
        "success": False,
        "message": message,
        "data": None,
        "errors": errors,
    }, status=status)


def created_response(data=None, message="Created successfully."):
    return success_response(data=data, message=message, status=201)


def no_content_response(message="Deleted successfully."):
    return Response(status=204)


def paginated_response(pagination_data, data, message="Success."):
    return Response({
        "success": True,
        "message": message,
        "data": {
            "pagination": pagination_data,
            "results": data,
        },
        "errors": None,
    })
