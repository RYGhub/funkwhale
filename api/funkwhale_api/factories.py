import uuid
import factory
import random
import persisting_theory

from django.conf import settings

from faker.providers import internet as internet_provider


class FactoriesRegistry(persisting_theory.Registry):
    look_into = "factories"

    def prepare_name(self, data, name=None):
        return name or data._meta.model._meta.label


registry = FactoriesRegistry()


def ManyToManyFromList(field_name):
    """
    To automate the pattern described in
    http://factoryboy.readthedocs.io/en/latest/recipes.html#simple-many-to-many-relationship
    """

    @factory.post_generation
    def inner(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            field = getattr(self, field_name)
            field.add(*extracted)

    return inner


class NoUpdateOnCreate:
    """
    Factory boy calls save after the initial create. In most case, this
    is not needed, so we disable this behaviour
    """

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        return


TAGS_DATA = {
    "type": [
        "acoustic",
        "acid",
        "ambient",
        "alternative",
        "brutalist",
        "chill",
        "club",
        "cold",
        "cool",
        "contemporary",
        "dark",
        "doom",
        "electro",
        "folk",
        "freestyle",
        "fusion",
        "garage",
        "glitch",
        "hard",
        "healing",
        "industrial",
        "instrumental",
        "hardcore",
        "holiday",
        "hot",
        "liquid",
        "modern",
        "minimalist",
        "new",
        "parody",
        "postmodern",
        "progressive",
        "smooth",
        "symphonic",
        "traditional",
        "tribal",
        "metal",
    ],
    "genre": [
        "blues",
        "classical",
        "chiptune",
        "dance",
        "disco",
        "funk",
        "jazz",
        "house",
        "hiphop",
        "NewAge",
        "pop",
        "punk",
        "rap",
        "RnB",
        "reggae",
        "rock",
        "soul",
        "soundtrack",
        "ska",
        "swing",
        "trance",
    ],
    "nationality": [
        "Afghan",
        "Albanian",
        "Algerian",
        "American",
        "Andorran",
        "Angolan",
        "Antiguans",
        "Argentinean",
        "Armenian",
        "Australian",
        "Austrian",
        "Azerbaijani",
        "Bahamian",
        "Bahraini",
        "Bangladeshi",
        "Barbadian",
        "Barbudans",
        "Batswana",
        "Belarusian",
        "Belgian",
        "Belizean",
        "Beninese",
        "Bhutanese",
        "Bolivian",
        "Bosnian",
        "Brazilian",
        "British",
        "Bruneian",
        "Bulgarian",
        "Burkinabe",
        "Burmese",
        "Burundian",
        "Cambodian",
        "Cameroonian",
        "Canadian",
        "Cape Verdean",
        "Central African",
        "Chadian",
        "Chilean",
        "Chinese",
        "Colombian",
        "Comoran",
        "Congolese",
        "Costa Rican",
        "Croatian",
        "Cuban",
        "Cypriot",
        "Czech",
        "Danish",
        "Djibouti",
        "Dominican",
        "Dutch",
        "East Timorese",
        "Ecuadorean",
        "Egyptian",
        "Emirian",
        "Equatorial Guinean",
        "Eritrean",
        "Estonian",
        "Ethiopian",
        "Fijian",
        "Filipino",
        "Finnish",
        "French",
        "Gabonese",
        "Gambian",
        "Georgian",
        "German",
        "Ghanaian",
        "Greek",
        "Grenadian",
        "Guatemalan",
        "Guinea-Bissauan",
        "Guinean",
        "Guyanese",
        "Haitian",
        "Herzegovinian",
        "Honduran",
        "Hungarian",
        "I-Kiribati",
        "Icelander",
        "Indian",
        "Indonesian",
        "Iranian",
        "Iraqi",
        "Irish",
        "Israeli",
        "Italian",
        "Ivorian",
        "Jamaican",
        "Japanese",
        "Jordanian",
        "Kazakhstani",
        "Kenyan",
        "Kittian and Nevisian",
        "Kuwaiti",
        "Kyrgyz",
        "Laotian",
        "Latvian",
        "Lebanese",
        "Liberian",
        "Libyan",
        "Liechtensteiner",
        "Lithuanian",
        "Luxembourger",
        "Macedonian",
        "Malagasy",
        "Malawian",
        "Malaysian",
        "Maldivian",
        "Malian",
        "Maltese",
        "Marshallese",
        "Mauritanian",
        "Mauritian",
        "Mexican",
        "Micronesian",
        "Moldovan",
        "Monacan",
        "Mongolian",
        "Moroccan",
        "Mosotho",
        "Motswana",
        "Mozambican",
        "Namibian",
        "Nauruan",
        "Nepalese",
        "New Zealander",
        "Ni-Vanuatu",
        "Nicaraguan",
        "Nigerian",
        "Nigerien",
        "North Korean",
        "Northern Irish",
        "Norwegian",
        "Omani",
        "Pakistani",
        "Palauan",
        "Panamanian",
        "Papua New Guinean",
        "Paraguayan",
        "Peruvian",
        "Polish",
        "Portuguese",
        "Qatari",
        "Romanian",
        "Russian",
        "Rwandan",
        "Saint Lucian",
        "Salvadoran",
        "Samoan",
        "San Marinese",
        "Sao Tomean",
        "Saudi",
        "Scottish",
        "Senegalese",
        "Serbian",
        "Seychellois",
        "Sierra Leonean",
        "Singaporean",
        "Slovakian",
        "Slovenian",
        "Solomon Islander",
        "Somali",
        "South African",
        "South Korean",
        "Spanish",
        "Sri Lankan",
        "Sudanese",
        "Surinamer",
        "Swazi",
        "Swedish",
        "Swiss",
        "Syrian",
        "Taiwanese",
        "Tajik",
        "Tanzanian",
        "Thai",
        "Togolese",
        "Tongan",
        "Trinidadian",
        "Tunisian",
        "Turkish",
        "Tuvaluan",
        "Ugandan",
        "Ukrainian",
        "Uruguayan",
        "Uzbekistani",
        "Venezuelan",
        "Vietnamese",
        "Welsh",
        "Yemenite",
        "Zambian",
        "Zimbabwean",
    ],
}


class FunkwhaleProvider(internet_provider.Provider):
    """
    Our own faker data generator, since built-in ones are sometimes
    not random enough
    """

    def federation_url(self, prefix="", local=False):
        def path_generator():
            return "{}/{}".format(prefix, uuid.uuid4())

        domain = settings.FEDERATION_HOSTNAME if local else self.domain_name()
        protocol = "https"
        path = path_generator()
        return "{}://{}/{}".format(protocol, domain, path)

    def user_name(self):
        u = super().user_name()
        return "{}{}".format(u, random.randint(10, 999))

    def music_genre(self):
        return random.choice(TAGS_DATA["genre"])

    def music_type(self):
        return random.choice(TAGS_DATA["type"])

    def music_nationality(self):
        return random.choice(TAGS_DATA["nationality"])

    def music_hashtag(self, prefix_length=4):
        genre = self.music_genre()
        prefixes = [genre]
        nationality = False
        while len(prefixes) < prefix_length:
            if nationality:
                t = "type"
            else:
                t = random.choice(["type", "nationality", "genre"])

            if t == "nationality":
                nationality = True

            choice = random.choice(TAGS_DATA[t])
            if choice in prefixes:
                continue
            prefixes.append(choice)

        return "".join(
            [p.capitalize().strip().replace(" ", "") for p in reversed(prefixes)]
        )


factory.Faker.add_provider(FunkwhaleProvider)
