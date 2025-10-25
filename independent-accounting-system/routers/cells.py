"""
Cell Management API Router
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.cell_models import (
    Cell, CellCreateRequest, CellUpdateRequest,
    CellListResponse, CellType, CellStatus
)
from services.cell_manager.cell_service import cell_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/cells", tags=["Cells"])


@router.post("/", response_model=Cell, status_code=status.HTTP_201_CREATED)
async def create_cell(request: CellCreateRequest, db: Session = Depends(get_db)):
    """Create new cell"""
    try:
        cell = await cell_service.create_cell(db, request)
        return cell
    except Exception as e:
        logger.error(f"Failed to create cell: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{cell_id}", response_model=Cell)
async def get_cell(cell_id: str, db: Session = Depends(get_db)):
    """Get cell by ID"""
    cell = await cell_service.get_cell(db, cell_id)

    if not cell:
        raise HTTPException(status_code=404, detail=f"Cell {cell_id} not found")

    return cell


@router.get("/", response_model=CellListResponse)
async def list_cells(
    cell_type: Optional[CellType] = None,
    status_filter: Optional[CellStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List cells with filters"""
    cells = await cell_service.list_cells(
        db, cell_type=cell_type, status=status_filter, skip=skip, limit=limit
    )

    return CellListResponse(
        total=len(cells),
        cells=cells,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.put("/{cell_id}", response_model=Cell)
async def update_cell(
    cell_id: str,
    request: CellUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update cell"""
    cell = await cell_service.update_cell(db, cell_id, request)

    if not cell:
        raise HTTPException(status_code=404, detail=f"Cell {cell_id} not found")

    return cell


@router.delete("/{cell_id}")
async def delete_cell(cell_id: str, db: Session = Depends(get_db)):
    """Delete (deactivate) cell"""
    success = await cell_service.delete_cell(db, cell_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Cell {cell_id} not found")

    return {"message": f"Cell {cell_id} deleted successfully"}
