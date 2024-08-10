from django.db import models  # noqa F401


# your models here
class Pokemon(models.Model):
    title_ru = models.CharField(max_length=200, verbose_name='Имя на русском языке')
    title_en = models.CharField(null=True, blank=True, max_length=200, verbose_name='Имя на английском')
    title_jp = models.CharField(null=True, blank=True, max_length=200, verbose_name='Имя на японском')
    image = models.ImageField(null=True, blank=True, verbose_name="Изображение")
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    previous_evolution = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='next_evolution', verbose_name="Предыдущая эволюция")

    def __str__(self):
        return self.title_ru


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE, related_name="pokemon_entities", verbose_name="Покемон")
    lat = models.FloatField(verbose_name='Широта')
    lon = models.FloatField(verbose_name='Долгота')
    appeared_at = models.DateTimeField(verbose_name='Появится в')
    disappear_at = models.DateTimeField(verbose_name='Убежит в')
    level = models.IntegerField(null=True, blank=True, verbose_name='Уровень')
    health = models.IntegerField(null=True, blank=True, verbose_name='Здоровье')
    strength = models.IntegerField(null=True, blank=True, verbose_name='Сила')
    defense = models.IntegerField(null=True, blank=True, verbose_name='Защита')
    stamina = models.IntegerField(null=True, blank=True, verbose_name='Выносливость')

    def __str__(self):
        return self.pokemon.title_ru
