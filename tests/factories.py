import factory
from src.models import Quote


class QuoteFactory(factory.Factory):
    class Meta:
        model = Quote

    id = factory.Sequence(lambda n: n + 1)
    # Rastgele 10 kelimelik bir söz üretir
    text = factory.Faker("sentence", nb_words=10)
    # Rastgele bir yazar ismi üretir
    author = factory.Faker("name")
    # Sırayla bu kategorileri atar
    category = factory.Iterator(["motivation", "philosophy", "history"])
