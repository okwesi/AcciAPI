from django.core.management.base import BaseCommand

from apps.member.models import Member


class Command(BaseCommand):
    help = 'Delete all members with phone numbers containing "+" or "-"'

    def handle(self, *args, **kwargs):
        # Filter members with invalid phone numbers
        invalid_members = Member.objects.filter(phone_number__regex=r'[+-]')

        # Get the count before deletion for reporting
        count = invalid_members.count()

        # Delete the invalid members
        invalid_members.delete()

        if count:
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} member(s) with invalid phone numbers.'))
        else:
            self.stdout.write(self.style.WARNING('No members found with invalid phone numbers.'))
