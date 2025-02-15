# Generated by Django 4.2.6 on 2024-08-31 14:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_user_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': [('account_management_list_groups_and_roles', 'view groups and roles'), ('account_management_create_group_and_assign_roles', 'create new groups and assign roles'), ('account_management_update_groups_and_roles', 'update existing groups and their roles'), ('account_management_create_admin', 'create a new admin'), ('account_management_list_admins', 'view admins'), ('account_management_delete_admin', 'delete admin'), ('account_management_update_admin', 'update admin'), ('member_management_list_members', 'view members'), ('member_management_update_member', 'update an existing member'), ('member_management_create_member', 'add a new member'), ('member_management_delete_member', 'delete a member'), ('jurisdiction_management_view_branch_members', 'view members of my branch'), ('jurisdiction_management_view_district_members', 'view members of my district'), ('jurisdiction_management_view_area_members', 'view members of my area'), ('jurisdiction_management_view_branches', 'view branches'), ('jurisdiction_management_update_branch', 'update an existing branch'), ('jurisdiction_management_create_branch', 'add a new branch'), ('jurisdiction_management_delete_branch', 'delete a branch'), ('jurisdiction_management_view_districts', 'view districts'), ('jurisdiction_management_update_district', 'update an existing district'), ('jurisdiction_management_create_district', 'add a new district'), ('jurisdiction_management_delete_district', 'delete a district'), ('jurisdiction_management_view_areas', 'view areas'), ('jurisdiction_management_update_area', 'update an existing area'), ('jurisdiction_management_create_area', 'add a new area'), ('jurisdiction_management_delete_area', 'delete a area')]},
        ),
    ]
