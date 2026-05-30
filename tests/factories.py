import factory
from src.models import Quote

class QuoteFactory(factory.Factory):
    class Meta:
        model = Quote

    id = factory.Sequence(lambda n: n + 1)
    text = factory.Faker("sentence", nb_words=10) # Rastgele 10 kelimelik bir söz üretir
    author = factory.Faker("name")                # Rastgele bir yazar ismi üretir
    category = factory.Iterator(["motivation", "philosophy", "history"]) # Sırayla bu kategorileri atar
