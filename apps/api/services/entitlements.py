"""Feature entitlements based on organization plan."""

from datetime import datetime
from typing import NamedTuple
from models import Organization

class EntitlementCheck(NamedTuple):
    allowed: bool
    reason: str
    upgrade_path: str

class EntitlementsService:
    """Check feature entitlements for an organization."""
    
    # Plan feature matrix
    FEATURE_MATRIX = {
        'free': {
            'unlimited_projects': False,
            'briefing_history_days': 7,
            'integrations.calendar': False,
            'integrations.gsc': False,
            'multi_runtime': False,
            'team_features': False,
            'max_users': 1,
        },
        'pro': {
            'unlimited_projects': True,
            'briefing_history_days': 365,  # unlimited
            'integrations.calendar': True,
            'integrations.gsc': True,
            'multi_runtime': True,
            'team_features': False,
            'max_users': 1,
        },
        'team': {
            'unlimited_projects': True,
            'briefing_history_days': 365,
            'integrations.calendar': True,
            'integrations.gsc': True,
            'multi_runtime': True,
            'team_features': True,
            'max_users': 999,  # Enforced at member-add time
        }
    }
    
    @staticmethod
    def get_plan(org: Organization) -> str:
        """Determine effective plan (including trial)."""
        if org.trial_ends_at and datetime.utcnow() < org.trial_ends_at:
            # Trial users get Pro features
            return 'pro'
        return org.plan or 'free'
    
    @staticmethod
    def check_entitlement(org: Organization, feature: str) -> EntitlementCheck:
        """Check if organization is entitled to a feature.
        
        In personal mode, all features are always allowed.
        In multi-tenant mode, feature access is determined by the organization's plan.
        """
        from personal_mode import is_personal
        
        # In personal mode, everything is allowed
        if is_personal():
            return EntitlementCheck(allowed=True, reason='personal_mode', upgrade_path='')
        
        # Multi-tenant mode: check against plan matrix
        plan = EntitlementsService.get_plan(org)
        matrix = EntitlementsService.FEATURE_MATRIX.get(plan, {})
        
        allowed = matrix.get(feature, False)
        
        if allowed:
            return EntitlementCheck(allowed=True, reason='', upgrade_path='')
        
        # Not allowed - provide reason and upgrade path
        if plan == 'free':
            reason = f"Feature '{feature}' requires Pro plan or higher"
            upgrade_path = '/settings/billing'
        elif plan == 'pro' and feature == 'team_features':
            reason = "Team features require Team plan"
            upgrade_path = '/settings/billing'
        else:
            reason = f"Feature '{feature}' not available on {plan} plan"
            upgrade_path = '/settings/billing'
        
        return EntitlementCheck(allowed=False, reason=reason, upgrade_path=upgrade_path)
    
    @staticmethod
    def check_project_limit(org: Organization, current_projects: int) -> EntitlementCheck:
        """Check if org can create another project.
        
        In personal mode, unlimited projects are allowed.
        """
        from personal_mode import is_personal
        
        # In personal mode, unlimited projects
        if is_personal():
            return EntitlementCheck(allowed=True, reason='personal_mode', upgrade_path='')
        
        # Multi-tenant mode: check against plan
        plan = EntitlementsService.get_plan(org)
        matrix = EntitlementsService.FEATURE_MATRIX.get(plan, {})
        
        if matrix.get('unlimited_projects', False):
            return EntitlementCheck(allowed=True, reason='', upgrade_path='')
        
        # Free plan: 1 project max
        if current_projects >= 1:
            return EntitlementCheck(
                allowed=False,
                reason="Free plan limited to 1 project. Upgrade to Pro for unlimited.",
                upgrade_path='/settings/billing'
            )
        
        return EntitlementCheck(allowed=True, reason='', upgrade_path='')
