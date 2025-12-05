from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
import pandas as pd
from .models import OfficialStudent, AuthorizedStudent, DeletedAuthorizedStudent
from django.shortcuts import render, redirect, get_object_or_404
import openpyxl
from .models import StudentChoice
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt





def home(request):
    return render(request, 'main/home.html')





def login_student(request): 
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password")

        # ✅ Vérifier dans AuthorizedStudent par email
        try:
            authorized = AuthorizedStudent.objects.get(email_institutionnel=email)
        except AuthorizedStudent.DoesNotExist:
            messages.error(request, "Vous n'êtes pas autorisé à vous connecter. Contactez l'administration.")
            return redirect("login_student")

        # ✅ Vérifier dans User (authentification)
        user = authenticate(request, username=authorized.registration_number, password=password)
        if user is not None:
            login(request, user)
            return redirect("student_dashboard")
        else:
            messages.error(request, "Email ou mot de passe incorrect.")
            return redirect("login_student")

    return render(request, "main/login_student.html")





def login_admin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff:  # Vérifie que c'est un admin
                login(request, user)
                return redirect('student_spending')  
            else:
                messages.error(request, "Vous n'êtes pas un administrateur.")
        else:
            messages.error(request, "Nom d’utilisateur ou mot de passe incorrect.")

    return render(request, 'main/login_admin.html')

@login_required(login_url='login_student')
def student_dashboard(request):
    user = request.user

    # ➤ Mise à jour du profil
    if request.method == 'POST' and 'first_name' in request.POST and 'order_preference' not in request.POST:
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        if request.POST.get('password'):
            user.set_password(request.POST.get('password'))
        if request.FILES.get('profile_photo'):
            user.profile_photo = request.FILES['profile_photo']
        user.save()
        messages.success(request, "Profil mis à jour avec succès ✅")
        return redirect('student_dashboard')

    # ➤ Récupérer le choix existant
    try:
        existing_choice = StudentChoice.objects.get(student=user)
    except StudentChoice.DoesNotExist:
        existing_choice = None

    # ➤ Gestion du formulaire des spécialités
    if request.method == 'POST' and 'order_preference' in request.POST:
        if existing_choice is None:
            existing_choice = StudentChoice.objects.create(
                student=user,
                inscription=request.POST.get("inscription"),
                last_name=request.POST.get("last_name"),
                first_name=request.POST.get("first_name"),
                identite=request.POST.get("identite"),
                birth_date=request.POST.get("birth_date"),
                email=request.POST.get("email"),
                order_preference=request.POST.get("order_preference")
            )
        else:
            existing_choice.inscription = request.POST.get("inscription")
            existing_choice.last_name = request.POST.get("last_name")
            existing_choice.first_name = request.POST.get("first_name")
            existing_choice.identite = request.POST.get("identite")
            existing_choice.birth_date = request.POST.get("birth_date")
            existing_choice.email = request.POST.get("email")
            existing_choice.order_preference = request.POST.get("order_preference")
            existing_choice.save()

        # ➤ Mettre à jour ou créer le record OfficialStudent
        try:
            first_choice = existing_choice.order_preference.split(",")[0]

            # Tenter de récupérer le student_record existant
            student_record = OfficialStudent.objects.filter(
                email_institutionnel=existing_choice.email
            ).first() or OfficialStudent.objects.filter(
                registration_number=existing_choice.inscription
            ).first()

            if student_record:
                # Mettre à jour le choix de spécialité
                student_record.specialite_choisit = first_choice
            else:
                # Si l'étudiant n'existe pas encore, le créer
                student_record = OfficialStudent.objects.create(
                    registration_number=existing_choice.inscription,
                    first_name=existing_choice.first_name,
                    last_name=existing_choice.last_name,
                    identite=existing_choice.identite,
                    birth_date=existing_choice.birth_date,
                    email_institutionnel=existing_choice.email,
                    specialite_choisit=first_choice
                )

            student_record.save()

        except Exception as e:
            print("Erreur mise à jour spécialité :", e)


        messages.success(request, "✅ Votre formulaire a été mis à jour avec succès !")
        return redirect('student_dashboard')

    # ➤ NOUVELLE PARTIE : Déterminer si une nouvelle décision a été prise
    student_record = OfficialStudent.objects.filter(email_institutionnel=user.email).first()
    new_decision = False
    if student_record and student_record.decision_admin != 'pending':
        new_decision = True

    return render(request, 'main/student_dashboard.html', {
        "user": user,
        "existing_choice": existing_choice,
        "student": student_record,
        "new_decision": new_decision,
        "news": []  # tu peux ajouter ici d'autres notifications si nécessaire
    })



def register_student(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        registration_number = request.POST.get("registration_number", "").strip()

        # ✅ Vérifier email institutionnel
        if not email.endswith("@isgb.ucar.tn"):
            messages.error(request, "Veuillez utiliser votre email institutionnel @isgb.ucar.tn.")
            return redirect("register_student")

        # ✅ Vérifier correspondance dans la base officielle
        try:
            official = OfficialStudent.objects.get(
                registration_number=registration_number,
                email_institutionnel=email
            )
        except OfficialStudent.DoesNotExist:
            messages.error(request, "Numéro d'inscription ou email incorrect ou non trouvé dans la base officielle.")
            return redirect("register_student")

        # ✅ Vérifier longueur matricule
        if not registration_number.isdigit() or len(registration_number) != 7:
            messages.error(request, "Le numéro d'inscription doit contenir exactement 7 chiffres.")
            return redirect("register_student")

        # ✅ Vérifier mots de passe
        if password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect("register_student")

        # ✅ Vérifier si l'étudiant est déjà autorisé
        if AuthorizedStudent.objects.filter(email_institutionnel=email).exists():
            messages.error(request, "Un compte avec cet email existe déjà dans les étudiants autorisés.")
            return redirect("register_student")

        # ✅ Vérifier si un compte utilisateur existe déjà (dans User)
        if User.objects.filter(username=registration_number).exists():
            messages.error(request, "Vous n’êtes pas autorisé à créer un compte.")
            return redirect("register_student")

        # ✅ Création du compte utilisateur
        user = User.objects.create_user(
            username=registration_number,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
            
            
        )

        # ✅ Ajouter dans AuthorizedStudent
        AuthorizedStudent.objects.create(
            registration_number=registration_number,
            first_name=first_name,
            last_name=last_name,
            email_institutionnel=email
        )

        # ✅ Connexion auto et redirection au dashboard
        login(request, user)
        messages.success(request, "Compte créé avec succès !")
        return redirect("register_student")

    return render(request, "main/register_student.html")

import requests




@login_required(login_url='login_admin')
@user_passes_test(lambda u: u.is_superuser)
def student_spending(request):

    FLASK_API_URL = "http://127.0.0.1:5000/predict"

    if request.method == "POST":

        # ----- IMPORT EXCEL -----
        if request.FILES.get('file'):
            excel_file = request.FILES['file']
            try:
                wb = openpyxl.load_workbook(excel_file)
                sheet = wb.active

                for row in sheet.iter_rows(min_row=2, values_only=True):
                    num_inscription, Nom, Prénom, cin, date_naissance, email = row

                    if not OfficialStudent.objects.filter(registration_number=num_inscription).exists():
                        student = OfficialStudent.objects.create(
                            registration_number=num_inscription,
                            first_name=Nom,
                            last_name=Prénom,
                            identite=cin,
                            birth_date=date_naissance,
                            email_institutionnel=email,
                            credit_2emme=row[6],
                            moyenne_generale_2emme=row[7],
                            diagnostic_financier=row[8],
                            gestion_production=row[9],
                            fondamentaux_management=row[10],
                            fondamentaux_marketing=row[11],
                            mathematiques_financieres=row[12],
                            principe_gestion1=row[13],
                            principe_gestion2=row[14],
                            moyenne_elements_specifiques=row[15],
                            score=row[16]
                        )

                        # Envoi prédiction si specialité existe
                        if student.specialite_choisit:
                            send_to_flask(student, FLASK_API_URL)

                messages.success(request, "Import Excel effectué avec succès !")

            except Exception as e:
                messages.error(request, f"Erreur d'importation : {e}")

            return redirect('student_spending')

        # ----- AJOUT MANUEL -----
        elif request.POST.get("action") == "add_student":

            matricule = request.POST.get("registration_number")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            cin = request.POST.get("identite")
            date_naissance = request.POST.get("birth_date")
            email = request.POST.get("email_institutionnel")
            credit_2emme = request.POST.get("Credit_totale____2emme")
            moyenne_generale_2emme = request.POST.get("Moyenne_generale__2emme")
            diagnostic_financier = request.POST.get("diagnostic__financier")
            gestion_production = request.POST.get("gestion_de_production")
            fondamentaux_management = request.POST.get("fondamentaux_du_managment")
            fondamentaux_marketing = request.POST.get("fondamenteaux_du_marketing")
            mathematiques_financieres = request.POST.get("Mathematiques_financieres")
            principe_gestion1 = request.POST.get("Principe_de_gestion_1")
            principe_gestion2 = request.POST.get("principe_de_gestion_2")
            moyenne_elements_specifiques = request.POST.get("moyenne_elements_specifiques")
            score = request.POST.get("scrore")
  

            if OfficialStudent.objects.filter(registration_number=matricule).exists():
                messages.error(request, "Cet étudiant existe déjà.")
            else:
                student = OfficialStudent.objects.create(
                    registration_number=matricule,
                    first_name=first_name,
                    last_name=last_name,
                    identite=cin,
                    birth_date=date_naissance,
                    email_institutionnel=email,
                    credit_2emme=credit_2emme,
                    moyenne_generale_2emme=moyenne_generale_2emme,
                    diagnostic_financier=diagnostic_financier,
                    gestion_production=gestion_production,
                    fondamentaux_management=fondamentaux_management,
                    fondamentaux_marketing=fondamentaux_marketing,
                    mathematiques_financieres=mathematiques_financieres,
                    principe_gestion1=principe_gestion1,
                    principe_gestion2=principe_gestion2,
                    moyenne_elements_specifiques=moyenne_elements_specifiques,
                    score=score,
                    
                )

                messages.success(request, "Étudiant ajouté avec succès !")



    # ----- RÉCUPÉRATION DES ÉTUDIANTS -----
    students = OfficialStudent.objects.all()
    authorized_students = AuthorizedStudent.objects.all()
    deleted_students = DeletedAuthorizedStudent.objects.all()
    submissions = StudentChoice.objects.all().order_by("-date_submitted")

    # ----- AUTO-PREDICTION POUR CEUX QUI ONT UNE SPÉCIALITÉ -----
    students_to_predict = OfficialStudent.objects.filter(
        specialite_choisit__isnull=False, 
        prediction__isnull=True
    )
    for student in students_to_predict:
        send_to_flask(student, FLASK_API_URL)


    # ----- RENDER -----
    return render(request, 'main/student_spending.html', {
        "students": students,
        "authorized_students": authorized_students,
        "deleted_students": deleted_students,
        "submissions": submissions
    })



# 🔹 Fonction utilitaire pour envoyer les données à Flask
def send_to_flask(student, url):
    import requests
    payload = {
        "Credit_totale____2emme": float(student.credit_2emme or 0),
        "Moyenne_generale__2emme": float(student.moyenne_generale_2emme or 0),
        "diagnostic__financier": float(student.diagnostic_financier or 0),
        "gestion_de_production": float(student.gestion_production or 0),
        "fondamentaux_du_managment": float(student.fondamentaux_management or 0),
        "fondamenteaux_du_marketing": float(student.fondamentaux_marketing or 0),
        "Mathematiques_financieres": float(student.mathematiques_financieres or 0),
        "Principe_de_gestion_1": float(student.principe_gestion1 or 0),
        "principe_de_gestion_2": float(student.principe_gestion2 or 0),
        "moyenne_elements_specifiques": float(student.moyenne_elements_specifiques or 0),
        "scrore": float(student.score or 0)
    }
    try:
        response = requests.post(url, json=payload, timeout=10)  # Timeout augmenté
        response.raise_for_status()  # Lève une exception si code != 200
        data = response.json()
        if data.get("status") == "success":
            student.prediction = str(round(data.get("prediction", 0), 2))
            student.save()
        else:
            print(f"Erreur Flask pour {student.registration_number}: {data.get('message')}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion Flask pour {student.registration_number}: {e}")


# 🔹 Éditer un étudiant
def edit_student(request, student_id):
    student = get_object_or_404(OfficialStudent, id=student_id)
    if request.method == "POST":
        student.registration_number = request.POST.get("registration_number")
        student.last_name = request.POST.get("last_name")
        student.first_name = request.POST.get("first_name")
        student.identite = request.POST.get("identite")
        student.birth_date = request.POST.get("birth_date")
        student.email_institutionnel = request.POST.get("email_institutionnel")

        # 🔹 Champs académiques correspondant aux noms Django
        student.credit_2emme = request.POST.get("Credit_totale____2emme")
        student.moyenne_generale_2emme = request.POST.get("Moyenne_generale__2emme")
        student.diagnostic_financier = request.POST.get("diagnostic__financier")
        student.gestion_production = request.POST.get("gestion_de_production")
        student.fondamentaux_management = request.POST.get("fondamentaux_du_managment")
        student.fondamentaux_marketing = request.POST.get("fondamenteaux_du_marketing")
        student.mathematiques_financieres = request.POST.get("Mathematiques_financieres")
        student.principe_gestion1 = request.POST.get("Principe_de_gestion_1")
        student.principe_gestion2 = request.POST.get("principe_de_gestion_2")
        student.moyenne_elements_specifiques = request.POST.get("moyenne_elements_specifiques")
        student.score = request.POST.get("scrore")

        student.save()
    return redirect('student_spending')



from .models import DeletedAuthorizedStudent  # ✅ Assure-toi que c'est importé

def delete_student(request, student_id):
    student = get_object_or_404(OfficialStudent, id=student_id)
    
    if request.method == "POST":
        # ✅ Supprimer dans AuthorizedStudent s'il existe
        AuthorizedStudent.objects.filter(
            registration_number=student.registration_number
        ).delete()

        # ✅ Supprimer aussi dans DeletedAuthorizedStudent s'il existe
        DeletedAuthorizedStudent.objects.filter(
            registration_number=student.registration_number
        ).delete()

        # ✅ Supprimer dans OfficialStudent
        student.delete()

    return redirect('student_spending')




def import_students(request):
    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            messages.error(request, "Aucun fichier sélectionné.")
            return redirect("student_pending")

        try:
            df = pd.read_excel(file)

            for _, row in df.iterrows():
                # Assure-toi que les colonnes Excel correspondent aux noms ci-dessous
                registration_number = row.get('registration_number')
                first_name = row.get('first_name') or row.get('Nom')
                last_name = row.get('last_name') or row.get('Prénom')
                identite = row.get('identite') or row.get('cin')
                birth_date = row.get('birth_date') or row.get('date_naissance')
                email = row.get('email') or row.get('email_institutionnel')

                OfficialStudent.objects.update_or_create(
                    registration_number=registration_number,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'identite': identite,
                        'birth_date': birth_date,
                        'email_institutionnel': email,

                        # 🔹 Champs académiques selon le modèle Django
                        'credit_2emme': row.get('Credit_totale____2emme') or row.get('credit_total'),
                        'moyenne_generale_2emme': row.get('Moyenne_generale__2emme') or row.get('moyenne_generale'),
                        'diagnostic_financier': row.get('diagnostic__financier') or row.get('diagnostic_financier'),
                        'gestion_production': row.get('gestion_de_production'),
                        'fondamentaux_management': row.get('fondamentaux_du_managment') or row.get('fondamentaux_management'),
                        'fondamentaux_marketing': row.get('fondamenteaux_du_marketing') or row.get('fondamentaux_marketing'),
                        'mathematiques_financieres': row.get('Mathematiques_financieres') or row.get('math_financieres'),
                        'principe_gestion1': row.get('Principe_de_gestion_1') or row.get('principe_gestion1'),
                        'principe_gestion2': row.get('principe_de_gestion_2') or row.get('principe_gestion2'),
                        'moyenne_elements_specifiques': row.get('moyenne_elements_specifiques'),
                        'score': row.get('scrore') or row.get('score'),
                    }
                )

            messages.success(request, "Importation réussie ✅")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'importation : {e}")
        
        return redirect("student_pending")

    return redirect("student_pending")










def authorized_students_list(request):
    authorized_students = AuthorizedStudent.objects.all()
    deleted_students = DeletedAuthorizedStudent.objects.all()  # si tu gères la restauration
    return render(request, "main/student_spending.html", {
        "authorized_students": authorized_students,
        "deleted_students": deleted_students,
    })


# Ajouter automatiquement un étudiant (à appeler quand un étudiant crée son compte)
def add_authorized_student(student_data):
    """student_data = dict avec registration_number, first_name, last_name, email"""
    if not AuthorizedStudent.objects.filter(registration_number=student_data['registration_number']).exists():
        AuthorizedStudent.objects.create(
            registration_number=student_data['registration_number'],
            first_name=student_data['first_name'],
            last_name=student_data['last_name'],
            email_institutionnel=student_data['email']
        )


def delete_authorized_student(request, student_id):
    student = get_object_or_404(AuthorizedStudent, id=student_id)

    # Copier dans DeletedAuthorizedStudent
    DeletedAuthorizedStudent.objects.create(
        registration_number=student.registration_number,
        first_name=student.first_name,
        last_name=student.last_name,
        email_institutionnel=student.email_institutionnel
    )

    # Supprimer de AuthorizedStudent
    student.delete()
    messages.success(request, "Étudiant supprimé et enregistré pour restauration ✅")
    return redirect('student_spending')




@login_required
@user_passes_test(lambda u: u.is_superuser)
def restore_authorized_student(request):
    if request.method == "POST":
        ids = request.POST.getlist("student_ids")
        for student_id in ids:
            deleted_student = get_object_or_404(DeletedAuthorizedStudent, id=student_id)
            
            # Réinsérer dans AuthorizedStudent
            AuthorizedStudent.objects.create(
                registration_number=deleted_student.registration_number,
                first_name=deleted_student.first_name,
                last_name=deleted_student.last_name,
                email_institutionnel=deleted_student.email_institutionnel
            )
            # Supprimer de DeletedAuthorizedStudent
            deleted_student.delete()
        messages.success(request, "Étudiants restaurés avec succès ✅")
    return redirect('student_spending')




from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required(login_url='login_admin')
@user_passes_test(lambda u: u.is_superuser)
def decide_specialite(request, student_id):
    student = OfficialStudent.objects.get(id=student_id)

    # Vérifier si l'étudiant a choisi une spécialité
    if not student.specialite_choisit:
        messages.error(request, "❗ Impossible : l’étudiant n’a pas encore choisi sa spécialité.")
        return redirect("student_spending")

    if request.method == "POST":
        decision = request.POST.get("decision")
        specialite_finale = request.POST.get("specialite_finale")

        # --- Logique de décision ---
        if decision == "accepted":
            student.decision_admin = "accepted"
            student.specialite_finale = student.specialite_choisit

        elif decision == "refused":
            if not specialite_finale:
                messages.error(request, "❗ Vous devez choisir une nouvelle spécialité si vous refusez.")
                return redirect("student_spending")

            student.decision_admin = "refused"
            student.specialite_finale = specialite_finale

        student.save()
        messages.success(request, "Décision enregistrée avec succès !")
        return redirect("student_spending")

    return redirect("student_spending")
