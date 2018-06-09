from django.conf.urls import include, url
from .views import APISearch, APISearchs


urlpatterns = [
    url(r"^search/$", APISearch.as_view(), name="search"),
    url(r"^searchs/$", APISearchs.as_view(), name="searchs"),
]
