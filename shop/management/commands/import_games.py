from django.core.management.base import BaseCommand
from shop.utils.rawg_api import search_games, add_game_from_rawg
from shop.models import Game
import random

class Command(BaseCommand):
    help = 'Import games from RAWG API'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of games to import')

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f"Starting import of {count} games from RAWG...")

        # Popular search terms to get variety
        queries = ['action', 'rpg', 'indie', 'strategy', 'shooter', 'adventure', 'cyberpunk', 'elden', 'hades', 'stardew']
        imported = 0

        for _ in range(count):
            query = random.choice(queries)
            result = search_games(query, page_size=5)
            
            if result.get('error') or not result.get('results'):
                continue

            for game_data in result['results'][:2]:
                game, created = add_game_from_rawg(game_data)
                if created:
                    imported += 1
                    self.stdout.write(self.style.SUCCESS(f"Added: {game.title}"))

        self.stdout.write(self.style.SUCCESS(f"\nSuccessfully imported {imported} new games."))
