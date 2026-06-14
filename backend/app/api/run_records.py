"""巡检记录API"""
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.run_record import RunRecord
from app.models.run_point import RunPoint
from app.models.run_plan import RunPlan
from app.schemas.run_record import RunRecordCreate, RunRecordResponse
from app.security import get_current_user
from app.websocket_manager import manager

router = APIRouter()


@router.post("")
async def create_record(data: RunRecordCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    record = RunRecord(
        plan_id=data.plan_id,
        point_id=data.point_id,
        user_id=current_user["id"],
        check_time=datetime.now(),
        nfc_uid=data.nfc_uid,
        latitude=data.latitude,
        longitude=data.longitude,
        status=data.status,
        remark=data.remark,
        photos=",".join(data.photos) if data.photos else None,
        is_offline=data.is_offline,
    )
    db.add(record)

    # Update plan status if exists
    if data.plan_id:
        plan = await db.get(RunPlan, data.plan_id)
        if plan:
            plan.status = 1

    await db.commit()
    await db.refresh(record)

    # Broadcast real-time progress update
    try:
        await manager.broadcast_progress({
            "plan_id": data.plan_id,
            "point_id": data.point_id,
            "status": data.status,
            "check_time": str(record.check_time),
            "user_name": current_user.get("username", ""),
        })
    except Exception:
        pass

    return {"id": record.id, "message": "提交成功"}


@router.get("")
async def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    point_id: int | None = None,
    plan_id: int | None = None,
    user_id: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(RunRecord).options(selectinload(RunRecord.point), selectinload(RunRecord.user))
    if point_id:
        query = query.where(RunRecord.point_id == point_id)
    if plan_id:
        query = query.where(RunRecord.plan_id == plan_id)
    if user_id:
        query = query.where(RunRecord.user_id == user_id)
    if date_from:
        query = query.where(RunRecord.check_time >= datetime.strptime(date_from, "%Y-%m-%d"))

    total_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_query)).scalar() or 0

    query = query.order_by(RunRecord.check_time.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    records = result.scalars().all()

    return {
        "list": [RunRecordResponse(
            id=r.id, plan_id=r.plan_id, point_id=r.point_id,
            point_name=r.point.name if r.point else None,
            user_id=r.user_id, user_name=r.user.real_name if r.user else None,
            check_time=str(r.check_time), status=r.status,
            remark=r.remark, is_offline=r.is_offline,
        ) for r in records],
        "total": total, "page": page, "page_size": page_size,
    }


@router.get("/today")
async def get_today_records(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    today = date.today()
    query = select(RunRecord).options(selectinload(RunRecord.point)).where(
        RunRecord.user_id == current_user["id"],
        func.date(RunRecord.check_time) == today,
    )
    result = await db.execute(query.order_by(RunRecord.check_time.desc()))
    records = result.scalars().all()
    return {"list": [{"id": r.id, "point_name": r.point.name if r.point else None, "check_time": str(r.check_time), "status": r.status} for r in records]}