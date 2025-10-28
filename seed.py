"""
Script de peuplement de la base de données avec des données de test
"""
import sys
import os

# Ajouter le dossier app au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.course import Course
from app.models.chapter import Chapter
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment
app = create_app()

def seed_database():
    """Peuple la base de données"""
    
    with app.app_context():
        print("🌱 Début du seeding...")
        
        # Supprimer toutes les données existantes
        print("🗑️  Suppression des données existantes...")
        db.drop_all()
        db.create_all()
        print("✅ Tables créées")
        
        # ========================================
        # UTILISATEURS
        # ========================================
        print("\n👤 Création des utilisateurs...")
        
        user1 = User(
            name="Jean Dupont",
            email="jean@test.com",
            phone="+509 1234 5678",
            location="Port-au-Prince, Haïti",
            bio="Étudiant passionné par les mathématiques et les sciences"
        )
        user1.set_password("password123")
        
        user2 = User(
            name="Marie Laurent",
            email="marie@test.com",
            phone="+509 9876 5432",
            location="Cap-Haïtien, Haïti",
            bio="Future ingénieure, j'adore apprendre de nouvelles choses"
        )
        user2.set_password("password123")
        
        db.session.add_all([user1, user2])
        db.session.commit()
        print(f"✅ {User.query.count()} utilisateurs créés")
        
        # ========================================
        # COURS 1: MATHÉMATIQUES
        # ========================================
        print("\n📚 Création du cours de Mathématiques...")
        
        course_math = Course(
            title="Introduction aux Mathématiques",
            category="Mathématiques",
            description="Maîtrisez les fondamentaux des mathématiques pour réussir à l'université. Ce cours couvre l'algèbre, la géométrie et les bases du calcul.",
            instructor="Dr. Marie Laurent",
            duration="12 heures",
            level="Débutant",
            rating=4.8,
            students_count=0
        )
        
        db.session.add(course_math)
        db.session.commit()
        
        # Chapitre 1: Les bases des nombres
        chapter1 = Chapter(
            course_id=course_math.id,
            title="Les bases des nombres",
            description="Comprendre les différents types de nombres et leurs propriétés",
            duration="2h 30min",
            order=1
        )
        
        db.session.add(chapter1)
        db.session.commit()
        
        lessons_ch1 = [
            Lesson(chapter_id=chapter1.id, title="Les nombres entiers", duration="25 min", order=1, 
                   content="Les nombres entiers sont des nombres sans partie décimale. Ils incluent les nombres positifs, négatifs et zéro."),
            Lesson(chapter_id=chapter1.id, title="Les nombres décimaux", duration="30 min", order=2,
                   content="Les nombres décimaux ont une partie après la virgule. Exemple: 3.14, 2.5, 0.75"),
            Lesson(chapter_id=chapter1.id, title="Les fractions", duration="35 min", order=3,
                   content="Une fraction représente une division. Exemple: 1/2, 3/4, 5/8"),
            Lesson(chapter_id=chapter1.id, title="Quiz - Les nombres", duration="15 min", order=4, is_quiz=True),
        ]
        
        # Chapitre 2: Algèbre élémentaire
        chapter2 = Chapter(
            course_id=course_math.id,
            title="Algèbre élémentaire",
            description="Introduction à l'algèbre et aux équations",
            duration="3h 15min",
            order=2
        )
        
        db.session.add(chapter2)
        db.session.commit()
        
        lessons_ch2 = [
            Lesson(chapter_id=chapter2.id, title="Les variables et expressions", duration="30 min", order=1,
                   content="Une variable est une lettre qui représente un nombre inconnu. Exemple: x, y, z"),
            Lesson(chapter_id=chapter2.id, title="Les équations du premier degré", duration="35 min", order=2,
                   content="Une équation est une égalité avec une inconnue. Exemple: 2x + 3 = 7"),
            Lesson(chapter_id=chapter2.id, title="Résoudre des équations", duration="40 min", order=3,
                   content="Pour résoudre une équation, on isole la variable d'un côté de l'égalité."),
            Lesson(chapter_id=chapter2.id, title="Quiz - Algèbre", duration="15 min", order=4, is_quiz=True, is_locked=True),
        ]
        
        # Chapitre 3: Géométrie plane
        chapter3 = Chapter(
            course_id=course_math.id,
            title="Géométrie plane",
            description="Les figures géométriques et leurs propriétés",
            duration="2h 45min",
            order=3
        )
        
        db.session.add(chapter3)
        db.session.commit()
        
        lessons_ch3 = [
            Lesson(chapter_id=chapter3.id, title="Les angles", duration="25 min", order=1, is_locked=True,
                   content="Un angle est formé par deux demi-droites ayant la même origine."),
            Lesson(chapter_id=chapter3.id, title="Les triangles", duration="30 min", order=2, is_locked=True,
                   content="Un triangle est un polygone à trois côtés et trois angles."),
            Lesson(chapter_id=chapter3.id, title="Quiz - Géométrie", duration="15 min", order=3, is_quiz=True, is_locked=True),
        ]
        
        db.session.add_all(lessons_ch1 + lessons_ch2 + lessons_ch3)
        db.session.commit()
        
        # ========================================
        # COURS 2: PHYSIQUE
        # ========================================
        print("📚 Création du cours de Physique...")
        
        course_physics = Course(
            title="Physique - Mécanique",
            category="Sciences",
            description="Explorez les lois de la physique et leurs applications pratiques. Comprenez le mouvement, les forces et l'énergie.",
            instructor="Prof. Jean Martin",
            duration="10 heures",
            level="Intermédiaire",
            rating=4.6,
            students_count=0
        )
        
        db.session.add(course_physics)
        db.session.commit()
        
        # Chapitre 1: Les forces
        chapter_phys1 = Chapter(
            course_id=course_physics.id,
            title="Introduction aux forces",
            description="Comprendre ce qu'est une force et comment elle agit",
            duration="3h",
            order=1
        )
        
        db.session.add(chapter_phys1)
        db.session.commit()
        
        lessons_phys = [
            Lesson(chapter_id=chapter_phys1.id, title="Qu'est-ce qu'une force ?", duration="30 min", order=1,
                   content="Une force est une action capable de modifier le mouvement d'un objet."),
            Lesson(chapter_id=chapter_phys1.id, title="Les lois de Newton", duration="45 min", order=2,
                   content="Newton a formulé trois lois fondamentales qui décrivent le mouvement."),
            Lesson(chapter_id=chapter_phys1.id, title="Quiz - Forces", duration="20 min", order=3, is_quiz=True),
        ]
        
        db.session.add_all(lessons_phys)
        db.session.commit()
        
        # ========================================
        # COURS 3: ANGLAIS
        # ========================================
        print("📚 Création du cours d'Anglais...")
        
        course_english = Course(
            title="Anglais Niveau B1",
            category="Langues",
            description="Améliorez votre anglais pour atteindre le niveau B1 du CECR. Vocabulaire, grammaire et conversation.",
            instructor="Sarah Williams",
            duration="15 heures",
            level="Débutant",
            rating=4.9,
            students_count=0
        )
        
        db.session.add(course_english)
        db.session.commit()
        
        # Chapitre 1: Grammaire de base
        chapter_eng1 = Chapter(
            course_id=course_english.id,
            title="Grammaire de base",
            description="Les temps et structures grammaticales essentielles",
            duration="4h",
            order=1
        )
        
        db.session.add(chapter_eng1)
        db.session.commit()
        
        lessons_eng = [
            Lesson(chapter_id=chapter_eng1.id, title="Present Simple", duration="35 min", order=1,
                   content="Le present simple est utilisé pour parler d'habitudes et de vérités générales."),
            Lesson(chapter_id=chapter_eng1.id, title="Present Continuous", duration="35 min", order=2,
                   content="Le present continuous décrit une action en cours au moment présent."),
            Lesson(chapter_id=chapter_eng1.id, title="Quiz - Present Tenses", duration="20 min", order=3, is_quiz=True),
        ]
        
        db.session.add_all(lessons_eng)
        db.session.commit()
        
        print(f"✅ {Course.query.count()} cours créés")
        print(f"✅ {Chapter.query.count()} chapitres créés")
        print(f"✅ {Lesson.query.count()} leçons créées")
        
        # ========================================
        # INSCRIPTIONS
        # ========================================
        print("\n✍️  Création des inscriptions...")
        
        # Jean s'inscrit au cours de maths (en cours)
        enrollment1 = Enrollment(
            user_id=user1.id,
            course_id=course_math.id,
            status='in-progress',
            progress=40
        )
        
        # Jean s'inscrit au cours de physique (pas commencé)
        enrollment2 = Enrollment(
            user_id=user1.id,
            course_id=course_physics.id,
            status='not-started',
            progress=0
        )
        
        db.session.add_all([enrollment1, enrollment2])
        
        # Mettre à jour les compteurs
        course_math.students_count = 1
        course_physics.students_count = 1
        
        db.session.commit()
        print(f"✅ {Enrollment.query.count()} inscriptions créées")
        
        # ========================================
        # RÉSUMÉ
        # ========================================
        print("\n" + "="*50)
        print("🎉 SEEDING TERMINÉ AVEC SUCCÈS !")
        print("="*50)
        print(f"\n📊 Résumé:")
        print(f"   👤 Utilisateurs: {User.query.count()}")
        print(f"   📚 Cours: {Course.query.count()}")
        print(f"   📑 Chapitres: {Chapter.query.count()}")
        print(f"   📝 Leçons: {Lesson.query.count()}")
        print(f"   ✍️  Inscriptions: {Enrollment.query.count()}")
        
        print(f"\n👤 Comptes de test créés:")
        print(f"   📧 Email: jean@test.com")
        print(f"   🔑 Mot de passe: password123")
        print(f"   ")
        print(f"   📧 Email: marie@test.com")
        print(f"   🔑 Mot de passe: password123")
        
        print(f"\n🚀 Prochaines étapes:")
        print(f"   1. Lancez le backend: make dev-backend")
        print(f"   2. Testez l'API: http://localhost:5000")
        print(f"   3. Connectez-vous avec jean@test.com")
        print("\n✨ Happy coding!\n")

if __name__ == '__main__':
    seed_database()