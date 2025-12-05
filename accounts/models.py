
from django.db import models
from django.core.validators import RegexValidator


class OfficialStudent(models.Model):
   

    registration_number = models.CharField(
    max_length=7,
    validators=[RegexValidator(r'^\d{7}$', message="Le numéro doit contenir exactement 7 chiffres.")])

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    identite= models.CharField(max_length=20)
    birth_date = models.CharField(max_length=100)
    email_institutionnel = models.EmailField(unique=True)

       # 🔹 Champs académiques (DB column correspond au HTML/.pkl)
    credit_2emme = models.IntegerField(null=True, blank=True, db_column='Credit_totale____2emme')
    moyenne_generale_2emme = models.FloatField(null=True, blank=True, db_column='Moyenne_generale__2emme')
    diagnostic_financier = models.FloatField(null=True, blank=True, db_column='diagnostic__financier')
    gestion_production = models.FloatField(null=True, blank=True)
    fondamentaux_management = models.FloatField(null=True, blank=True, db_column='fondamentaux_du_managment')
    fondamentaux_marketing = models.FloatField(null=True, blank=True, db_column='fondamenteaux_du_marketing')
    mathematiques_financieres = models.FloatField(null=True, blank=True, db_column='Mathematiques_financieres')
    principe_gestion1 = models.FloatField(null=True, blank=True, db_column='Principe_de_gestion_1')
    principe_gestion2 = models.FloatField(null=True, blank=True, db_column='principe_de_gestion_2')
    moyenne_elements_specifiques = models.FloatField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True, db_column='scrore')

    specialite_choisit = models.CharField(max_length=255, null=True, blank=True)
    prediction = models.CharField(max_length=255, null=True, blank=True, editable=False)

    decision_admin = models.CharField(
    max_length=20,
    choices=[
        ('pending', 'En attente'),
        ('accepted', 'Accepté'),
        ('refused', 'Refusé'),
    ],
    default='pending'
)

    specialite_finale = models.CharField(
    max_length=100,
    blank=True,
    null=True,
    help_text="La spécialité finale décidée par l’administration"
)
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.registration_number}"



class AuthorizedStudent(models.Model):
    registration_number = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email_institutionnel = models.EmailField(unique=True)
    date_created = models.DateTimeField(auto_now_add=True)  # optionnel : date d'inscription
    is_deleted = models.BooleanField(default=False)  # ✅ Nouveau champ

    def __str__(self):
        return f"{self.first_name} {self.last_name}"





# accounts/models.py

class DeletedAuthorizedStudent(models.Model):
    registration_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email_institutionnel = models.EmailField()
    date_deleted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.registration_number}"


from django.contrib.auth.models import User
class StudentChoice(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    inscription = models.CharField(max_length=50)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    identite = models.CharField(max_length=20)
    birth_date = models.DateField()
    email = models.EmailField(unique=True)
    order_preference = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.inscription} - {self.last_name} {self.first_name}"
