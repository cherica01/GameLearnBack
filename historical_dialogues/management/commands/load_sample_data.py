import json
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import requests
from historical_dialogues.models import (
    HistoricalCharacter, CharacterTag, CharacterAchievement,
    DialogueScenario, DialogueResponse, ResponseKeyword,
    DefaultResponse, Quiz, QuizOption
)


class Command(BaseCommand):
    help = 'Load sample data for historical dialogues'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to load sample data...'))
        
        # Load historical characters
        self.load_historical_characters()
        
        # Load dialogue scenarios
        self.load_dialogue_scenarios()
        
        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))

    def load_historical_characters(self):
        characters_data = [
            {
                "id": "leonardo-da-vinci",
                "name": "Léonard de Vinci",
                "period": "Renaissance (1452-1519)",
                "short_description": "Artiste, inventeur et scientifique polymathe italien, considéré comme l'archétype de l'homme de la Renaissance.",
                "portrait_url": "https://example.com/leonardo-da-vinci.jpg",
                "birth_year": 1452,
                "death_year": 1519,
                "nationality": "Italien",
                "tags": ["art", "science", "invention"],
                "achievements": [
                    "La Joconde", 
                    "La Cène", 
                    "L'Homme de Vitruve", 
                    "Codex Atlanticus"
                ]
            },
            {
                "id": "cleopatra",
                "name": "Cléopâtre VII",
                "period": "Égypte ptolémaïque (69-30 av. J.-C.)",
                "short_description": "Dernière souveraine active de l'Égypte ptolémaïque, célèbre pour ses relations avec Jules César et Marc Antoine.",
                "portrait_url": "https://example.com/cleopatra.jpg",
                "birth_year": -69,
                "death_year": -30,
                "nationality": "Égyptienne",
                "tags": ["politique", "Égypte", "antiquité"],
                "achievements": [
                    "Restauration de l'économie égyptienne",
                    "Alliance avec Rome",
                    "Préservation de l'indépendance égyptienne"
                ]
            },
            {
                "id": "napoleon-bonaparte",
                "name": "Napoléon Bonaparte",
                "period": "Révolution française et Empire (1769-1821)",
                "short_description": "Général et empereur français qui a conquis la majeure partie de l'Europe au début du XIXe siècle.",
                "portrait_url": "https://example.com/napoleon.jpg",
                "birth_year": 1769,
                "death_year": 1821,
                "nationality": "Français",
                "tags": ["guerre", "politique", "France"],
                "achievements": [
                    "Code civil", 
                    "Réformes administratives", 
                    "Victoires militaires", 
                    "Concordat de 1801"
                ]
            }
        ]
        
        for char_data in characters_data:
            # Download and save portrait
            try:
                portrait_url = char_data.pop('portrait_url')
                response = requests.get(portrait_url)
                if response.status_code == 200:
                    file_name = f"historical_characters/{char_data['id']}.jpg"
                    portrait_file = ContentFile(response.content)
                    portrait_path = default_storage.save(file_name, portrait_file)
                    char_data['portrait'] = portrait_path
                else:
                    self.stdout.write(self.style.WARNING(f"Could not download portrait for {char_data['id']}"))
                    char_data['portrait'] = None
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error downloading portrait: {e}"))
                char_data['portrait'] = None
            
            # Extract tags and achievements
            tags = char_data.pop('tags', [])
            achievements = char_data.pop('achievements', [])
            
            # Create character
            character, created = HistoricalCharacter.objects.update_or_create(
                id=char_data['id'],
                defaults=char_data
            )
            
            # Add tags
            for tag_name in tags:
                CharacterTag.objects.get_or_create(character=character, name=tag_name)
            
            # Add achievements
            for achievement_desc in achievements:
                CharacterAchievement.objects.get_or_create(
                    character=character, 
                    description=achievement_desc
                )
            
            self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Updated'} character: {character.name}"))

    def load_dialogue_scenarios(self):
        # Leonardo da Vinci dialogue scenario
        leonardo = HistoricalCharacter.objects.get(id="leonardo-da-vinci")
        leonardo_scenario, created = DialogueScenario.objects.update_or_create(
            character=leonardo,
            defaults={
                "introduction": "Buongiorno! Je suis Leonardo da Vinci, artiste, inventeur et homme de science. Je suis ravi de partager avec vous mes connaissances sur l'art, la science et la période fascinante de la Renaissance. Que souhaitez-vous savoir?",
                "quiz_introduction": "Vous semblez avoir un vif intérêt pour mon époque et mon travail! Permettez-moi de tester vos connaissances avec quelques questions sur la Renaissance et mes contributions.",
                "conclusion": "Quel plaisir d'avoir pu partager avec vous mes connaissances et mes passions! La Renaissance était une époque extraordinaire où l'art et la science se nourrissaient mutuellement. J'espère vous avoir transmis un peu de l'émerveillement que j'ai ressenti en explorant les mystères de notre monde. Continuez à cultiver votre curiosité et votre créativité, car comme je l'ai toujours cru, 'L'apprentissage ne finit jamais'."
            }
        )
        
        # Add responses for Leonardo
        if created:
            # Joconde response
            joconde_response = DialogueResponse.objects.create(
                scenario=leonardo_scenario,
                text="Ah, La Gioconda! Ce portrait de Lisa Gherardini est l'une de mes œuvres les plus chères. J'ai travaillé sur cette peinture pendant des années, perfectionnant la technique du sfumato pour créer ces transitions douces entre les couleurs. Son sourire énigmatique continue de fasciner, n'est-ce pas?",
                mood="happy",
                fact="La Joconde a été peinte entre 1503 et 1506, mais Leonardo a continué à y travailler jusqu'à sa mort en 1519."
            )
            for keyword in ["joconde", "mona lisa", "monalise", "portrait"]:
                ResponseKeyword.objects.create(response=joconde_response, keyword=keyword)
            
            # Flying machines response
            flying_response = DialogueResponse.objects.create(
                scenario=leonardo_scenario,
                text="Les machines volantes sont parmi mes inventions préférées! J'ai étudié le vol des oiseaux pendant des années, remplissant mes carnets de croquis de leurs ailes et mouvements. Mes designs d'ornithoptères étaient basés sur l'idée que l'homme pourrait voler en imitant les oiseaux. Bien sûr, la technologie de l'époque ne permettait pas de les construire efficacement.",
                mood="thinking",
                fact="Leonardo a conçu de nombreuses machines volantes, dont un parachute, un hélicoptère primitif et plusieurs ornithoptères, 400 ans avant les premiers vols humains réussis."
            )
            for keyword in ["invention", "machine", "voler", "vol"]:
                ResponseKeyword.objects.create(response=flying_response, keyword=keyword)
            
            # Default responses
            default_responses = [
                "Voilà une question intéressante. Dans mes carnets, j'ai exploré de nombreux sujets, de l'anatomie à l'hydraulique, toujours guidé par l'observation directe de la nature.",
                "Hmm, je ne suis pas certain de comprendre votre question. Peut-être pourriez-vous me demander quelque chose sur mes peintures, mes inventions ou mes études scientifiques?",
                "La curiosité est la clé de la connaissance! J'ai toujours cherché à comprendre les mécanismes qui régissent notre monde, que ce soit dans l'art ou la science.",
                "Permettez-moi de réfléchir à cela... À la Renaissance, nous avions une approche holistique du savoir, ne séparant pas l'art de la science comme vous le faites aujourd'hui."
            ]
            for text in default_responses:
                DefaultResponse.objects.create(scenario=leonardo_scenario, text=text)
            
            # Add quizzes
            sfumato_quiz = Quiz.objects.create(
                scenario=leonardo_scenario,
                question="Quelle technique picturale ai-je perfectionnée, caractérisée par des transitions douces entre les couleurs?",
                correct_response="Excellent! Le sfumato, qui signifie 'évanoui comme la fumée' en italien, est une technique que j'ai perfectionnée pour créer des transitions douces entre les couleurs, sans lignes de contour visibles. C'est particulièrement visible dans le visage de La Joconde.",
                incorrect_response="Pas tout à fait. J'ai perfectionné le sfumato, une technique qui crée des transitions douces entre les couleurs, comme si elles s'évanouissaient comme la fumée. Le chiaroscuro concerne plutôt les contrastes marqués entre lumière et ombre.",
                order=1
            )
            QuizOption.objects.create(quiz=sfumato_quiz, text="Sfumato", is_correct=True)
            QuizOption.objects.create(quiz=sfumato_quiz, text="Chiaroscuro", is_correct=False)
            QuizOption.objects.create(quiz=sfumato_quiz, text="Trompe-l'œil", is_correct=False)
            QuizOption.objects.create(quiz=sfumato_quiz, text="Pointillisme", is_correct=False)
            
            milan_quiz = Quiz.objects.create(
                scenario=leonardo_scenario,
                question="Dans quelle ville italienne ai-je peint 'La Cène'?",
                correct_response="Bravo! J'ai peint La Cène sur un mur du réfectoire du couvent de Santa Maria delle Grazie à Milan, alors que je travaillais pour Ludovic Sforza, duc de Milan.",
                incorrect_response="Ce n'est pas correct. J'ai peint La Cène à Milan, dans le réfectoire du couvent de Santa Maria delle Grazie, pendant que j'étais au service de Ludovic Sforza.",
                order=2
            )
            QuizOption.objects.create(quiz=milan_quiz, text="Florence", is_correct=False)
            QuizOption.objects.create(quiz=milan_quiz, text="Rome", is_correct=False)
            QuizOption.objects.create(quiz=milan_quiz, text="Milan", is_correct=True)
            QuizOption.objects.create(quiz=milan_quiz, text="Venise", is_correct=False)
            
            self.stdout.write(self.style.SUCCESS(f"Created dialogue scenario for {leonardo.name}"))
        
        # Cleopatra dialogue scenario
        cleopatra = HistoricalCharacter.objects.get(id="cleopatra")
        cleopatra_scenario, created = DialogueScenario.objects.update_or_create(
            character=cleopatra,
            defaults={
                "introduction": "Salutations! Je suis Cléopâtre VII Philopator, dernière souveraine de l'Égypte ptolémaïque. On me connaît pour mon intelligence, mon éducation et mes alliances stratégiques avec Rome. Que souhaitez-vous savoir sur mon règne ou sur l'Égypte ancienne?",
                "quiz_introduction": "Vous semblez fasciné par l'Égypte ptolémaïque et mon règne! Permettez-moi de tester vos connaissances avec quelques questions sur cette période fascinante de l'histoire.",
                "conclusion": "Je vous remercie pour cet échange stimulant! Vous avez maintenant un aperçu de mon règne et des défis auxquels l'Égypte faisait face à cette époque charnière. Mon histoire a souvent été déformée par les récits romains et les interprétations ultérieures, me réduisant à une simple séductrice. La vérité est que j'étais avant tout une souveraine déterminée à préserver l'indépendance de mon royaume dans un monde en mutation. J'espère que notre conversation vous a permis de voir au-delà des mythes pour découvrir la femme politique et intellectuelle que j'étais réellement."
            }
        )
        
        if created:
            # Caesar response
            caesar_response = DialogueResponse.objects.create(
                scenario=cleopatra_scenario,
                text="Ma relation avec Jules César était autant politique que personnelle. Lorsqu'il est arrivé en Égypte en 48 avant votre ère, j'étais en conflit avec mon frère Ptolémée XIII pour le trône. César m'a aidée à reprendre le pouvoir, et nous avons eu un fils, Ptolémée XV, surnommé Césarion. Notre alliance a renforcé la position de l'Égypte face à Rome.",
                mood="thinking",
                fact="Cléopâtre a eu un fils avec Jules César, nommé Ptolémée XV César (Césarion), qui a brièvement régné comme dernier pharaon d'Égypte avant d'être exécuté sur ordre d'Octave."
            )
            for keyword in ["césar", "jules", "julius", "rome"]:
                ResponseKeyword.objects.create(response=caesar_response, keyword=keyword)
            
            # Default responses
            default_responses = [
                "Voilà une question intéressante. En tant que pharaonne d'Égypte et descendante des Ptolémées, j'ai toujours cherché à préserver l'indépendance de mon royaume face à l'expansion romaine.",
                "Hmm, cette question mérite réflexion. L'Égypte de mon époque était un carrefour de cultures, mêlant traditions égyptiennes millénaires et influences hellénistiques.",
                "Permettez-moi de vous éclairer sur ce point. Mon règne a été marqué par des alliances stratégiques visant à maintenir l'Égypte comme puissance indépendante dans un monde dominé par Rome.",
                "Je ne suis pas certaine de comprendre votre question. Peut-être pourriez-vous m'interroger sur la politique égyptienne, mes relations avec Rome, ou la culture alexandrine?"
            ]
            for text in default_responses:
                DefaultResponse.objects.create(scenario=cleopatra_scenario, text=text)
            
            # Add quizzes
            dynasty_quiz = Quiz.objects.create(
                scenario=cleopatra_scenario,
                question="De quelle origine était la dynastie des Ptolémées qui a régné sur l'Égypte?",
                correct_response="Excellent! La dynastie des Ptolémées était d'origine grecque macédonienne, fondée par Ptolémée Ier, un général d'Alexandre le Grand. Nous avons maintenu notre culture grecque tout en adoptant certaines traditions égyptiennes pour légitimer notre règne.",
                incorrect_response="Ce n'est pas exact. La dynastie des Ptolémées, dont je suis issue, était d'origine grecque macédonienne. Mon ancêtre Ptolémée Ier était un général d'Alexandre le Grand qui a pris le contrôle de l'Égypte après sa mort.",
                order=1
            )
            QuizOption.objects.create(quiz=dynasty_quiz, text="Égyptienne", is_correct=False)
            QuizOption.objects.create(quiz=dynasty_quiz, text="Perse", is_correct=False)
            QuizOption.objects.create(quiz=dynasty_quiz, text="Grecque (Macédonienne)", is_correct=True)
            QuizOption.objects.create(quiz=dynasty_quiz, text="Romaine", is_correct=False)
            
            self.stdout.write(self.style.SUCCESS(f"Created dialogue scenario for {cleopatra.name}"))

