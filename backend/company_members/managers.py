from django.db import models


class MembershipManager(models.Manager):
    """
    Manager for CompanyMember model.
    Membership resolves tenancy - NOT CompanyManager.
    """

    def for_user(self, user):
        return self.filter(user=user, is_active=True)

    def primary_for_user(self, user):
        return self.filter(user=user, is_active=True, is_primary=True).first()

    def for_company(self, company):
        return self.filter(company=company, is_active=True)

    def active_members(self, company):
        return self.filter(company=company, is_active=True)

    def add_member(self, user, company, role, is_primary=False):
        membership, created = self.get_or_create(
            user=user,
            company=company,
            defaults={"role": role, "is_primary": is_primary},
        )
        if not created and not membership.is_active:
            membership.is_active = True
            membership.role = role
            membership.save()
        return membership

    def deactivate_member(self, user, company):
        return self.filter(user=user, company=company).update(is_active=False)

    def set_primary(self, user, company):
        self.filter(user=user, is_active=True).update(is_primary=False)
        return self.filter(user=user, company=company).update(is_primary=True)
