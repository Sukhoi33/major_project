from django.contrib import admin
from django.urls import include, path
from django.urls.resolvers import URLPattern, URLResolver
from django.conf import settings
from django.conf.urls.static import static
from users.views import SecureTwoFactorLoginView


def get_two_factor_patterns():
    from two_factor import urls as tf_urls
    patterns = getattr(tf_urls, 'urlpatterns', [])
    if isinstance(patterns, (list, tuple)) and patterns and isinstance(patterns[0], str):
        patterns = patterns[1]
    if isinstance(patterns, (list, tuple)) and patterns and isinstance(patterns[0], (list, tuple)):
        patterns = patterns[0]
    if not isinstance(patterns, (list, tuple)) or not all(
        isinstance(p, (URLPattern, URLResolver)) for p in patterns
    ):
        raise RuntimeError("two_factor.urls did not yield URLPattern/URLResolver list after normalization")
    return list(patterns)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/login/', SecureTwoFactorLoginView.as_view(), name='account_login'),
    path('', include((get_two_factor_patterns(), 'two_factor'), namespace='two_factor')),
    path('', include(('chipin.urls', 'chipin'), namespace='chipin')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
