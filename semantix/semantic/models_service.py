import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from semantix.core.errors import AppError
from semantix.models.semantic import Metric, MdlRevision, SemanticModel
from semantix.semantic.mdl import parse_mdl_yaml


class SemanticService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_models(self, project_id: str) -> list[SemanticModel]:
        result = await self.session.scalars(
            select(SemanticModel).where(SemanticModel.project_id == project_id).order_by(SemanticModel.name)
        )
        return list(result.all())

    async def create_model(
        self,
        *,
        project_id: str,
        name: str,
        table_name: str,
        description: str | None,
        columns: list[dict],
    ) -> SemanticModel:
        existing = await self.session.scalar(
            select(SemanticModel).where(SemanticModel.project_id == project_id, SemanticModel.name == name)
        )
        if existing:
            raise AppError("model_exists", "Semantic model already exists", status_code=409)
        model = SemanticModel(
            project_id=project_id,
            name=name,
            table_name=table_name,
            description=description,
            columns_json=json.dumps(columns),
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def list_metrics(self, project_id: str) -> list[Metric]:
        result = await self.session.scalars(
            select(Metric).where(Metric.project_id == project_id).order_by(Metric.name)
        )
        return list(result.all())

    async def create_metric(
        self,
        *,
        project_id: str,
        name: str,
        model_name: str,
        expression: str,
        dimensions: list[str],
        description: str | None = None,
    ) -> Metric:
        metric = Metric(
            project_id=project_id,
            name=name,
            model_name=model_name,
            expression=expression,
            dimensions_json=json.dumps(dimensions),
            description=description,
            status="draft",
        )
        self.session.add(metric)
        await self.session.commit()
        await self.session.refresh(metric)
        return metric

    async def create_mdl_revision(self, *, project_id: str, yaml_text: str, note: str | None = None) -> MdlRevision:
        _, issues = parse_mdl_yaml(yaml_text)
        if issues:
            raise AppError(
                "mdl_invalid",
                "MDL validation failed",
                status_code=400,
                details=[{"code": i.code, "message": i.message, "path": i.path} for i in issues],
            )
        rev = MdlRevision(project_id=project_id, yaml_text=yaml_text, status="draft", note=note)
        self.session.add(rev)
        await self.session.commit()
        await self.session.refresh(rev)
        return rev

    async def publish_mdl_revision(self, *, project_id: str, revision_id: str) -> MdlRevision:
        rev = await self.session.scalar(
            select(MdlRevision).where(MdlRevision.id == revision_id, MdlRevision.project_id == project_id)
        )
        if rev is None:
            raise AppError("not_found", "MDL revision not found", status_code=404)
        rev.status = "published"
        models = await self.list_models(project_id)
        for model in models:
            model.published_revision_id = rev.id
        metrics = await self.list_metrics(project_id)
        for metric in metrics:
            metric.status = "published"
        await self.session.commit()
        await self.session.refresh(rev)
        return rev

    async def list_revisions(self, project_id: str) -> list[MdlRevision]:
        result = await self.session.scalars(
            select(MdlRevision)
            .where(MdlRevision.project_id == project_id)
            .order_by(MdlRevision.created_at.desc())
        )
        return list(result.all())
