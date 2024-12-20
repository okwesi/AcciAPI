import factory
from django.utils import timezone

from apps.accounts.tests.factory import UserFactory
from apps.events.models import Event, EventAmount, EventRegistration


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    location = factory.Faker('address')
    start_datetime = factory.LazyFunction(timezone.now)
    end_datetime = factory.LazyFunction(timezone.now)
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('paragraph')
    cover_image = factory.django.ImageField(filename='cover_image.jpg')


class EventAmountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventAmount

    event = factory.SubFactory(EventFactory)
    amount = factory.Faker('random_int', min=100, max=1000)
    currency = factory.Faker('currency_code')


class EventRegistrationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventRegistration

    event = factory.SubFactory(EventFactory)
    user = factory.SubFactory(UserFactory)
    full_name = factory.Faker('name')
    email = factory.Faker('email')
    phone_number = factory.Faker('phone_number')
    gender = factory.Iterator(['M', 'F'])
    already_iyf_member = factory.Iterator(['yes', 'no'])
    region = factory.Faker('state')
    city_town = factory.Faker('city')
    age_range = factory.Iterator(['14-16', '17-19', '20-24', '25-29', '30-34', '35-39', '39+'])
    institution = factory.Faker('company')
    academy = factory.Faker('word')
    preferred_language = factory.Faker('language_name')
    shirt_size = factory.Iterator(['s', 'm', 'l', 'xl', 'xxl'])
    section_category = factory.Iterator(['jhs', 'shs', 'tertiary'])
    amount = factory.Faker('random_int', min=50, max=500)
    currency = factory.Faker('currency_code')
    terms_and_conditions = True
    is_paid = factory.Faker('boolean')
