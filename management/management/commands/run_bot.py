from django.core.management.base import BaseCommand, CommandError
import asyncio
from telega.views import bot


class Command(BaseCommand):
    help = "starting bot"

    def add_arguments(self, parser):
        parser.add_argument("poll_ids", nargs="+", type=int)

    def handle(self, *args, **options):

        asyncio.run(bot.polling())