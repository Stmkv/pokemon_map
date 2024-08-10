import folium
import json

from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.utils.timezone import localtime

from pokemon_entities.models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def get_url(request, url):
    return f'http://{request.get_host()}{url}'


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    local_time = localtime()
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    pokemons = PokemonEntity.objects.filter(disappear_at__gt=local_time, appeared_at__lt=local_time)
    for pokemon_entity in pokemons:
        add_pokemon(
            folium_map,
            pokemon_entity.lat,
            pokemon_entity.lon,
            get_url(request, pokemon_entity.pokemon.image.url)
        )

    pokemons_on_page = []
    pokemons = Pokemon.objects.all()
    for pokemon in pokemons:
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': get_url(request, pokemon.image.url),
            'title_ru': pokemon.title_ru
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    local_time = localtime()
    requested_pokemon = Pokemon.objects.get(id=pokemon_id)

    pokemon_map = PokemonEntity.objects.filter(pokemon=requested_pokemon,
                                               disappear_at__gt=local_time,
                                               appeared_at__lt=local_time)
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon in pokemon_map:
        add_pokemon(
            folium_map,
            pokemon.lat,
            pokemon.lon,
            f'http://{request.get_host()}{requested_pokemon.image.url}'
        )
    pokemon_view = {
        'pokemon_id': requested_pokemon,
        'img_url': f'http://{request.get_host()}{requested_pokemon.image.url}',
        'title_ru': requested_pokemon.title_ru,
        'title_en': requested_pokemon.title_en,
        'title_jp': requested_pokemon.title_jp,
        "description": requested_pokemon.description,
    }

    if requested_pokemon.previous_evolution:
        pokemon_view['previous_evolution'] = {
            'pokemon_id': requested_pokemon.previous_evolution.id,
            'img_url': f'http://{request.get_host()}{requested_pokemon.previous_evolution.image.url}',
            'title_ru': requested_pokemon.previous_evolution.title_ru,
            'title_en': requested_pokemon.previous_evolution.title_en,
            'title_jp': requested_pokemon.previous_evolution.title_jp
        }

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemon_view
    })
