from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Restrict a view to users whose .role is in `roles`. Implies login_required."""
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied('You do not have access to this page.')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


def admin_required(view_func):
    return role_required('ADMIN')(view_func)


def teacher_required(view_func):
    return role_required('TEACHER')(view_func)


def student_required(view_func):
    return role_required('STUDENT')(view_func)
