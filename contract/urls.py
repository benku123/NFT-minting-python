from django.urls import path, include
from contract.views import *


urlpatterns = [
    path('', home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', signup_view, name='signup'),
    path('api/save_account/', save_account, name='save_account'),

    path('logout/', logout_view, name='logout'),
    path('folders/', list_folders, name='list_folders'),
    path('images/generate/', generate_images_view, name='view_generated_images'),
    path('images/list/', GeneratedImageView.as_view(), name='view_list_images'),
    path('create/folder', CreatingFolderView.as_view(), name='creating-file-view'),
    path('create/upload/folder/', create_folder, name='create_folder'),
]
