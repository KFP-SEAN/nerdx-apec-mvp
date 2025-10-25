"""
Cell Management Service
셀 관리 핵심 서비스
"""
import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import uuid4

from database import CellDB
from models.cell_models import (
    Cell, CellCreateRequest, CellUpdateRequest, CellStatus, CellType
)
from services.integrations.odoo_service import odoo_service

logger = logging.getLogger(__name__)


class CellService:
    """Cell management service"""

    async def create_cell(
        self,
        db: Session,
        request: CellCreateRequest
    ) -> Cell:
        """
        Create new cell

        Args:
            db: Database session
            request: Cell creation request

        Returns:
            Created cell
        """
        try:
            # Generate cell ID
            cell_id = f"cell-{uuid4().hex[:12]}"

            # Create Odoo analytic account
            odoo_account_id = None
            odoo_account_code = None

            if request.cell_type == CellType.DOMESTIC:
                odoo_account_code = f"CELL-DOM-{cell_id[-6:].upper()}"
            elif request.cell_type == CellType.GLOBAL:
                odoo_account_code = f"CELL-GLO-{cell_id[-6:].upper()}"
            else:  # NEW_MARKET
                odoo_account_code = f"CELL-NEW-{cell_id[-6:].upper()}"

            try:
                odoo_account_id = await odoo_service.create_analytic_account(
                    name=request.cell_name,
                    code=odoo_account_code
                )
                logger.info(f"Created Odoo analytic account: {odoo_account_id}")
            except Exception as e:
                logger.warning(f"Failed to create Odoo analytic account: {e}")
                # Continue without Odoo account

            # Create database record
            db_cell = CellDB(
                cell_id=cell_id,
                cell_name=request.cell_name,
                cell_type=request.cell_type.value,
                manager_name=request.manager_name,
                manager_email=request.manager_email,
                manager_phone=request.manager_phone,
                salesforce_account_ids=request.salesforce_account_ids,
                odoo_analytic_account_id=odoo_account_id,
                odoo_analytic_account_code=odoo_account_code,
                monthly_revenue_target=request.monthly_revenue_target,
                monthly_gross_profit_target=request.monthly_gross_profit_target,
                status="active"
            )

            db.add(db_cell)
            db.commit()
            db.refresh(db_cell)

            logger.info(f"Created cell: {cell_id} - {request.cell_name}")

            # Convert to Pydantic model
            return self._db_to_model(db_cell)

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create cell: {e}")
            raise

    async def get_cell(self, db: Session, cell_id: str) -> Optional[Cell]:
        """Get cell by ID"""
        db_cell = db.query(CellDB).filter(CellDB.cell_id == cell_id).first()

        if not db_cell:
            return None

        return self._db_to_model(db_cell)

    async def list_cells(
        self,
        db: Session,
        cell_type: Optional[CellType] = None,
        status: Optional[CellStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Cell]:
        """List cells with filters"""
        query = db.query(CellDB)

        if cell_type:
            query = query.filter(CellDB.cell_type == cell_type.value)

        if status:
            query = query.filter(CellDB.status == status.value)

        db_cells = query.offset(skip).limit(limit).all()

        return [self._db_to_model(cell) for cell in db_cells]

    async def update_cell(
        self,
        db: Session,
        cell_id: str,
        request: CellUpdateRequest
    ) -> Optional[Cell]:
        """Update cell"""
        try:
            db_cell = db.query(CellDB).filter(CellDB.cell_id == cell_id).first()

            if not db_cell:
                return None

            # Update fields
            if request.cell_name is not None:
                db_cell.cell_name = request.cell_name

            if request.manager_name is not None:
                db_cell.manager_name = request.manager_name

            if request.manager_email is not None:
                db_cell.manager_email = request.manager_email

            if request.manager_phone is not None:
                db_cell.manager_phone = request.manager_phone

            if request.salesforce_account_ids is not None:
                db_cell.salesforce_account_ids = request.salesforce_account_ids

            if request.monthly_revenue_target is not None:
                db_cell.monthly_revenue_target = request.monthly_revenue_target

            if request.monthly_gross_profit_target is not None:
                db_cell.monthly_gross_profit_target = request.monthly_gross_profit_target

            if request.status is not None:
                db_cell.status = request.status.value

            db_cell.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(db_cell)

            logger.info(f"Updated cell: {cell_id}")

            return self._db_to_model(db_cell)

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update cell {cell_id}: {e}")
            raise

    async def delete_cell(self, db: Session, cell_id: str) -> bool:
        """Delete (deactivate) cell"""
        try:
            db_cell = db.query(CellDB).filter(CellDB.cell_id == cell_id).first()

            if not db_cell:
                return False

            # Soft delete - set status to inactive
            db_cell.status = "inactive"
            db_cell.updated_at = datetime.utcnow()

            db.commit()

            logger.info(f"Deleted (deactivated) cell: {cell_id}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete cell {cell_id}: {e}")
            raise

    def _db_to_model(self, db_cell: CellDB) -> Cell:
        """Convert database model to Pydantic model"""
        return Cell(
            cell_id=db_cell.cell_id,
            cell_name=db_cell.cell_name,
            cell_type=CellType(db_cell.cell_type),
            manager_name=db_cell.manager_name,
            manager_email=db_cell.manager_email,
            manager_phone=db_cell.manager_phone,
            salesforce_account_ids=db_cell.salesforce_account_ids or [],
            salesforce_opportunity_filters=db_cell.salesforce_opportunity_filters,
            odoo_analytic_account_id=db_cell.odoo_analytic_account_id,
            odoo_analytic_account_code=db_cell.odoo_analytic_account_code,
            monthly_revenue_target=db_cell.monthly_revenue_target,
            monthly_gross_profit_target=db_cell.monthly_gross_profit_target,
            gross_profit_margin_target=db_cell.gross_profit_margin_target,
            status=CellStatus(db_cell.status),
            created_at=db_cell.created_at,
            updated_at=db_cell.updated_at
        )


# Singleton instance
cell_service = CellService()
