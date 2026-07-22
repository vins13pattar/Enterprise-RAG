from sqlmodel import Session, select
from apps.api.app.db import init_db, engine
from packages.shared.models import User, Workspace, WorkspaceMembership, RoleName
from packages.ingestion.service import IngestionService
init_db()
with Session(engine) as s:
    u=s.exec(select(User).where(User.email=='admin@example.com')).first()
    w=Workspace(name='Demo Knowledge Base', description='Seeded enterprise documents')
    s.add(w); s.commit(); s.refresh(w); s.add(WorkspaceMembership(user_id=u.id,workspace_id=w.id,role=RoleName.admin)); s.commit()
    for path in ['sample-data/employee-leave-policy.md','sample-data/travel-reimbursement-policy.md','sample-data/information-security-policy.md','sample-data/product-documentation.md','sample-data/customer-support-faq.md']:
        IngestionService(s).create_document(w.id,path,'text/markdown',open(path).read(),u.id,path)
print('seeded')
