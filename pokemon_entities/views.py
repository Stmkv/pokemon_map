import folium

from django.shortcuts import get_object_or_404, render
from django.utils.timezone import localtime

from pokemon_entities.models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    local_time = localtime()
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    entity = PokemonEntity.objects.filter(disappear_at__gt=local_time, appeared_at__lt=local_time)
    for pokemon_entity in entity:
        add_pokemon(
            folium_map,
            pokemon_entity.lat,
            pokemon_entity.lon,
            request.build_absolute_uri(pokemon_entity.pokemon.image.url)
        )

    pokemons_on_page = []
    pokemons = Pokemon.objects.all()
    for pokemon in pokemons:
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': request.build_absolute_uri(pokemon.image.url),
            'title_ru': pokemon.title_ru
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    local_time = localtime()
    requested_pokemon = get_object_or_404(Pokemon, id=pokemon_id)

    pokemon_entities = PokemonEntity.objects.filter(pokemon=requested_pokemon,
                                               disappear_at__gt=local_time,
                                               appeared_at__lt=local_time)
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon in pokemon_entities:
        add_pokemon(
            folium_map,
            pokemon.lat,
            pokemon.lon,
            request.build_absolute_uri(requested_pokemon.image.url)
        )
    pokemon_view = {
        'pokemon_id': requested_pokemon,
        'img_url': request.build_absolute_uri(requested_pokemon.image.url),
        'title_ru': requested_pokemon.title_ru,
        'title_en': requested_pokemon.title_en,
        'title_jp': requested_pokemon.title_jp,
        "description": requested_pokemon.description,
    }

    if requested_pokemon.previous_evolution:
        pokemon_view['previous_evolution'] = {
            'pokemon_id': requested_pokemon.previous_evolution.id,
            'img_url': request.build_absolute_uri(requested_pokemon.previous_evolution.image.url),
            'title_ru': requested_pokemon.previous_evolution.title_ru,
            'title_en': requested_pokemon.previous_evolution.title_en,
            'title_jp': requested_pokemon.previous_evolution.title_jp
        }
    next_evolution = requested_pokemon.next_evolutions.all()
    if next_evolution:
        next_evolution = next_evolution[0]
        next_evolution = {
            'pokemon_id': next_evolution.id,
            'img_url': request.build_absolute_uri(next_evolution.image.url),
            'title_ru': next_evolution.title_ru
        }
        pokemon_view['next_evolution'] = next_evolution
    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemon_view
    })
