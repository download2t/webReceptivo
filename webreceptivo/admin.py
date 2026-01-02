"""
Custom Admin Site Configuration
Adds custom CSS to Django Admin
"""
from django.contrib import admin


class WebReceptivoAdminSite(admin.AdminSite):
    """Custom Admin Site with additional styling"""
    
    site_header = "WebReceptivo Admin"
    site_title = "WebReceptivo Admin"
    index_title = "Painel Administrativo"
    
    class Media:
        css = {
            'all': (
                'css/theme-colors.css',
                'css/admin/admin-override.css',
            )
        }


# Replace default admin site
admin.site = WebReceptivoAdminSite()
admin.sites.site = admin.site
