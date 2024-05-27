from django.urls import path, include
from contract.views import *

urlpatterns = [
    path('', home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', signup_view, name='signup'),
    path('api/save_account/', save_account, name='save_account'),
    path('logout/', logout_view, name='logout'),
    path('folders/', list_folders, name='list_folders'),
    path('user/folders/', personal_list_folder, name='personal_list_folder'),
    path('images/generate/', generate_and_mint_nfts, name='generate_and_mint_nfts'),
    path('images/list/<int:pk>/', list_folders_details, name='view_list_images'),
    path('create/folder', CreatingFolderView.as_view(), name='creating-file-view'),
    path("mint_nfts/<int:pk>", mint_nft, name="mint_nft"),
    path('create/upload/folder/', create_folder, name='create_folder'),
    path('like/<int:image_id>/', like_image, name='like_image'),
    path('dislike/<int:image_id>/', dislike_image, name='dislike_image'),
]
