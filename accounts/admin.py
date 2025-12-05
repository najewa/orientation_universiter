from django.contrib import admin
from .models import OfficialStudent

@admin.register(OfficialStudent)
class StudentRecordAdmin(admin.ModelAdmin):
    # Colonnes affichées dans l'interface admin
    list_display = (
        'registration_number', 'first_name', 'last_name', 'identite', 'birth_date',
        'email_institutionnel',

        'credit_2emme', 'moyenne_generale_2emme',
        'diagnostic_financier', 'gestion_production',
        'fondamentaux_management', 'fondamentaux_marketing',
        'mathematiques_financieres',
        'principe_gestion1', 'principe_gestion2',

        'moyenne_elements_specifiques', 'score',
        'specialite_choisit', 'prediction'
    )

    # Champs sur lesquels on peut faire des recherches
    search_fields = (
        'registration_number', 'first_name', 'last_name',
        'identite', 'email_institutionnel'
    )

    # Filtres latéraux
    list_filter = ('specialite_choisit',)

    # Champs éditables directement depuis la liste (exclure prediction car editable=False)
    list_editable = (
        'first_name', 'last_name', 'email_institutionnel',

        'credit_2emme', 'moyenne_generale_2emme',
        'diagnostic_financier', 'gestion_production',
        'fondamentaux_management', 'fondamentaux_marketing',
        'mathematiques_financieres',
        'principe_gestion1', 'principe_gestion2',

        'moyenne_elements_specifiques', 'score',
        'specialite_choisit'
    )

    # Pagination
    list_per_page = 20
