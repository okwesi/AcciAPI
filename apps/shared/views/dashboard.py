from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.jurisdiction.models import Branch
from apps.member.models import Member
from apps.shared.serializers.custom_types import CustomTypesSerializer


class DashboardViewSet(viewsets.GenericViewSet):
    serializer_class = CustomTypesSerializer
    permission_classes = [IsAuthenticated]

    def get_dashboard_data(self, request):
        # Get the user's branch
        branch = request.user.branch

        # Calculate the current date and age thresholds
        current_date = timezone.now().date()
        child_threshold = current_date.replace(year=current_date.year - 15)
        youth_threshold = current_date.replace(year=current_date.year - 45)

        # Perform queries to get all required data
        jurisdiction_counts = Branch.objects.aggregate(
            branches=Count('id'),
            districts=Count('district', distinct=True),
            areas=Count('district__area', distinct=True)
        )

        member_data = Member.objects.aggregate(
            branch_members=Count('id', filter=Q(branch=branch)),
            district_members=Count('id', filter=Q(branch__district=branch.district)),
            area_members=Count('id', filter=Q(branch__district__area=branch.district.area)),
            church_members=Count('id'),
            male_count=Count('id', filter=Q(gender='m')),
            female_count=Count('id', filter=Q(gender='f')),
            children_count=Count('id', filter=Q(date_of_birth__gt=child_threshold)),
            youth_count=Count('id', filter=Q(date_of_birth__lte=child_threshold, date_of_birth__gt=youth_threshold)),
            adult_count=Count('id', filter=Q(date_of_birth__lte=youth_threshold))
        )

        total_members = member_data['church_members']
        male_percentage = (member_data['male_count'] / total_members) * 100 if total_members > 0 else 0
        female_percentage = (member_data['female_count'] / total_members) * 100 if total_members > 0 else 0

        results = {
            "jurisdictions": jurisdiction_counts,
            "members": {
                'branch_members': member_data['branch_members'],
                'district_members': member_data['district_members'],
                'area_members': member_data['area_members'],
                'church_members': total_members
            },
            "gender_distribution": {
                'male_percentage': round(male_percentage, 2),
                'female_percentage': round(female_percentage, 2)
            },
            "age_demographics": {
                'children_percentage': round((member_data['children_count'] / total_members) * 100,
                                             2) if total_members > 0 else 0,
                'youth_percentage': round((member_data['youth_count'] / total_members) * 100,
                                          2) if total_members > 0 else 0,
                'adult_percentage': round((member_data['adult_count'] / total_members) * 100,
                                          2) if total_members > 0 else 0
            }
        }

        return Response(results, status=status.HTTP_200_OK)
