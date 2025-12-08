"""
Layer 5: Company Service

Manages company profiles and links users to companies.
Uses synchronous SQLAlchemy sessions (same pattern as L1-L4).
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, update, func

from app.models.company_profile_models import CompanyProfile
from app.layer5.schemas.company import CompanyProfileResponse, CompanyProfileUpdate, CompanyCreate


class CompanyService:
    """Service for company profile management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_company(self, company_id: str) -> Optional[CompanyProfile]:
        """Get company by ID"""
        result = self.db.execute(
            select(CompanyProfile).where(CompanyProfile.company_id == company_id)
        )
        return result.scalar_one_or_none()
    
    def get_companies_by_industry(self, industry: str) -> List[CompanyProfile]:
        """Get all companies in an industry"""
        result = self.db.execute(
            select(CompanyProfile).where(CompanyProfile.industry == industry)
        )
        return list(result.scalars().all())
    
    def list_companies(
        self, 
        industry: Optional[str] = None,
        business_scale: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[CompanyProfile]:
        """List companies with optional filters"""
        query = select(CompanyProfile)
        
        if industry:
            query = query.where(CompanyProfile.industry == industry)
        if business_scale:
            query = query.where(CompanyProfile.business_scale == business_scale)
        
        query = query.limit(limit).offset(offset)
        
        result = self.db.execute(query)
        return list(result.scalars().all())
    
    def get_industries(self) -> List[str]:
        """Get list of all unique industries"""
        result = self.db.execute(
            select(CompanyProfile.industry).distinct()
        )
        return [row[0] for row in result.fetchall() if row[0]]
    
    def create_company(self, company_data: CompanyCreate) -> CompanyProfile:
        """Create a new company profile"""
        # Check if company already exists
        existing = self.get_company(company_data.company_id)
        if existing:
            raise ValueError(f"Company with ID {company_data.company_id} already exists")
        
        company = CompanyProfile(
            company_id=company_data.company_id,
            company_name=company_data.company_name,
            industry=company_data.industry,
            sub_industry=company_data.sub_industry,
            business_scale=company_data.business_scale,
            description=company_data.description
        )
        
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        
        return company
    
    def update_company(
        self, 
        company_id: str, 
        update_data: CompanyProfileUpdate
    ) -> Optional[CompanyProfile]:
        """Update company profile"""
        company = self.get_company(company_id)
        
        if not company:
            return None
        
        # Build update dict from non-None fields
        update_dict = {
            k: v for k, v in update_data.model_dump().items() 
            if v is not None
        }
        
        if update_dict:
            self.db.execute(
                update(CompanyProfile)
                .where(CompanyProfile.company_id == company_id)
                .values(**update_dict)
            )
            self.db.commit()
            self.db.refresh(company)
        
        return company
    
    def count_companies(self, industry: Optional[str] = None) -> int:
        """Count companies with optional industry filter"""
        query = select(func.count(CompanyProfile.company_id))
        
        if industry:
            query = query.where(CompanyProfile.industry == industry)
        
        result = self.db.execute(query)
        return result.scalar() or 0
    
    def get_company_stats(self) -> dict:
        """Get company statistics"""
        # Total companies
        total_result = self.db.execute(
            select(func.count(CompanyProfile.company_id))
        )
        total = total_result.scalar() or 0
        
        # By industry
        industry_result = self.db.execute(
            select(
                CompanyProfile.industry,
                func.count(CompanyProfile.company_id).label('count')
            ).group_by(CompanyProfile.industry)
        )
        by_industry = {row[0]: row[1] for row in industry_result.fetchall()}
        
        # By scale
        scale_result = self.db.execute(
            select(
                CompanyProfile.business_scale,
                func.count(CompanyProfile.company_id).label('count')
            ).group_by(CompanyProfile.business_scale)
        )
        by_scale = {row[0] or 'unknown': row[1] for row in scale_result.fetchall()}
        
        return {
            "total": total,
            "by_industry": by_industry,
            "by_scale": by_scale
        }
