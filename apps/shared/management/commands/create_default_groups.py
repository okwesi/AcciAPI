from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

from apps.accounts.models import GroupRank


class Command(BaseCommand):
    help = 'Create default groups and set their ranks'

    def handle(self, *args, **kwargs):
        # List of group names and ranks to get or create
        group_data = [{'name': 'Super Admin', 'rank': 1}, {'name': 'Admin', 'rank': 2}]

        for data in group_data:
            group, created = Group.objects.get_or_create(name=data['name'])
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created group {data["name"]}'))

            # Set the rank
            GroupRank.objects.update_or_create(group=group, defaults={'rank': data['rank']},
                                               is_default=True)
            self.stdout.write(self.style.SUCCESS(f'Set rank {data["rank"]} for group {data["name"]}'))
